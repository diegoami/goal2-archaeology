#!/usr/bin/env python3
"""Rework R2: re-derive the per-tick RNG draw classification from the emulation.

Emulates E011-r0001's second half (the original binary's own code, no skips beyond the
BIOS key thunk and the unreachable 000E waits) and counts, from guest state at the draw
sites themselves:

- rand(5) draws at 0791:8AD1: the MOVEMENT RETRIES (a failed 86D0 move redraws the run
  direction 1..5 and loops), not restart/contest events;
- coin draws at 0791:8A2E, classified by the guard state the listing's early exits
  (8894/88E4/88F8 -> 88D3/89E5, which lead INTO the target block, not out of 8889)
  leave open at the draw: DS:8302 == 0, the record is the holder DS:830B, the record is
  DS:830C, or none of those;
- per 9564 sweep: the number of 8A2E coins, the number of ball phases (executions of
  the 95F2 block entry, which runs for EVERY slot whose guards pass - R4) and the number
  of 8AE9 update_player calls, split by return site: 9669 (the keeper special, inside the
  ball phase, so once per ball phase at most) and 96CB (the per-slot tail, once per slot).

Writes a fixed report to rng-counts.txt (the tracked output notes.md and F013 cite).

    python3 experiments/E011-q010-watched-engine/instrument_rng.py [--runs runs/E011]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/E011-q010-watched-engine"))
sys.path.insert(0, str(ROOT / "runtime/emul"))
from emu_check import halftime_sav  # noqa: E402
from unicorn import UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import *  # noqa: E402
from watched import WatchedHalf  # noqa: E402


class Instrumented(WatchedHalf):
    def __init__(self, data):
        super().__init__(data)
        self.rand5 = 0                 # draws at 8AD1 (movement retries)
        self.coins = Counter()         # 8A2E coins by class
        self.coins_per_sweep = Counter()
        self.ballphases_per_sweep = Counter()
        self.updates_by_site = Counter()   # 8AE9 calls by return site (9669/96CB)
        self.updates_per_sweep = Counter() # distribution of 8AE9 calls per sweep
        self._sweep_coins = 0
        self._sweep_ball = 0
        self._sweep_updates = 0
        mu, C = self.mu, self.CODE * 16

        def record_ptr(uc):
            # 8889's frame: the argument block pointer is ss:[bp+4]; its +6/+8 hold the
            # far pointer to the pitch record (every les in seg_0791_14.asm:8889-8AE6).
            bp = uc.reg_read(UC_X86_REG_BP)
            ss = uc.reg_read(UC_X86_REG_SS) * 16
            args = int.from_bytes(uc.mem_read(ss + bp + 4, 2), "little")
            off = int.from_bytes(uc.mem_read(ss + args + 6, 2), "little")
            seg = int.from_bytes(uc.mem_read(ss + args + 8, 2), "little")
            return seg * 16 + off

        def at_coin(uc, addr, size, data):
            if self.rd(0x8302, 1) == 0:
                self.coins["8302==0"] += 1
            else:
                slot = int.from_bytes(uc.mem_read(record_ptr(uc) + 6, 1), "little")
                if slot == self.rd(0x830B, 1):
                    self.coins["holder 830B"] += 1
                elif slot == self.rd(0x830C, 1):
                    self.coins["830C"] += 1
                else:
                    self.coins["other"] += 1
            self._sweep_coins += 1

        def at_rand5(uc, addr, size, data):
            self.rand5 += 1

        def at_ball(uc, addr, size, data):
            self._sweep_ball += 1

        def at_update(uc, addr, size, data):
            # 8AE9's return address on the stack names the caller: 9669 the keeper
            # special (seg_0791_15.asm:9666, inside the ball phase), 96CB the
            # per-slot tail (96C8).
            sp = uc.reg_read(UC_X86_REG_SP)
            ss = uc.reg_read(UC_X86_REG_SS) * 16
            ret = int.from_bytes(uc.mem_read(ss + sp, 2), "little")
            self.updates_by_site[ret] += 1
            self._sweep_updates += 1

        def at_engine(uc, addr, size, data):
            if self._sweep_coins or self._sweep_ball:
                self.coins_per_sweep[self._sweep_coins] += 1
                self.ballphases_per_sweep[self._sweep_ball] += 1
            if self._sweep_updates:
                self.updates_per_sweep[self._sweep_updates] += 1
            self._sweep_updates = 0
            self._sweep_coins = 0
            self._sweep_ball = 0

        mu.hook_add(UC_HOOK_CODE, at_coin, begin=C + 0x8A2E, end=C + 0x8A2E)
        mu.hook_add(UC_HOOK_CODE, at_rand5, begin=C + 0x8AD1, end=C + 0x8AD1)
        mu.hook_add(UC_HOOK_CODE, at_ball, begin=C + 0x95F2, end=C + 0x95F2)
        mu.hook_add(UC_HOOK_CODE, at_update, begin=C + 0x8AE9, end=C + 0x8AE9)
        mu.hook_add(UC_HOOK_CODE, at_engine, begin=C + 0x9564, end=C + 0x9564)

    def close_sweep(self):
        """Account the last sweep (no following 9564 entry to close it)."""
        if self._sweep_coins or self._sweep_ball:
            self.coins_per_sweep[self._sweep_coins] += 1
            self.ballphases_per_sweep[self._sweep_ball] += 1
        if self._sweep_updates:
            self.updates_per_sweep[self._sweep_updates] += 1
        self._sweep_updates = 0
        self._sweep_coins = 0
        self._sweep_ball = 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs/E011"))
    a = ap.parse_args(argv)
    rec = json.loads(sorted(Path(a.runs).glob("E011-r*.json"))[0].read_text())
    entry = next(o for o in rec["outputs"] if o["name"].endswith("-halftime.sav"))
    half = Instrumented(halftime_sav(entry)).run()
    half.close_sweep()
    lines = [
        f"E011 {rec['run_id']} second half, instrumented emulation (original guest code):",
        f"  ticks {half.final['ticks']}, main-seed draws {len(half.draws)},"
        f" final seed 0x{half.final['7B62']:04x}, score {half.final['score']}",
        "",
        "coin draws at 0791:8A2E (the sprint-axis choice), by guard state at the draw:",
        *(f"  {k:<14} {v}" for k, v in sorted(half.coins.items())),
        f"  total          {sum(half.coins.values())}",
        f"rand(5) draws at 0791:8AD1 (movement retries after a failed 86D0 move): {half.rand5}",
        "",
        "ball phases (95F2 block entries) per 9564 sweep: "
        + ", ".join(f"{k}:{v}" for k, v in sorted(half.ballphases_per_sweep.items())),
        f"  max per sweep {max(half.ballphases_per_sweep)}",
        "8A2E coins per 9564 sweep: "
        + ", ".join(f"{k}:{v}" for k, v in sorted(half.coins_per_sweep.items())),
        f"  max per sweep {max(half.coins_per_sweep)}",
        "8AE9 update_player calls by return site: "
        + ", ".join(f"{k:#06x}:{v}" for k, v in sorted(half.updates_by_site.items()))
        + " (9669 the keeper special inside the ball phase, 96CB the per-slot tail)",
        "update_player calls per 9564 sweep: "
        + ", ".join(f"{k}:{v}" for k, v in sorted(half.updates_per_sweep.items())),
        f"  max per sweep {max(half.updates_per_sweep)}",
    ]
    text = "\n".join(lines) + "\n"
    (Path(__file__).parent / "rng-counts.txt").write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
