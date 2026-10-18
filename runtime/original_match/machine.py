"""The guest machine: Unicorn running the original's code on a memory image (no original bytes here).

A 16-bit real-mode x86 with 1 MiB + the HMA mapped, holding the memory of a DOSBox-X savestate of goal (version 2).
Addresses are written as the listing writes them ('SSSS:OOOO', a paragraph of the load module and an offset) and
relocated by the load segment. Interrupts are swallowed: the BIOS and DOS calls the match makes are display,
speaker and keyboard, and the keyboard is answered by the kit's own hooks (match.py).

Stopping: a hook calls `stop(reason)`; Unicorn then leaves the instruction at the hooked address unexecuted, and
every hook at that address fires again when the run resumes there (probed: E033 notes, section 3). Handlers are
told so (`replay=True` on that first call after a resume) and those that count things skip it."""
try:                     # the kit imports without unicorn (a checkout that lacks it; the CI code tier installs it, #304); a match needs it
    from unicorn import Uc, UcError, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INTR, UC_HOOK_MEM_WRITE
    from unicorn import x86_const as X
except ImportError:
    Uc = None

    class UcError(Exception):
        pass

MEM_SIZE = 0x110000          # 1 MiB and the high memory area
DS_PARAGRAPH = 0x2581        # GOAL.EXE's data segment, a paragraph of the load module (static/goal-exe/README.md)
REGS = ("EAX", "EBX", "ECX", "EDX", "ESI", "EDI", "EBP", "ESP", "EFLAGS", "EIP", "CS", "DS", "ES", "SS", "FS", "GS")


class GuestError(RuntimeError):
    """The original did something the kit does not declare (an unknown key read, a stray routine)."""


