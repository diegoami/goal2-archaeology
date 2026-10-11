#!/usr/bin/env python3
"""Unicorn emulation of a whole watched match of the original, with declared inputs and a
substitution hook (T38, milestone M0; E021 notes.md).

`Guest` is a Unicorn machine resumed from a DOSBox-X 2024.03.01 savestate: guest memory from the
`Memory` component (savestate.py, F001) and the CPU's registers, flags and segments from the `CPU`
component (layout calibrated in E021 notes.md §1). `Guest.hook(address, fn)` substitutes a routine:
when the guest reaches the routine's entry, `fn(guest)` runs instead (it reads and writes registers
and memory through the guest), the guest returns as the routine's own `ret`/`retf n` would (read
from the routine's listing block, or given), and the routine's own code is not executed; every
hooked call is counted in `guest.hook_counts[address]`.

`WatchedMatch(savestate_bytes)` resumes an E011 watchstart state (the captain screen `0791:CC7B`,
inside the wait `CC2E`, before the kick-off; notes.md §1) and runs the original as guest code to
the full-time board: the rest of the captain screen and of `ED8A`'s tail, `0791:F1F6`, the match
proper `0791:F098` (first half, walk-off `9955`, the half-time sequence `9A32` with its board and
team screen, the second half, the full-time walk-off), `CAB0`, `15B9`, and the board `0791:0106`,
stopping at the board's key wait (`0791:0415`, `call far 214B:08DD`; the "hit any key" screen
E011's records read as "full time"). Interventions, and nothing else (notes.md §2):
- interrupts swallowed (the BIOS/DOS calls are display, speaker and keyboard);
- the key thunk `214B:0723` (keypressed) answers "no key" unless a key is queued, and the key read
  `214B:08DD` is answered at the declared stopped screens only, each with the key E004's discipline
  sends there: the starting burst's Enter at the captain screen (queued at the start), an Enter at
  the half-time board (`0106`'s read, returning to `0791:041A`) and an Enter at the half-time team
  screen (`214B:1560`'s read, returning to `214B:157C`, called by `ED8A` at `0791:EE9A`); any other
  key read voids the run (`KeyWaitError`); a read with the pushed-back flag `DS:79AE` set runs as
  guest code (it waits for nothing);
- the `000E` wait family (05F6/0572/04F5/045D, an RNG consumer reachable from menu code only) is
  skipped and LOGGED in `strays`, which must stay empty (E010's lesson; watched.py);
- declared input writes into the start state (`inputs`), each recorded with its address, old and
  new bytes (an I3 intervention); `run()` always declares one: the delay byte `[DS:A923]+0x3F`
  := 0, the effect of the starting burst's five Rights (`0791:9372` lowers it per key code 0xAF),
  which E011's records read 0 at full time.
Every value the main seed word `DS:7B62` takes is recorded with the match clock (`draws`: the
ordered (minute DS:831F, sub-tick DS:831D, before, after) of every write to the word, by guest
code or by a hook's fn), and the clock `0791:970C`'s entries are marked (`tick_marks`), so
`tick_values()` gives the (minute, sub-tick) -> seed-values sets the ground-truth reads are
checked against tick-exactly (E011 notes.md §6), the stalls included.

Requirements: python3-unicorn; a watchstart savestate (release E011, fetched by sha256)."""
import io
import re
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402
from unicorn import (Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE,  # noqa: E402
                     UC_HOOK_MEM_WRITE)
from unicorn import x86_const as X  # noqa: E402

LISTINGS = ROOT / "static" / "goal-exe" / "code"
DS_PARAGRAPH = 0x2581                  # static/goal-exe/README.md, "Data segment 2581"

# The savestate's CPU component (zlib stream), calibrated on the four E011 states (notes.md §1):
CPU_GPR = 0x00      # EAX ECX EDX EBX ESP EBP ESI EDI, 32-bit each
CPU_EIP = 0x20      # 32-bit
CPU_FLAGS = 0x28    # 64-bit
CPU_SEGS = 0xEB     # ES CS SS DS FS GS, a word every CPU_SEG_STRIDE bytes
CPU_SEG_STRIDE = 8
GPR_NAMES = ("EAX", "ECX", "EDX", "EBX", "ESP", "EBP", "ESI", "EDI")
SEG_NAMES = ("ES", "CS", "SS", "DS", "FS", "GS")

ENTER = 0x0D        # 214B:08DD stores AL of INT 16h AH=0 (0x1C0D for Enter) in DS:A976/A977


