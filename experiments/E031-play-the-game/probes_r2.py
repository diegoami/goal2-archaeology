#!/usr/bin/env python3
"""The review round 2 mutation probes, run against the checks as they were at 2ad69bf and as they are
now, in throw-away copies (nothing in the tree is changed). Writes out/review2-probes.txt.
1. checks.sh with verify_saves.py replaced by a script that exits 1.
2. claims.py with out/saves.tsv emptied.
3. claims.py with out/g1/game-folder.tsv emptied.
Usage: python3 experiments/E031-play-the-game/probes_r2.py"""
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = "experiments/E031-play-the-game"
OLD = "2ad69bf"


def old(path):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{OLD}:{path}"], capture_output=True, text=True,
                          check=True).stdout


def tree(tmp, version):
    """A copy of the repository parts the checks read: E031 (logs linked), docs/play-guide.md,
    tools/check_links.py; with the 2ad69bf files when version == 'old'."""
    root = Path(tmp) / version
    e = root / REL
    e.mkdir(parents=True)
    for f in HERE.iterdir():
        if f.is_file():
            shutil.copy(f, e / f.name)
    (e / "out").mkdir()
    for d in (HERE / "out").iterdir():
        if d.is_dir():
            (e / "out" / d.name).mkdir()
            for f in d.iterdir():
                (e / "out" / d.name / f.name).symlink_to(f)
        else:
            shutil.copy(d, e / "out" / d.name)
    (root / "docs").mkdir()
    shutil.copy(ROOT / "docs" / "play-guide.md", root / "docs" / "play-guide.md")
    if version == "old":
        for name in ("checks.sh", "claims.py", "claims.tsv"):
            (e / name).write_text(old(f"{REL}/{name}"))
        (root / "docs" / "play-guide.md").write_text(old("docs/play-guide.md"))
    return root, e


def empty(path):
    if path.is_symlink():
        path.unlink()
    path.write_text("")


def sh(argv, cwd):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip().split("\n")[-1]


def main():
    lines = [f"Review round 2 probes: the checks at {OLD} (old) and now (new), in throw-away copies.", ""]
    with tempfile.TemporaryDirectory() as tmp:
        for version in ("old", "new"):
            root, e = tree(tmp, version)
            (e / "verify_saves.py").write_text("import sys\nprint('verify failed')\nsys.exit(1)\n")
            if version == "old":
                rc, last = sh(["bash", str(e / "checks.sh")], root)
            else:
                rc, last = sh(["python3", str(e / "checks.py"), "--out", str(e / "out" / "checks-probe.txt")], root)
            lines.append(f"1 {version}: checks with a failing verify_saves -> exit {rc}; last line: {last}")
        for n, target in ((2, "saves.tsv"), (3, "g1/game-folder.tsv")):
            for version in ("old", "new"):
                root, e = tree(Path(tmp) / f"p{n}", version)
                empty(e / "out" / target)
                rc, last = sh(["python3", str(e / "claims.py")], root)
                lines.append(f"{n} {version}: claims with out/{target} emptied -> exit {rc}; last line: {last}")
    (HERE / "out" / "review2-probes.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
