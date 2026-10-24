"""Strict comparator over declared selected ALL members, without relaxed fields."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'experiments/E036-match-port'))
import compare, families

candidate = compare.load(sys.argv[1])
if not candidate:
    raise compare.Malformed('a selected comparison requires at least one record')
definitions = families.discover()
declared = {mid: digest for f in definitions.values() for mid, digest in f.expected().items()}
if set(candidate) - set(declared):
    raise compare.Malformed('candidate contains undeclared ALL members')
ref = {}
for f in definitions.values():
    ref.update(compare.load(ROOT/f.reference))
expected = {mid: declared[mid] for mid in candidate}
lines, ok = compare.check(ref, candidate, expected, expect=sys.argv[2] if len(sys.argv)>2 else 'identical',
                          image_sha256=families.image_sha256())
print('\n'.join(lines))
raise SystemExit(0 if ok else 1)
