"""Read the unpacked GOAL.EXE and find its code by recursive descent (16-bit real mode).

Shared by listing.py and xrefs.py. Addresses are `segment:offset` where the segment is the
paragraph number in the unpacked image BEFORE relocation (what the file holds); the image offset
is segment * 16 + offset. The loader adds the load segment to every relocated word; the tools
never do, so a segment value in a listing is a name for a place in the image.

Requires capstone (pinned in requirements.txt).
"""
import struct

import capstone

CAPSTONE_PIN = "5.0.9"  # the pip package version (the module's own __version__ string lags it)


def capstone_version():
    from importlib.metadata import version
    return version("capstone"), ".".join(str(x) for x in capstone.cs_version()[:2]) + "." + str(capstone.cs_version()[2])

DOS_FUNCTIONS = {  # INT 21h, by AH (public DOS documentation)
    0x02: "write char", 0x09: "write $-string", 0x0A: "buffered input", 0x0B: "check stdin",
    0x0E: "select drive", 0x19: "get drive", 0x1A: "set DTA", 0x25: "set interrupt vector",
    0x2A: "get date", 0x2C: "get time", 0x2F: "get DTA", 0x30: "get DOS version",
    0x31: "terminate and stay resident", 0x35: "get interrupt vector", 0x36: "get free disk space",
    0x39: "mkdir", 0x3A: "rmdir", 0x3B: "chdir", 0x3C: "create file", 0x3D: "open file",
    0x3E: "close file", 0x3F: "read file", 0x40: "write file", 0x41: "delete file",
    0x42: "seek", 0x43: "get/set attributes", 0x47: "get current directory", 0x48: "allocate memory",
    0x49: "free memory", 0x4A: "resize memory", 0x4B: "exec", 0x4C: "terminate",
    0x4E: "find first", 0x4F: "find next", 0x56: "rename", 0x57: "get/set file time",
}


def printable(b):
    return 0x20 <= b < 0x7F


def track_ah(prev_ah, i):
    raw = bytes(i.bytes)
    if raw[0] == 0xB4:  # mov ah, imm8
        return raw[1]
    if raw[0] == 0xB8:  # mov ax, imm16
        return raw[2]
    if i.mnemonic in ("call", "jmp", "ret", "retf", "iret") or raw[0] in (0x9A, 0xEA):
        return None
    if any(r in (capstone.x86.X86_REG_AH, capstone.x86.X86_REG_AX) for r in i.regs_access()[1]):
        return None
    return prev_ah


class Image:
    def __init__(self, exe_bytes):
        w = struct.unpack("<14H", exe_bytes[:0x1C])
        if w[0] != 0x5A4D:
            raise ValueError("not an MZ file")
        self.header = w
        self.ip, self.cs, self.sp, self.ss = w[10], w[11], w[8], w[7]
        hdr = w[4] * 16
        self.data = exe_bytes[hdr:]
        self.relocs = set()  # image offsets of relocated words
        for i in range(w[3]):
            off, seg = struct.unpack_from("<HH", exe_bytes, w[12] + 4 * i)
            self.relocs.add(seg * 16 + off)
        self.reloc_value = {a: struct.unpack_from("<H", self.data, a)[0] for a in self.relocs}
        self.ds = None
        self.code_segments = []  # sorted (start_paragraph, end_paragraph)
        self._find_segments()

    def _find_segments(self):
        """Code segments: 0 and every segment named by a relocated far call or far jump
        (9a / ea: opcode, offset word, relocated segment word). The data segment is
        the one a relocated `mov reg, imm16` loads before `mov ds, reg` in the start-up code."""
        far = set()
        other = {}
        for a, v in self.reloc_value.items():
            if a >= 3 and self.data[a - 3] in (0x9A, 0xEA):
                far.add(v)
            else:
                other.setdefault(v, []).append(a)
        far.add(self.cs)
        self.far_segments = sorted(far)
        # data segment: relocated non-call references; the most referenced one
        if other:
            self.ds = max(other, key=lambda v: len(other[v]))
        starts = sorted(far)
        limit = self.ds if self.ds is not None else len(self.data) // 16
        for i, s in enumerate(starts):
            e = starts[i + 1] if i + 1 < len(starts) else limit
            self.code_segments.append((s, min(e, limit)))
        self.other_segment_refs = other

    def segment_of(self, linear):
        for s, e in self.code_segments:
            if s * 16 <= linear < e * 16:
                return s
        return None


