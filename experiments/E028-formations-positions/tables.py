"""Decode, from the data-segment image (static/goal-exe/data/ds_2581_0*.hex), the tables the position code indexes.
usage: python3 -B tables.py OUTDIR   -> OUTDIR/tables-<UTC>.txt (never overwritten) and stdout."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ds import load_full
m = load_full()
def b(o, n): return [m[o + i] for i in range(n)]
def s8(v): return v - 256 if v > 127 else v
NAMES = ["goalkeeper","sweeper","centre back","left back","right back","defensive midfield","central midfield","left midfield",
         "right midfield","forward midfield","left winger","right winger","centre forward","striker"]
out = []
def P(*a): out.append(" ".join(str(x) for x in a))
P("# decoded from static/goal-exe/data/ds_2581_01.hex (DS offsets); position code p = 0..13")
P("\n## DS:079E  start post (x, y) per position, 14 words (x low byte, y high byte, signed); read by 0791:419C at 4218-421A")
for p in range(14):
    P("%2d %-20s (%3d, %4d)   bytes %02X %02X" % (p, NAMES[p], s8(m[0x79E + 2*p]), s8(m[0x79F + 2*p]), m[0x79E + 2*p], m[0x79F + 2*p]))
P("\n## DS:07BA  group code table g = DS:07BA[2*(pos>4) + flag] (0791:42CB); flag=1 when pos>=12, or pos<12 with tactic element 1 set and the slot on the ball's side; pos 0 -> 4")
P(b(0x7BA, 4))
P("\n## DS:07BE  home-depth offset per position, read by 0791:4438 (added to the post's y unless state 9)")
P(b(0x7BE, 14))
P("\n## DS:0812  kick-off depth per position, read by 0791:69BD (state 1): destination y = post y + this")
P(b(0x812, 14))
P("\n## DS:07CB  defending depth offset DS:07CB[e5*8 + e6*4 + g], g = 1..4 (0791:4B64 4CF8, 4649); e5, e6 = effective tactic elements 5, 6 (0/1)")
for e5 in (0, 1):
    for e6 in (0, 1):
        P("e5=%d e6=%d  g=1..4: %s" % (e5, e6, b(0x7CB + e5*8 + e6*4 + 1, 4)))
P("\n## DS:07DB  attacking depth offset DS:07DB[e7*4 + g], e7 = effective tactic element 7 (0791:4B64 4C85, 4532)")
for e7 in (0, 1):
    P("e7=%d  g=1..4: %s" % (e7, b(0x7DB + e7*4 + 1, 4)))
P("\n## DS:0820, DS:0822  kick-off words (x, y): the holder (DS:830B) and the last slot of the side (69BD)")
P("DS:0820", (s8(m[0x820]), s8(m[0x821])), "DS:0822", (s8(m[0x822]), s8(m[0x823])))
P("\n## DS:0D4E  line routing of the quick engine (F012)", b(0xD4E, 14))
P("## DS:0D5C  formation-label class (1771:0E6C): 0 keeper (not shown), 1 defence, 2 midfield, 3 attack", b(0xD5C, 14))
P("\n## DS:0E46 base height (inches) by club position; DS:0E54 jitter by player number mod 12 (1771:2FAD)")
P(b(0xE46, 14)); P(b(0xE54, 12))
P("## DS:0A28  position a computer team converts a forward-mid/winger to (0791:BEC7): [short, tall >= 72 in]", b(0xA28, 2))
P("\n## DS:0E7C  foot-row selector by player number mod 3; DS:0E60 foot index (0 left, 1 right; words at DS:0F2C + 6 * index) per row of 14 club positions")
P(b(0xE7C, 3))
for r in (0, 1):
    P("row %d:" % r, b(0xE60 + 14*r, 14))
P("\n## DS:0EF4..  who marks whom in man-to-man (1771:3E2F with 3EF8): row r (1..4), index = the OPPOSING position, value = the position code of my player taken to mark him")
for r in range(1, 5):
    P("priority %d:" % r, b(0xEE6 + 14*r, 14))
P("\n## DS:099A  bench roles per outgoing position, 8 bytes a row: [count, club positions accepted...] (0791:AAE8)")
for p in range(14):
    row = b(0x99A + 8*p, 8)
    P("%2d %-20s count %d roles %s" % (p, NAMES[p], row[0], row[1:1 + row[0]]))
P("\n## DS:08D5  keeper fallback score table DS:08D5[14*pos + role] (0791:A9B8)")
for p in range(14):
    P("%2d" % p, b(0x8D5 + 14*p, 14))
P("\n## CS:3139 left-flank set, CS:3159 right-flank set (1771:3179) -- from the code segment, see foot_truth.py output; CS:BEA7 {9,10,11}, CS:BFFA {12,13}, CS:3411 {0,1,3,4}")
txt = "\n".join(out)
print(txt)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
os.makedirs(sys.argv[1], exist_ok=True)
with open(os.path.join(sys.argv[1], "tables-%s.txt" % ts), "x") as f:
    f.write(txt + "\n")
