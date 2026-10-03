"""DOSBox-X spike helpers for T02: launch under Xvfb, send keys, read the text screen from a
savestate, terminate. A spike, not the reusable driver (a later task).

Every wait is a poll with a timeout or a delay that the caller records (see Session.log).
Constants that came from a measurement name the finding that holds it (F001)."""
import hashlib
import os
import signal
import subprocess
import time
import zipfile
import zlib

ROWS, COLS = 25, 80
# F001 "Where the screen is in a savestate": in DOSBox-X 2024.03.01, machine svga_s3 (vmemsize 2),
# the savestate component `Vga` is one zlib stream; the text page sits in it with 8 bytes per
# cell (char, attribute, 6 bytes of other planes). The offset was calibrated once by matching a
# DOSBox-X PNG capture and checked on every read by `check_layout`.
VGA_TEXT_BASE = 0x86024  # calibrated on svga_s3, memsize 16: 0 cells differ from the PNG capture (F001)
# F001: component `Memory` is one zlib stream whose guest physical address 0 is at offset 0x78;
# the BIOS data area (mode at 0x449, columns 0x44A, rows-1 0x484) is read from it.
MEM_HDR = 0x78

CP437_LOW = "\u263a\u263b\u2665\u2666\u2663\u2660\u2022\u25d8\u25cb\u25d9\u2642\u2640\u266a\u266b\u263c\u25ba\u25c4\u2195\u203c\u00b6\u00a7\u25ac\u21a8\u2191\u2193\u2192\u2190\u221f\u2194\u25b2\u25bc"  # glyphs of 0x01..0x1F
KEYMAP = {"Enter": "Return", "Esc": "Escape", "Space": "space", "Up": "Up", "Down": "Down",
          "Left": "Left", "Right": "Right", "Backspace": "BackSpace", "Tab": "Tab"}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


