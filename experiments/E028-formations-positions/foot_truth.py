"""Run the ORIGINAL bytes of 1771:3179 (the wrong-foot / goalkeeper-mismatch test), 1771:3088 (foot_index) and
1771:3041 (is_two_footed) in Unicorn on synthetic player records, for every played position (+6), club position (+7),
player number mod 3 and two-footed flag, and compare each result with the rule as read from the listing
(static/goal-exe/code/seg_1771_05.asm:120-215 for 3179).

    python3 -B experiments/E028-formations-positions/foot_truth.py <GOAL.EXE packed> OUTDIR

Nothing of GOAL2 is written but derived results: OUTDIR/foot-truth-<UTC>.tsv (never overwritten) and a summary on stdout.
The guest: the unpacked image mapped at physical 0 (load segment 0, so the listing's segment numbers are the real ones),
DS = 2581, the players array (DS:A91B far pointer) at 6000:0000, stack at 9000:FF00. The code under test is the
image's own; the harness supplies only the player bytes +2, +5, +6, +7 and the argument n."""
import hashlib, os, struct, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "static"))
import unlzexe
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
from unicorn import x86_const as X

def load(path):
    packed = open(path, "rb").read()
    mz = unlzexe.unpack(packed)
    hdr = struct.unpack("<14H", mz[:28])
    image = mz[hdr[4] * 16:]
    return hashlib.sha256(packed).hexdigest(), hashlib.sha256(mz).hexdigest(), image

class Guest:
    def __init__(self, image):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x110000)
        self.mu.mem_write(0, image)
        self.DS = 0x2581
        self.mu.reg_write(X.UC_X86_REG_DS, self.DS)
        self.mu.reg_write(X.UC_X86_REG_ES, self.DS)
        self.mu.reg_write(X.UC_X86_REG_SS, 0x9000)
        self.players = 0x6000
        self.put(self.DS * 16 + 0xA91B, struct.pack("<HH", 0, self.players))

    def put(self, lin, raw):
        self.mu.mem_write(lin, bytes(raw))

    def call(self, cs, ip, arg, ret_seg=0x0100):
        mu = self.mu
        sp = 0xFF00
        # far call frame: arg (word), then return CS:IP; retf 2 pops IP, CS, then the arg word
        mu.mem_write(0x90000 + sp - 2, struct.pack("<H", arg))
        mu.mem_write(0x90000 + sp - 4, struct.pack("<H", ret_seg))
        mu.mem_write(0x90000 + sp - 6, struct.pack("<H", 0))
        mu.reg_write(X.UC_X86_REG_SP, sp - 6)
        mu.reg_write(X.UC_X86_REG_CS, cs)
        mu.mem_write(ret_seg * 16, b"\xF4")
        mu.emu_start(cs * 16 + ip, ret_seg * 16, count=2000)
        return mu.reg_read(X.UC_X86_REG_AX) & 0xFF

def rule_3179(pos, club, foot, two):
    """The rule as read: 3179 (seg_1771_05.asm:120-215)."""
    left = {3, 7, 10}     # CS:3139 = 88 04 -> bits 3, 7 (byte 0), 10 (byte 1 bit 2)
    right = {4, 8, 11}    # CS:3159 = 10 09 -> bit 4 (byte 0), bits 8, 11 (byte 1 bits 0, 3)
    if not two and foot != 0 and pos in left:
        return 1
    if foot == 0 and pos in right:
        return 1
    if pos == 0 and club != 0:
        return 1
    if club == 0 and pos != 0:
        return 1
    return 0

def main():
    exe, outdir = sys.argv[1], sys.argv[2]
    psha, usha, image = load(exe)
    g = Guest(image)
    print("packed sha256", psha, "unpacked sha256", usha)
    bits = {}
    for name, off in (("left", 0x3139), ("right", 0x3159)):
        bits[name] = image[0x1771 * 16 + off: 0x1771 * 16 + off + 2]
        print("CS:%04X set bytes" % off, bits[name].hex())
    rows, mism = [], 0
    for n in range(0, 6):
        for pos in range(14):
            for club in range(14):
                for two in (0, 1):
                    rec = bytearray(20)
                    rec[2] = 15 if two else 0
                    rec[5] = 15 if two else 0
                    rec[6], rec[7] = pos, club
                    g.put(g.players * 16 + n * 20, rec)
                    foot = g.call(0x1771, 0x3088, n)
                    twof = g.call(0x1771, 0x3041, n)
                    r = g.call(0x1771, 0x3179, n)
                    exp = rule_3179(pos, club, foot, twof)
                    if r != exp:
                        mism += 1
                    rows.append((n, n % 3, pos, club, two, twof, foot, r, exp))
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "foot-truth-%s.tsv" % ts)
    with open(path, "x") as o:
        o.write("# packed sha256 %s; unpacked sha256 %s\n" % (psha, usha))
        o.write("n\tn_mod_3\tplayed_pos\tclub_pos\ttwo_flag_set\tis_two_footed\tfoot_index\t3179_original\t3179_rule\n")
        for r in rows:
            o.write("\t".join(map(str, r)) + "\n")
    print("cases", len(rows), "mismatches original vs rule", mism, "->", path)

if __name__ == "__main__":
    main()
