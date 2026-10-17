"""Tests that need the network skip, visibly, when it is down (#236).

A test that needs something only GitHub serves is marked with `needs(what, probe)`: before the
test (or the `setUp`) runs, `probe` fetches that thing once per process, through gh calls that
already retry a network failure once (`tools/net.py`). When the probe still fails on the network,
the test is skipped with gh's message as its reason, and the reason is also printed to stderr, so
an offline run shows each skip even without `-v`: a skipped test proves nothing, and the run must
say so (CLAUDE.md rule 9). Any other failure of the probe (a blob sha mismatch, gh missing, an
auth error) is not a skip: it is raised, and the test errors on it.

`needs_pinned_tools` is the common case: game-archaeologist's pinned tools, which `tools/ga.py`
fetches with `gh api` on every use (it lists the pinned tree before trusting the cache).
"""
from __future__ import annotations

import functools
import inspect
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import ga, net  # noqa: E402

# what -> the network failure that made it unavailable in this process ("" once it was fetched).
_state: dict[str, str] = {}


def failure_text(e: BaseException) -> str:
    """Everything an exception says, a CalledProcessError's captured stderr included."""
    return "\n".join(t for t in (net.text(getattr(e, "stderr", None)), str(e)) if t)


def skip_offline(name: str, what: str, reason: str):
    """Print the reason and skip: the one way a network test leaves the run without a result."""
    lines = [line.strip() for line in reason.splitlines() if line.strip()]
    first = next((line for line in lines if net.is_network_error(line)),
                 lines[0] if lines else "network unreachable")
    message = f"offline, needs the network for {what}: {first}"
    print(f"SKIPPED {name}: {message}", file=sys.stderr)
    raise unittest.SkipTest(message)


def require(what: str, probe, name: str = "test") -> None:
    """Run `probe` once per process for `what`, or skip `name` when it failed on the network."""
    if what not in _state:
        try:
            probe()
        except (ga.GaError, SystemExit, subprocess.CalledProcessError, OSError) as e:
            text = failure_text(e)
            if not net.is_network_error(text):
                raise
            _state[what] = text
        else:
            _state[what] = ""
    if _state[what]:
        skip_offline(name, what, _state[what])


def needs(what: str, probe):
    """Mark a test method or `setUp`, or every test method of a class, as needing `what`."""
    def mark(obj):
        if inspect.isclass(obj):
            for attr, value in list(vars(obj).items()):
                if attr.startswith("test") and callable(value):
                    setattr(obj, attr, mark(value))
            return obj

        @functools.wraps(obj)
        def wrapper(self, *args, **kwargs):
            require(what, probe, self.id())
            return obj(self, *args, **kwargs)
        return wrapper
    return mark


needs_pinned_tools = needs("the pinned game-archaeologist tools", lambda: ga.fetch())
