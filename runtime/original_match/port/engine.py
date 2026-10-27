"""T78a: run registered Python ports on plain memory, never original instructions.

The control protocol is machine.py with guest.PortFrame: entry handlers precede
ports, near/far returns retain their declared stack ABI, and a stop inside a
ported body is deferred until it yields/returns. This is assembly machinery,
not an x86 interpreter. Unregistered execution addresses are refused.
"""
import time

from ..machine import Machine, MEM_SIZE, DS_PARAGRAPH, REGS, NOOP
from .mem import MachineMem, PortError


class _PortMemory(MachineMem):
    def read(self, linear, n):
        # As MachineMem's native read, a port's own read is not a kit IO-tap read.
        self.m._bounds(linear, n)
        return bytes(self.m._memory[linear:linear+n])


class PortMachine(Machine):
    """The existing port/call/listener interface with no Unicorn object or opcode runner."""
    def __init__(self, memory, load):
        if len(memory) < MEM_SIZE:
            raise ValueError(f'the image holds {len(memory)} bytes; {MEM_SIZE} are needed')
        self._memory = bytearray(memory[:MEM_SIZE])
        self._registers = {name.lower(): 0 for name in REGS}
        # x86 reserved flag bit1, independently checked against the reference API
        # by out/T78a/register-controls-v1.json; other supplied bits are retained.
        self._registers['eflags'] = 2
        self.load, self.DS = load, load + DS_PARAGRAPH
        self.proving = False
        self.foreign_hooks = 0
        self._recorder = None
        self.stop_reason = self.error = None
        self._handlers, self._ports = {}, {}
        self._resume_lin = self._pc_override = self.no_replay_at = None
        self._writes, self.frames = [], []
        self.muted = False
        self.muted_hook = self.site_tap = self.write_tap = None
        self.io_tap = self.listen_tap = None
        self.running = False

    def port_memory(self, keys=None):
        return _PortMemory(self, keys)

    @staticmethod
    def _bounds(linear, n):
        if (not isinstance(linear, int) or not isinstance(n, int)
                or linear < 0 or n < 0 or linear+n > MEM_SIZE):
            raise PortError(f'plain-memory read/write outside mapped range: {linear}+{n}')

    def read(self, linear, n):
        self._bounds(linear, n)
        data = bytes(self._memory[linear:linear+n])
        if self.io_tap is not None:self.io_tap('r', linear, data)
        return data

    def write(self, linear, data):
        data = bytes(data);self._bounds(linear, len(data))
        if self.write_tap is not None:self.write_tap(linear, data)
        self._memory[linear:linear+len(data)] = data

    @staticmethod
    def _alias(name):
        name = name.lower()
        if name in ('eax','ebx','ecx','edx','esi','edi','ebp','esp','eip','eflags'):
            return name, 0, 32
        if name in ('cs','ds','es','ss','fs','gs'):
            return name, 0, 16
        if name in ('ax','bx','cx','dx','si','di','bp','sp','ip','flags'):
            return 'e'+name, 0, 16
        if len(name)==2 and name[0] in 'abcd' and name[1] in 'lh':
            return 'e'+name[0]+'x', 8 if name[1]=='h' else 0, 8
        raise PortError(f'unsupported plain register {name!r}')

    def reg(self, name):
        base, shift, bits = self._alias(name)
        value = self._registers[base] >> shift & ((1 << bits)-1)
        if self.io_tap is not None:self.io_tap('g', name.lower(), value)
        return value

    def set_reg(self, name, value):
        base, shift, bits = self._alias(name)
        mask = ((1 << bits)-1) << shift
        self._registers[base] = ((self._registers[base] & ~mask) | ((value << shift) & mask)) & 0xFFFFFFFF
        if base=='eflags':self._registers[base] |= 2
        if self.io_tap is not None:self.io_tap('s', name.lower(), value)

    def at_linear(self, linear, handler):
        self._handlers.setdefault(linear, []).append(handler)

    def _add_write(self, begin, end, fn, recorder):
        self._writes.append((begin, end, fn, recorder))

    def write_as(self, linear, size, value, at):
        self._bounds(linear, size)
        value &= (1 << (8*size))-1
        saved, self._pc_override = self._pc_override, at
        try:
            for index, (begin, end, fn, recorder) in enumerate(list(self._writes)):
                if begin <= linear <= end and (recorder or not self.muted):
                    if recorder:fn(linear, size, value)
                    else:self._listen(index, fn, linear, size, value)
                    if self.error is not None:
                        error, self.error = self.error, None
                        raise error
        finally:self._pc_override = saved
        self._memory[linear:linear+size] = value.to_bytes(size, 'little')

    def watch(self, linear, size, handler):
        def hook(address, wsize, value):
            if address+wsize <= linear or address >= linear+size:return
            old = self.read(linear, size);new = bytearray(old)
            for i in range(wsize):
                j = address+i-linear
                if 0 <= j < size:new[j] = value >> (8*i) & 255
            try:handler(old, bytes(new))
            except Exception as error:self.error = error
        self.on_write(max(0, linear-3), linear+size-1, hook)

    def stop(self, reason):
        self.stop_reason = reason

    def _dispatch(self, linear):
        replay = linear == self._resume_lin
        self._resume_lin = None
        handlers = list(self._handlers.get(linear, ()))
        tap = self.site_tap if any(h is not NOOP for h in handlers) else None
        if tap is not None:tap.site_enter(linear, replay)
        stopped = False
        for handler in handlers:
            handler(replay)
            if self.stop_reason is not None or self.error is not None:
                stopped = True;break
        if tap is not None:tap.site_leave(linear, stopped)
        if stopped:return
        runner = self._ports.get(linear)
        frame = self.frames[-1] if self.frames else None
        if runner is not None:runner(self)
        elif frame is not None and frame.ret_lin==linear and frame.returned(self):
            self.frames.pop();frame.resume(self)
        elif self.pc()!=linear:
            return  # a registered kit service explicitly returned/redirected
        else:
            raise PortError('no registered port/return at '+self.where(self.reg('cs'), self.reg('ip')))
        if self.stop_reason is not None:self.no_replay_at = self.pc()

    def run(self, until, timeout_s=600, fresh=False):
        if self.muted:raise PortError('plain engine cannot execute a muted original proof')
        self.stop_reason = None
        start = self.pc()
        self._resume_lin = None if fresh or start==self.no_replay_at else start
        self.no_replay_at = None
        deadline = time.monotonic()+timeout_s
        self.running = True
        try:
            while self.pc()!=until:
                if time.monotonic() > deadline:raise PortError('plain dispatch time limit exceeded')
                self._dispatch(self.pc())
                if self.error is not None:
                    error, self.error = self.error, None
                    raise error
                if self.stop_reason is not None:break
        finally:self.running = False
        return self.stop_reason
