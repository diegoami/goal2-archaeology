"""The proof mode (T59): every call of a ported routine run side by side with the original's (E021's rule, moved in
from runtime/emul/watched_match.py Guest.hook(prove=True)).

At a ported routine's entry, once the proof is armed (Match(prove=...)): the CPU is kept, the ORIGINAL routine runs
as plain guest code to its return, muted (machine.py: no handler, port or write listener of the kit runs in it, so
the kit sees nothing of it; another ported routine it calls runs as the original's too), with every byte it writes
recorded in order; its return state is taken, its writes are undone and the CPU is put back; then the port runs on
the same state, the kit live, its writes (its own and those of the original's code it calls, port/guest.py) recorded
the same way. At the port's return the two must be identical: the registers of REGS_RETURNED, and the written bytes
and their order outside the routine's own dead frame (from the lowest the original's stack reached while it wrote
up to the caller's SP after the return). The first difference raises ProofError naming the routine, the call, where
the match is and the byte (or the register); the match goes on from the port's state otherwise. A difference in
REGS_SCRATCH is counted per register, not an error (Turbo Pascal's convention: they are scratch across a call).

A call whose original reaches an address where the kit has a handler (a key read, a menu, the tick, an event's
routine) cannot run muted: the original would need the kit's answer, or the kit would miss what it observes. That
call is not proved: its original's writes are undone, the CPU put back, the port runs as in an unproved match, and
the call is counted in `unproved` with the address that stopped it. So is a call reached while another proof runs
(a ported routine the port calls). The hooks are added once, when the proof is installed (Unicorn keeps a deleted hook
listed until emu_start returns, E021); a write hook over all memory costs every guest write a Python call, so a
proved match is slower (locate.py only)."""
from .mem import PortError

# Compared at a proved call's return (E021 notes.md section 5): AX, DX (the result), and what the caller relies on.
REGS_RETURNED = ("AX", "DX", "SP", "BP", "SS", "DS", "CS", "IP")
# Not compared; a difference is counted per register (E021: the owner, 2026-10-11).
REGS_SCRATCH = ("BX", "CX", "SI", "DI", "ES", "FLAGS")
REGS_ALL = ("EAX", "EBX", "ECX", "EDX", "ESI", "EDI", "EBP", "ESP", "EFLAGS", "CS", "DS", "ES", "SS", "FS", "GS", "EIP")
# The instructions that write below SP (push, call, pushf, pusha, enter, int): during such a write Unicorn's SP is the
# value before it (E021, probed 2026-10-12), so the slot written is where the stack reaches. Opcodes after any prefix;
# FF only with /2, /3 (call) or /6 (push). From watched_match.py.
PUSH_OPCODES = {0x06, 0x0E, 0x16, 0x1E, *range(0x50, 0x58), 0x60, 0x68, 0x6A, 0x9A, 0x9C, 0xC8, 0xCC, 0xCD, 0xCE, 0xE8}
PUSH_0F = {0xA0, 0xA8}
PREFIXES = {0x26, 0x2E, 0x36, 0x3E, 0x64, 0x65, 0x66, 0x67, 0xF0, 0xF2, 0xF3}


class ProofError(RuntimeError):
    """A port differs from the original routine at one call (the message names the routine, the call, the byte or
    the register)."""


def pushes(code):
    """Does the instruction whose bytes start `code` write below SP (a push or a call)?"""
    i = 0
    while i < len(code) - 1 and code[i] in PREFIXES:
        i += 1
    op = code[i]
    if op == 0x0F:
        return code[i + 1] in PUSH_0F
    if op == 0xFF:
        return (code[i + 1] >> 3) & 7 in (2, 3, 6)
    return op in PUSH_OPCODES


class _Call:
    """The proof of one call in progress."""

    def __init__(self, address, number, runner, done, regs, ss, sp, ret_lin, ret_sp):
        self.address, self.number, self.runner, self.done = address, number, runner, done
        self.regs, self.ss, self.sp, self.ret_lin, self.ret_sp = regs, ss, sp, ret_lin, ret_sp
        self.phase = "original"
        self.writes = []            # the original's: (linear, old bytes, new bytes) in order
        self.model = []             # the port's: (linear, byte) in order
        self.low = ss * 16 + sp
        self.original_regs = None
        self.where = ""


