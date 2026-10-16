#!/usr/bin/env python3
"""E033 (issue 250): can the original's run_match (0791:F1F6) be entered directly from a menu-state image,
and is the match it plays the original's? An independent probe on runtime/emul/watched_match.py's Guest
(not on the kit), so the kit's own check has a second implementation to agree with.

    python3 -B experiments/E033-original-match-kit/entry_probe.py --log experiments/E033-original-match-kit/out/<new>.jsonl

The frame is route_fixture's own (static/goal-exe/code/seg_000E_09.asm:308, `6F18 call far 0791:F1F6`): the
fixture far pointer and the return address 000E:6F1D pushed so that SP = 0x3EC0 at F1F6's entry, the SP
E011-r0001's watchstart stack shows for that call (its BP chain holds F1F6's frame at 3EBE with the return
0831:6F1D and the argument 5DB4:00A6 = fixture 21). Declared writes: the game record's fixture index
[A923]+0x26 := the fixture number (route_fixture's own value while it plays that fixture), and the delay
calibration dword DS:A9FF := 20 (E032: delays only count passes). Key reads are answered at the declared
screens only (team screen, captain prompt, boards: Enter); any other read stops the run.

Runs (one JSON line each):
- `faithful`: E006-r0005 (E011-r0001's own start state), fixture 21 of its calendar (Denmark v 19), no other
  input; compared with E021's emulated E011-r0001 record (experiments/E021-m0-whole-match/out/
  20261011T201945897620Z-none-E011-r0001.json), whose reads E021 placed on E011's DOSBox-X reads.
- `family`: the same with the main seed written at the captain prompt's wait (where E011's watchstart was
  taken) and the delay byte := 0, as E032's timing.py did from the watchstart; compared with E032's records
  of the same seeds (timing-delay20-kickoff-20261015.jsonl, timing-delay20-8seeds-20261015.jsonl).
- `reseed`: two entry seeds; the first write of DS:7B62 after the entry, its writer and value."""
import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
from watched_match import Guest, WatchedMatch, routine_return  # noqa: E402
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_INTR  # noqa: E402

E006_R0005 = ("3789d8490d2b42d8a589fec2afeb51de0ace4b4c5d1e5e24ff232321874dd106", "e006-2100-r0005.sav")
E021_RECORD = ROOT / "experiments/E021-m0-whole-match/out/20261011T201945897620Z-none-E011-r0001.json"
E032_LOGS = [ROOT / "experiments/E032-match-engine-inventory/out" / n
             for n in ("timing-delay20-kickoff-20261015.jsonl", "timing-delay20-8seeds-20261015.jsonl")]
ENTER = 0x0D


def image(sha, name):
    path = ROOT / ".cache" / "dl" / f"{sha[:16]}-{name}"
    if not path.is_file():
        sys.exit(f"missing {path}: gh release download E006 --repo diegoami/goal2-archaeology "
                 f"--pattern {sha[:16]}-{name} --dir {path.parent}")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        sys.exit(f"{path}: sha256 differs from {sha}")
    return data


def digest(draws):
    return hashlib.sha256("\n".join("%d %d %04x %04x" % d for d in draws).encode()).hexdigest()


