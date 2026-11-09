"""T130 (#705): the stack and BP chain the Play action's entry stands in, read from the published E006-r0001 state
(a manager menu: main_menu_loop 000E:7439's frame is live), and the same words after one press of the original's
own branch. Reads the state only; the press is the route harness's play_action entry on the original under Unicorn."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import route as R
from original_match.image import Image
from original_match.match import SS_PARAGRAPH

state = ROOT / ".cache/dl/e0afff6751747233-e006-1000-r0001.sav"
r = R.Route(Image.from_savestate(state.read_bytes()), entry="play_action")
m = r.m
ss = m.seg(SS_PARAGRAPH) * 16
w = lambda a: m.word_at(ss + a)
print("state", state.name)
print("DS:A923 (offset, segment)", hex(m.rd(0xA923, 2)), hex(m.rd(0xA925, 2)))
for name, a in (("SS:3FF0 [bp-6] = di (offset)", 0x3FF0), ("SS:3FF2 [bp-4] = es (segment)", 0x3FF2),
                ("SS:3FF4 [bp-2] loop local", 0x3FF4), ("SS:3FF6 [bp] saved BP", 0x3FF6), ("SS:3FF8 return", 0x3FF8)):
    print(f"{name}: {w(a):#06x}")
print("entry: SS = load + 0x3052 =", hex(m.seg(SS_PARAGRAPH)), "SP", hex(R.ACTION_SP), "BP", hex(R.MENU_BP),
      "BP-0x108 =", hex(R.MENU_BP - 0x108), "CS:IP", R.ACTION_AT, "ends", R.ACTION_END)
frames = []
m.at("000E:70D1", lambda replay: replay or frames.append(
    (m.reg("sp"), m.reg("bp"), w(0x3EEA), w(0x3EEC), m.read(m.far(0xA923) + 1, 1)[0])))
game = m.far(0xA923)
r._write("synthetic: cursor := count (as T124a)", game + 0x26, m.read(game + 0x28, 2))
r.call()
print("at 70D1 (SP, BP, SS:3EEA, SS:3EEC, [A923]+1):", [tuple(hex(x) for x in f) for f in frames])
print("actions:", [e for e in r.record if e[0] == "action"], "return:", r.record[-1], "SP", hex(m.reg("sp")),
      "BP", hex(m.reg("bp")))