class Prover:
    """The proof of every installed port's calls (port.install's Installed). armed() says whether a call is proved
    (Match: from a given draw on); where() describes the match's point for a message (the minute, the draw)."""

    def __init__(self, machine, installed, armed=lambda: True, where=lambda: ""):
        from ..machine import MEM_SIZE
        if machine.muted_hook is not None:
            raise PortError("one proof per machine")
        self.m, self.armed, self.where = machine, armed, where
        self.state = None
        self.proved, self.unproved, self.scratch = {}, {}, {}
        self.first_scratch = {}
        names = {}
        for reg, _ in installed.loaded:
            for address in reg.entries:
                names[address] = reg.name
        self.names = names
        for address in names:
            lin = machine.lin(address)
            machine._ports[lin] = self._wrap(address, machine._ports[lin], installed.calls)
            self.proved[address] = 0
            self.unproved[address] = {}
            self.scratch[address] = {r: 0 for r in REGS_SCRATCH}
        machine.on_write(0, MEM_SIZE - 1, self._record, always=True)    # once, before the run
        machine.muted_hook = self._muted_at

    # -- the entry: the original first, muted --------------------------------------------------------------------
    def _wrap(self, address, runner, calls):
        def run(machine, done=None):
            if self.state is not None or not self.armed():
                return runner(machine, done)        # a port called inside a proof, or before the proof starts
            m = machine
            far, pop = runner.entry.far, runner.entry.pop
            sp, ss = m.reg("sp"), m.reg("ss")
            ip = m.stack_word(0)
            cs = m.stack_word(2) if far else m.reg("cs")
            st = _Call(address, calls.get(address, 0) + 1, runner, done, {r: m.reg(r) for r in REGS_ALL}, ss, sp,
                       cs * 16 + ip, (sp + (4 if far else 2) + pop) & 0xFFFF)
            st.where = self.where()
            st.caller = m.where(cs, ip)
            self.state = st
            if st.ret_lin not in m._handlers:     # the return address is where the original's run ends
                from ..machine import NOOP
                m.at_linear(st.ret_lin, NOOP)
            m.muted = True                          # the guest now runs the original's entry instruction
        run.entry = runner.entry
        return run

    def _record(self, address, size, value):
        st = self.state
        if st is None:
            return
        new = (value & ((1 << (8 * size)) - 1)).to_bytes(size, "little")
        if st.phase == "original":
            m = self.m
            st.writes.append((address, m.read(address, size), new))
            if m.reg("ss") == st.ss:            # how far the stack reached
                sp = st.ss * 16 + m.reg("sp")
                if pushes(m.read(m.pc(), 6)) and sp - 16 <= address < sp:
                    sp = address
                st.low = min(st.low, sp)
        elif st.phase == "model":
            st.model.extend((address + i, b) for i, b in enumerate(new))

    def _muted_at(self, lin):
        """The muted original reached a hooked address: its own return, a site of the kit (the proof gives way), or a
        port's entry or a guest call's return (guest code here)."""
        st, m = self.state, self.m
        if lin == st.ret_lin and m.reg("ss") == st.ss and m.reg("sp") == st.ret_sp:
            self._original_returned()
        elif m.hooked(lin):
            self._give_way(m.where(m.reg("cs"), m.reg("ip")))

    def _undo(self, st):
        m = self.m
        for address, old, _ in reversed(st.writes):
            m.write(address, old)
        for r, v in st.regs.items():
            m.set_reg(r, v)

    def _give_way(self, site):
        st = self.state
        self._undo(st)
        self.m.muted = False
        self.state = None
        counts = self.unproved[st.address]
        counts[site] = counts.get(site, 0) + 1
        st.runner(self.m, st.done)              # the port, as in an unproved match

    # -- the return: the port on the same state, then the comparison ----------------------------------------------
    def _original_returned(self):
        st, m = self.state, self.m
        m.muted = False
        st.original_regs = {r: m.reg(r) for r in REGS_RETURNED + REGS_SCRATCH}
        self._undo(st)
        st.phase = "model"
        st.runner(m, self._model_done)

    def _model_done(self, frame):
        st, m = self.state, self.m
        self.state = None
        try:
            self._compare(st, {r: m.reg(r) for r in REGS_RETURNED + REGS_SCRATCH})
        finally:
            if st.done is not None:
                st.done(frame)

    def describe(self, linear):
        ds = self.m.DS * 16
        where = f" (DS:{linear - ds:04X})" if ds <= linear < ds + 0x10000 else ""
        return f"linear 0x{linear:05X}{where}"

    def _compare(self, st, model_regs):
        m = self.m
        frame = (st.low, st.ss * 16 + m.reg("sp"))

        def live(ws):
            return [(a, b) for a, b in ws if not frame[0] <= a < frame[1]]
        original = live([(a + i, n[i]) for a, _, n in st.writes for i in range(len(n))])
        model = live(st.model)
        head = (f"{st.address} ({self.names[st.address]}), call #{st.number} from {st.caller}"
                + (f", {st.where}" if st.where else ""))
        for i, (o, p) in enumerate(zip(original, model)):
            if o != p:
                raise ProofError(f"{head}: written byte #{i} differs: the original wrote 0x{o[1]:02X} at "
                                 f"{self.describe(o[0])}, the port wrote 0x{p[1]:02X} at {self.describe(p[0])}")
        if len(original) != len(model):
            i = min(len(original), len(model))
            who, extra = ("original", original[i]) if len(original) > i else ("port", model[i])
            raise ProofError(f"{head}: the {who} writes more: byte #{i}, 0x{extra[1]:02X} at {self.describe(extra[0])} "
                             f"({len(original)} bytes by the original, {len(model)} by the port)")
        for r in REGS_RETURNED:
            if st.original_regs[r] != model_regs[r]:
                raise ProofError(f"{head}: register {r} at the return: the original 0x{st.original_regs[r]:04X}, "
                                 f"the port 0x{model_regs[r]:04X}")
        for r in REGS_SCRATCH:
            if st.original_regs[r] != model_regs[r]:
                self.scratch[st.address][r] += 1
        self.proved[st.address] += 1

    def summary(self):
        """{address: {"proved": n, "unproved": {site: n}, "scratch": {register: n}}}."""
        return {a: {"proved": self.proved[a], "unproved": dict(self.unproved[a]),
                    "scratch": {r: n for r, n in self.scratch[a].items() if n}} for a in self.names}
