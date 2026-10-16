"""One file from a glob: sorted, and exactly one match or an error (a glob that matches two files must not
silently pick one)."""
import glob


def one(pattern):
    m = sorted(glob.glob(pattern))
    if len(m) != 1:
        raise RuntimeError('expected exactly one match for %r, got %d: %s' % (pattern, len(m), m))
    return m[0]
