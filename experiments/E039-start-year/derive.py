#!/usr/bin/env python3
"""E039 (T83, #369): the state goal2's core resumes "at a DOS call": the original's own code run under Unicorn from a
DOSBox-X savestate caught during GOAL's start-up (run.py, `pre-date`) to the `int 21h` with AH=2Ah at 235C:0071,
the program's only DOS date read (214B:206A -> 214B:1C63 -> 235C:006C; T83 static reading), and written there.

    python3 experiments/E039-start-year/derive.py <pre-date.sav> <out.sav> --log out/derive-r<nnnn>.json

What runs between the catch and the call, and how each input is served (every one logged):
- the BIOS tick count 0040:006C, which the start-up's delay calibration 214B:1DA7 waits on (it busy-waits for the
  dword to change, then counts passes until it changes again): advanced by one every TICK instructions, the
  nominal length of a tick at the run's fixed `cycles=30000` (30000 per ms x 54.925 ms); nothing else of IRQ 0
  is modelled;
- `Intr` 235C:000B (E038 trace.py: it enters the vector by a far return) and `int` instructions, served as DOS and
  the BIOS do for: INT 21h AH=25h (set vector: 0000:4n = DS:DX) and AH=35h (get vector: ES:BX = 0000:4n); INT 10h
  AH=0Fh (get mode: AL, AH, BH from 0040:0049, 004A, 0062), AH=03h (get cursor: DX from 0040:0050 + 2*BH, CX from
  0040:0060), AH=01h (set cursor shape: 0040:0060 = CX), AH=02h (set cursor position: 0040:0050 + 2*BH = DX);
  the BIOS's effects on the video hardware (CRTC registers) are not modelled; any other interrupt stops the
  derivation;
- port I/O: logged; IN returns 0.
The run stops on reaching 235C:0071 with AH = 2Ah, before the `int` executes. The written state is the caught
savestate with its `Memory` component replaced by the emulated memory (header and trailer kept) and its `CPU`
component's registers (E021 notes section 1: EAX..EDI, EIP, EFLAGS, ES CS SS DS FS GS) set to the emulated ones;
every other component, the `Vga` text page included, is the caught state's (nothing in between writes the text
page: logged by a write hook on B800:0000-0F9F). It is a state for goal2's core (which reads `CPU`, `Memory` and
the text page), not a DOSBox-X state: DOSBox-X keeps more CPU state (cached segment bases, the prefetch queue)
that is not rewritten, and loading it into DOSBox-X was not tried."""
import argparse
import importlib.util
import io
import json
import struct
import sys
import zipfile
import zlib
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE, UC_HOOK_INSN, UC_HOOK_MEM_WRITE
from unicorn import x86_const as X

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("e038_trace", ROOT / "experiments" / "E038-new-game-keywait" / "trace.py")
e038 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e038)

TICK = 30000 * 54925 // 1000          # instructions per BIOS tick at cycles=30000 (docstring)
BDA_TICKS, BDA_CURSOR = 0x46C, 0x450
DATE_INT = (0x235C, 0x0071)           # 235C:006C GetDate: `mov ah, 2Ah; int 21h` (seg_235C_01.asm:99)
INTR = (0x235C, 0x000B)
REC = e038.REC
GPR_ORDER = ("EAX", "ECX", "EDX", "EBX", "ESP", "EBP", "ESI", "EDI")
SEG_ORDER = ("ES", "CS", "SS", "DS", "FS", "GS")


