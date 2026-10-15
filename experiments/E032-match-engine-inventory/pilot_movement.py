#!/usr/bin/env python3
"""E032 pilot: the plan's porting method tried on one piece of the watched engine, the player's run step.

    python3 -B experiments/E032-match-engine-inventory/pilot_movement.py --seeds 0x1234,0x2345 [--variant NAME] --log experiments/E032-match-engine-inventory/out/<new file>.jsonl

The method (docs/match-engine-plan.md): port a routine from the listing (the named view as a guide),
memory-faithful (it reads and writes the same bytes as the original), substitute it in the E021 harness
WITHOUT a side-by-side proof, and check the whole match: score, ticks, every main-seed draw (their digest),
the board's raw statistics and the commentary's template counts must equal the unhooked match of the same
seed (timing.py's log). A wrong port shows as a different trajectory; a proof (Guest.hook(prove=True)) is
kept for locating the first wrong call, not for accepting a port.

Ported here (static/goal-exe/code/seg_0791_14.asm, seg_0791_05.asm, seg_0791_04.asm, seg_0791_01.asm,
seg_23E4_01.asm, seg_214B_01.asm; the line comments are listing offsets):
- `0791:8889` player_run_step (called only from 8AE9 update_player, with 8AE9's BP: a nested procedure),
- `0791:86D0` the move test it calls (one cell in the run direction +0xF; blocked off the pitch, or, while
  the clock runs, for an outfield player who is neither the holder 830B nor 830C, by a cell of the pitch
  picture [DS:7C16] whose attribute is not 0x0D and whose character is in the set DS:0648),
- the helpers `2BE5` attack_direction, `2974` pitch_slot_side, `045D` is_keeper_slot, `2CC5` (on target),
  `2DCA` (on the pitch), the set test `23E4:08DF`, and the draws `214B:06FA` (coin) and `214B:06B1` (rand n)
  on the seed word at the far pointer DS:A978.

Variants (falsifiers: each must change the trajectory): `coin-swapped` (the coin's two axis orders swapped,
8A33), `bound-36` (2DCA's row bound 0x25 read as 0x24), `no-picture` (86D0 never blocked by the picture)."""
import argparse
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E021-m0-whole-match"))
sys.path.insert(0, str(ROOT / "experiments" / "E032-match-engine-inventory"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
from check import asset, draws_digest  # noqa: E402
from timing import set_delay_at_kickoff, RECORD  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402

VARIANTS = ("exact", "coin-swapped", "bound-36", "no-picture")


def s8(v):
    return v - 0x100 if v & 0x80 else v


class Port:
    def __init__(self, g, variant="exact"):
        self.g, self.variant = g, variant
        self.calls = 0

    # -- memory --------------------------------------------------------------------------------
    def b(self, lin):
        return self.g.mem(lin, 1)[0]

    def put8(self, lin, v):
        self.g.put(lin, bytes([v & 0xFF]))

    def ds8(self, off):
        return self.g.rd(off, 1)

    def farptr(self, off):
        return self.g.rd(off), self.g.rd(off + 2)      # (offset, segment)

    @staticmethod
    def lin(seg, off):
        return seg * 16 + (off & 0xFFFF)

    # -- 214B: the draws on the seed word at the far pointer DS:A978 ----------------------------------
    def rand(self, n):                                   # 214B:0688 via 06B1 (seg_214B_01.asm:873-911)
        off, seg = self.farptr(0xA978)
        lin = self.lin(seg, off)
        new = (self.g.word_at(lin) * 0x7ABD + 0x1B0F) & 0xFFFF
        self.g.put(lin, new.to_bytes(2, "little"))
        return (((new * n) >> 16) + 1) & 0xFFFF

    def coin(self):                                      # 214B:06FA: rand(2) == 1 (0706-0717)
        return 1 if self.rand(2) == 1 else 0

    def in_set(self, set_lin, element):                  # 23E4:08DF: bit e of byte e>>3 (08E5-08FA)
        return bool(self.b(set_lin + (element >> 3)) & (1 << (element & 7)))

    # -- helpers -------------------------------------------------------------------------------
    def pitch_slot_side(self, rec):                      # 2974: slot +6 < 0x0C (297D-2988)
        return 1 if self.b(rec + 6) < 0x0C else 0

    def attack_direction(self, rec):                     # 2BE5 (2BEB-2C19)
        half = s8(self.ds8(0x8319))                      # sign-extended to a long
        left = self.g.rd(0x831B)                         # zero-extended to a long
        flag = 1 if (half < 0 or left > half) else 0     # 2BF9-2C07: dx=0 against bx, then unsigned ax > cx
        return s8(self.ds8(0x7920 + (flag ^ self.pitch_slot_side(rec))))

    @staticmethod
    def is_keeper_slot(slot):                            # 045D: word 1 or 0x0C (0463-0473)
        return slot in (1, 0x0C)

    def on_target(self, rec):                            # 2CC5: word +0 == word +7 (2CCE-2CDE)
        return self.g.word_at(rec) == self.g.word_at(rec + 7)

    def on_pitch(self, word):                            # 2DCA: |s8 lo| <= 8 and |s8 hi| <= 0x25 (2DD0-2DF2)
        bound = 0x24 if self.variant == "bound-36" else 0x25
        return abs(s8(word & 0xFF)) <= 8 and abs(s8(word >> 8)) <= bound

    # -- 86D0: one step in direction +0xF, and whether the cell is free ----------------------------------
    def can_move(self, rec):
        self.g.put(rec, self.g.mem(rec + 2, 2))          # 86E1-86F0: position := the drawn position
        f = self.b(rec + 0xF)
        if f == 1:
            self.put8(rec, self.b(rec) - 1)              # 8711
        elif f == 2:
            self.put8(rec, self.b(rec) + 1)              # 8725
        elif f == 3:
            self.put8(rec + 1, self.b(rec + 1) - 1)      # 8739
        elif f == 4:
            self.put8(rec + 1, self.b(rec + 1) + 1)      # 874E
        if self.b(rec + 0xF) == 5:                       # 875D
            return True
        if not self.on_pitch(self.g.word_at(rec)):      # 8772-877C
            return False
        if self.ds8(0x8325) == 0:                        # 877F
            return True
        slot = self.b(rec + 6)
        if slot == self.ds8(0x830C) or slot == self.ds8(0x830B):   # 8798, 87B0
            return True
        poff, pseg = self.farptr(0xA91B)                 # 87C4-87D8: the player's position code +6
        player = self.g.word_at(rec + 0xD)
        if self.b(self.lin(pseg, poff + ((player * 0x14) & 0xFFFF)) + 6) == 0:
            return True
        if self.variant == "no-picture":
            return True
        boff, bseg = self.farptr(0x7C16)                 # 87E8-8813: the pitch picture's cell
        cell = (boff + ((s8(self.b(rec)) * 0xA0) & 0xFFFF) + ((s8(self.b(rec + 1)) * 2) & 0xFFFF)) & 0xFFFF
        if self.b(self.lin(bseg, cell + 0x90F)) == 0x0D:
            return True
        ch = self.b(self.lin(bseg, cell + 0x90E))        # 8845-8855: a character of the set DS:0648 blocks
        return not self.in_set(self.g.DS * 16 + 0x648, ch)

    # -- 8889 ----------------------------------------------------------------------------------
    def run_step(self, rec):
        self.calls += 1
        skip = False
        if self.ds8(0x8302) != 0:                        # 888F
            own = s8(self.b(rec + 1)) * self.attack_direction(rec)       # 88A0-88B2
            ball = s8(self.ds8(0x82F7)) * self.attack_direction(rec)     # 88BF-88C9
            if ball > own:                               # 88CC jle 88D3, else 89E5
                skip = True
        if not skip:
            slot = self.b(rec + 6)
            if slot == self.ds8(0x830B) or slot == self.ds8(0x830C):     # 88DE, 88F2
                skip = True
        if not skip:
            a = self.attack_direction(rec) > 0           # 8905-8912
            c = s8(self.b(rec + 8)) > 0                  # 891B-8928
            if a != c:
                skip = True
        if not skip:
            idx = 1 if self.pitch_slot_side(rec) == 0 else 0             # 8939-8946
            line = abs(s8(self.ds8(0x82E3 + 6 * idx)))                    # 8951-895C
            if abs(s8(self.b(rec + 8))) < line:          # 8965-8972 jl 89E5
                skip = True
            elif not self.in_set(self.lin(self.g.seg(0x791), 0x8869),
                                 self.b(rec + 0x12)):    # 897B-898A: the state in CS:8869 = {5, 7, 8, 11}
                skip = True
            elif self.is_keeper_slot(self.b(rec + 6)):   # 898C-899F
                skip = True
            else:
                d = self.attack_direction(rec)           # 89AB
                idx = 1 if self.pitch_slot_side(rec) == 0 else 0
                self.put8(rec + 8, s8(self.ds8(0x82E3 + 6 * idx)) - d)    # 89D2-89E1
        # 89E5: the target test, the coin, the run direction, and the move with its retries
        dx = s8((self.b(rec + 7) - self.b(rec)) & 0xFF)  # 89EC-89FD
        dy = s8((self.b(rec + 8) - self.b(rec + 1)) & 0xFF)               # 8A07-8A0B
        if self.on_target(rec):                          # 8A18-8A26
            self.put8(rec + 0xF, 5)
        else:
            coin = self.coin()                           # 8A2E
            if self.variant == "coin-swapped":
                coin ^= 1
            if coin:                                     # 8A33 je 8A7F
                f = (1 if dx > 0 else 0) + 1 if abs(dx) > 0 else (1 if dy > 0 else 0) + 3
            else:
                f = (1 if dy > 0 else 0) + 3 if abs(dy) > 0 else (1 if dx > 0 else 0) + 1
            self.put8(rec + 0xF, f)
        while not self.can_move(rec):                    # 8AC5-8AE1
            self.put8(rec + 0xF, self.rand(5))


def hook_fn(port):
    def fn(g):
        parent_bp = g.arg(0, far=False)                  # 8AE9's BP (8AC5's `push bp` analogue in 8AE9)
        ss = g.reg("ss")
        off = g.word_at(ss * 16 + ((parent_bp + 6) & 0xFFFF))
        seg = g.word_at(ss * 16 + ((parent_bp + 8) & 0xFFFF))
        port.run_step(seg * 16 + off)
    return fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--variant", choices=VARIANTS, default="exact")
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    log.parent.mkdir(parents=True, exist_ok=True)
    record = json.loads(RECORD.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    data = asset(entry)
    for s in a.seeds.split(","):
        seed = int(s, 0)
        m = WatchedMatch(data)
        m.set_seed(seed)
        set_delay_at_kickoff(m, 20)
        port = Port(m, a.variant)
        m.hook("0791:8889", hook_fn(port))
        t, c = time.time(), time.process_time()
        error = None
        try:
            m.run(timeout_s=300)
            if not m.stopped_at_board:
                error = "no full-time board within 300 s"
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        wall, cpu = round(time.time() - t, 1), round(time.process_time() - c, 1)
        stats = templates = None
        if not error:
            stats = m.statistics()
            templates = dict(collections.Counter(r["template"] for r in m.commentary()))
        rec = {"seed": seed, "delay_count": 20, "ported": ["0791:8889", "0791:86D0"], "variant": a.variant,
               "port_calls": port.calls, "hook_counts": dict(m.hook_counts), "error": error,
               "wall_s": wall, "cpu_s": cpu, "score": m.state()["score"], "ticks": len(m.tick_marks),
               "draws": len(m.draws), "draws_digest": draws_digest(m.draws), "strays": list(m.strays),
               "stopped_at_board": m.stopped_at_board, "inputs": m.inputs, "statistics_raw": stats,
               "templates": templates, "start_record": "E011-r0001", "watchstart_sha256": entry["sha256"]}
        with open(log, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps({k: rec[k] for k in ("seed", "variant", "port_calls", "score", "ticks", "draws", "cpu_s",
                                              "error")}), flush=True)


if __name__ == "__main__":
    main()