class Machine:
    def __init__(self, memory, load):
        if Uc is None:
            raise ModuleNotFoundError("original_match needs the unicorn package to run a match: pip install unicorn")
        if len(memory) < MEM_SIZE:
            raise ValueError(f"the image holds {len(memory)} bytes of guest memory, {MEM_SIZE} are needed")
        self.uc = Uc(UC_ARCH_X86, UC_MODE_16)
        self.uc.mem_map(0, MEM_SIZE)
        self.uc.mem_write(0, bytes(memory[:MEM_SIZE]))
        self.load = load
        self.DS = load + DS_PARAGRAPH
        self.stop_reason = None
        self.error = None
        self._handlers = {}        # linear address -> [handler]
        self._resume_lin = None
        # The port mode (port/; inert without ports): the write listeners a port's write reaches as a guest write
        # would, the port at a routine's entry, the instruction a port's write or site stands for (pc()), and the
        # address a port returned to before a stop made inside it (not a replay when the run resumes there).
        self._writes = []          # (begin, end, fn(address, size, value))
        self._ports = {}           # linear address -> runner(machine)
        self._pc_override = None
        self.no_replay_at = None
        self.uc.hook_add(UC_HOOK_INTR, lambda uc, intno, data: None)

    # -- addresses ---------------------------------------------------------------------------------
    def seg(self, paragraph):
        return (self.load + paragraph) & 0xFFFF

    def lin(self, address):
        seg, off = address.split(":")
        return self.seg(int(seg, 16)) * 16 + int(off, 16)

    def where(self, seg, off):
        """A runtime segment:offset as the listing writes it."""
        return "%04X:%04X" % ((seg - self.load) & 0xFFFF, off)

    # -- memory --------------------------------------------------------------------------------------
    def read(self, linear, n):
        return bytes(self.uc.mem_read(linear, n))

    def write(self, linear, data):
        self.uc.mem_write(linear, bytes(data))

    def word_at(self, linear):
        return int.from_bytes(self.uc.mem_read(linear, 2), "little")

    def rd(self, off, n=2):
        """The little-endian value of n bytes at DS:off."""
        return int.from_bytes(self.uc.mem_read(self.DS * 16 + off, n), "little")

    def wr(self, off, value, n=2):
        self.uc.mem_write(self.DS * 16 + off, int(value).to_bytes(n, "little"))

    def far(self, off):
        """The linear address a far pointer at DS:off holds."""
        return self.rd(off + 2) * 16 + self.rd(off)

    def rd_far(self, ptr, off, n=2):
        """The value of n bytes at offset `off` of the record the far pointer DS:ptr points to."""
        return int.from_bytes(self.uc.mem_read(self.far(ptr) + off, n), "little")

    # -- registers and the stack ---------------------------------------------------------------------
    def reg(self, name):
        return self.uc.reg_read(getattr(X, f"UC_X86_REG_{name.upper()}"))

    def set_reg(self, name, value):
        self.uc.reg_write(getattr(X, f"UC_X86_REG_{name.upper()}"), value)

    def stack_word(self, offset):
        return self.word_at(self.reg("ss") * 16 + ((self.reg("sp") + offset) & 0xFFFF))

    def frame_word(self, bp, offset):
        return self.word_at(self.reg("ss") * 16 + ((bp + offset) & 0xFFFF))

    def return_from(self, far, pop=0):
        """Return to the caller as `retf pop` / `ret pop` would, from a routine's first instruction."""
        sp = self.reg("sp")
        ip = self.stack_word(0)
        if far:
            cs = self.stack_word(2)
            self.set_reg("sp", (sp + 4 + pop) & 0xFFFF)
            self.set_reg("cs", cs)
        else:
            self.set_reg("sp", (sp + 2 + pop) & 0xFFFF)
        self.set_reg("eip", ip)

    def far_call(self, target, args, return_to, ss, sp):
        """Set up the registers and stack of a far call of `target` ('SSSS:OOOO') with the argument words `args`
        (pushed in order, so the last is nearest the return address) returning to `return_to`, so that SP is `sp`
        at the routine's first instruction. Returns the linear address of the return."""
        rseg, roff = return_to.split(":")
        words = [int(roff, 16), self.seg(int(rseg, 16))] + list(reversed(args))
        for i, w in enumerate(words):
            self.write(ss * 16 + ((sp + 2 * i) & 0xFFFF), (w & 0xFFFF).to_bytes(2, "little"))
        tseg, toff = target.split(":")
        for name, value in (("ss", ss), ("sp", sp), ("ds", self.DS), ("es", self.DS),
                            ("cs", self.seg(int(tseg, 16))), ("eip", int(toff, 16))):
            self.set_reg(name, value)
        return self.lin(return_to)

    # -- hooks and running -------------------------------------------------------------------------------
    def at(self, address, handler):
        """Call handler(replay) when the guest reaches `address` ('SSSS:OOOO'), before its instruction runs."""
        lin = self.lin(address)
        if lin not in self._handlers:
            self._handlers[lin] = []

            def dispatch(uc, addr, size, data, lin=lin):
                replay = lin == self._resume_lin
                self._resume_lin = None
                try:
                    for h in list(self._handlers[lin]):
                        h(replay)
                        if self.stop_reason is not None or self.error is not None:
                            break
                    else:                       # a port runs after the kit's handlers, only when none stopped: it
                        runner = self._ports.get(lin)      # never ran before a replay, and once it ran CS:IP is
                        if runner is not None:             # its caller's, so it never runs twice
                            runner(self)
                            if self.stop_reason is not None:   # a site inside the port stopped: the run resumes at
                                self.no_replay_at = self.pc()  # the return, where no hook has fired yet
                except Exception as e:          # stop the emulation; run() re-raises it
                    self.error = e
                    uc.emu_stop()
            self.uc.hook_add(UC_HOOK_CODE, dispatch, begin=lin, end=lin)
        self._handlers[lin].append(handler)

    def port(self, address, runner):
        """Run runner(machine) in place of the routine at `address` (the port mode, port/): it runs from the entry,
        after every handler `at` the entry, and returns to the caller itself."""
        lin = self.lin(address)
        if lin in self._ports:
            raise ValueError(f"two ports of {address}")
        self._ports[lin] = runner
        if lin not in self._handlers:
            self.at(address, lambda replay: None)

    def on_write(self, begin, end, fn):
        """Call fn(address, size, value) at every write starting in [begin, end], before it lands: a guest
        instruction's (Unicorn's write hook) or a port's (write_as)."""
        def hook(uc, access, address, size, value, data):
            fn(address, size, value)
        self._writes.append((begin, end, fn))
        self.uc.hook_add(UC_HOOK_MEM_WRITE, hook, begin=begin, end=end)

    def write_as(self, linear, size, value, at):
        """A port's write of `size` bytes at `linear`, as the original's instruction at the linear address `at`
        makes it: every write listener sees it (with pc() = at) before it lands, as a guest write's hooks would."""
        value &= (1 << (8 * size)) - 1
        saved, self._pc_override = self._pc_override, at
        try:
            for begin, end, fn in list(self._writes):
                if begin <= linear <= end:
                    fn(linear, size, value)
                    if self.error is not None:       # a watch's handler refused the write
                        err, self.error = self.error, None
                        raise err
        finally:
            self._pc_override = saved
        self.uc.mem_write(linear, value.to_bytes(size, "little"))

    def fire(self, address):
        """A port reaching `address` inside the routine it replaces: the handlers `at` it run as the original's
        reaching it would (replay False, pc() = the address). A stop they make takes effect at the port's return."""
        lin = self.lin(address)
        saved, self._pc_override = self._pc_override, lin
        try:
            for h in list(self._handlers.get(lin, ())):
                h(False)
                if self.error is not None:
                    err, self.error = self.error, None
                    raise err
        finally:
            self._pc_override = saved

    def watch(self, linear, size, handler):
        """Call handler(old, new), the watched `size` bytes at `linear` before and after, at every guest write that
        touches them, before the write lands (Unicorn calls write hooks first: the old bytes are still in memory).
        A write that starts up to 3 bytes below the range is caught too. A port's write (write_as) is seen the same."""
        def hook(address, wsize, value):
            if address + wsize <= linear or address >= linear + size:
                return
            old = bytes(self.uc.mem_read(linear, size))
            new = bytearray(old)
            for i in range(wsize):
                j = address + i - linear
                if 0 <= j < size:
                    new[j] = (value >> (8 * i)) & 0xFF
            try:
                handler(old, bytes(new))
            except Exception as e:
                self.error = e
                self.uc.emu_stop()
        self.on_write(max(0, linear - 3), linear + size - 1, hook)

    def stop(self, reason):
        self.stop_reason = reason
        self.uc.emu_stop()

    def pc(self):
        """The linear address of the instruction running: during a port's write or site, the listing's."""
        if self._pc_override is not None:
            return self._pc_override
        return self.reg("cs") * 16 + self.reg("ip")

    def run(self, until, timeout_s=600, fresh=False):
        """Run from CS:IP until the linear address `until` or a stop; returns the stop reason (None at `until`).
        `fresh`: CS:IP is a new start (a call set up by far_call), not the instruction a stop left unexecuted; so is
        the return a port stopped at (no_replay_at)."""
        self.stop_reason = None
        start = self.pc()
        self._resume_lin = None if fresh or start == self.no_replay_at else start
        self.no_replay_at = None
        try:
            self.uc.emu_start(start, until, timeout=int(timeout_s * 1_000_000))
        except UcError as e:
            raise GuestError(f"the emulator stopped at {self.where(self.reg('cs'), self.reg('ip'))}: {e}") from e
        if self.error is not None:
            err, self.error = self.error, None
            raise err
        if self.stop_reason is None and self.pc() != until:
            raise GuestError(f"the run ended at {self.where(self.reg('cs'), self.reg('ip'))} without reaching its end "
                             f"(time limit {timeout_s} s)")
        return self.stop_reason

    # -- snapshots ---------------------------------------------------------------------------------------
    def snapshot(self):
        return {"memory": self.read(0, MEM_SIZE), "regs": {r: self.reg(r) for r in REGS}, "load": self.load}

    def restore(self, snap):
        self.write(0, snap["memory"])
        for r, v in snap["regs"].items():
            self.set_reg(r, v)