class Derive:
    def __init__(self, data):
        self.data = data
        c = e038.components(data)
        self.regs0 = e038.cpu_regs(c["CPU"])
        mem = bytearray(c["Memory"][e038.MEM_BASE:e038.MEM_BASE + e038.MEM_SIZE])
        self.load = e038.find_load(mem)
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, e038.MEM_SIZE)
        mu.mem_write(0, bytes(mem))
        v = c["Vga"]
        self.page0 = bytes(b for i in range(2000) for b in (v[e038.VGA_TEXT_BASE + e038.CELL * i], v[e038.VGA_TEXT_BASE + e038.CELL * i + 1]))
        mu.mem_write(0xB8000, self.page0)
        for n in GPR_ORDER + ("EFLAGS",) + SEG_ORDER:
            mu.reg_write(getattr(X, f"UC_X86_REG_{n}"), self.regs0[n])
        mu.reg_write(X.UC_X86_REG_EIP, self.regs0["EIP"] & 0xFFFF)
        self.events, self.ticks, self.instructions, self.stop, self.page_writes = [], 0, 0, None, 0
        mu.hook_add(UC_HOOK_INTR, self.on_int)
        a = self.seg(INTR[0]) * 16 + INTR[1]
        mu.hook_add(UC_HOOK_CODE, self.on_intr, begin=a, end=a)
        a = self.seg(DATE_INT[0]) * 16 + DATE_INT[1]
        mu.hook_add(UC_HOOK_CODE, self.on_date, begin=a, end=a)
        mu.hook_add(UC_HOOK_INSN, self.on_in, None, 1, 0, X.UC_X86_INS_IN)
        mu.hook_add(UC_HOOK_INSN, self.on_out, None, 1, 0, X.UC_X86_INS_OUT)
        mu.hook_add(UC_HOOK_MEM_WRITE, self.on_page, begin=0xB8000, end=0xB8F9F)

    def seg(self, p):
        return (self.load + p) & 0xFFFF

    def r(self, n):
        return self.mu.reg_read(getattr(X, f"UC_X86_REG_{n}"))

    def w(self, n, v):
        self.mu.reg_write(getattr(X, f"UC_X86_REG_{n}"), v)

    def where(self, s, o):
        rel = (s - self.load) & 0xFFFF
        return f"{rel:04X}:{o:04X}" if rel < 0x3000 else f"{s:04X}:{o:04X} (absolute)"

    def stack(self, k):
        a = self.r("SS") * 16 + ((self.r("SP") + k) & 0xFFFF)
        return int.from_bytes(self.mu.mem_read(a, 2), "little")

    def bda(self, off, n=2):
        return int.from_bytes(self.mu.mem_read(0x400 + off, n), "little")

    def serve(self, n, regs):
        """Serve interrupt n as DOS or the BIOS does, for the functions start-up uses (docstring): returns (regs out,
        note), or None for anything else (the derivation then stops)."""
        ah, al = regs["AX"] >> 8, regs["AX"] & 0xFF
        out = dict(regs)
        if n == 0x21 and ah == 0x25:
            self.mu.mem_write(4 * al, struct.pack("<HH", regs["DX"], regs["DS"]))
            return out, f"set interrupt vector {al:02X}h = {regs['DS']:04X}:{regs['DX']:04X} (0000:{4 * al:04X})"
        if n == 0x21 and ah == 0x35:
            off, seg = struct.unpack("<HH", bytes(self.mu.mem_read(4 * al, 4)))
            out["BX"], out["ES"] = off, seg
            return out, f"get interrupt vector {al:02X}h: ES:BX = {seg:04X}:{off:04X}"
        if n == 0x10 and ah == 0x0F:
            out["AX"] = (self.bda(0x4A, 1) << 8) | self.bda(0x49, 1)
            out["BX"] = (self.bda(0x62, 1) << 8) | (regs["BX"] & 0xFF)
            return out, f"get video mode: AL = {self.bda(0x49, 1):02X}, AH = {self.bda(0x4A, 1)} columns, BH = page {self.bda(0x62, 1)} (from 0040:0049, 004A, 0062)"
        if n == 0x10 and ah == 0x03:
            page = regs["BX"] >> 8
            out["DX"], out["CX"] = self.bda(0x50 + 2 * page), self.bda(0x60)
            return out, f"get cursor: DX = {out['DX']:04X} (0040:{0x50 + 2 * page:04X}), CX = {out['CX']:04X} (0040:0060)"
        if n == 0x10 and ah == 0x01:
            self.mu.mem_write(0x460, struct.pack("<H", regs["CX"]))
            return out, f"set cursor shape: CX = {regs['CX']:04X} -> 0040:0060"
        if n == 0x10 and ah == 0x02:
            page = regs["BX"] >> 8
            self.mu.mem_write(BDA_CURSOR + 2 * page, struct.pack("<H", regs["DX"]))
            return out, f"set cursor position: page {page}, row {regs['DX'] >> 8:#x}, column {regs['DX'] & 0xFF:#x} -> 0040:{0x50 + 2 * page:04X}"
        return None

    def log(self, n, regs, at, how, served):
        self.events.append({"kind": "interrupt", "via": how, "int": f"{n:02X}", "ah": f"{regs['AX'] >> 8:02X}",
                            "regs_in": {k: f"{regs[k]:04X}" for k in ("AX", "BX", "CX", "DX", "DS", "ES") if k in regs}, "at": at,
                            "tick": self.ticks, "served": served[1] if served else "NOT SERVED: the derivation stops"})

    def on_intr(self, uc, addr, size, _):
        n = self.stack(8) & 0xFF
        rec = self.stack(6) * 16 + self.stack(4)
        regs = dict(zip(REC, struct.unpack("<10H", bytes(uc.mem_read(rec, 20)))))
        at = self.where(self.stack(2), self.stack(0)) + " (Intr 235C:000B, return address)"
        served = self.serve(n, regs)
        self.log(n, regs, at, "Intr", served)
        if served is None:
            self.stop = f"unserved INT {n:02X}h AH={regs['AX'] >> 8:02X} via Intr at {at}"
            uc.emu_stop()
            return
        uc.mem_write(rec, struct.pack("<10H", *(served[0][k] for k in REC)))
        ip, cs = self.stack(0), self.stack(2)
        self.w("SP", (self.r("SP") + 10) & 0xFFFF)
        self.w("CS", cs)
        self.w("IP", ip)

    def on_int(self, uc, n, _):
        regs = {k: self.r(k) for k in ("AX", "BX", "CX", "DX", "SI", "DI", "DS", "ES")}
        at = self.where(self.r("CS"), (self.r("IP") - 2) & 0xFFFF)
        served = self.serve(n, regs)
        self.log(n, regs, at, "int", served)
        if served is None:
            self.stop = f"unserved INT {n:02X}h AH={regs['AX'] >> 8:02X} at {at}"
            uc.emu_stop()
            return
        for k in ("AX", "BX", "CX", "DX", "ES"):
            self.w(k, served[0][k])

    def on_date(self, uc, addr, size, _):
        if (self.r("AX") >> 8) != 0x2A:
            raise RuntimeError("235C:0071 reached without AH=2Ah")
        self.stop = "date call"
        uc.emu_stop()

    def on_in(self, uc, port, size, _):
        self.events.append({"kind": "port", "dir": "in", "port": f"{port:02X}", "tick": self.ticks})
        return 0

    def on_out(self, uc, port, size, value, _):
        self.events.append({"kind": "port", "dir": "out", "port": f"{port:02X}", "value": f"{value:02X}", "tick": self.ticks})

    def on_page(self, uc, access, address, size, value, _):
        self.page_writes += 1

    def run(self, limit_ticks=1000):
        while self.stop is None and self.ticks < limit_ticks:
            pc = self.r("CS") * 16 + self.r("IP")
            self.mu.emu_start(pc, 1 << 21, count=TICK)
            if self.stop is None:
                self.instructions += TICK
                t = int.from_bytes(self.mu.mem_read(BDA_TICKS, 4), "little") + 1
                self.mu.mem_write(BDA_TICKS, t.to_bytes(4, "little"))
                self.ticks += 1
        if self.stop is None:
            self.stop = f"no date call within {limit_ticks} ticks"
        return self

    def regs(self):
        out = {n: self.r(n) for n in GPR_ORDER + ("EFLAGS",) + SEG_ORDER}
        out["EIP"] = self.r("IP")
        return out

    def write(self):
        """The caught savestate with Memory and the CPU registers replaced (docstring)."""
        regs = self.regs()
        mem = bytes(self.mu.mem_read(0, e038.MEM_SIZE))
        src = zipfile.ZipFile(io.BytesIO(self.data))
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as dst:
            for info in src.infolist():
                body = src.read(info.filename)
                if info.filename in ("Memory", "CPU"):
                    d = zlib.decompressobj()
                    comp = bytearray(d.decompress(body))
                    if info.filename == "Memory":
                        page_now = mem[0xB8000:0xB8000 + 4000]
                        comp[e038.MEM_BASE:e038.MEM_BASE + e038.MEM_SIZE] = mem
                        assert page_now is not None
                    else:
                        struct.pack_into("<8I", comp, e038.CPU_GPR, *(regs[n] for n in GPR_ORDER))
                        struct.pack_into("<I", comp, e038.CPU_EIP, regs["EIP"])
                        flags = struct.unpack_from("<Q", comp, e038.CPU_FLAGS)[0]
                        struct.pack_into("<Q", comp, e038.CPU_FLAGS, (flags & ~0xFFFFFFFF) | regs["EFLAGS"])
                        for i, n in enumerate(SEG_ORDER):
                            struct.pack_into("<H", comp, e038.CPU_SEGS + e038.CPU_SEG_STRIDE * i, regs[n])
                    body = zlib.compress(bytes(comp), 1) + d.unused_data
                dst.writestr(info, body, compress_type=info.compress_type)
        return out.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("savestate")
    ap.add_argument("out")
    ap.add_argument("--log")
    a = ap.parse_args(argv)
    data = Path(a.savestate).read_bytes()
    d = Derive(data).run()
    if d.stop != "date call":
        raise SystemExit(d.stop)
    blob = d.write()
    Path(a.out).write_bytes(blob)
    import hashlib
    back = e038.cpu_regs(e038.components(blob)["CPU"])
    regs = d.regs()
    assert all(back[k] == regs[k] for k in regs), "the CPU component does not read back"
    ss, sp = regs["SS"], regs["ESP"] & 0xFFFF
    frame = [f"{d.stack(k):04X}" for k in range(0, 0x14, 2)]
    result = {"argv": list(sys.argv[1:] if argv is None else argv),
              "from": {"sha256": hashlib.sha256(data).hexdigest(), "cpu": f"{d.regs0['CS']:04X}:{d.regs0['EIP'] & 0xFFFF:04X}",
                       "where": d.where(d.regs0["CS"], d.regs0["EIP"] & 0xFFFF)},
              "stop": d.stop, "ticks_served": d.ticks, "instructions_before_last_tick_chunk": d.instructions,
              "text_page_writes": d.page_writes, "events": d.events,
              "state": {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
                        "cpu": {k: (f"{v:04X}" if k in SEG_ORDER else f"{v:08X}") for k, v in regs.items()},
                        "at": d.where(regs["CS"], regs["EIP"]), "stack_words_from_SS_SP": f"{ss:04X}:{sp:04X} " + " ".join(frame),
                        "DS:A9FD": d.mu.mem_read(d.seg(0x2581) * 16 + 0xA9FD, 2).hex(),
                        "DS:A9FF": int.from_bytes(d.mu.mem_read(d.seg(0x2581) * 16 + 0xA9FF, 4), "little"),
                        "bios_ticks": int.from_bytes(d.mu.mem_read(BDA_TICKS, 4), "little")}}
    print(json.dumps({k: v for k, v in result.items() if k != "events"}, indent=1))
    if a.log:
        Path(a.log).write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
