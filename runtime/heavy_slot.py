"""Run this command as a heavy job (#318): wait for a slot of tools/harness/heavy.sh, then go on.

    if __name__ == "__main__":
        heavy_slot.take("family-run", weight=workers)    # first thing; main() and the tests never call it
        sys.exit(main())

`take` re-runs the whole command (sys.orig_argv, so `-m pkg.mod` and `-B` survive) under heavy.sh, which holds
`weight` of the machine's slots (harness.json heavy.slots, two by default) for as long as the command runs, and
says "heavy: <name>: waiting for a slot (k ahead)" while it queues. It returns, running the command as it is,
when the command already is inside a heavy job (HARNESS_HEAVY_HELD: the outer job holds the slot), in CI (CI is
set: a runner is not this machine), when HARNESS_HEAVY_OFF is set, or when heavy.sh or flock is missing."""
import contextlib
import io
import os
import shutil
import sys
from pathlib import Path

HEAVY = Path(__file__).resolve().parents[1] / "tools" / "harness" / "heavy.sh"


def parsed(parser, argv=None):
    """What `parser` makes of the command line, or None when it would refuse it (an error, --help, a value out of
    its choices). An entry point derives its slot weight from this, with the parser main() uses, so the weight and the
    run cannot disagree (repeated options, --opt=value, abbreviations, invalid values: argparse's own rules). A refused
    command line holds no slot and prints nothing here: main() then prints argparse's own message and exits."""
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit:
        return None


def take(name, weight=1, argv=None):
    """Replace this process by `heavy.sh --weight <weight> <name> -- <this command>`; return when it should not."""
    if os.environ.get("HARNESS_HEAVY_HELD") or os.environ.get("CI") or os.environ.get("HARNESS_HEAVY_OFF"):
        return
    if not HEAVY.is_file() or not os.access(HEAVY, os.X_OK) or shutil.which("flock") is None:
        return
    command = list(argv if argv is not None else sys.orig_argv)
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv(str(HEAVY), [str(HEAVY), "--weight", str(weight), name, "--", *command])
