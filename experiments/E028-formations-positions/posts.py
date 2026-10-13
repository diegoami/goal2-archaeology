"""The start posts of every formation in GOAL.DAT block 10, from the ORIGINAL routine 0791:419C run in Unicorn,
cross-checked against a Python port of the rule read from the listing.

    python3 -B experiments/E028-formations-positions/posts.py <GOAL.EXE packed> <GOAL.DAT> OUTDIR

For each country 1..128 the eleven are block 10's bytes 0..10 (R011, `DS:9F03 + 20 c + k - 1` for slot k, 1771:97CC), put in
ascending order of position code as 0791:230C / 1771:52CC leave them (the pitch records of a side run in that order).
A "formation" here is the multiset of those eleven codes. For each distinct one the script
 1. fills pitch records 1..11 (side 1, DS:0668 = 00) and 12..22 (side 0, DS:0668 = 0B) with synthetic players of those positions,
 2. runs 0791:419C of the image (a near routine, `ret`), and reads each record's word at +9 (x, y: signed bytes),
 3. computes the same posts with `port()` (DS:079E[2 * position], then the adjacent-equal separation of 419C),
 4. writes formations.tsv (never overwritten): id, label D-M-A (1771:0E6C's classes DS:0D5C), countries, the eleven codes and posts.
The guest memory is the one of foot_truth.py (image at physical 0, DS = 2581, players at 6000:0000, stack 9000:FF00)."""
import os, struct, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foot_truth import load, Guest, X
from ds import load_full

BLOCK10 = 0xA1F4

def squads(dat_path):
    d = open(dat_path, "rb").read()
    out = {}
    for c in range(1, 129):
        rec = d[BLOCK10 + 20 * c: BLOCK10 + 20 * c + 20]
        out[c] = list(rec[:11]), list(rec[11:])
    return out

def s8(v):
    return v - 256 if v > 127 else v

def port(poss, ds):
    """Python port of 0791:419C for one side: posts (x, y) per slot, slots in the order given."""
    tab = [(s8(ds[0x79E + 2 * p]), s8(ds[0x79F + 2 * p])) for p in range(14)]
    posts = [list(tab[p]) for p in poss]
    for i in range(1, len(posts)):
        if tuple(posts[i - 1]) == tuple(tab[poss[i]]):      # 4241: previous record's word == the fresh word
            x = posts[i][0]
            if abs(x) <= 4:                                  # 425C: abs(x) > 4 jumps to the else branch
                posts[i][0] += 3
                posts[i - 1][0] -= 3                         # 429E-42A8
            else:
                posts[i][0] -= 3 * (1 if x > 0 else -1)      # 4274-4281: DS:7920[x > 0] = FF, 01
                posts[i - 1][1] -= 3                         # 428F
    return [tuple(p) for p in posts]

def emulate(g, poss_a, poss_b):
    """Run 419C with side 1 (slots 1..11) holding poss_a and side 0 (slots 12..22) holding poss_b; return the posts."""
    mu = g.mu
    ds = g.DS * 16
    g.put(ds + 0x668, bytes([0x0B, 0x00]))
    n = 0
    for base, poss in ((0, poss_a), (11, poss_b)):
        for k, p in enumerate(poss):
            rec = bytearray(20); rec[6] = rec[7] = p
            g.put(g.players * 16 + n * 20, rec)
            slot = base + k + 1
            pr = bytearray(0x16); struct.pack_into("<H", pr, 0xD, n)
            g.put(ds + 0x80E8 + 0x16 * slot, pr)
            n += 1
    sp = 0xFF00
    mu.mem_write(0x90000 + sp - 2, struct.pack("<H", 0xFFF0))      # near return address (never executed)
    mu.reg_write(X.UC_X86_REG_SP, sp - 2)
    mu.reg_write(X.UC_X86_REG_CS, 0x0791)
    mu.emu_start(0x0791 * 16 + 0x419C, 0x0791 * 16 + 0xFFF0, count=100000)
    res = []
    for base in (0, 11):
        side = []
        for k in range(11):
            w = struct.unpack("<bb", bytes(mu.mem_read(ds + 0x80E8 + 0x16 * (base + k + 1) + 9, 2)))
            side.append(w)
        res.append(side)
    return res

def main():
    exe, dat, outdir = sys.argv[1:4]
    psha, usha, image = load(exe)
    ds = load_full()
    g = Guest(image)
    cls = [ds[0x0D5C + p] for p in range(14)]
    forms = defaultdict(list)
    for c, (first, bench) in squads(dat).items():
        forms[tuple(sorted(first))].append(c)
    rows, bad = [], 0
    for i, (f, cs) in enumerate(sorted(forms.items(), key=lambda kv: (-len(kv[1]), kv[0])), 1):
        poss = list(f)
        a, b = emulate(g, poss, poss)
        pp = port(poss, ds)
        ok = (a == pp and b == pp)
        bad += 0 if ok else 1
        cnt = Counter(cls[p] for p in poss)
        label = "%d-%d-%d" % (cnt[1], cnt[2], cnt[3])
        rows.append((i, label, len(cs), ",".join(map(str, cs)), "".join("%X" % p for p in poss),
                     " ".join("(%d,%d)" % w for w in a), ok))
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "formations-%s.tsv" % ts)
    with open(path, "x") as o:
        o.write("# packed GOAL.EXE sha256 %s; GOAL.DAT block 10 (squad_20) at 0xA1F4; posts are 0791:419C's, run in Unicorn\n" % psha)
        o.write("id\tlabel_D-M-A\tcountries\tcountry_numbers\tcodes_hex_ascending\tposts_slot1..11_x,y\tport_equals_original\n")
        for r in rows:
            o.write("\t".join(map(str, r)) + "\n")
    print("countries", sum(len(v) for v in forms.values()), "distinct formations", len(forms), "port differs from original:", bad, "->", path)
    print(Counter(r[1] for r in rows).most_common())
    lab = Counter()
    for r in rows:
        lab[r[1]] += r[2]
    print("countries by label:", lab.most_common())

if __name__ == "__main__":
    main()
