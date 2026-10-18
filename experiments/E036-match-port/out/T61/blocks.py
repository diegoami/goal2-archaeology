import re, sys, glob, json
ROUT = ["0AA7","0B77","0E24","0E6C","2E20","2E93","2FAD","2FFB","3041","3088","30D9","3179","3216","33CD","3431","34E7","377E","3A06","3A82","3E2F","3EF8","5A03"]
lines = {}
order = []
for f in sorted(glob.glob("static/goal-exe/code/seg_1771_*.asm")):
    cur = None
    for ln in open(f):
        m = re.match(r"; ---- routine 1771:([0-9A-F]{4})", ln)
        if m:
            cur = m.group(1); order.append(cur); lines[cur] = []; continue
        if cur and re.match(r"[0-9A-F]{4}  ", ln):
            lines[cur].append(ln.rstrip())
        elif cur and ln.startswith("loc_"):
            lines[cur].append(ln.rstrip())
out = {}
for r in ROUT:
    ins = [l for l in lines[r] if re.match(r"[0-9A-F]{4}  ", l)]
    addrs = [l[:4] for l in ins]
    targets = set([addrs[0]])
    for i, l in enumerate(ins):
        mn = l[22:].strip() if len(l) > 22 else ""
        m = re.match(r"(j\w+|loop\w*)\s+0x([0-9a-f]+)", mn)
        if m:
            t = m.group(2).upper().zfill(4)
            if t in addrs:
                targets.add(t)
            if i + 1 < len(ins):
                targets.add(addrs[i + 1])
    out[r] = sorted(targets)
print(json.dumps(out))
print(sum(len(v) for v in out.values()), file=sys.stderr)
