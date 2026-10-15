"""Raw XTEST key events through ctypes (libX11, libXtst): press or release one keycode, with no modifier
added. xdotool, asked for a function key, finds its keysym on a level that needs a modifier and sends
Left Alt with it (the guest received Alt+F2 = 0x6900, Alt+F10 = 0x7100 and Alt+F12 = 0x8C00 in the BIOS
buffer; with `keydown` and `keyup` in two calls the Alt it pressed was never released, and the guest
kept Left Alt held: 0040:0017 bit 3). The keycode of a keysym is the X server's own (XKeysymToKeycode),
the same that xdotool would press, only without the modifier."""
import ctypes
import ctypes.util

_x11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11") or "libX11.so.6")
_xtst = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Xtst") or "libXtst.so.6")
_x11.XOpenDisplay.restype = ctypes.c_void_p
_x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
_x11.XStringToKeysym.restype = ctypes.c_ulong
_x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
_x11.XKeysymToKeycode.restype = ctypes.c_ubyte
_x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
_x11.XFlush.argtypes = [ctypes.c_void_p]
_x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
_xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]


def key_event(display, keysym_name, press):
    """Press (True) or release (False) the key of `keysym_name` on X display `display` (":411")."""
    dpy = _x11.XOpenDisplay(display.encode())
    if not dpy:
        raise RuntimeError(f"cannot open display {display}")
    try:
        sym = _x11.XStringToKeysym(keysym_name.encode())
        code = _x11.XKeysymToKeycode(dpy, sym)
        if not code:
            raise ValueError(f"no keycode for {keysym_name!r} on {display}")
        _xtst.XTestFakeKeyEvent(dpy, code, 1 if press else 0, 0)
        _x11.XFlush(dpy)
        return code
    finally:
        _x11.XCloseDisplay(dpy)
