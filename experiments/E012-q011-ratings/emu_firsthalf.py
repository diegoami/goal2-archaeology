#!/usr/bin/env python3
"""Instrumented Unicorn emulation of a watched match's FIRST half (T26, E012).

    python3 experiments/E012-q011-ratings/emu_firsthalf.py <watchstart.sav> [record.json]

`runtime/emul/watched.py` runs a SECOND half from a half-time savestate; this script runs the
FIRST half from E011's published `watchstart` savestate (the state at the captain screen —
mid-`0791:F1F6`, after match_setup A4A1, before the pre-match loop). The savestate is a release
asset (E011), fetched into scratch/ or .cache/, never committed; the record argument is the
E012 run whose first half this reproduces (line log and half-time words to compare against).

Entry `0791:998C` (the pre-half routine the fixture router's F1F6 reaches through F098): its
head sets `DS:8319`, `DS:830B`, emits the toss line (`1EB5`, template 0x3B) and calls `983F`
(the half); it ends at the `ret` at `99F1`. Before entry the script applies F1F6's pre-match
loop by hand, exactly as the listing writes it (seg_0791_23.asm F234-F2CD): for both sides,
for every squad slot 1..20 with a player — copy the record's `+0xC` form byte to
`DS:9B07 + 0x14*side + slot` (F2A4) and, for slots 1..11, set the `+0x12` word to 0x37 (F2C7).
Hooks beyond `watched.py`'s (interrupts swallowed, key thunk "no key", 000E wait family skipped
and logged, LCG draws and ticks recorded):

- `0791:1E53` (the delta applier): the event frame (id at bp+4, p2 slot bp+6, p1 slot bp+8,
  team bp+0xA), the pitch record's player word and the table delta;
- `0791:1D4A` (the ring writer): a counter of its ENTRIES (every call, whether the routine
  accepts the line or refuses it as a duplicate), and — at `0791:1D66`, the instruction
  reached only when the write proceeds (`1D54`: counter zero, or `1C78` returned nonzero;
  a refused call jumps straight to the epilogue at `1E4A`, `1D61`→`1D63`) — the line as
  written: (n, template, p1, p2, team). Entries minus accepted lines is the MEASURED dedup
  refusal count (T26 rework R3: logging at 1D4A's entry counts refused writes too, so it
  cannot detect a refusal);
- `0791:56CB` (the only ring-invisible +0x12 writer): the player word it adds 10 to;
- `0791:C6FA` (the incoming substitute's 0x2747 store): the player word.

Output (stdout, redirected by the caller into the experiment's committed emu logs): the line
log (accepted writes only), the 56CB/C6FA events with the ring index they fall between, the
1E53/1D4A-entry/accepted-line counts (a 1E53 count above the accepted count is a delta whose
line was refused — the delta is still applied, notes.md §2), and every squad slot's final
+0x12 word; against a record, the line log and the final words are diffed with the record's
first-half extent."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
import players  # noqa: E402
import savestate  # noqa: E402
from unicorn import UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import *  # noqa: E402
from watched import WatchedHalf  # noqa: E402

TAB = [0, -10, -10, 0, 0, -1, 0, -10, 10, 10, 10, -10, 20, 0, 20, 20, 0, 0, 0, 0, 0,
       2, 16, 2, 16, 1, 8, 8, 1, 20, 10, 0, 0, 0, 4, 1, 0, 0, 40, -50, -10, -10, 0,
       0, 0, 0, 0, -20, 0, 0, -20, -100, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -10, 0]
FIRST_ENTRY, FIRST_END = 0x998C, 0x99F1   # the pre-half routine (seg_0791_16.asm:294-337)


class FirstHalf(WatchedHalf):
    def __init__(self, data):
        super().__init__(data)
        self.raw = data
        self.writes = []   # (kind, player word, delta, ring index at the moment)
        self.lines = []    # (n, template, p1, p2, team) as 1D4A ACCEPTS them (hook at 1D66)
        self.entries = 0   # 1D4A entries, accepted or refused (hook at 1D4A)
        self.deltas = []   # 1E53 events: (id, team, slot, player word, delta)
        CODE = self.CODE * 16
        mu = self.mu

        def far(off):     # a DS far pointer's linear address
            return self.rd(off + 2) * 16 + self.rd(off)

        def word_at(lin):
            return int.from_bytes(mu.mem_read(lin, 2), "little")

        def hook_1e53(uc, addr, size, data):
            # bp is still 1EB5's bp: the event frame (id +4, p2 slot +6, p1 slot +8, team +0xA)
            bp = uc.reg_read(UC_X86_REG_BP)
            ss = uc.reg_read(UC_X86_REG_SS) * 16
            rid = int.from_bytes(uc.mem_read(ss + bp + 4, 1), "little")
            p2s = int.from_bytes(uc.mem_read(ss + bp + 6, 2), "little")
            p1s = int.from_bytes(uc.mem_read(ss + bp + 8, 2), "little")
            team = int.from_bytes(uc.mem_read(ss + bp + 0xA, 1), "little")
            base = self.rd(0x668 + team, 1)
            pw = word_at(self.DS * 16 + 0x80E8 + 0x16 * (base + p1s) + 0xD)
            self.deltas.append((rid, team, p1s, p2s, pw, TAB[rid] if rid < len(TAB) else None))
            self.writes.append(("ring", pw, TAB[rid] if rid < len(TAB) else None, len(self.lines)))

        def hook_1d4a(uc, addr, size, data):
            # entry: count the invocation, accepted or refused (1D4A's head, before 1C78)
            self.entries += 1

        def hook_1d66(uc, addr, size, data):
            # the accepted-write path: 1D66 is reached only when the line will be written
            # (1D54: ring counter 0, or 1C78 returned nonzero; a refused call jumps 1D61 ->
            # 1D63 -> 1E4A, the epilogue, and never gets here). bp is 1D4A's frame.
            bp = uc.reg_read(UC_X86_REG_BP)
            ss = uc.reg_read(UC_X86_REG_SS) * 16
            rid = int.from_bytes(uc.mem_read(ss + bp + 4, 1), "little")
            p1s = int.from_bytes(uc.mem_read(ss + bp + 8, 2), "little")
            p2s = int.from_bytes(uc.mem_read(ss + bp + 6, 2), "little")
            team = int.from_bytes(uc.mem_read(ss + bp + 0xA, 1), "little")
            t = self.rd(0x9B34 + 2 * team)
            cbase = far(0xA917) + 0xBF * t          # the country's squad words (F1F6 F24F)
            p1 = word_at(cbase + 2 * p1s - 2) if p1s > 0 else 0
            p2 = word_at(cbase + 2 * p2s - 2) if p2s > 0 else 0
            self.lines.append((len(self.lines) + 1, rid, p1, p2, team))

        def hook_56cb(uc, addr, size, data):
            es = uc.reg_read(UC_X86_REG_ES) * 16
            di = uc.reg_read(UC_X86_REG_DI)
            pw = (di - far(0xA91B)) // 0x14          # es:di is at the player record
            self.writes.append(("direct10", pw, 10, len(self.lines)))

        def hook_c6fa(uc, addr, size, data):
            es = uc.reg_read(UC_X86_REG_ES) * 16
            di = uc.reg_read(UC_X86_REG_DI)
            pw = (di - far(0xA91B)) // 0x14
            self.writes.append(("sub2747", pw, 0x2747, len(self.lines)))

        mu.hook_add(UC_HOOK_CODE, hook_1e53, begin=CODE + 0x1E53, end=CODE + 0x1E53)
        mu.hook_add(UC_HOOK_CODE, hook_1d4a, begin=CODE + 0x1D4A, end=CODE + 0x1D4A)
        mu.hook_add(UC_HOOK_CODE, hook_1d66, begin=CODE + 0x1D66, end=CODE + 0x1D66)
        mu.hook_add(UC_HOOK_CODE, hook_56cb, begin=CODE + 0x56CB, end=CODE + 0x56CB)
        mu.hook_add(UC_HOOK_CODE, hook_c6fa, begin=CODE + 0xC6FA, end=CODE + 0xC6FA)

    def apply_prematch(self):
        """F1F6's loop F234-F2CD by hand: the form copy (F2A4) and the 0x37 store (F2C7)."""
        st = savestate.Savestate(self.raw)
        arr = players.countries(st)
        base = self.rd(0xA91B + 2) * 16 + self.rd(0xA91B)
        for side in (0, 1):
            c = self.rd(0x9B34 + 2 * side)
            for slot, w in enumerate(players.squad(arr, c), start=1):
                if not w:
                    continue
                rec = base + 0x14 * w
                form = self.mu.mem_read(rec + 0xC, 1)[0]
                self.mu.mem_write(self.DS * 16 + 0x9B07 + 0x14 * side + slot, bytes([form]))
                if slot < 0xC:
                    self.mu.mem_write(rec + 0x12, (0x37).to_bytes(2, "little"))

    def run(self, timeout_s=7200):
        self.apply_prematch()
        self.mu.emu_start(self.CODE * 16 + FIRST_ENTRY, self.CODE * 16 + FIRST_END,
                          timeout=timeout_s * 1000000)
        return self

    def final_words(self):
        st = savestate.Savestate(self.raw)
        arr = players.countries(st)
        base = self.rd(0xA91B + 2) * 16 + self.rd(0xA91B)
        out = []
        for side in (0, 1):
            c = self.rd(0x9B34 + 2 * side)
            out.append([int.from_bytes(self.mu.mem_read(base + 0x14 * w + 0x12, 2), "little")
                        for w in players.squad(arr, c)])
        return out


