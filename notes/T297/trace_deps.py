"""usage: trace_deps.py ROOT MODULEFILE OUT -- run one tests/test_x.py under an audit hook; write the
repo-relative paths it opens, imports or passes to subprocess."""
import json
import os
import sys
import unittest

root, mod, out = sys.argv[1], sys.argv[2], sys.argv[3]
seen = set()
root = os.path.realpath(root)


def note(p):
    try:
        p = os.path.realpath(p) if isinstance(p, (str, bytes, os.PathLike)) else None
    except Exception:
        return
    if p and p.startswith(root + os.sep):
        seen.add(os.path.relpath(p, root))


def hook(ev, args):
    if ev == "open":
        note(args[0]) if not isinstance(args[0], int) else None
    elif ev == "subprocess.Popen":
        for a in (args[1] if isinstance(args[1], (list, tuple)) else [args[1]]):
            if isinstance(a, str) and root in a:
                note(a.split()[0] if a.startswith(root) else a)
    elif ev == "os.listdir" or ev == "os.scandir":
        if args and args[0] is not None:
            note(args[0])


sys.addaudithook(hook)
sys.path.insert(0, os.path.join(root, "tests"))
os.chdir(root)
suite = unittest.defaultTestLoader.discover(os.path.join(root, "tests"), pattern=os.path.basename(mod))
res = unittest.TextTestRunner(stream=open(os.devnull, "w")).run(suite)
json.dump({"ok": res.wasSuccessful(), "files": sorted(seen)}, open(out, "w"), indent=0)
