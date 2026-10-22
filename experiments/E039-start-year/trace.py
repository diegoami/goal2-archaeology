#!/usr/bin/env python3
"""E039 (T83, #369): the original's code under Unicorn from the state at the DOS date call (derive.py: CPU at
235C:0071, AH = 2Ah) through the title and E038's new-game screens to the first manager menu, every interrupt and
port access logged; the date is the one given, answered as DOS does.

    python3 experiments/E039-start-year/trace.py <date-call.sav> --date 1990-10-04 --keys 6E,0D,0D,62,6F,62,0D,0D,0D \
        --key-polls 214B:0DB9 --time 10:00:SS.hh --out out/trace-1990.json

E038's `Trace` (its trace.py: keys at 214B:08DD, polls at 214B:0723, `Intr` hooked, DOS file I/O on GOAL.DAT and
the time served) with: the entry at the saved CPU state instead of 08DD's read (the core's "resume at a DOS call":
the first instruction is the `int 21h`); INT 21h AH=2Ah answered CX = year, DH = month, DL = day, AL = weekday
(0 = Sunday), as DOS does; derive.py's INT 21h AH=25h/35h and INT 10h AH=01h/02h/03h/0Fh; port IN/OUT logged (IN
returns 0); no timer (the BIOS tick 0040:006C stays as the state holds it: goal2's core has none). At each read the
log also holds DS:A9FD, DS:A9FF, DS:8336 and the game record's +0x38..+0x41 (1771:9B85), for summarise.py."""
import argparse
import datetime
import importlib.util
import json
import sys
from pathlib import Path

from unicorn import UC_HOOK_INSN
from unicorn import x86_const as X

ROOT = Path(__file__).resolve().parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e038 = _load("e038_trace", ROOT / "experiments" / "E038-new-game-keywait" / "trace.py")
derive = _load("e039_derive", Path(__file__).resolve().parent / "derive.py")


