"""Tests that need the network skip, visibly, when it is down (#236).

The tests marked `@needs_pinned_tools` run game-archaeologist's pinned tools, which `tools/ga.py`
fetches with `gh api` on every use (it lists the pinned tree before trusting the cache). Before such
a test runs, `require_pinned_tools` calls `ga.fetch()` once per process; `ga` already retries a
network failure once. When the fetch still fails on the network, the test is skipped with the gh
message as its reason, and the reason is also printed to stderr, so an offline run shows each skip
even without `-v`: a skipped test proves nothing, and the run must say so (CLAUDE.md rule 9). Any
other failure of the fetch (a blob sha mismatch, gh missing, an auth error) is not a skip: the test
runs and fails on it.
"""
from __future__ import annotations

import functools
import inspect
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import ga, net  # noqa: E402

# None until the first fetch; then "" (fetched) or the network failure's message (offline).
_offline: str | None = None


def skip_offline(name: str, reason: str):
    """Print the reason and skip: the one way a network test leaves the run without a result."""
    first = reason.strip().splitlines()[0] if reason.strip() else "network unreachable"
    message = f"offline, needs the network: {first}"
    print(f"SKIPPED {name}: {message}", file=sys.stderr)
    raise unittest.SkipTest(message)


def require_pinned_tools(name: str = "test") -> None:
    """Fetch the pinned tools (once per process), or skip `name` with the network failure."""
    global _offline
    if _offline is None:
        try:
            ga.fetch()
            _offline = ""
        except ga.GaError as e:
            if not net.is_network_error(str(e)):
                return  # not the network: let the test run and fail on it
            _offline = str(e)
    if _offline:
        skip_offline(name, _offline)


def needs_pinned_tools(obj):
    """Mark a test method, or every test method of a class, as needing the pinned tools."""
    if inspect.isclass(obj):
        for attr, value in list(vars(obj).items()):
            if attr.startswith("test") and callable(value):
                setattr(obj, attr, needs_pinned_tools(value))
        return obj

    @functools.wraps(obj)
    def wrapper(self, *args, **kwargs):
        require_pinned_tools(self.id())
        return obj(self, *args, **kwargs)
    return wrapper