def record_first_half(path):
    d = json.loads(Path(path).read_text())

    def field(needle):
        return next((o["value"] for o in d["observations"] if needle in o.get("field", "")), None)

    n_half = int(field("commentary lines seen at the half-time stall"))
    lines = [(t, p1, p2) for _, t, p1, p2, _ in json.loads(field("commentary line log in ring order"))][:n_half]
    half = json.loads(field("half-time team-screen stall"))
    return lines, [s["perf12"] for s in half]


def main(argv):
    data = Path(argv[1]).read_bytes()
    h = FirstHalf(data).run()
    if len(argv) > 3:
        out = Path(argv[3])
        out.write_text(json.dumps({"lines": h.lines, "entries": h.entries,
                                    "words": h.final_words(),
                                    "writes": h.writes, "deltas": h.deltas,
                                    "draws": len(h.draws), "ticks": h.ticks,
                                    "strays": h.strays}, separators=(",", ":")) + "\n")
        print("dumped to", out)
    print("final clock/seed:", h.rd(0x831F), h.rd(0x831D), h.rd(0x8325, 1), "0x%04x" % h.rd(0x7B62))
    print("ticks:", h.ticks, "draws:", len(h.draws), "strays(000E, must be empty):", h.strays)
    print("1E53 delta events:", len(h.deltas), "1D4A entries:", h.entries,
          "accepted ring lines:", len(h.lines),
          "(entries - accepted = measured dedup refusals; 1E53 - accepted = deltas whose",
          "line was refused, notes.md §2)")
    print("+0x12 writers other than 1E53:",
          [w for w in h.writes if w[0] != "ring"])
    print("final +0x12 words (side 0 then side 1, slots 1..20):")
    for side, words in enumerate(h.final_words()):
        print("  side", side, " ".join("%04X" % w for w in words))
    if len(argv) > 2:
        lines, perf = record_first_half(argv[2])
        emu = [(t, p1, p2) for _, t, p1, p2, _ in h.lines]
        same = emu == lines
        print("record first-half lines:", len(lines), "emulated:", len(emu), "identical:", same)
        if not same:
            for i, (a, b) in enumerate(zip(emu, lines)):
                if a != b:
                    print("  first divergence at line", i + 1, "emu", a, "record", b)
                    break
        words = h.final_words()
        for side in (0, 1):
            bad = [(i + 1, "%04X" % a, "%04X" % b) for i, (a, b) in
                   enumerate(zip(words[side], perf[side])) if a != b]
            print("  side", side, "half-time words identical:", not bad, bad[:8])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
