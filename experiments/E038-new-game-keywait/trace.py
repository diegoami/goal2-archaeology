#!/usr/bin/env python3
"""E038 (T82, #367): the original's own code under Unicorn, from a savestate stopped in 214B:08DD's INT 16h read,
through the new-game screens to the first manager menu, with every interrupt it makes logged and served.

    python3 experiments/E038-new-game-keywait/trace.py <savestate> --keys n,0D,0D,... [--time 10:00:00] [--out log.json]

The interrupts arrive two ways (static/goal-exe/code): an `int` instruction (Unicorn's interrupt hook), and
Turbo Pascal's `Intr` 235C:000B, which reaches the vector's handler by a far return (235C:000B-0044: it pushes
the flags, a return to 235C:0045 and the vector [0:4n], loads the registers from the record and `retf`s), so no
`int` instruction runs; `MsDos` 235C:0000 enters it with n = 21h. `Intr` is hooked at its entry and served as the
interrupt it asks for, its register record written back as 235C:0045 would, and returns `retf 6`.

Served, each from DOSBox-X 2024.03.01's BIOS and DOS as far as the trace needs (and every call logged, so the
log is the list goal2 asks for): INT 16h AH=0 (the key read, only through 214B:08DD) and AH=1 (key pressed: no
key), INT 21h AH=2Ch (the time given by --time, hundredths 0) and AH=2Ah (the date 10/04/2026, Sunday), INT 10h
(logged; the functions seen are served as noted in the log). Any other interrupt stops the trace (it is not
guessed). Keys are answered at 214B:08DD's entry as the core does (goal2 core/runner.py): DS:A976 = DS:A977 = the
code, AL the code, `retf`. Requirements: python3-unicorn."""
import argparse
import io
import json
import struct
import sys
import zipfile
import zlib
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE
from unicorn import x86_const as X

MEM_BASE = 0x78                      # F001: the Memory component's header
MEM_SIZE = 0x110000
DS_PARAGRAPH = 0x2581                # static/goal-exe/README.md
# The CPU component (E021 notes section 1; runtime/emul/watched_match.py cpu_state)
CPU_GPR, CPU_EIP, CPU_FLAGS, CPU_SEGS, CPU_SEG_STRIDE = 0x00, 0x20, 0x28, 0xEB, 8
GPR = ("EAX", "ECX", "EDX", "EBX", "ESP", "EBP", "ESI", "EDI")
SEGS = ("ES", "CS", "SS", "DS", "FS", "GS")
VGA_TEXT_BASE, CELL = 0x86024, 8     # F001: the text page in the Vga component
READKEY, KEYPRESSED, INTR = (0x214B, 0x08DD), (0x214B, 0x0723), (0x235C, 0x000B)
INTR_RETURN = 0x0904                 # 214B:08DD's call far 235C:000B at 08FF returns here
PUSHED_BACK, KEY = 0x79AE, 0xA976    # 08DD 08E3; 0947/097C
SEED, SEED2 = 0x7B62, 0x7B64         # F004
SCREEN_PTR = 0xA96A                  # the text page's far pointer (214B:0755)
# TP's Registers record, as 235C:000B loads it (0028-003E): AX BX CX DX BP SI DI DS ES Flags
REC = ("AX", "BX", "CX", "DX", "BP", "SI", "DI", "DS", "ES", "FLAGS")
CP437_LOW = "☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼"


