"""Read a DOSBox-X 2024.03.01 savestate (the zip Host+S writes): the 80x25 text screen and guest memory.

Standard library only; no DOSBox-X needed, so the tests build a synthetic savestate and run in CI.
Every constant here comes from F001 ("Method", "Screen read"); copied from runtime/spike/dbx.py.
The layout is specific to DOSBox-X 2024.03.01 (F001): another version needs a new calibration.
"""
import hashlib
import zipfile
import zlib

ROWS, COLS = 25, 80
# F001: component `Vga` is one zlib stream; the text page is at stream offset 0x86024, 8 bytes per
# cell (character, attribute, 6 bytes of other planes). Calibrated on svga_s3, memsize 16, by matching
# a DOSBox-X PNG capture (F001, M:layout `base`).
VGA_TEXT_BASE = 0x86024
CELL_BYTES = 8
# F001: component `Memory` is one zlib stream holding guest physical memory from stream offset 0x78
# (M:layout `mem_header`).
MEM_BASE = 0x78

# BIOS data area (guest physical addresses): video mode byte 0040:0049, timer tick count dword 0040:006C.
BDA_VIDEO_MODE = 0x449
BDA_TICKS = 0x46C

CP437_LOW = ("☺☻♥♦♣♠•◘○◙♂♀♪♫☼"
             "►◄↕‼¶§▬↨↑↓→←∟↔▲▼")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


class Screen:
    """The text page: 2000 characters and 2000 attributes."""

    def __init__(self, chars, attrs):
        self.chars, self.attrs = bytes(chars), bytes(attrs)

    def raw(self):
        """chars and attributes interleaved: the 4000 bytes B800:0000 would hold."""
        return bytes(b for c, a in zip(self.chars, self.attrs) for b in (c, a))

    def digest(self):
        return sha256(self.raw())

    def lines(self):
        def ch(c):
            return " " if c == 0 else (CP437_LOW[c - 1] if c < 32 else bytes([c]).decode("cp437"))
        return ["".join(ch(c) for c in self.chars[r * COLS:(r + 1) * COLS]) for r in range(ROWS)]

    def text(self):
        return "\n".join(line.rstrip() for line in self.lines())


class Savestate:
    """The two components the driver reads, inflated once."""

    def __init__(self, path_or_bytes):
        src = path_or_bytes
        if isinstance(src, (bytes, bytearray)):
            import io
            src = io.BytesIO(src)
        with zipfile.ZipFile(src) as z:
            self.vga = zlib.decompressobj().decompress(z.read("Vga"))
            self.mem = zlib.decompressobj().decompress(z.read("Memory"))

    def screen(self):
        b = VGA_TEXT_BASE
        n = ROWS * COLS
        if len(self.vga) < b + CELL_BYTES * n:
            raise ValueError(f"Vga component too short for the text page: {len(self.vga)} bytes")
        return Screen(self.vga[b:b + CELL_BYTES * n:CELL_BYTES], self.vga[b + 1:b + 1 + CELL_BYTES * n:CELL_BYTES])

    def memory(self, addr, n):
        """n bytes of guest physical memory from address addr."""
        o = MEM_BASE + addr
        if addr < 0 or n < 0 or o + n > len(self.mem):
            raise ValueError(f"guest memory 0x{addr:x}+{n} outside the Memory component ({len(self.mem)} bytes)")
        return bytes(self.mem[o:o + n])

    def video_mode(self):
        return self.memory(BDA_VIDEO_MODE, 1)[0]

    def ticks(self):
        """The BIOS timer tick count dword at 0040:006C, little-endian, with its raw bytes."""
        b = self.memory(BDA_TICKS, 4)
        return int.from_bytes(b, "little"), b