def cpu_state(data):
    """The registers a DOSBox-X 2024.03.01 savestate holds: {name: value} (notes.md §1)."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        d = zlib.decompressobj().decompress(z.read("CPU"))
    regs = dict(zip(GPR_NAMES, struct.unpack_from("<8I", d, CPU_GPR)))
    regs["EIP"] = struct.unpack_from("<I", d, CPU_EIP)[0]
    regs["EFLAGS"] = struct.unpack_from("<Q", d, CPU_FLAGS)[0] & 0xFFFFFFFF
    for i, name in enumerate(SEG_NAMES):
        regs[name] = struct.unpack_from("<H", d, CPU_SEGS + CPU_SEG_STRIDE * i)[0]
    return regs


def parse_address(address):
    """'214B:0688' or (0x214B, 0x0688) -> (image paragraph, offset)."""
    if isinstance(address, str):
        seg, off = address.split(":")
        return int(seg, 16), int(off, 16)
    return tuple(address)


def routine_return(address):
    """How the routine at `address` returns, from its block in the listing: (far, pop bytes).
    Every `ret`/`retf` of the block must agree; a block without one, or with two forms, raises."""
    return routine_returns(address)[:2]


def routine_returns(address):
    """(far, pop bytes, [offsets of the block's ret/retf instructions]) from the listing."""
    seg, off = parse_address(address)
    head = f"; ---- routine {seg:04X}:{off:04X} "
    forms = set()
    offsets = []
    for path in sorted(LISTINGS.glob(f"seg_{seg:04X}_*.asm")):
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            if line.startswith(head):
                for body in lines[i + 1:]:
                    if body.startswith("; ---- routine"):
                        break
                    m = re.match(r"^[0-9A-F]{4}  [0-9A-F ]+?\s{2,}(retf|ret)(?: (0x[0-9a-f]+|\d+))?\s*$", body)
                    if m:
                        forms.add((m.group(1) == "retf", int(m.group(2), 0) if m.group(2) else 0))
                        offsets.append(int(body[:4], 16))
                if len(forms) != 1:
                    raise ValueError(f"routine {seg:04X}:{off:04X}: return forms {sorted(forms)} in {path.name}")
                far, pop = forms.pop()
                return far, pop, offsets
    raise ValueError(f"routine {seg:04X}:{off:04X} not found under {LISTINGS}")


class ProofError(RuntimeError):
    """A hooked model differs from the original routine at one call (Guest.hook(prove=True))."""


# Compared at a proved call's return: the Turbo Pascal convention's result registers (AX, DX)
# and the state the caller relies on (SP, BP, SS, DS, and the return address CS:IP). BX, CX,
# SI, DI, ES and the flags are scratch across a call in that convention (E021 notes.md §5).
REGS_RETURNED = ("AX", "DX", "SP", "BP", "SS", "DS", "CS", "IP")
# Not compared, but a difference at the return is a WARNING, counted per register
# (`scratch_differences`; the first one per register is printed to stderr): the owner, 2026-10-11.
REGS_SCRATCH = ("BX", "CX", "SI", "DI", "ES", "FLAGS")
REGS_ALL = ("EAX", "EBX", "ECX", "EDX", "ESI", "EDI", "EBP", "ESP", "EFLAGS",
            "CS", "DS", "ES", "SS", "FS", "GS", "EIP")


class _RecordingUc:
    """Stands in for the Unicorn object while a hook's fn runs: every `mem_write` (through
    `Guest.put`, `set_word` or `guest.mu.mem_write` itself) is recorded byte by byte, in order,
    and reported to the watched words at write time; everything else is the real object's."""

    def __init__(self, guest, uc):
        self._guest, self._uc = guest, uc

    def __getattr__(self, name):
        return getattr(self._uc, name)

    def mem_write(self, address, data):
        self._guest._fn_write(address, bytes(data))


class KeyWaitError(RuntimeError):
    """The guest waited for a key at a screen the harness does not declare: the run is void."""


class Guest:
    """A Unicorn machine (16-bit real mode, 1 MiB + HMA) holding GOAL.EXE's memory.

    `Guest(savestate_bytes)` resumes the savestate's own CPU state; `Guest.from_memory(...)` builds
    a bare machine (the tests' synthetic programs). Addresses given as 'SSSS:OOOO' are image
    paragraphs, relocated by the load segment (`seg()`)."""

    def __init__(self, data=None, *, memory=None, load=0, regs=None):
        self.mu = self._uc = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x110000)
        if data is not None:
            st = savestate.Savestate(data)
            self.load = st.program().ds_base // 16 - DS_PARAGRAPH
            self.mu.mem_write(0, bytes(st.mem[savestate.MEM_BASE:savestate.MEM_BASE + 0x110000]))
            regs = cpu_state(data)
        else:
            self.load = load
            if memory:
                self.mu.mem_write(0, bytes(memory))
        self.DS = self.load + DS_PARAGRAPH
        self.start_regs = dict(regs or {})
        for name, value in self.start_regs.items():
            self.mu.reg_write(getattr(X, f"UC_X86_REG_{name}"), value)
        self.hook_counts = {}
        self._watch = []          # (linear, on_change(old, new)) words whose fn writes are reported
        self._fn_writes = None    # (linear, byte) per byte a running fn writes
        self.suppress_guest_watch = False   # set while a proved call runs the original
        self.proved_calls = {}    # address -> calls compared without a difference
        self.scratch_differences = {}   # address -> {register: proved calls where it differed}
        self.error = None         # an error a callback met; it stops the emulation

    # -- addresses and memory ------------------------------------------------------------------
    def seg(self, paragraph):
        return self.load + paragraph

    def lin(self, address):
        seg, off = parse_address(address)
        return self.seg(seg) * 16 + off

    def mem(self, linear, n):
        return bytes(self.mu.mem_read(linear, n))

    def word_at(self, linear):
        return int.from_bytes(self.mu.mem_read(linear, 2), "little")

    def put(self, linear, raw):
        """Write guest memory. Inside a hook's fn `mu` is a `_RecordingUc`, so the write is
        recorded and every watched word it touches is reported at write time, with its value
        before and after (a same-value write and a write later undone included): Python writes
        do not reach Unicorn's memory hooks."""
        self.mu.mem_write(linear, bytes(raw))

    def _fn_write(self, linear, raw):
        touched = [(lin, self.word_at(lin), cb) for lin, cb in self._watch
                   if linear < lin + 2 and lin < linear + len(raw)]
        self._uc.mem_write(linear, raw)
        self._fn_writes.extend((linear + i, b) for i, b in enumerate(raw))
        for lin, old, cb in touched:
            cb(old, self.word_at(lin))

    def word(self, segment, offset):
        """The word at segment:offset, with segment a runtime value (a far pointer's)."""
        return self.word_at(segment * 16 + offset)

    def set_word(self, segment, offset, value):
        self.put(segment * 16 + offset, (value & 0xFFFF).to_bytes(2, "little"))

    def rd(self, off, n=2):
        return int.from_bytes(self.mu.mem_read(self.DS * 16 + off, n), "little")

    def far(self, off):
        """The linear address a far pointer at DS:off holds."""
        return self.rd(off + 2) * 16 + self.rd(off)

    def reg(self, name):
        return self.mu.reg_read(getattr(X, f"UC_X86_REG_{name.upper()}"))

    def set_reg(self, name, value):
        self.mu.reg_write(getattr(X, f"UC_X86_REG_{name.upper()}"), value)

    def stack_word(self, offset):
        return self.word_at(self.reg("ss") * 16 + ((self.reg("sp") + offset) & 0xFFFF))

    def arg(self, i, far=True):
        """At a routine's entry: the i-th argument word from the top of the stack (the last pushed
        is 0), past the return address (4 bytes for a far call, 2 for a near one)."""
        return self.stack_word((4 if far else 2) + 2 * i)

    def return_from(self, far, pop):
        """Return to the caller as `retf pop` / `ret pop` would, from a routine's entry."""
        sp = self.reg("sp")
        ip = self.stack_word(0)
        if far:
            cs = self.stack_word(2)
            self.set_reg("sp", (sp + 4 + pop) & 0xFFFF)
            self.set_reg("cs", cs)
        else:
            self.set_reg("sp", (sp + 2 + pop) & 0xFFFF)
        self.set_reg("eip", ip)            # 16-bit mode: EIP is the offset in CS

    def watch_word(self, linear, on_change):
        """Report every write a hook's fn makes to the word at `linear`, at write time (`put`);
        a change made around `put` (straight to `mu`) is reported when the fn returns. Guest
        writes are the caller's to watch with a memory hook."""
        self._watch.append((linear, on_change))

    # -- the substitution hook ----------------------------------------------------------------
    def _run_fn(self, fn):
        """Run a hook's fn with `mu` recording; return the bytes it wrote, in order."""
        last = {lin: self.word_at(lin) for lin, cb in self._watch}

        def seen(lin, cb):
            def report(old, new):
                last[lin] = new
                cb(old, new)
            return report
        watch, self._watch = self._watch, [(lin, seen(lin, cb)) for lin, cb in self._watch]
        self._fn_writes = []
        self.mu = _RecordingUc(self, self._uc)
        try:
            fn(self)
        finally:
            self.mu = self._uc
            self._watch = watch
            writes, self._fn_writes = self._fn_writes, None
        for lin, cb in watch:              # a change made past the recorder (guest._uc)
            now = self.word_at(lin)
            if now != last[lin]:
                cb(last[lin], now)
        return writes

    def describe(self, linear):
        ds = self.DS * 16
        where = f" (DS:{linear - ds:04X})" if ds <= linear < ds + 0x10000 else ""
        return f"linear 0x{linear:05X}{where}"

    def hook(self, address, fn, ret=None, prove=False, ret_at=None):
        """Substitute the routine at `address` ('SSSS:OOOO', an image paragraph and offset): when
        the guest reaches its entry, `fn(self)` runs instead and the guest returns as the routine
        would — `ret` = (far, pop bytes), by default read from the routine's listing block (with
        `ret` given, `ret_at` lists the offsets of its return instructions, for a proof). The
        routine's own code is not executed. Calls are counted in `hook_counts[address]`.

        With `prove=True` every call is also a side-by-side proof (E021 notes.md §5): the CPU is
        snapshotted, the ORIGINAL routine runs as guest code to its own `ret`/`retf` (the
        listing's) with every byte it writes recorded in order (address, old, new), its return
        state is taken, memory and registers are put back, `fn` runs on the same state with its
        writes recorded the same way, and the two must be identical: the registers of
        REGS_RETURNED after the return, and the written bytes and their order, outside the
        routine's own stack frame (SS below the caller's SP after the return: the return address,
        the arguments, saved registers and locals, dead once it returns). The first difference
        raises ProofError naming the call number, the address and the byte (or the register).
        The match continues from the model's state; `proved_calls[address]` counts clean calls.
        A difference in BX, CX, SI, DI, ES or the flags at the return is not an error but a WARNING,
        counted per register in `scratch_differences[address]`.
        (A proved call runs the original as guest code; the substituted run is `prove=False`.)"""
        seg, off = parse_address(address)
        key = f"{seg:04X}:{off:04X}"
        far, pop, ret_offsets = routine_returns(key) if ret is None else (*ret, ret_at)
        self.hook_counts[key] = 0
        state = {"phase": None}
        if prove:
            if not ret_offsets:
                raise ValueError(f"{key}: a proof needs the routine's return instructions from the listing")
            self.proved_calls[key] = 0
            self.scratch_differences[key] = {r: 0 for r in REGS_SCRATCH}

        def stop(uc, e):
            self.error = e
            uc.emu_stop()

        def record_original(uc, access, address, size, value, data):
            if state["phase"] != "original":
                return
            old = bytes(uc.mem_read(address, size))
            new = (value & ((1 << (8 * size)) - 1)).to_bytes(size, "little")
            state["writes"].append((address, old, new))

        def at_entry(uc, addr, size, data):
            if state["phase"] == "original":
                return                     # a nested call inside the original runs as guest code
            try:
                self.hook_counts[key] += 1
                if not prove:
                    self._run_fn(fn)
                    self.return_from(far, pop)
                    return
                state.update(phase="original", writes=[], regs={r: self.reg(r) for r in REGS_ALL},
                             ss=self.reg("ss"), sp=self.reg("sp"))
                self.suppress_guest_watch = True
            except Exception as e:        # stop the emulation and re-raise after it
                stop(uc, e)

        def at_return(uc, addr, size, data):
            if state["phase"] != "original" or self.reg("sp") != state["sp"] or self.reg("ss") != state["ss"]:
                return                     # not the proved call's own return
            try:
                state["phase"] = None
                self.suppress_guest_watch = False
                self.return_from(far, pop)
                frame = (state["ss"] * 16, state["ss"] * 16 + self.reg("sp"))
                original_regs = {r: self.reg(r) for r in REGS_RETURNED + REGS_SCRATCH}
                original = [(a + i, n[i]) for a, o, n in state["writes"] for i in range(len(n))]
                for a, o, n in reversed(state["writes"]):     # undo the original
                    uc.mem_write(a, o)
                for r, v in state["regs"].items():
                    self.set_reg(r, v)
                model = self._run_fn(fn)
                self.return_from(far, pop)
                model_regs = {r: self.reg(r) for r in REGS_RETURNED + REGS_SCRATCH}

                def live(ws):
                    return [(a, b) for a, b in ws if not frame[0] <= a < frame[1]]
                original, model = live(original), live(model)
                call = self.hook_counts[key]
                for i, (o, m) in enumerate(zip(original, model)):
                    if o != m:
                        raise ProofError(
                            f"call #{call} of {key}: written byte #{i} differs: the original wrote 0x{o[1]:02X}"
                            f" at {self.describe(o[0])}, the model wrote 0x{m[1]:02X} at {self.describe(m[0])}")
                if len(original) != len(model):
                    i = min(len(original), len(model))
                    who, extra = ("original", original[i]) if len(original) > i else ("model", model[i])
                    raise ProofError(
                        f"call #{call} of {key}: the {who} writes more: byte #{i}, 0x{extra[1]:02X} at"
                        f" {self.describe(extra[0])} ({len(original)} original bytes, {len(model)} model bytes)")
                for r in REGS_RETURNED:
                    if original_regs[r] != model_regs[r]:
                        raise ProofError(f"call #{call} of {key}: register {r} at the return: the original"
                                         f" 0x{original_regs[r]:04X}, the model 0x{model_regs[r]:04X}")
                counts = self.scratch_differences[key]
                for r in REGS_SCRATCH:
                    if original_regs[r] != model_regs[r]:
                        if counts[r] == 0:
                            print(f"WARNING: call #{call} of {key}: uncompared register {r} at the return:"
                                  f" the original 0x{original_regs[r]:04X}, the model 0x{model_regs[r]:04X}"
                                  f" (counted, not an error; further ones counted only)", file=sys.stderr)
                        counts[r] += 1
                self.proved_calls[key] += 1
            except Exception as e:
                stop(uc, e)

        lin = self.lin(key)
        self.mu.hook_add(UC_HOOK_CODE, at_entry, begin=lin, end=lin)
        if prove:
            # one memory-write hook for the whole run, recording only while a call's original runs
            # (a hook added and deleted per call slows Unicorn down call by call: deleted hooks
            # stay listed until emu_start returns)
            self.mu.hook_add(UC_HOOK_MEM_WRITE, record_original, begin=0, end=0x10FFFF)
            for r_off in ret_offsets:
                rl = self.seg(seg) * 16 + r_off
                self.mu.hook_add(UC_HOOK_CODE, at_return, begin=rl, end=rl)
        return key

    def emulate(self, until, timeout_s):
        cs, ip = self.reg("cs"), self.reg("ip")
        self.mu.emu_start(cs * 16 + ip, until, timeout=int(timeout_s * 1000000))
        if self.error is not None:
            raise self.error


# ---- the watched match ----------------------------------------------------------------------
SEED = 0x7B62                          # DS:7B62, the main RNG word (F004; DS:A978 points to it)
MINUTE, SUBTICK, CLOCK_RUNNING, MINUTES_LEFT = 0x831F, 0x831D, 0x8325, 0x831B
SCORE = 0x9B3C                         # bytes DS:9B3C (engine team 0), DS:9B3D (team 1)
SIDES = 0x9B34                         # words: the two countries of the match
SPEED_PTR, SPEED_FIELD = 0xA923, 0x3F  # the delay byte (commentary.py; 0791:9372)
COUNTRIES, COUNTRY_SIZE, TACTICS = 0xA917, 0xBF, 0x2D   # F007, F010
PLAYERS, PLAYER_SIZE = 0xA91B, 0x14                     # F007
SQUAD_WORDS = 20                                        # country +0, word[20] (F007)
MAN_OF_THE_MATCH = 0x7C3A                               # F014
RING, REC, RING_SIZE, COUNTER = 0x7C38, 6, 200, 0x80EE  # commentary.py
TEMPLATES, TEMPLATE_STRIDE, N_TEMPLATES = 0x00BE, 0x15, 67
NAMES, NAME_LEN = 0x9B6C, 11
SCORERS, SCORERS_SIDE, SCORER_REC = 0x7BD1, 0x21, 3     # 0106: 0x7BD1 + 0x21*side + 3*k, k = 1..11
STATS, STATS_SIDE, N_STATS = 0x7B7E, 10, 9              # 0106: byte DS:7B7E + 10*side + k, k = 0..8
BARS = (0x80F2, 0x80F6)                                 # 0106: f_0791_006C rows 0x13, 0x14
SCREEN_PTR = 0xA96A                                     # far pointer to the text page (214B:0755)

ENTRY_TICK = "0791:970C"               # the clock (E011 notes.md §4)
COMMENTARY_WRITE = "0791:1D4A"         # write_commentary_line
MATCH_RETURN = "0791:F2E3"             # F1F6, after `F2E0 call 0xF098` (play_match)
KEYPRESSED, READKEY = "214B:0723", "214B:08DD"
BOARD_READ_RETURN = ("0791", 0x041A)   # 0106: `0415 call far 214B:08DD`
CAPTAIN_READ_RETURN = ("0791", 0xCEED)  # CC7B: `CEE8 call far 214B:08DD` (seg_0791_20.asm:1348)
MENU_READ_RETURN = ("214B", 0x157C)    # 1560: `1579 call 0x8DD` (push cs; near-as-far)
MENU_CALLER_RETURN = ("0791", 0xEE9F)  # ED8A: `EE9A call far 214B:1560`
PUSHED_BACK = 0x79AE                   # 08DD: `08E3 cmp byte ptr [0x79ae], 0`
KEY, LAST_KEY = 0xA976, 0xA977
WAIT_FAMILY = ("000E:05F6", "000E:0572", "000E:04F5", "000E:045D")   # watched.py; returns from the listing


class WatchedMatch(Guest):
    def __init__(self, data):
        super().__init__(data)
        self.seed_lin = self.DS * 16 + SEED
        self.draws = []          # (minute, sub-tick, before, after) per change of DS:7B62
        self.tick_marks = []     # (minute, sub-tick, seed) at each 970C entry
        self.strays = []         # 000E wait-family skips: must stay empty
        # the starting burst's Enter, for CC7B's read only (`CEE8 call far 214B:08DD` returns to CEED)
        self.keys = [{"screen": "captain screen (the starting burst's Enter)", "key": ENTER,
                      "read_return": CAPTAIN_READ_RETURN}]
        self.key_log = []        # (screen, key, minute, sub-tick, seed) per key delivered
        self.inputs = []         # declared writes
        self.lines_written = 0
        self.full_time = None    # the state when F098 returned
        self.stopped_at_board = False
        self.max_ticks = None
        self._interventions()

    # -- interventions -------------------------------------------------------------------------
    def _seed_changed(self, old, new):
        self.draws.append((self.rd(MINUTE), self.rd(SUBTICK), old, new))

    def _interventions(self):
        mu = self.mu
        mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)

        def seed_write(uc, access, address, size, value, data):
            if self.suppress_guest_watch:      # a proved call's original run, undone after it
                return
            old = self.word_at(self.seed_lin)
            raw = bytearray(old.to_bytes(2, "little"))
            for i in range(size):
                j = address + i - self.seed_lin
                if 0 <= j < 2:
                    raw[j] = (value >> (8 * i)) & 0xFF
            new = int.from_bytes(raw, "little")
            self.draws.append((self.rd(MINUTE), self.rd(SUBTICK), old, new))

        mu.hook_add(UC_HOOK_MEM_WRITE, seed_write, begin=self.seed_lin, end=self.seed_lin + 1)
        self.watch_word(self.seed_lin, self._seed_changed)

        def code_at(address, fn):
            lin = self.lin(address)
            mu.hook_add(UC_HOOK_CODE, fn, begin=lin, end=lin)

        def tick(uc, addr, size, data):
            self.tick_marks.append((self.rd(MINUTE), self.rd(SUBTICK), self.rd(SEED)))
            if self.max_ticks is not None and len(self.tick_marks) >= self.max_ticks:
                uc.emu_stop()

        def line(uc, addr, size, data):
            self.lines_written += 1

        def match_returned(uc, addr, size, data):
            self.full_time = self.state()

        code_at(ENTRY_TICK, tick)
        code_at(COMMENTARY_WRITE, line)
        code_at(MATCH_RETURN, match_returned)

        def keypressed(uc, addr, size, data):
            self.set_reg("ax", (self.reg("ax") & 0xFF00) | (1 if self.keys else 0))
            self.return_from(True, 0)

        def readkey(uc, addr, size, data):
            try:
                if self.rd(PUSHED_BACK, 1):
                    return                      # the guest's own path: no wait
                ret = (self.stack_word(2), self.stack_word(0))
                if self.keys:
                    want = self.keys[0]["read_return"]
                    if ret != (self.seg(int(want[0], 16)), want[1]):
                        raise KeyWaitError("undeclared key wait: 214B:08DD called from %04X:%04X with the %s"
                                           " queued for the read returning to %s:%04X" % (
                                               (ret[0] - self.load) & 0xFFFF, ret[1], self.keys[0]["screen"],
                                               want[0], want[1]))
                    k = self.keys.pop(0)
                    screen, key = k["screen"], k["key"]
                elif ret == (self.seg(0x791), BOARD_READ_RETURN[1]) and self.full_time is not None:
                    self.stopped_at_board = True
                    uc.emu_stop()
                    return
                elif ret == (self.seg(0x791), BOARD_READ_RETURN[1]):
                    screen, key = "half-time board ('hit any key', 0791:0106)", ENTER
                elif (ret == (self.seg(0x214B), MENU_READ_RETURN[1]) and
                      self._caller_of_1560() == (self.seg(0x791), MENU_CALLER_RETURN[1])):
                    screen, key = "team screen (0791:ED8A, ' play ')", ENTER
                else:
                    raise KeyWaitError("undeclared key wait: 214B:08DD called from %04X:%04X at clock "
                                       "(%d, %d)" % (ret[0] - self.load, ret[1], self.rd(MINUTE), self.rd(SUBTICK)))
                self.key_log.append((screen, key, self.rd(MINUTE), self.rd(SUBTICK), self.rd(SEED)))
                self.put(self.DS * 16 + KEY, bytes([key, key]))   # 0947 A976, 097C A977
                self.return_from(True, 0)
            except Exception as e:
                self.error = e
                uc.emu_stop()

        code_at(KEYPRESSED, keypressed)
        code_at(READKEY, readkey)

        def skip(name):
            far, pop = routine_return(name)

            def fn(uc, addr, size, data):
                self.strays.append(name)
                self.return_from(far, pop)
            return fn

        for address in WAIT_FAMILY:
            code_at(address, skip(address))

    def _caller_of_1560(self):
        # at 08DD's entry BP is still 1560's frame pointer (1560: push bp; mov bp, sp)
        bp = self.reg("bp")
        ss = self.reg("ss") * 16
        return (self.word_at(ss + bp + 4), self.word_at(ss + bp + 2))

    # -- declared inputs (I3) ------------------------------------------------------------------
    def write_input(self, what, linear, raw):
        raw = bytes(raw)
        old = self.mem(linear, len(raw))
        self.put(linear, raw)
        self.inputs.append({"what": what, "linear": linear, "old": old.hex(), "new": raw.hex()})

    def set_seed(self, value):
        self.write_input("main seed word DS:7B62", self.DS * 16 + SEED, value.to_bytes(2, "little"))

    def set_delay(self, value):
        self.write_input("delay byte [DS:A923]+0x3F", self.far(SPEED_PTR) + SPEED_FIELD, [value])

    def country_lin(self, country):
        return self.far(COUNTRIES) + COUNTRY_SIZE * country

    def player_lin(self, player):
        return self.far(PLAYERS) + PLAYER_SIZE * player

    def set_country_tactics(self, country, value):
        self.write_input(f"country {country} +0x2D (default team tactic set)",
                         self.country_lin(country) + TACTICS, [value])

    def set_player_bytes(self, player, offset, raw):
        self.write_input(f"player {player} +0x{offset:X}", self.player_lin(player) + offset, raw)

    def squad(self, country):
        lin = self.country_lin(country)
        return [self.word_at(lin + 2 * i) for i in range(SQUAD_WORDS)]

    def set_squad(self, country, words):
        if len(words) != SQUAD_WORDS:
            raise ValueError("a squad is 20 player words")
        self.write_input(f"country {country} squad words +0..+0x27",
                         self.country_lin(country), b"".join(w.to_bytes(2, "little") for w in words))

    def sides(self):
        return [self.rd(SIDES), self.rd(SIDES + 2)]

    # -- the run -------------------------------------------------------------------------------
    def run(self, timeout_s=1800, max_ticks=None):
        """Resume the start state and run to the full-time board's key wait (or `max_ticks`
        clock ticks). Declares the delay byte write first. Returns self."""
        self.max_ticks = max_ticks
        if not any(i["what"].startswith("delay") for i in self.inputs):
            self.set_delay(0)
        self.start_state = self.state()
        board = self.lin("0791:FFFF")   # never reached: the run stops in the board's key read
        self.emulate(board, timeout_s)
        self.final = self.state()
        return self

    def state(self):
        return {"831F": self.rd(MINUTE), "831D": self.rd(SUBTICK), "8325": self.rd(CLOCK_RUNNING, 1),
                "831B": self.rd(MINUTES_LEFT), "7B62": self.rd(SEED),
                "score": [self.rd(SCORE, 1), self.rd(SCORE + 1, 1)], "ticks": len(self.tick_marks),
                "draws": len(self.draws)}

    def tick_values(self):
        """(minute, sub-tick) -> the set of values DS:7B62 takes while the clock words read that
        pair: each write's value before and after, under the clock at the write, and the value at
        each 970C entry under the tick that just ran. The word changes only by writes, so the set
        is exactly the values it holds under that clock reading (a stall included: the clock
        words do not move while 8325 is clear)."""
        sets = {}
        if not self.draws and not self.tick_marks:
            return sets
        for minute, subtick, seed in self.tick_marks:
            sets.setdefault((minute, subtick), set()).add(seed)
        for minute, subtick, before, after in self.draws:
            s = sets.setdefault((minute, subtick), set())
            s.add(before)
            s.add(after)
        return sets

    # -- outputs -------------------------------------------------------------------------------
    def screen(self):
        lin = self.far(SCREEN_PTR)
        raw = self.mem(lin, 4000)
        return savestate.Screen(raw[0::2], raw[1::2])

    def name(self, index):
        if not index:
            return ""
        raw = self.mem(self.far(NAMES) + NAME_LEN * index, NAME_LEN)
        return raw[1:1 + min(raw[0], NAME_LEN - 1)].decode("cp437", errors="replace")

    def commentary(self):
        """The ring's records oldest first (DS:80EE is the newest record's n; the ring keeps the
        last 200 lines; 0xFF records are unwritten or the end marker), as commentary.py reads
        them, raw and as text."""
        templates = []
        for t in range(N_TEMPLATES):
            raw = self.mem(self.DS * 16 + TEMPLATES + TEMPLATE_STRIDE * t, TEMPLATE_STRIDE)
            templates.append(raw[1:1 + min(raw[0], TEMPLATE_STRIDE - 1)].decode("cp437", errors="replace"))
        out = []
        newest = self.rd(COUNTER)
        order = list(range(newest + 1, RING_SIZE + 1)) + list(range(1, newest + 1))   # oldest first
        for n in order:
            r = self.mem(self.DS * 16 + RING + REC * n, REC)
            if r[0] == 0xFF:            # never written since A4A1's fill, or the end marker
                continue
            rec = {"n": n, "template": r[0], "p1": int.from_bytes(r[1:3], "little"),
                   "p2": int.from_bytes(r[3:5], "little"), "team": r[5]}
            t = templates[r[0]] if r[0] < N_TEMPLATES else f"<template {r[0]}>"
            t = t.replace("\x01", f" {self.name(rec['p1'])} ").replace("\x02", f" {self.name(rec['p2'])} ")
            rec["text"] = " ".join(t.split())
            out.append(rec)
        return out

    def scorers(self):
        """Per engine team t (DS:9B34[t], the index of DS:9B3C's score bytes; 0106 places its column
        by DS:0672[t]), 0106's scorer list: (player word, name, minute byte raw) for k = 1..11."""
        out = []
        for side in (0, 1):
            rows = []
            for k in range(1, 12):
                lin = self.DS * 16 + SCORERS + SCORERS_SIDE * side + SCORER_REC * k
                word = self.word_at(lin)
                if word:
                    rows.append({"player": word, "name": self.name(word), "minute_byte_raw": self.mem(lin + 2, 1)[0]})
            out.append(rows)
        return out

    def statistics(self):
        """The full-time board's numbers, RAW, per engine team t: the bytes DS:7B7E + 10*t + k
        (k = 0..8, drawn by 0106 in row k + 9) and the words at DS:80F2/80F6 (rows 0x13, 0x14),
        each with the label the emulated board shows in that row (the left column's, 21..33)."""
        rows = self.screen().lines()
        stats = []
        for k in range(N_STATS):
            label = rows[k + 8][21:34].strip()
            stats.append({"row_label": label, "raw_bytes": [self.rd(STATS + STATS_SIDE * s + k, 1) for s in (0, 1)],
                          "address": f"DS:{STATS + k:04X}+10*t"})
        for i, off in enumerate(BARS):
            label = rows[0x13 - 1 + i][21:34].split(":")[0].strip()
            stats.append({"row_label": label, "raw_words": [self.rd(off), self.rd(off + 2)],
                          "address": f"DS:{off:04X}/{off + 2:04X}"})
        return stats

    def outputs(self):
        scr = self.screen()
        return {"final": self.final, "full_time_at_F2E3": self.full_time, "score": self.final["score"],
                "scorers": self.scorers(), "man_of_the_match_word": self.rd(MAN_OF_THE_MATCH),
                "man_of_the_match": self.name(self.rd(MAN_OF_THE_MATCH)),
                "statistics_raw": self.statistics(), "commentary_writer_calls_1D4A": self.lines_written,
                "sides_9B34": self.sides(),
                "commentary": self.commentary(), "board_screen_sha256": scr.digest(),
                "board_screen": scr.text(), "key_log": self.key_log, "strays": list(self.strays),
                "inputs": self.inputs, "hook_counts": dict(self.hook_counts),
                "stopped_at_board": self.stopped_at_board,
                "draws": [list(d) for d in self.draws]}
