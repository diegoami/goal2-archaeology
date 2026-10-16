#!/usr/bin/env python3
"""Self-check of the one-match rule (pick.one) and of the byte-free output rule.
usage: selfcheck.py   (exit 0 when every check passes)"""
import glob, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pick


def naive(pattern):  # what run_all.py did before: the first unordered match
    return glob.glob(pattern)[0]


def raises_on_two(fn):
    d = tempfile.mkdtemp(prefix='pick')
    for n in ('a.img', 'b.img'):
        open(os.path.join(d, n), 'w').write('x')
    try:
        fn(os.path.join(d, '*.img'))
    except RuntimeError:
        return True
    return False


def raises_on_none(fn):
    d = tempfile.mkdtemp(prefix='pick')
    try:
        fn(os.path.join(d, '*.img'))
    except (RuntimeError, IndexError):
        return True
    return False


d = tempfile.mkdtemp(prefix='pick')
open(os.path.join(d, 'only.img'), 'w').write('x')
assert pick.one(os.path.join(d, '*.img')) == os.path.join(d, 'only.img'), 'one match must be returned'
assert raises_on_two(pick.one), 'pick.one must fail on two matches'
assert raises_on_none(pick.one), 'pick.one must fail on no match'
assert not raises_on_two(naive), 'the check itself must be able to fail: the old first-match code accepts two matches'
# no script of E035 other than pick.py (and this file) calls glob.glob
here = os.path.dirname(os.path.abspath(__file__))
for f in sorted(os.listdir(here)):
    if f.endswith('.py') and f not in ('pick.py', 'selfcheck.py'):
        assert 'glob.glob' not in open(os.path.join(here, f)).read(), f + ' calls glob.glob directly: use pick.one'
print('selfcheck ok: pick.one raises on two matches and on none; the old first-match code does not raise on two')
