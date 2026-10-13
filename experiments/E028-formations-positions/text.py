"""Print a data-segment range as text with control bytes shown (usage: text.py START END, hex DS offsets)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ds import load_full
mem = load_full()
a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
out = ""
for o in range(a, b):
    c = mem.get(o)
    if c is None: out += "<--->"; continue
    out += chr(c) if 32 <= c < 127 else "<%02X>" % c
print(out)
