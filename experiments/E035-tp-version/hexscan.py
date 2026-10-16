#!/usr/bin/env python3
"""Count runs of more than 8 hex-encoded bytes (contiguous 'a1b2c3...' of 18+ hex digits, or 9+ space-separated
pairs) in the tracked files under a directory.  usage: hexscan.py DIR [--list]"""
import re, subprocess, sys

d = sys.argv[1]
files = subprocess.run(['git', 'ls-files', d], capture_output=True, text=True).stdout.split()
pat_c = re.compile(r'(?<![0-9A-Za-z])(?:[0-9a-fA-F]{2}){9,}(?![0-9A-Za-z])')
pat_s = re.compile(r'(?<![0-9A-Za-z])(?:[0-9a-fA-F]{2} ){8,}[0-9a-fA-F]{2}(?![0-9A-Za-z])')
total = 0
for f in files:
    try:
        t = open(f, errors='replace').read()
    except OSError:
        continue
    # sha256 digests (64 hex) are not byte runs
    t = re.sub(r'(?<![0-9A-Za-z])[0-9a-f]{64}(?![0-9A-Za-z])', 'SHA', t)
    t = re.sub(r'(?<![0-9A-Za-z])[0-9a-f]{16}(?![0-9A-Za-z])', 'SHA16', t)
    n = len(pat_c.findall(t)) + len(pat_s.findall(t))
    if n:
        total += n
        if '--list' in sys.argv:
            print(n, f)
print('hex runs of more than 8 bytes:', total)