class Entry(Guest):
    screen = WatchedMatch.screen
    name = WatchedMatch.name
    commentary = WatchedMatch.commentary
    scorers = WatchedMatch.scorers
    statistics = WatchedMatch.statistics

    def __init__(self, data, fixture_n=21, seed_override=None, delay_byte=0, entry_seed=None):
        super().__init__(data)
        self.seed_override, self.delay_byte = seed_override, delay_byte
        self.recording = False
        self.draws, self.ticks, self.reads, self.strays = [], 0, [], []
        self.pending = None
        self.full_time = False
        self.board = None
        self.captain_wait = None
        self.first_seed_write = None
        self.put(self.far(0xA923) + 0x26, fixture_n.to_bytes(2, "little"))
        self.put(self.DS * 16 + 0xA9FF, (20).to_bytes(4, "little"))
        if entry_seed is not None:
            self.put(self.DS * 16 + 0x7B62, entry_seed.to_bytes(2, "little"))
        self.entry_seed = self.rd(0x7B62)
        fix_off, fix_seg = self.rd(0xA92B) + 8 * (fixture_n - 1), self.rd(0xA92D)
        self.fixture_bytes = self.mem(fix_seg * 16 + fix_off, 8).hex()
        ss, sp = 0x3875, 0x3EC0
        for i, w in enumerate([0x6F1D, self.seg(0x000E), fix_off, fix_seg]):
            self.put(ss * 16 + sp + 2 * i, w.to_bytes(2, "little"))
        for r, v in (("ss", ss), ("sp", sp), ("bp", 0x3EDE), ("ds", self.DS), ("es", self.DS),
                     ("cs", self.seg(0x791)), ("eip", 0xF1F6)):
            self.set_reg(r, v)
        self._hooks()

    def where(self, seg, off):
        return "%04X:%04X" % ((seg - self.load) & 0xFFFF, off)

    def _hooks(self):
        mu = self.mu
        mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
        seed_lin = self.DS * 16 + 0x7B62

        def seed_write(uc, access, address, size, value, data):
            old = self.word_at(seed_lin)
            raw = bytearray(old.to_bytes(2, "little"))
            for i in range(size):
                j = address + i - seed_lin
                if 0 <= j < 2:
                    raw[j] = (value >> (8 * i)) & 0xFF
            new = int.from_bytes(raw, "little")
            if self.first_seed_write is None:
                self.first_seed_write = {"writer": self.where(self.reg("cs"), self.reg("ip")),
                                         "old": old, "new": new}
            if self.recording:
                self.draws.append((self.rd(0x831F), self.rd(0x831D), old, new))
        mu.hook_add(UC_HOOK_MEM_WRITE, seed_write, begin=seed_lin, end=seed_lin + 1)

        def code_at(address, fn):
            lin = self.lin(address)
            mu.hook_add(UC_HOOK_CODE, fn, begin=lin, end=lin)

        def tick(uc, addr, size, data):
            if self.recording:
                self.ticks += 1
        code_at("0791:970C", tick)

        def match_returned(uc, addr, size, data):
            self.full_time = True
        code_at("0791:F2E3", match_returned)

        def keypressed(uc, addr, size, data):
            self.set_reg("ax", (self.reg("ax") & 0xFF00) | (1 if self.pending else 0))
            self.return_from(True, 0)

        def readkey(uc, addr, size, data):
            try:
                if self.rd(0x79AE, 1):
                    return
                site = self.where(self.stack_word(2), self.stack_word(0))
                bp, ssl = self.reg("bp"), self.reg("ss") * 16
                caller = self.where(self.word_at(ssl + bp + 4), self.word_at(ssl + bp + 2))
                if site == "0791:CEED" and self.pending:
                    what = "captain prompt"
                elif site == "214B:157C" and caller == "0791:EE9F":
                    what = "team screen"
                elif site == "0791:041A":
                    what = "board"
                    if self.full_time and self.board is None:
                        self.board = self.outputs_now()
                else:
                    raise RuntimeError(f"undeclared key read at {site} (frame caller {caller})")
                self.reads.append([what, site, self.rd(0x831F), self.rd(0x831D)])
                self.pending = None
                self.put(self.DS * 16 + 0xA976, bytes([ENTER, ENTER]))
                self.return_from(True, 0)
            except Exception as e:
                self.error = e
                uc.emu_stop()
        code_at("214B:0723", keypressed)
        code_at("214B:08DD", readkey)

        def captain(uc, addr, size, data):
            if self.stack_word(2) & 0xFF == 1:      # role 1: the captain (CC7B's last-pushed argument)
                self.pending = ENTER
        code_at("0791:CC7B", captain)

        def wait_entry(uc, addr, size, data):
            if not self.recording and self.pending and 0xCC7B <= self.stack_word(0) < 0xD016:
                if self.seed_override is not None:
                    self.put(self.DS * 16 + 0x7B62, self.seed_override.to_bytes(2, "little"))
                if self.delay_byte is not None:
                    self.put(self.far(0xA923) + 0x3F, bytes([self.delay_byte]))
                self.captain_wait = {"seed": self.rd(0x7B62), "kickoff_side_831A": self.rd(0x831A, 1)}
                self.recording = True
        code_at("0791:CC2E", wait_entry)

        for name in ("000E:05F6", "000E:0572", "000E:04F5", "000E:045D"):
            far, pop = routine_return(name)

            def skip(uc, addr, size, data, name=name, far=far, pop=pop):
                self.strays.append(name)
                self.return_from(far, pop)
            code_at(name, skip)

    def outputs_now(self):
        return {"score": [self.rd(0x9B3C, 1), self.rd(0x9B3D, 1)], "ticks": self.ticks, "draws": len(self.draws),
                "draws_digest": digest(self.draws), "statistics_raw": self.statistics(),
                "templates": {str(k): v for k, v in collections.Counter(r["template"] for r in self.commentary()).items()},
                "scorers": self.scorers(), "man_of_the_match_word": self.rd(0x7C3A),
                "board_screen_sha256": self.screen().digest(), "seed_at_board": self.rd(0x7B62)}

    def go(self, timeout_s=600):
        t, c = time.time(), time.process_time()
        self.emulate(self.lin("000E:6F1D"), timeout_s)
        self.wall_s, self.cpu_s = round(time.time() - t, 1), round(time.process_time() - c, 1)
        return self


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    data = image(*E006_R0005)
    out = open(log, "x")

    def emit(rec):
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print(json.dumps({k: rec[k] for k in rec if k not in ("board", "statistics_raw")})[:400], flush=True)

    for s in (None, 0x1234):
        p = Entry(data, entry_seed=s, delay_byte=None)
        p.go()
        emit({"run": "reseed", "entry_seed": p.entry_seed, "first_seed_write": p.first_seed_write,
              "captain_wait": p.captain_wait, "error": None})
    e021 = json.loads(E021_RECORD.read_text())
    p = Entry(data).go()
    b = p.board
    checks = {"score": b["score"] == e021["score"], "ticks": b["ticks"] == e021["final"]["ticks"],
              "draws": b["draws"] == e021["draws_count"], "draws_digest": b["draws_digest"] == e021["draws_sha256"],
              "statistics_raw": b["statistics_raw"] == e021["statistics_raw"], "scorers": b["scorers"] == e021["scorers"],
              "man_of_the_match": b["man_of_the_match_word"] == e021["man_of_the_match_word"],
              "board_screen_sha256": b["board_screen_sha256"] == e021["board_screen_sha256"],
              "seed_at_board": b["seed_at_board"] == e021["final"]["7B62"]}
    emit({"run": "faithful", "fixture_bytes": p.fixture_bytes, "captain_wait": p.captain_wait, "reads": p.reads,
          "strays": p.strays, "board": b, "against": str(E021_RECORD.relative_to(ROOT)), "checks": checks,
          "identical": all(checks.values()) and not p.strays, "wall_s": p.wall_s, "cpu_s": p.cpu_s})
    fam = {}
    for f in E032_LOGS:
        for line in f.read_text().splitlines():
            r = json.loads(line)
            fam[r["seed"]] = r
    same = 0
    for seed in sorted(fam):
        r = fam[seed]
        p = Entry(data, seed_override=seed).go()
        b = p.board
        checks = {k: b[k] == r[k] for k in ("score", "ticks", "draws", "draws_digest", "statistics_raw", "templates")}
        ok = all(checks.values()) and not p.strays and p.error is None
        same += ok
        emit({"run": "family", "seed": seed, "checks": checks, "identical": ok, "score": b["score"], "ticks": b["ticks"],
              "draws": b["draws"], "reads": p.reads, "strays": p.strays, "wall_s": p.wall_s, "cpu_s": p.cpu_s})
    emit({"run": "summary", "family_identical": same, "family_size": len(fam)})


if __name__ == "__main__":
    main()
