"""Derive the substitution picker's foot rule from the ORIGINAL 0791:AAE8 (Unicorn, as foot_truth.py), exhaustively over
(outgoing code 0..13) x (candidate club code of the mapped role) x (foot index 0/1) x (two-footed) x (mapped or not), then on random
multi-candidate maps (last accepted wins). AAE8(map far ptr = the country's squad words, outgoing player): the byte DS:99A2+role is the
bench slot mapped to a role (0 = none); the row DS:099A + 8 * outgoing +6 lists the accepted roles.
usage: python3 -B picker_truth.py <GOAL.EXE> OUTDIR -> OUTDIR/picker-truth-<UTC>.log (+ .tsv)"""
import os, random, struct, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foot_truth import load, Guest, X
psha, usha, image = load(sys.argv[1]); g = Guest(image)
ds = g.DS * 16
SQ = 0x7000  # segment of the squad word array
ROWS = {p: [image[0x25810 + 0x99A + 8 * p + i] for i in range(8)] for p in range(14)}
STR = [3, 7, 10, 4, 8, 11]

def setup_player(n, club, two, foot_row_n=None):
    rec = bytearray(20); rec[7] = club; rec[6] = club
    if two: rec[2] = 15; rec[5] = 15
    g.put(g.players * 16 + n * 20, rec)

def call_foot(fn, n):
    mu = g.mu; sp = 0xFF00
    mu.mem_write(0x90000 + sp - 2, struct.pack("<H", n)); mu.mem_write(0x90000 + sp - 4, struct.pack("<H", 0x0100)); mu.mem_write(0x90000 + sp - 6, struct.pack("<H", 0))
    mu.reg_write(X.UC_X86_REG_SP, sp - 6); mu.reg_write(X.UC_X86_REG_CS, 0x1771)
    mu.emu_start(0x1771 * 16 + fn, 0x1000, count=3000)
    return mu.reg_read(X.UC_X86_REG_AX) & 0xFF

def run(out_code, cands):
    """cands: {role: (slot, player_number)}; returns AAE8's result (a role's slot byte value or 0)."""
    g.put(ds + 0x99A2, bytes(16))
    for role, (slot, pn) in cands.items():
        g.put(ds + 0x99A2 + role, bytes([slot]))
        g.put(SQ * 16 + 2 * (slot - 1), struct.pack("<H", pn))
    g.put(g.players * 16 + 0 * 20, bytearray([0] * 6 + [out_code, out_code] + [0] * 12))
    mu = g.mu; sp = 0xFF00
    mu.mem_write(0x90000 + sp - 10, struct.pack("<HHH", 0, SQ, 0))   # bp+4 = map off, bp+6 = map seg, bp+8 = outgoing player 0
    mu.mem_write(0x90000 + sp - 12, struct.pack("<H", 0xFFF0))
    mu.reg_write(X.UC_X86_REG_SP, sp - 12); mu.reg_write(X.UC_X86_REG_CS, 0x0791)
    mu.emu_start(0x0791 * 16 + 0xAAE8, 0x0791 * 16 + 0xFFF0, count=20000)
    return mu.reg_read(X.UC_X86_REG_AX) & 0xFFFF

def expected_foot(code):
    return None if code not in STR else (0 if STR.index(code) + 1 <= 3 else 1)

def rule(out_code, cands):
    """The rule as read: scan the row's roles in order; a mapped role is accepted when the outgoing code has no expectation,
    or the candidate is two-footed, or foot_index == expectation; the LAST accepted wins; 0 if none."""
    row = ROWS[out_code]; res = 0; exp = expected_foot(out_code)
    for role in row[1:1 + row[0]]:
        if role in cands:
            slot, pn, two, foot = cands[role]
            if exp is None or two or foot == exp:
                res = slot
    return res

rows, bad = [], 0
# exhaustive single-candidate table
for oc in range(14):
    role = ROWS[oc][1]                      # the first accepted role
    for club in range(14):
        for n in (1, 2, 3):                 # n mod 3 chooses the foot row
            for two in (0, 1):
                setup_player(5, club, 0)    # placeholder
                pn = 10 + n
                setup_player(pn, club, two)
                foot = call_foot(0x3088, pn); tw = call_foot(0x3041, pn)
                got = run(oc, {role: (4, pn)})
                exp = rule(oc, {role: (4, pn, tw, foot)})
                rows.append((oc, expected_foot(oc), club, n % 3, tw, foot, 1, got, exp))
                bad += got != exp
    rows.append((oc, expected_foot(oc), "-", "-", "-", "-", 0, run(oc, {}), 0))  # nothing mapped (unavailable)
    bad += rows[-1][7] != 0
single_bad = bad
# random multi-candidate maps: last accepted wins
rnd = random.Random(54); multi = 0
for _ in range(3000):
    oc = rnd.randrange(14); row = ROWS[oc]; roles = row[1:1 + row[0]]
    cands, c2 = {}, {}
    for k, role in enumerate(rnd.sample(roles, rnd.randint(0, len(roles)))):
        club = rnd.randrange(14); pn = 20 + k; two = rnd.randint(0, 1)
        setup_player(pn, club, two)
        foot = call_foot(0x3088, pn); tw = call_foot(0x3041, pn)
        slot = 12 + k
        cands[role] = (slot, pn); c2[role] = (slot, pn, tw, foot)
    got = run(oc, cands)
    multi += 1; bad += got != rule(oc, c2)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
base = os.path.join(sys.argv[2], "picker-truth-" + ts)
with open(base + ".tsv", "x") as o:
    o.write("# packed GOAL.EXE %s\n# outgoing_code\texpected_foot(None=no check)\tcand_club\tn_mod_3\ttwo\tfoot_index\tmapped\toriginal_AAE8\trule\n" % psha)
    for r in rows: o.write("\t".join(map(str, r)) + "\n")
acc = {}
for r in rows:
    if r[6] == 1:
        acc.setdefault((r[0], r[4], r[5]), set()).add(r[7] != 0)
msg = ["packed GOAL.EXE %s" % psha,
       "single-candidate cases %d, multi-candidate random maps %d, differences original vs rule: %d (single %d)" % (len(rows), multi, bad, single_bad),
       "string DS:08CE = %s; expected foot by outgoing code: %s" % (STR, {c: expected_foot(c) for c in range(14)}),
       "accepted? by (outgoing code, two-footed, foot index) over all candidate club codes and n mod 3 (True only / False only / both):"]
for k in sorted(acc, key=str):
    msg.append("  %s -> %s" % (k, "accepted" if acc[k] == {True} else "rejected" if acc[k] == {False} else "both"))
open(base + ".log", "x").write("\n".join(msg) + "\n")
print("\n".join(msg[:3]))
