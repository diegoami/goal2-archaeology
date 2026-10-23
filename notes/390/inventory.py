#!/usr/bin/env python3
"""Read-only #390 artifact inventory. Original bytes stay under --assets, outside Git.

Hashes come from E031's committed tables and E014's evidence manifests. The read-entry
stack reconstruction follows goal2/core/runner.py R1 (214B:08DD's prologue and its
Intr call at 08FF); the stack search is bounded to the same 0x200 bytes. No guest runs.
"""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "runtime/driver"), str(ROOT / "runtime/emul")]
from savestate import Savestate  # noqa: E402
from watched_match import cpu_state  # noqa: E402

E031 = "experiments/E031-play-the-game/out"
DRIVE = "goal2drive:goal2-archaeology/390-existing-states-20261023"


def commit(path):
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", path], cwd=ROOT, text=True).strip()


def entry(state, regs):
    """Locate 08DD's actual Intr frame; never interpret BIOS EBP as a game BP."""
    load = state.program().load
    ss, sp = regs["SS"], regs["ESP"] & 0xffff

    def word(off):
        return int.from_bytes(state.memory(ss * 16 + (off & 0xffff), 2), "little")

    hits = []
    for off in range(sp, sp + 0x200, 2):
        bp = (off + 4 + 6 + 0x14) & 0xffff
        if (word(off) == 0x0904 and word(off + 2) == (load + 0x214b) & 0xffff
                and word(off + 4) == (bp - 0x14) & 0xffff
                and word(off + 6) == ss and word(off + 8) & 0xff == 0x16):
            hits.append(bp)
    assert len(hits) == 1, f"expected one original 08DD frame, got {hits}"
    bp = hits[0]
    return {"ss": ss, "read_bp": bp, "caller_bp": word(bp),
            "site": f"{(word(bp + 4) - load) & 0xffff:04X}:{word(bp + 2):04X}"}


def inventory(folder):
    assets = []
    for table, name_column, kind in [(f"{E031}/saves.tsv", "file", "game-save"),
                                      (f"{E031}/states.tsv", "asset", "savestate")]:
        with (ROOT / table).open() as f:
            for row in csv.DictReader(f, delimiter="\t"):
                assets.append({"file": row[name_column], "sha256": row["sha256"],
                               "bytes": int(row["bytes"]), "kind": kind,
                               "source": table, "source_commit": commit(table),
                               "meaning": row.get("what", row.get("note"))})
    seen = {a["sha256"] for a in assets}
    for path in sorted((ROOT / "evidence/E014").glob("*.manifest.json")):
        manifest = json.loads(path.read_text())
        for row in manifest["files"]:
            if row["sha256"] in seen:
                continue
            seen.add(row["sha256"])
            source = str(path.relative_to(ROOT))
            assets.append({"file": row["asset"], "sha256": row["sha256"],
                           "bytes": row["bytes"], "kind": "savestate",
                           "source": source, "source_commit": commit(source),
                           "meaning": f"{manifest['run_id']} published starting state {row['name']}"})
    assert len({a["file"] for a in assets}) == len(assets), "duplicate artifact names"
    for a in assets:
        blob = (folder / a["file"]).read_bytes()
        assert len(blob) == a["bytes"], f"size mismatch: {a['file']}"
        assert hashlib.sha256(blob).hexdigest() == a["sha256"], f"hash mismatch: {a['file']}"
        a["drive_path"] = f"{DRIVE}/{a['file']}"
    p = next(a for a in assets if "shootout-start" in a["file"])
    blob = (folder / p["file"]).read_bytes()
    s, regs = Savestate(blob), cpu_state(blob)
    assert s.screen().digest() == "b4406ce687da4b2cbff84104287686bcf25a2230fbeb10c74fd08a0f5f5ba0cd"
    frame = entry(s, regs)
    assert frame["site"] == "214B:098A"
    bp, ss = frame["caller_bp"], frame["ss"] * 16

    def w(b, off):
        return int.from_bytes(s.memory(ss + b + off, 2), "little")

    parent = w(bp, 0)
    frame.update({"message_box_bp": parent,
                  "read_caller_return": f"{w(bp, 4) - s.program().load:04X}:{w(bp, 2):04X}",
                  "message_box_near_return": f"{w(parent, 2):04X}"})
    assert frame["read_caller_return"] == "214B:054E"
    assert frame["message_box_near_return"] == "A137"
    game = s.ds_word(0xa923) + 16 * s.ds_word(0xa925)
    p["observed"] = {"session": "g1", "step": 3874,
                     "screen_digest": s.screen().digest(), "cpu": regs, "frame": frame,
                     "state": {"season": int.from_bytes(s.memory(game + 0x38, 2), "little"),
                               "stage": s.memory(game + 0x3c, 1)[0],
                               "fixture": int.from_bytes(s.memory(game + 0x26, 2), "little"),
                               "fixtures": int.from_bytes(s.memory(game + 0x28, 2), "little")},
                     "countries": [s.ds_word(0x9b34), s.ds_word(0x9b36)],
                     "rng_word": s.ds_word(0x7b62)}
    return {"schema": "390-existing-state-inventory/1", "assets": assets}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--assets", type=Path, required=True)
    ap.add_argument("--check", type=Path)
    args = ap.parse_args()
    result = inventory(args.assets)
    if args.check:
        assert result == json.loads(args.check.read_text()), "inventory differs"
        print(f"{len(result['assets'])} artifacts verified; shootout screen, key wait and caller frame match")
    else:
        print(json.dumps(result, indent=2) + "\n", end="")


if __name__ == "__main__":
    main()
