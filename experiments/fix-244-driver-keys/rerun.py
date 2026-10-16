#!/usr/bin/env python3
"""Re-run one earlier experiment's own script once on the fixed driver, writing its run records under
experiments/fix-244-driver-keys/out/rerun-default/<E>/ instead of runs/<E>/ (the originals are never touched,
and the numbering restarts: these are r0001... of this folder). out/rerun/ holds the first re-runs,
made when the savestate key was held 0.15 s (the read pace was 4 times faster than the original's);
the driver's default hold is now SAVE_HOLD, and the re-runs with it are in out/rerun-default/.

    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 --runs 1 --dos-time 10:00:00 --dos-date 10/04/1993 --batch fix244
    python3 experiments/fix-244-driver-keys/rerun.py E006 games --times 10:00 --batch fix244
    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 ... --legacy-keys   # control: old keys, into out/rerun-legacy-keys/
    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 ... --legacy-only keys|save   # control: one part the old way
    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 ... --hold-alt   # control: Left Alt held after the launch, into out/rerun-alt-held/
    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 ... --f12-per-read   # control: a plain F12 into the guest before each read, into out/rerun-f12-per-read/
    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 ... --save-key-hold 0.6   # control: slow reads, into out/rerun-save-key-hold-0.6/

The experiment script is loaded unchanged and only its output folder (OUT, and E006's copy of E003's)
is replaced; its own clean-tree rule applies (commit before running)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = {"E003": "E003-q001-inputs", "E006": "E006-q004-skills"}


def load(exp):
    path = ROOT / "experiments" / SCRIPTS[exp] / "run.py"
    spec = importlib.util.spec_from_file_location(f"rerun_{exp}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    exp, argv = sys.argv[1], sys.argv[2:]
    legacy = "--legacy-keys" in argv  # a control: the same script on the fixed driver with its old xdotool keys
    argv = [a for a in argv if a != "--legacy-keys"]
    mix = None  # a control: only the game keys, or only the savestate key, the old way (the other part fixed)
    if "--legacy-only" in argv:
        i = argv.index("--legacy-only")
        mix = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
        sys.path.insert(0, str(ROOT / "runtime" / "driver"))
        import driver

        def old_way(name):
            orig = getattr(driver.Driver, name)

            def wrapped(self, *a, **k):
                was, self.legacy_keys = self.legacy_keys, True
                try:
                    return orig(self, *a, **k)
                finally:
                    self.legacy_keys = was
            setattr(driver.Driver, name, wrapped)
        for name in {"keys": ("keys",), "save": ("_hostkey", "_write_mapper")}[mix]:
            old_way(name)
    hold_alt = "--hold-alt" in argv  # a control: the fixed driver, plus Left Alt pressed after the launch and never released
    argv = [a for a in argv if a != "--hold-alt"]
    if hold_alt:
        sys.path.insert(0, str(ROOT / "runtime" / "driver"))
        import driver
        import xkeys
        launch = driver.Driver.launch

        def launch_then_alt(self, *a, **k):
            sc = launch(self, *a, **k)
            dpy = xkeys._x11.XOpenDisplay(self.display.encode())
            code = xkeys._x11.XKeysymToKeycode(dpy, xkeys._x11.XStringToKeysym(b"Alt_L"))
            xkeys._xtst.XTestFakeKeyEvent(dpy, code, 1, 0)
            xkeys._x11.XFlush(dpy)
            xkeys._x11.XCloseDisplay(dpy)
            self.log("control: Alt_L pressed and left down")
            return sc
        driver.Driver.launch = launch_then_alt
    f12 = "--f12-per-read" in argv  # a control: a plain F12 pressed into the guest before each savestate key, as the old chord did on Ubuntu 24.04
    argv = [a for a in argv if a != "--f12-per-read"]
    if f12:
        sys.path.insert(0, str(ROOT / "runtime" / "driver"))
        import driver
        import xkeys
        hostkey = driver.Driver._hostkey

        def f12_then_hostkey(self, name, hold=None):
            xkeys.press_release(self.display, "F12", 0.05)
            return hostkey(self, name, hold)
        driver.Driver._hostkey = f12_then_hostkey
    slow = None  # a control: the fixed driver with a longer hold of the savestate key (reads as slow as the F12 chord's)
    if "--save-key-hold" in argv:
        i = argv.index("--save-key-hold")
        slow = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
        sys.path.insert(0, str(ROOT / "runtime" / "driver"))
        import driver
        hostkey = driver.Driver._hostkey
        driver.Driver._hostkey = lambda self, name, hold=slow: hostkey(self, name, hold)
    if legacy:
        sys.path.insert(0, str(ROOT / "runtime" / "driver"))
        import driver
        init = driver.Driver.__init__
        driver.Driver.__init__ = lambda self, *a, **k: init(self, *a, **{**k, "legacy_keys": True})
    mod = load(exp)
    out = HERE / "out" / ("rerun-legacy-keys" if legacy else f"rerun-save-key-hold-{slow}" if slow else f"rerun-legacy-only-{mix}" if mix else "rerun-alt-held" if hold_alt else "rerun-f12-per-read" if f12 else "rerun-default") / exp
    mod.OUT = out
    if hasattr(mod, "e003"):  # E006 loads E003's script for its keys and helpers
        mod.e003.OUT = out
    if exp == "E006":
        # E006 names the kept savestate by run id in .cache/states/driver/ and never replaces one: number past those
        next_id = mod.next_id

        def next_id_past_kept_states():
            kept = [int(p.stem.rsplit("-r", 1)[1]) for p in mod.driver.STATES.glob("e006-*-r*.sav")]
            return max(next_id(), 1 + max(kept, default=0))
        mod.next_id = next_id_past_kept_states
    if exp == "E003":
        # E003's Run.add skips a read whose id() it has seen, and the reads are freed after their step: under
        # Python 3.14 a new read gets a freed one's id and is skipped, so E003-r0001 and r0002 of this folder
        # (made without this) lack steps 2-4, 7 and 9-11. Keeping every read alive makes ids unique.
        add = mod.Run.add

        def add_keeping_reads(self, label, read=None):
            self.__dict__.setdefault("_kept", []).append(read or self.d.last)
            return add(self, label, read)
        mod.Run.add = add_keeping_reads
    return mod.main(argv)


if __name__ == "__main__":
    sys.exit(main())
