"""Raw XTEST key events for the driver (issue 244), through ctypes (libX11, libXtst), and the mapper
that moves DOSBox-X's savestate and load keys off the host key F12. Standard library only.

Why: `xdotool keydown F10` presses Left Alt (X keycode 64) around F10, because Xvfb's keymap holds
F10 on a level xdotool reaches with a modifier (an xinput capture on a bare Xvfb: Alt_L press, F10
press, Alt_L release, F10 release). The guest then read Alt+F10 (BIOS word 0x7100) instead of F10
(0x4400), and the driver's F12+S chord, sent as `keydown` and `keyup` in separate calls, left the
guest's Left Alt held from the launch on (0040:0017 bit 3, 0040:0018 bit 1). Here a key is the one X
keycode of its keysym (XKeysymToKeycode, as E031's xtest.py), pressed and released as itself; a keysym
that is not on the first or second level of its keycode (a shifted character is sent with Left Shift
around it) is refused, never sent with a modifier nobody asked for."""
import ctypes
import ctypes.util
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MAP = HERE.parents[1] / "runtime" / "human" / "dosbox-x-2024.03.01-default.map"

# The driver's names for keys, as X keysym names.
KEYMAP = {"Enter": "Return", "Esc": "Escape", "Space": "space", "Up": "Up", "Down": "Down",
          "Left": "Left", "Right": "Right", "Backspace": "BackSpace", "Tab": "Tab"}

# What a mapper file binds the emulator's savestate (`s`), load (`l`) and screenshot (`p`) events to decides
# which keys the driver presses for them (hostkeys): a bind "key N" is the one key N, a bind "key N host" is
# the host key F12 held with key N. N is an SDL scancode. The keys follow the mapper in effect, never a
# separate setting, so a mapper and the keys pressed cannot disagree.
HOST_KEY = "F12"
BIND_EVENTS = {"s": "hand_savestate", "l": "hand_loadstate", "p": "hand_scrshot"}
SCANCODE_KEYS = {**{4 + i: chr(ord("a") + i) for i in range(26)}, 69: "F12", 70: "Print", 71: "Scroll_Lock", 72: "Pause"}


def bind_keys(text, event):
    """The X keysym names to press for a mapper bind of `event` (hand_savestate ...): [name] for "key N",
    [HOST_KEY, name] for "key N host". ValueError when the file has no such bind, or only binds this
    function does not understand (another modifier, a scancode it has no name for): never a guess."""
    m = re.search(rf"^{event} (.*)$", text, re.M)
    if not m:
        raise ValueError(f"the mapper has no {event} bind")
    binds = re.findall(r'"([^"]*)"', m[1])
    for b in binds:
        parts = b.split()
        if len(parts) >= 2 and parts[0] == "key" and parts[1].isdigit() and set(parts[2:]) <= {"host"}:
            name = SCANCODE_KEYS.get(int(parts[1]))
            if name is None:
                raise ValueError(f"the mapper's {event} bind {b!r}: no key name for scancode {parts[1]}")
            return [HOST_KEY, name] if "host" in parts[2:] else [name]
    raise ValueError(f"the mapper's {event} bind(s) {binds} are not understood: only 'key N' and 'key N host'")


def hostkeys(text):
    """{"s": keys, "l": keys} for the mapper text's savestate and load binds: the keys the driver presses
    (ValueError when either cannot be read), and "p" for the screenshot bind when it can be read."""
    keys = {"s": bind_keys(text, BIND_EVENTS["s"]), "l": bind_keys(text, BIND_EVENTS["l"])}
    try:
        keys["p"] = bind_keys(text, BIND_EVENTS["p"])
    except ValueError:
        pass
    return keys

# DOSBox-X 2024.03.01's default binds (SDL scancodes), with the savestate on Scroll Lock (71) and the
# load on Print Screen (70), both taken from the guest, and a screenshot on Pause (72), the one way to
# see a screen a savestate cannot be taken on (the help viewer, F1). Same edits as E031's make_mapper.py.
MAPPER_CHANGES = {'hand_savestate "key 22 host" \n': 'hand_savestate "key 71" \n',
                  'hand_loadstate "key 15 host" \n': 'hand_loadstate "key 70" \n',
                  'key_printscreen "key 70" \n': 'key_printscreen \n',
                  'key_scrolllock "key 71" \n': 'key_scrolllock \n',
                  'hand_scrshot "key 19 host" \n': 'hand_scrshot "key 72" \n',
                  'key_pause "key 72" \n': 'key_pause \n'}


