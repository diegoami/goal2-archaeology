"""Print the markdown table of formations.tsv (posts.py output) for findings/F028: id, label, countries, codes, the eleven posts.
usage: python3 -B mdtable.py formations-<ts>.tsv"""
import sys
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if not l.startswith("#")][1:]
LET = "0123456789ABCD"
print("| id | label | countries | codes (slots 1..11) | start posts (x,y) of slots 1..11, the team's own frame |")
print("| --- | --- | --- | --- | --- |")
for r in rows:
    codes = " ".join(str(int(ch, 16)) for ch in r[4])
    posts = " ".join(r[5].replace(" ", ";").split(";"))
    print("| %s | %s | %s | %s | %s |" % (r[0], r[1], r[2], codes, r[5]))