def components(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return {n: zlib.decompressobj().decompress(z.read(n)) for n in ("CPU", "Memory", "Vga")}


def cpu_regs(cpu):
    r = dict(zip(GPR, struct.unpack_from("<8I", cpu, CPU_GPR)))
    r["EIP"] = struct.unpack_from("<I", cpu, CPU_EIP)[0]
    r["EFLAGS"] = struct.unpack_from("<Q", cpu, CPU_FLAGS)[0] & 0xFFFFFFFF
    for i, n in enumerate(SEGS):
        r[n] = struct.unpack_from("<H", cpu, CPU_SEGS + CPU_SEG_STRIDE * i)[0]
    return r


def find_load(mem):
    """The load segment of GOAL.EXE: the MCB named GOAL whose owner is the next paragraph, a PSP (CD 20) behind it."""
    found = []
    for seg in range(0x50, 0xA000 - 1):
        a = seg * 16
        if mem[a] in (0x4D, 0x5A) and int.from_bytes(mem[a + 1:a + 3], "little") == seg + 1 \
                and mem[a + 8:a + 12] == b"GOAL" and mem[(seg + 1) * 16:(seg + 1) * 16 + 2] == b"\xcd\x20":
            found.append(seg + 1 + 0x10)
    if len(found) != 1:
        raise SystemExit(f"{len(found)} GOAL.EXE programs in memory")
    return found[0]


def decode(raw):
    def ch(c):
        return " " if c == 0 else (CP437_LOW[c - 1] if c < 32 else bytes([c]).decode("cp437"))
    return "\n".join("".join(ch(c) for c in raw[0::2][r * 80:(r + 1) * 80]).rstrip() for r in range(25))


def read_entry(mem, load, regs):
    """08DD's frame on the state's own stack (goal2 core/runner.py read_entry): {'sp', 'bp', 'chain'}."""
    ss, sp = regs["SS"], regs["ESP"] & 0xFFFF
    seg = (load + 0x214B) & 0xFFFF
    w = lambda off: int.from_bytes(mem[ss * 16 + (off & 0xFFFF):ss * 16 + (off & 0xFFFF) + 2], "little")
    hits = []
    for off in range(sp, sp + 0x200, 2):
        if w(off) == INTR_RETURN and w(off + 2) == seg:
            bp = (off + 4 + 6 + 0x14) & 0xFFFF
            if w(off + 4) == (bp - 0x14) & 0xFFFF and w(off + 6) == ss and w(off + 8) & 0xFF == 0x16:
                hits.append(bp)
    if len(hits) != 1:
        raise SystemExit(f"not stopped in 214B:08DD's INT 16h read: {len(hits)} frames (CPU {regs['CS']:04X}:{regs['EIP'] & 0xFFFF:04X})")
    return {"sp": (hits[0] + 2) & 0xFFFF, "bp": w(hits[0])}


class Trace:
    def __init__(self, data, keys, time, date=(2026, 10, 4, 0), key_polls=(), game=None, hundredths=0):
        c = components(data)
        self.regs0 = cpu_regs(c["CPU"])
        mem = bytearray(c["Memory"][MEM_BASE:MEM_BASE + MEM_SIZE])
        self.load = find_load(mem)
        self.DS = self.load + DS_PARAGRAPH
        entry = read_entry(mem, self.load, self.regs0)
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, MEM_SIZE)
        mu.mem_write(0, bytes(mem))
        v = c["Vga"]
        page = bytes(b for i in range(2000) for b in (v[VGA_TEXT_BASE + CELL * i], v[VGA_TEXT_BASE + CELL * i + 1]))
        mu.mem_write(0xB8000, page)          # the text page lives in the Vga component, not in Memory (F001)
        for n in ("EAX", "EBX", "ECX", "EDX", "ESI", "EDI", "EFLAGS"):
            mu.reg_write(getattr(X, f"UC_X86_REG_{n}"), self.regs0[n])
        for n, val in (("SS", self.regs0["SS"]), ("SP", entry["sp"]), ("BP", entry["bp"]), ("DS", self.DS),
                       ("ES", self.DS), ("CS", self.seg(READKEY[0])), ("IP", READKEY[1])):
            mu.reg_write(getattr(X, f"UC_X86_REG_{n}"), val)
        self.keys = list(keys)
        self.key_polls = set(key_polls)   # poll sites answered "a key waits" while keys remain
        self.time, self.date, self.hundredths = time, date, hundredths
        self.game = Path(game or Path(__file__).resolve().parents[2] / ".cache" / "goal2")   # the verified release copy
        self.files = {}                   # DOS handle -> [bytes, position, name]
        self.events = []                  # every read, interrupt and Intr call, in order
        self.reads = 0
        self.stop = None
        mu.hook_add(UC_HOOK_INTR, self.on_int)
        for (s, o), fn in ((READKEY, self.on_read), (KEYPRESSED, self.on_poll), (INTR, self.on_intr)):
            a = self.seg(s) * 16 + o
            mu.hook_add(UC_HOOK_CODE, fn, begin=a, end=a)

    # -- helpers ------------------------------------------------------------------------------------------
    def seg(self, p):
        return (self.load + p) & 0xFFFF

    def where(self, s, o):
        rel = (s - self.load) & 0xFFFF
        return f"{rel:04X}:{o:04X}" if rel < 0x3000 else f"{s:04X}:{o:04X} (absolute)"

    def r(self, n):
        return self.mu.reg_read(getattr(X, f"UC_X86_REG_{n}"))

    def w(self, n, v):
        self.mu.reg_write(getattr(X, f"UC_X86_REG_{n}"), v)

    def word(self, lin):
        return int.from_bytes(self.mu.mem_read(lin, 2), "little")

    def ds(self, off, n=2):
        return int.from_bytes(self.mu.mem_read(self.DS * 16 + off, n), "little")

    def stack(self, k):
        return self.word(self.r("SS") * 16 + ((self.r("SP") + k) & 0xFFFF))

    def text(self):
        a = self.ds(SCREEN_PTR + 2) * 16 + self.ds(SCREEN_PTR)
        return decode(bytes(self.mu.mem_read(a, 4000)))

    def chain(self, bp, depth=6, cs=None):
        """The callers' return addresses up the BP chain from a frame whose code segment is `cs` (default the
        current one), as the listing writes them (run.py `callers`): a frame is near when the call before its return
        address in the current segment is `E8` and the word above it does not name a segment whose bytes before it are a
        `call far` (9A) or `push cs; call` (0E E8); its caller is then in the same segment; else far."""
        out, ss = [], self.r("SS") * 16
        cs = self.r("CS") if cs is None else cs
        for _ in range(depth):
            ip, fcs = self.word(ss + bp + 2), self.word(ss + bp + 4)
            far = bytes(self.mu.mem_read(fcs * 16 + ((ip - 5) & 0xFFFF), 5))
            near = not (far[0] == 0x9A or far[1:3] == b"\x0e\xe8") and \
                self.mu.mem_read(cs * 16 + ((ip - 3) & 0xFFFF), 1)[0] == 0xE8
            if not near:
                cs = fcs
            rel = (cs - self.load) & 0xFFFF
            if rel >= 0x2581:
                out.append(f"{cs:04X}:{ip:04X} (outside the program)")
                break
            out.append(f"{rel:04X}:{ip:04X}" + (" (near)" if near else ""))
            nb = self.word(ss + bp)
            if nb <= bp:
                break
            bp = nb
        return out

    def ret_far(self, pop):
        ip, cs = self.stack(0), self.stack(2)
        self.w("SP", (self.r("SP") + 4 + pop) & 0xFFFF)
        self.w("CS", cs)
        self.w("IP", ip)

    # -- the key ------------------------------------------------------------------------------------------
    def on_read(self, uc, addr, size, _):
        site = self.where(self.stack(2), self.stack(0))
        if self.ds(PUSHED_BACK, 1):
            self.events.append({"kind": "read", "site": site, "pushed_back": True})
            return
        sp = self.r("SP")
        bp_caller = self.r("BP")
        ev = {"kind": "read", "site": site, "callers": self.chain(bp_caller, cs=self.stack(2)), "ss_sp_at_08DD": f"{self.r('SS'):04X}:{sp:04X}",
              "seed": f"{self.ds(SEED):04X}", "seed2": f"{self.ds(SEED2):04X}", "screen": self.text()}
        self.reads += 1
        if not self.keys:
            ev["key"] = None
            self.events.append(ev)
            self.stop = "keys done"
            uc.emu_stop()
            return
        key = self.keys.pop(0)
        ev["key"] = f"{key:02X}"
        self.events.append(ev)
        uc.mem_write(self.DS * 16 + KEY, bytes([key, key]))
        self.w("EAX", (self.r("EAX") & ~0xFF) | key)
        self.ret_far(0)

    def on_poll(self, uc, addr, size, _):
        site = self.where(self.stack(2), self.stack(0))
        last = self.events[-1] if self.events else None
        if last and last["kind"] == "poll" and last["site"] == site:
            last["count"] += 1
            if site in self.key_polls and self.keys:
                self.events.append({"kind": "poll", "site": site, "count": 1, "answer": "no key"})
        else:
            self.events.append({"kind": "poll", "site": site, "count": 1, "answer": "no key"})
        has = int(site in self.key_polls and bool(self.keys))
        if has:
            self.events[-1]["answer"] = "a key waits (the next read takes it)"
        self.w("EAX", (self.r("EAX") & 0xFF00) | has)
        self.ret_far(0)

    # -- interrupts ---------------------------------------------------------------------------------------
    def serve(self, n, regs, how):
        """Serve interrupt n with the register dict `regs` (AX..FLAGS words); returns (regs out, note) or None."""
        ah, al = regs["AX"] >> 8, regs["AX"] & 0xFF
        out = dict(regs)
        ok = lambda: out.__setitem__("FLAGS", out["FLAGS"] & ~1)  # noqa: E731  CF clear
        if n == 0x21 and ah == 0x2C:
            h, m, s = self.time
            out["CX"], out["DX"] = (h << 8) | m, (s << 8) | self.hundredths
            return out, f"get time: CH:CL = {h}:{m:02d}, DH:DL = {s}.{self.hundredths:02d} (served from --time)"
        if n == 0x21 and ah == 0x2A:
            y, mo, d, wd = self.date
            out["CX"], out["DX"], out["AX"] = y, (mo << 8) | d, (regs["AX"] & 0xFF00) | wd
            return out, f"get date: CX = {y}, DH:DL = {mo}:{d}, AL = weekday {wd} (served)"
        if n == 0x21 and ah == 0x3D:
            name = self.asciiz(regs["DS"], regs["DX"])
            path = next((p for p in self.game.iterdir() if p.name.upper() == name.upper().lstrip("C:\\")), None)
            if path is None:
                out["AX"], out["FLAGS"] = 2, out["FLAGS"] | 1
                return out, f"open {name!r} mode {al:02X}: not found, CF set, AX 2"
            h = min(set(range(5, 20)) - set(self.files))
            self.files[h] = [path.read_bytes(), 0, name]
            out["AX"] = h
            ok()
            return out, f"open {name!r} mode {al:02X}: handle {h} ({len(self.files[h][0])} bytes)"
        if n == 0x21 and ah in (0x3E, 0x3F, 0x42) and regs["BX"] in self.files:
            f = self.files[regs["BX"]]
            if ah == 0x3E:
                del self.files[regs["BX"]]
                ok()
                return out, f"close handle {regs['BX']} ({f[2]})"
            if ah == 0x3F:
                chunk = f[0][f[1]:f[1] + regs["CX"]]
                self.mu.mem_write(regs["DS"] * 16 + regs["DX"], chunk)
                f[1] += len(chunk)
                out["AX"] = len(chunk)
                ok()
                return out, f"read handle {regs['BX']} ({f[2]}): {regs['CX']} bytes asked, {len(chunk)} read to {regs['DS']:04X}:{regs['DX']:04X}, at offset {f[1] - len(chunk)}"
            off = (regs["CX"] << 16) | regs["DX"]
            base = (0, f[1], len(f[0]))[al]
            f[1] = (base + (off if off < 0x80000000 else off - (1 << 32))) & 0xFFFFFFFF
            out["DX"], out["AX"] = f[1] >> 16, f[1] & 0xFFFF
            ok()
            return out, f"seek handle {regs['BX']} ({f[2]}) mode {al} by {off:#x}: position {f[1]}"
        if n == 0x10:
            return out, "video BIOS: logged, nothing written (no effect served)"
        return None

    def asciiz(self, seg, off):
        b = bytes(self.mu.mem_read(seg * 16 + off, 80))
        return b.split(b"\0")[0].decode("cp437")

    def log_int(self, n, regs, pc, how, served, cs=None):
        ev = {"kind": "interrupt", "via": how, "int": f"{n:02X}", "ah": f"{regs['AX'] >> 8:02X}", "al": f"{regs['AX'] & 0xFF:02X}",
              "regs_in": {k: f"{regs[k]:04X}" for k in ("AX", "BX", "CX", "DX", "SI", "DI", "DS", "ES")}, "at": pc,
              "callers": self.chain(self.r("BP"), cs=cs)}
        if served is None:
            ev["served"] = "NOT SERVED: the trace stops"
        else:
            out, note = served
            ev["served"] = note
            ev["regs_out"] = {k: f"{out[k]:04X}" for k in ("AX", "BX", "CX", "DX") if out[k] != regs[k]}
        self.events.append(ev)
        return served

    def on_intr(self, uc, addr, size, _):
        """235C:000B Intr(n, var regs): stack at entry: return IP, CS, regs offset, regs segment, n."""
        n = self.stack(8) & 0xFF
        rec = self.stack(6) * 16 + self.stack(4)
        regs = dict(zip(REC, struct.unpack("<10H", bytes(uc.mem_read(rec, 20)))))
        pc = self.where(self.stack(2), self.stack(0))
        if n == 0x16 and (regs["AX"] >> 8) in (0, 1) and pc in ("214B:0904", "214B:073A"):
            raise RuntimeError(f"INT 16h from {pc} reached Intr: 214B:08DD/0723 should have been answered")
        served = self.log_int(n, regs, pc + " (Intr 235C:000B, return address)", "Intr", self.serve(n, regs, "Intr"),
                              cs=self.stack(2))
        if served is None:
            self.stop = f"unserved INT {n:02X}h AH={regs['AX'] >> 8:02X} via Intr at {pc}"
            uc.emu_stop()
            return
        uc.mem_write(rec, struct.pack("<10H", *(served[0][k] for k in REC)))
        self.ret_far(6)

    def on_int(self, uc, n, _):
        cs, ip = self.r("CS"), self.r("IP")
        at = (ip - 2) & 0xFFFF
        regs = {k: self.r(k) for k in ("AX", "BX", "CX", "DX", "BP", "SI", "DI", "DS", "ES")}
        regs["FLAGS"] = self.r("EFLAGS") & 0xFFFF
        # A frameless far routine (23E4:11D7 is one) has its return at SS:SP; its caller's frame is BP.
        rcs = self.stack(2)
        top = (rcs - self.load) & 0xFFFF < 0x2581
        served = self.log_int(n, regs, self.where(cs, at), "int", self.serve(n, regs, "int"), cs=rcs if top else None)
        if top:
            self.events[-1]["callers"].insert(0, f"{self.where(rcs, self.stack(0))} (far return at SS:SP)")
        if served is None:
            self.stop = f"unserved INT {n:02X}h AH={regs['AX'] >> 8:02X} at {self.where(cs, at)}"
            uc.emu_stop()
            return
        for k in ("AX", "BX", "CX", "DX"):
            self.w(k, served[0][k])
        self.w("EFLAGS", (self.r("EFLAGS") & ~1) | (served[0]["FLAGS"] & 1))

    def run(self, budget=4_000_000_000):
        start = self.seg(READKEY[0]) * 16 + READKEY[1]
        try:
            self.mu.emu_start(start, 1 << 21, count=budget)
        except Exception as e:  # noqa: BLE001
            self.stop = f"emulator error at {self.where(self.r('CS'), self.r('IP'))}: {e}"
        if self.stop is None:
            self.stop = f"budget of {budget} instructions spent at {self.where(self.r('CS'), self.r('IP'))}"
        return self