def _md():
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
    md.detail = True
    return md


class Disassembly:
    """Instructions per code segment, found from entry points, calls and jumps, then from
    routine prologues in what remains."""

    PROLOGUES = (b"\x55\x89\xe5", b"\x55\x8b\xec")

    def __init__(self, image):
        self.img = image
        self.md = _md()
        self.ins = {}  # linear -> capstone instruction (offset-addressed in its segment)
        self.starts = {}  # linear -> set of reasons, 'entry' | 'call' | 'far' | 'jump' | 'prologue'
        self.seg_range = {s: (s * 16, e * 16) for s, e in image.code_segments}
        self.covered = bytearray(len(image.data))
        self._run()

    def _seg_end(self, linear):
        s = self.img.segment_of(linear)
        return None if s is None else self.seg_range[s]

    def _decode(self, linear):
        rng = self._seg_end(linear)
        if rng is None:
            return None
        base = rng[0]
        code = self.img.data[linear:rng[1]]
        for i in self.md.disasm(code, linear - base, 1):
            return i
        return None

    def _add_root(self, linear, why):
        self.starts.setdefault(linear, set()).add(why)

    def _follow(self, root):
        work = [root]
        while work:
            a = work.pop()
            while True:
                rng = self._seg_end(a)
                if rng is None or a in self.ins:
                    break
                if any(self.covered[a:a + 1]):  # inside a decoded instruction already
                    break
                i = self._decode(a)
                if i is None:
                    break
                size = i.size
                if any(self.covered[a:a + size]):
                    break
                for k in range(a, a + size):
                    self.covered[k] = 1
                self.ins[a] = i
                nxt = a + size
                b0 = i.bytes[0]
                base = rng[0]
                grp = set(i.groups)
                end_flow = False
                if b0 == 0x9A:
                    seg = struct.unpack_from("<H", self.img.data, a + 3)[0]
                    off = struct.unpack_from("<H", self.img.data, a + 1)[0]
                    if (a + 3) in self.img.relocs:
                        t = seg * 16 + off
                        self._add_root(t, "far")
                        work.append(t)
                elif b0 == 0xEA:
                    seg = struct.unpack_from("<H", self.img.data, a + 3)[0]
                    off = struct.unpack_from("<H", self.img.data, a + 1)[0]
                    if (a + 3) in self.img.relocs:
                        t = seg * 16 + off
                        self._add_root(t, "far")
                        work.append(t)
                    end_flow = True
                elif capstone.x86.X86_GRP_CALL in grp or capstone.x86.X86_GRP_JUMP in grp:
                    op = i.operands[0] if i.operands else None
                    if op is not None and op.type == capstone.x86.X86_OP_IMM:
                        t = base + (op.imm & 0xFFFF)
                        if rng[0] <= t < rng[1]:
                            is_call = capstone.x86.X86_GRP_CALL in grp
                            self._add_root(t, "call" if is_call else "jump")
                            work.append(t)
                    if i.mnemonic == "jmp":
                        end_flow = True
                if capstone.x86.X86_GRP_RET in grp or capstone.x86.X86_GRP_IRET in grp or i.mnemonic in ("hlt",):
                    end_flow = True
                if end_flow:
                    break
                a = nxt

    def _run(self):
        img = self.img
        self._add_root(img.cs * 16 + img.ip, "entry")
        self._follow(img.cs * 16 + img.ip)
        # far-call targets found in any code segment are followed as they are met;
        # then routine prologues in the gaps
        while True:
            added = False
            for s, e in img.code_segments:
                lo, hi = s * 16, e * 16
                a = lo
                while a < hi:
                    if self.covered[a]:
                        a += 1
                        continue
                    if img.data[a:a + 3] in self.PROLOGUES:
                        self._add_root(a, "prologue")
                        n0 = len(self.ins)
                        self._follow(a)
                        if len(self.ins) > n0:
                            added = True
                            continue
                    a += 1
            if not added:
                break
