"""One retry for a `gh` call that fails on the network, and the test that says what a network
failure looks like (#236).

A reviewer's run of the suite met GitHub TLS timeouts (PR 222 round 1): a `gh` call that fails
because the network did not answer is retried once here, with a printed line saying so; any other
failure (a 404, an auth error, gh missing) is returned at once, never retried. What counts as a
network failure is `NETWORK_ERROR`, from the messages gh printed with the network blocked
(`unshare -cn`: "error connecting to api.github.com"), with HTTPS_PROXY at a closed port
("proxyconnect tcp: dial tcp ...: connect: connection refused") and at an unroutable address
("... i/o timeout", after 30 s), plus the TLS handshake timeout of the issue.
"""
from __future__ import annotations

import re
import subprocess
import sys

NETWORK_ERROR = re.compile(
    r"TLS handshake timeout|i/o timeout|dial tcp|proxyconnect|error connecting to"
    r"|connection (?:refused|reset)|context deadline exceeded|Client\.Timeout"
    r"|no such host|could not resolve host|temporary failure in name resolution"
    r"|network is unreachable",
    re.IGNORECASE,
)


def text(stream) -> str:
    """A captured stream as text (bytes are decoded, None is empty)."""
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", "replace")
    return stream


def is_network_error(message) -> bool:
    """True when `message` (text or bytes) is a network failure rather than an answer."""
    return bool(NETWORK_ERROR.search(text(message)))


def run_retrying(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run `argv` with its output captured; when it fails with a network error, print why and run
    it once more. The second result is returned whatever it is: one retry, never a loop."""
    result = subprocess.run(argv, check=False, capture_output=True, **kwargs)
    if result.returncode != 0 and is_network_error(result.stderr):
        first = text(result.stderr).strip().splitlines()
        reason = first[0] if first else f"exit {result.returncode}"
        print(f"{' '.join(argv[:3])}: network failure, retrying once: {reason}", file=sys.stderr)
        result = subprocess.run(argv, check=False, capture_output=True, **kwargs)
    return result