class Session:
    def __init__(self, workdir, game_dir, conf_extra="", machine="svga_s3", memsize=16,
                 cycles="auto", core="auto", cputype="auto", savefile_name="state.sav",
                 load_state=None):
        self.workdir = os.path.abspath(workdir)
        self.game_dir = os.path.abspath(game_dir)
        self.machine, self.memsize, self.cycles = machine, memsize, cycles
        self.core, self.cputype = core, cputype
        self.conf_extra = conf_extra
        self.savefile = os.path.join(self.workdir, savefile_name)
        self.load_state = load_state
        self.xvfb = self.dbx = None
        self.display = None
        self.events = []  # (monotonic seconds, what): the recorded waits and polls
        os.makedirs(self.workdir, exist_ok=True)

    def log(self, what):
        self.events.append((round(time.monotonic() - self.t0, 3), what))

    # ---- launch -------------------------------------------------------------------------
    def conf_text(self):
        return f"""[sdl]
fullscreen=false
output=surface
mapperfile={self.workdir}/mapper.map
[mixer]
nosound=true
[midi]
mididevice=none
[dosbox]
machine={self.machine}
memsize={self.memsize}
saveremark=false
captures={self.workdir}/cap
[cpu]
core={self.core}
cputype={self.cputype}
cycles={self.cycles}
{self.conf_extra}
[autoexec]
mount c {self.game_dir}
c:
goal
exit
"""

    def start(self):
        self.t0 = time.monotonic()
        os.makedirs(os.path.join(self.workdir, "cap"), exist_ok=True)
        conf = os.path.join(self.workdir, "dosbox.conf")
        open(conf, "w").write(self.conf_text())
        # Xvfb's -displayfd cannot choose a display here (WSLg owns /tmp/.X11-unix/X0), so a
        # number is picked explicitly, as xvfb-run does, and the server is polled until it answers.
        for attempt in range(20):
            num = 200 + (os.getpid() + attempt * 7) % 700
            if os.path.exists(f"/tmp/.X{num}-lock"):
                continue
            self.xvfb = subprocess.Popen(
                ["Xvfb", f":{num}", "-screen", "0", "1024x768x24", "-nolisten", "tcp"],
                stderr=subprocess.DEVNULL, start_new_session=True)
            self.display = f":{num}"
            if self._poll_x(10):
                break
            self.xvfb.kill()
            self.xvfb.wait()
        else:
            raise RuntimeError("no Xvfb display could be started")
        self.log(f"Xvfb {self.display} answering")
        env = dict(os.environ, DISPLAY=self.display, SDL_AUDIODRIVER="dummy")
        args = ["dosbox-x", "-conf", conf, "-fastlaunch", "-nogui", "-nomenu",
                "-savedir", self.workdir, "-set", f"dosbox savefile={self.savefile}"]
        self.dbx = subprocess.Popen(args, env=env, stdout=open(os.path.join(self.workdir, "dosbox.out"), "w"),
                                    stderr=subprocess.STDOUT, start_new_session=True)
        self.log("dosbox-x started")
        self.wid = self._wait_window(15)
        self.env = env
        self._x("windowfocus", self.wid)
        self.log("window focused")

    def _poll_x(self, timeout):
        end = time.monotonic() + timeout
        env = dict(os.environ, DISPLAY=self.display)
        while time.monotonic() < end and self.xvfb.poll() is None:
            if subprocess.run(["xdotool", "getdisplaygeometry"], env=env, capture_output=True).returncode == 0:
                return True
            time.sleep(0.1)
        return False

    def _x(self, *a):
        return subprocess.run(["xdotool", *a], env=self.env, capture_output=True, text=True, timeout=10)

    def _wait_window(self, timeout):
        env = dict(os.environ, DISPLAY=self.display)
        end = time.monotonic() + timeout
        n = 0
        while time.monotonic() < end:
            n += 1
            p = subprocess.run(["xdotool", "search", "--class", "dosbox"], env=env, capture_output=True, text=True)
            if p.stdout.split():
                self.log(f"window found after {n} polls")
                return p.stdout.split()[0]
            time.sleep(0.1)
        raise RuntimeError("no DOSBox-X window within %ss" % timeout)

    # ---- input --------------------------------------------------------------------------
    def key(self, name, hold=0.08):
        """One keystroke through XTEST: press, `hold` seconds, release."""
        k = KEYMAP.get(name, name)
        self._x("keydown", k)
        time.sleep(hold)
        self._x("keyup", k)
        self.log(f"key {name} pressed (held {hold}s)")

    def hostkey(self, name, hold=0.15):
        """DOSBox-X host key (F12 here) + a key: a DOSBox-X hotkey, not game input."""
        self._x("keydown", "F12"); time.sleep(hold)
        self._x("keydown", name); time.sleep(hold)
        self._x("keyup", name); time.sleep(hold)
        self._x("keyup", "F12")

    # ---- observe ------------------------------------------------------------------------
    def savestate(self, timeout=15):
        """Host+S; poll until a complete savestate zip (all members readable) is on disk.
        Returns the file's bytes. I1: reading emulator state."""
        if os.path.exists(self.savefile):
            os.remove(self.savefile)
        self.hostkey("s")
        end = time.monotonic() + timeout
        polls = 0
        while time.monotonic() < end:
            polls += 1
            if os.path.exists(self.savefile):
                try:
                    with zipfile.ZipFile(self.savefile) as z:
                        if z.testzip() is None and "Vga" in z.namelist() and "Save_Remark" in z.namelist():
                            data = open(self.savefile, "rb").read()
                            self.log(f"savestate complete after {polls} polls")
                            return data
                except (zipfile.BadZipFile, OSError):
                    pass
            time.sleep(0.05)
        raise RuntimeError("savestate not complete within %ss" % timeout)

    def screen(self):
        """Take a savestate, return Screen(chars, attrs, mode) from the Vga and Memory components."""
        data = self.savestate()
        return read_screen_from_savestate(self.savefile), data

    def wait_screen(self, pred, timeout=20, what="screen"):
        """Poll (a savestate read each time) until pred(screen) is true. Returns (screen, polls).
        The wait is bounded by `timeout`; polls and elapsed time go to self.events."""
        end = time.monotonic() + timeout
        polls = 0
        sc = None
        while time.monotonic() < end:
            polls += 1
            sc, _ = self.screen()
            if pred(sc):
                self.log(f"{what}: matched after {polls} polls")
                return sc, polls
        raise RuntimeError(f"{what}: not seen within {timeout}s ({polls} polls); last screen:\n{sc.text() if sc else None}")

    def capture_png(self, timeout=10):
        """Host+P: DOSBox-X's own PNG capture of the rendered screen. Returns its path."""
        d = os.path.join(self.workdir, "cap")
        before = set(os.listdir(d))
        self.hostkey("p")
        end = time.monotonic() + timeout
        polls = 0
        while time.monotonic() < end:
            polls += 1
            new = sorted(set(os.listdir(d)) - before)
            if new and os.path.getsize(os.path.join(d, new[0])) > 0:
                time.sleep(0.05)
                self.log(f"png capture after {polls} polls")
                return os.path.join(d, new[0])
            time.sleep(0.05)
        raise RuntimeError("no capture within %ss" % timeout)

    def restore(self, path):
        """Host+L loads the savestate named by `savefile`; the caller copies `path` there first."""
        self.hostkey("l")

    # ---- terminate ----------------------------------------------------------------------
    def stop(self):
        for p in (self.dbx, self.xvfb):
            if p and p.poll() is None:
                try:
                    os.killpg(p.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        for p in (self.dbx, self.xvfb):
            if p:
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.wait()
        self.log("terminated")


class Screen:
    def __init__(self, chars, attrs, mode, cols, rows):
        self.chars, self.attrs, self.mode, self.cols, self.rows = chars, attrs, mode, cols, rows

    def lines(self):
        # CP437 for 32..255 (the DOS code page of the text mode); NUL as space, other controls as "?"
        def ch(c):
            return " " if c == 0 else (CP437_LOW[c - 1] if c < 32 else bytes([c]).decode("cp437"))
        return ["".join(ch(c) for c in self.chars[r * COLS:(r + 1) * COLS]) for r in range(ROWS)]

    def text(self):
        return "\n".join(l.rstrip() for l in self.lines())

    def highlighted(self):
        """Runs of cells whose attribute has a non-black background nibble (a selection bar,
        a title): (row, first col, text). Raw attribute bytes are in raw()."""
        runs = []
        lines = self.lines()
        for r in range(ROWS):
            c = 0
            while c < COLS:
                if self.attrs[r * COLS + c] >> 4 & 7:
                    e = c
                    while e < COLS and self.attrs[r * COLS + e] >> 4 & 7:
                        e += 1
                    runs.append((r, c, lines[r][c:e]))
                    c = e
                else:
                    c += 1
        return runs

    def raw(self):
        """chars then attributes, the 4000 bytes B800:0000 would hold."""
        return bytes(b for c, a in zip(self.chars, self.attrs) for b in (c, a))

    def digest(self):
        return sha256(self.raw())


def components(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def inflate(b):
    return zlib.decompressobj().decompress(b)


def read_screen_from_savestate(path, base=None):
    comps = components(path)
    vga = inflate(comps["Vga"])
    mem = inflate(comps["Memory"])
    # BIOS data area, guest physical 0x449 video mode, 0x44A columns, 0x484 rows-1
    o = MEM_HDR
    mode, cols, rows = mem[o + 0x449], mem[o + 0x44A] | (mem[o + 0x44B] << 8), mem[o + 0x484] + 1
    b = base if base is not None else VGA_TEXT_BASE
    chars = bytes(vga[b + 8 * i] for i in range(ROWS * COLS))
    attrs = bytes(vga[b + 8 * i + 1] for i in range(ROWS * COLS))
    return Screen(chars, attrs, (mode, cols, rows), cols, rows)


def png_pixels(path):
    """Decode a non-interlaced PNG (colour type 0, 2 or 3, bit depth 8, or 3 with depth <= 8)
    into (width, height, rows of per-pixel tuples). Standard library only."""
    import struct
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, pal = 8, b"", None
    while pos < len(d):
        ln, typ = struct.unpack(">I4s", d[pos:pos + 8])
        body = d[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
        elif typ == b"PLTE":
            pal = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif typ == b"IDAT":
            idat += body
        pos += 12 + ln
    assert inter == 0 and ctype in (0, 2, 3)
    bpp_bits = {0: depth, 2: 3 * depth, 3: depth}[ctype]
    stride = (w * bpp_bits + 7) // 8
    bpp = max(1, bpp_bits // 8)
    raw = zlib.decompress(idat)
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        prev = line
        if ctype == 3:
            if depth == 8:
                px = [pal[v] for v in line[:w]]
            else:
                per = 8 // depth
                px = [pal[(line[i // per] >> (8 - depth * (i % per + 1))) & ((1 << depth) - 1)] for i in range(w)]
        elif ctype == 2:
            px = [tuple(line[3 * i:3 * i + 3]) for i in range(w)]
        else:
            px = [(line[i],) * 3 for i in range(w)]
        rows.append(px)
    return w, h, rows


def lit_cells(path, cw=9, ch=16):
    """For a DOSBox-X text-mode PNG capture of w x h pixels: the set of (row, col) cells holding
    any pixel other than the screen's most common colour (the background)."""
    w, h, rows = png_pixels(path)
    from collections import Counter
    bg = Counter(p for r in rows for p in r).most_common(1)[0][0]
    lit = set()
    for y in range(h):
        for x in range(w):
            if rows[y][x] != bg:
                lit.add((y // ch, x // cw))
    return (w, h), lit