def ranges(a, b, base):
    """The differing byte ranges of a and b, as [start, end) offsets from base, hex."""
    out, i, n = [], 0, min(len(a), len(b))
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            out.append(f"{base + i:05X}-{base + j:05X}")
            i = j
        else:
            i += 1
    return out


def compare(t, data):
    """The trace's end against a DOSBox-X savestate of the same screen: screens, seed words, the game arrays (F007's
    far pointers DS:A91B, DS:A917) and GOAL.EXE's data segment (64 KiB from DS:0000)."""
    c = components(data)
    mem = c["Memory"][MEM_BASE:MEM_BASE + MEM_SIZE]
    v = c["Vga"]
    page = bytes(b for i in range(2000) for b in (v[VGA_TEXT_BASE + CELL * i], v[VGA_TEXT_BASE + CELL * i + 1]))
    ds = t.DS * 16
    mine = bytes(t.mu.mem_read(0, MEM_SIZE))
    word = lambda m, off: int.from_bytes(m[ds + off:ds + off + 2], "little")  # noqa: E731
    out = {"screen_equal": decode(page) == t.text(), "screen_bytes_equal": page == bytes(t.mu.mem_read(0xB8000, 4000)),
           "seed": [f"{word(mine, SEED):04X}", f"{word(mem, SEED):04X}"], "seed2": [f"{word(mine, SEED2):04X}", f"{word(mem, SEED2):04X}"]}
    for name, ptr, size in (("players", 0xA91B, 0x14 * 3061), ("countries", 0xA917, 0xBF * 129)):
        a, b = word(mine, ptr + 2) * 16 + word(mine, ptr), word(mem, ptr + 2) * 16 + word(mem, ptr)
        out[name] = {"pointer": [f"{a:05X}", f"{b:05X}"], "equal": mine[a:a + size] == mem[b:b + size],
                     "differ": ranges(mine[a:a + size], mem[b:b + size], 0)[:20]}
    out["data_segment_differs"] = ranges(mine[ds:ds + 0x10000], mem[ds:ds + 0x10000], 0)
    out["conventional_differs"] = ranges(mine[:0xA0000], mem[:0xA0000], 0)[:60]
    if not out["screen_equal"]:
        out["dosbox_screen"] = decode(page)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("savestate")
    ap.add_argument("--keys", required=True, help="key codes in hex, comma separated, as 08DD returns them (0D Enter)")
    ap.add_argument("--time", default="10:00:00.00", help="HH:MM:SS.hh the INT 21h AH=2Ch answer gives")
    ap.add_argument("--key-polls", default="", help="poll sites (SSSS:OOOO, the return address of 214B:0723) "
                    "answered 'a key waits' while keys remain; every other poll is answered 'no key'")
    ap.add_argument("--compare", help="a savestate of the same screen from DOSBox-X: compare the end with it")
    ap.add_argument("--out", help="write the events as JSON here")
    a = ap.parse_args(argv)
    keys = [int(k, 16) for k in a.keys.split(",") if k]
    hms, _, hh = a.time.partition(".")
    t = Trace(Path(a.savestate).read_bytes(), keys, tuple(int(x) for x in hms.split(":")),
              key_polls=[k for k in a.key_polls.split(",") if k], hundredths=int(hh or 0)).run()
    for ev in t.events:
        e = {k: v for k, v in ev.items() if k != "screen"}
        print(json.dumps(e))
    print("stop:", t.stop)
    print(t.text())
    result = {"argv": list(sys.argv[1:] if argv is None else argv), "stop": t.stop, "events": t.events,
              "final_screen": t.text(), "seed": f"{t.ds(SEED):04X}", "seed2": f"{t.ds(SEED2):04X}"}
    if a.compare:
        result["compare"] = compare(t, Path(a.compare).read_bytes())
        print(json.dumps(result["compare"], indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