def mapper_text(src=DEFAULT_MAP):
    """The mapper file text: the default binds with MAPPER_CHANGES, each applied to exactly one line."""
    text = Path(src).read_text()
    for old, new in MAPPER_CHANGES.items():
        if text.count(old) != 1:
            raise RuntimeError(f"{old!r} is not in {src} exactly once")
        text = text.replace(old, new)
    return text


_x11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11") or "libX11.so.6")
_xtst = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Xtst") or "libXtst.so.6")
_x11.XOpenDisplay.restype = ctypes.c_void_p
_x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
_x11.XStringToKeysym.restype = ctypes.c_ulong
_x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
_x11.XKeysymToKeycode.restype = ctypes.c_ubyte
_x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
_x11.XKeycodeToKeysym.restype = ctypes.c_ulong
_x11.XKeycodeToKeysym.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_int]
_x11.XFlush.argtypes = [ctypes.c_void_p]
_x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
_xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]


def plan(dpy, keysym_name):
    """The keycodes to press for `keysym_name`, outermost first: [code], or [Left Shift, code] when the
    keysym is the second level of its keycode (an upper-case letter). Raises ValueError for an unknown
    keysym, one without a keycode, or one on a level that would need another modifier."""
    sym = _x11.XStringToKeysym(keysym_name.encode())
    if not sym:
        raise ValueError(f"no X keysym named {keysym_name!r}")
    code = _x11.XKeysymToKeycode(dpy, sym)
    if not code:
        raise ValueError(f"no keycode for {keysym_name!r}")
    if _x11.XKeycodeToKeysym(dpy, code, 0) == sym:
        return [code]
    if _x11.XKeycodeToKeysym(dpy, code, 1) == sym:
        shift = _x11.XKeysymToKeycode(dpy, _x11.XStringToKeysym(b"Shift_L"))
        return [shift, code]
    raise ValueError(f"{keysym_name!r} is on keycode {code} above the first two levels: it would need a modifier")


def press_release(display, keysym_name, hold, sleep=time.sleep):
    """Press `keysym_name` on X display `display` (":411"), wait `hold` seconds, release it (and any
    Left Shift it needed), all as XTEST events on one connection. Returns the keycodes pressed."""
    dpy = _x11.XOpenDisplay(display.encode())
    if not dpy:
        raise RuntimeError(f"cannot open display {display}")
    try:
        codes = plan(dpy, keysym_name)
        for c in codes:
            _xtst.XTestFakeKeyEvent(dpy, c, 1, 0)
        _x11.XFlush(dpy)
        sleep(hold)  # key hold; the caller logs it
        for c in reversed(codes):
            _xtst.XTestFakeKeyEvent(dpy, c, 0, 0)
        _x11.XFlush(dpy)
        return codes
    finally:
        _x11.XCloseDisplay(dpy)



def key_down(display, keysym_name):
    """Press `keysym_name` (and the Left Shift it needs, if any) and leave it down; returns the keycodes."""
    dpy = _x11.XOpenDisplay(display.encode())
    if not dpy:
        raise RuntimeError(f"cannot open display {display}")
    try:
        codes = plan(dpy, keysym_name)
        for c in codes:
            _xtst.XTestFakeKeyEvent(dpy, c, 1, 0)
        _x11.XFlush(dpy)
        return codes
    finally:
        _x11.XCloseDisplay(dpy)


def key_up(display, keysym_name):
    """Release what key_down pressed for `keysym_name`; returns the keycodes."""
    dpy = _x11.XOpenDisplay(display.encode())
    if not dpy:
        raise RuntimeError(f"cannot open display {display}")
    try:
        codes = plan(dpy, keysym_name)
        for c in reversed(codes):
            _xtst.XTestFakeKeyEvent(dpy, c, 0, 0)
        _x11.XFlush(dpy)
        return codes
    finally:
        _x11.XCloseDisplay(dpy)