class DateTrace(e038.Trace):
    def __init__(self, data, keys, time, date, key_polls=(), hundredths=0):
        # E038's constructor wants 08DD's frame; this entry is the saved CPU itself, so build the same machine here.
        c = e038.components(data)
        self.regs0 = e038.cpu_regs(c["CPU"])
        mem = bytearray(c["Memory"][e038.MEM_BASE:e038.MEM_BASE + e038.MEM_SIZE])
        self.load = e038.find_load(mem)
        self.DS = self.load + e038.DS_PARAGRAPH
        if (self.regs0["CS"] - self.load) & 0xFFFF != 0x235C or self.regs0["EIP"] & 0xFFFF != 0x0071 \
                or (self.regs0["EAX"] >> 8) & 0xFF != 0x2A:
            raise SystemExit("the state is not stopped at the date call 235C:0071 with AH = 2Ah")
        from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, e038.MEM_SIZE)
        mu.mem_write(0, bytes(mem))
        v = c["Vga"]
        mu.mem_write(0xB8000, bytes(b for i in range(2000) for b in (v[e038.VGA_TEXT_BASE + e038.CELL * i],
                                                                     v[e038.VGA_TEXT_BASE + e038.CELL * i + 1])))
        for n in derive.GPR_ORDER + ("EFLAGS",) + derive.SEG_ORDER:
            mu.reg_write(getattr(X, f"UC_X86_REG_{n}"), self.regs0[n])
        mu.reg_write(X.UC_X86_REG_EIP, self.regs0["EIP"] & 0xFFFF)
        self.keys, self.key_polls = list(keys), set(key_polls)
        y, mo, d = date
        self.time, self.date, self.hundredths = time, (y, mo, d, datetime.date(y, mo, d).isoweekday() % 7), hundredths
        self.game = ROOT / ".cache" / "goal2"
        self.files, self.events, self.reads, self.stop = {}, [], 0, None
        mu.hook_add(UC_HOOK_INTR, self.on_int)
        for (s, o), fn in ((e038.READKEY, self.on_read), (e038.KEYPRESSED, self.on_poll), (e038.INTR, self.on_intr)):
            a = self.seg(s) * 16 + o
            mu.hook_add(UC_HOOK_CODE, fn, begin=a, end=a)
        mu.hook_add(UC_HOOK_INSN, self.on_in, None, 1, 0, X.UC_X86_INS_IN)
        mu.hook_add(UC_HOOK_INSN, self.on_out, None, 1, 0, X.UC_X86_INS_OUT)

    # derive.py's BIOS and DOS functions, then E038's (the date, the time, GOAL.DAT)
    bda = derive.Derive.bda

    def serve(self, n, regs, how):
        regs = dict(regs)
        regs.setdefault("ES", self.r("ES"))
        regs.setdefault("DS", self.r("DS"))
        got = derive.Derive.serve(self, n, regs)
        return got if got is not None else super().serve(n, regs, how)

    def on_in(self, uc, port, size, _):
        self._port("in", port, None)
        return 0

    def on_out(self, uc, port, size, value, _):
        self._port("out", port, value)

    def _port(self, d, port, value):
        last = self.events[-1] if self.events else None
        key = f"{d} {port:02X}"
        if last and last["kind"] == "ports":
            last["count"][key] = last["count"].get(key, 0) + 1
        else:
            self.events.append({"kind": "ports", "count": {key: 1}, "first_at": self.where(self.r("CS"), self.r("IP"))})

    def on_read(self, uc, addr, size, data):
        n = len(self.events)
        super().on_read(uc, addr, size, data)
        ev = next((e for e in self.events[n:] if e["kind"] == "read"), None)
        if ev is not None:
            ev.update(self.fields())

    def fields(self):
        out = {"A9FD": f"{self.ds(0xA9FD):04X}", "A9FF": self.ds(0xA9FF, 4), "8336": f"{self.ds(0x8336):04X}"}
        seg, off = self.ds(0xA925), self.ds(0xA923)
        if seg:
            out["game_38_41"] = bytes(self.mu.mem_read(seg * 16 + off + 0x38, 10)).hex()
        return out

    def run(self, budget=8_000_000_000):
        try:
            self.mu.emu_start(self.r("CS") * 16 + self.r("IP"), 1 << 21, count=budget)
        except Exception as e:  # noqa: BLE001
            self.stop = f"emulator error at {self.where(self.r('CS'), self.r('IP'))}: {e}"
        if self.stop is None:
            self.stop = f"budget of {budget} instructions spent at {self.where(self.r('CS'), self.r('IP'))}"
        return self


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("savestate")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD, the answer to INT 21h AH=2Ah")
    ap.add_argument("--keys", required=True)
    ap.add_argument("--key-polls", default="")
    ap.add_argument("--time", default="10:00:00.00")
    ap.add_argument("--compare", help="a DOSBox-X savestate of the end screen: E038 trace.py's compare at the end")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    hms, _, hh = a.time.partition(".")
    t = DateTrace(Path(a.savestate).read_bytes(), [int(k, 16) for k in a.keys.split(",") if k],
                  tuple(int(x) for x in hms.split(":")), tuple(int(x) for x in a.date.split("-")),
                  key_polls=[k for k in a.key_polls.split(",") if k], hundredths=int(hh or 0)).run()
    for ev in t.events:
        print(json.dumps({k: v for k, v in ev.items() if k != "screen"})[:300])
    print("stop:", t.stop)
    result = {"argv": list(sys.argv[1:] if argv is None else argv), "stop": t.stop, "events": t.events,
              "final_screen": t.text(), "final": t.fields(), "seed": f"{t.ds(e038.SEED):04X}", "seed2": f"{t.ds(e038.SEED2):04X}"}
    if a.compare:
        result["compare"] = e038.compare(t, Path(a.compare).read_bytes())
        print(json.dumps({k: v for k, v in result["compare"].items() if k != "dosbox_screen"})[:1500])
    if a.out:
        Path(a.out).write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
