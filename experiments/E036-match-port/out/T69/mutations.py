#!/usr/bin/env python3
"""T69: mutation check of tests/test_port_frame.py. Each rule changes one place of runtime/original_match/port/frame.py in
a copy of the tree (under TMPDIR) and runs the test module there; every mutation must make it fail. The unmutated copy
must pass (the control). Usage: python3 -B experiments/E036-match-port/out/T69/mutations.py [--list]"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FRAME = "runtime/original_match/port/frame.py"

# (name, old text, new text): the old text must occur exactly once in frame.py
RULES = [
    ("970C: the reload 0x24 -> 0x25", 'else 0x24, "0791:9771"', 'else 0x25, "0791:9771"'),
    ("970C: the minute bound < 0x80 -> <= 0x80", "if mem.ds16(0x831F) < 0x80:", "if mem.ds16(0x831F) <= 0x80:"),
    ("970C: the second-counter flag inverted", "flag = 1 if total == 0 else 0", "flag = 1 if total != 0 else 0"),
    ("970C: the target compared with >=", "reached = wanted >= 0 and ax == wanted", "reached = wanted >= 0 and ax >= wanted"),
    ("970C: the minute written by another instruction", '"0791:9762"', '"0791:9763"'),
    ("970C: the tenths decrement on the wrong counter", 'mem.wds16(0x831B, mem.ds16(0x831B) - 1, "0791:9750")',
     'mem.wds16(0x8321, mem.ds16(0x8321) - 1, "0791:9750")'),
    ("970C: the whistle at the end of the half dropped", "                yield go(0x97B6, 3)                        # 0441 match_whistle\n", ""),
    ("97D0: the snapshot taken with the replay", "            elif mem.ds8(0x9B55) != 0:                     # 97EB", "            if mem.ds8(0x9B55) != 0:                       # 97EB"),
    ("97D0: DS:7C37 not cleared", '            mem.wds8(0x7C37, 0, "0791:9806")\n', ""),
    ("97D0: the offside line and the referee called in quick mode", "            if mem.ds8(QUICK) == 0:                        # 980E", "            if True:                                       # 980E"),
    ("97D0: the loop ends without the argument test", "        if fr.u8(4) == 0:                                  # 982C\n            continue\n", ""),
    ("97D0: DS:0C20 not tested", "        if mem.ds8(0x0C20) != 0:                           # 9832\n            continue\n", ""),
    ("97D0: the referee's call without the zero argument", "yield go(0x9821, ax, ds, 0x82EE)", "yield go(0x9821, 1, ds, 0x82EE)"),
    ("9564: the gate <= -> <", "if gate <= mem.ds16(0x8300):", "if gate < mem.ds16(0x8300):"),
    ("9564: the sweep's last slot 0x16 -> 0x15", "if fr.u16(-2) != 0x16:", "if fr.u16(-2) != 0x15:"),
    ("9564: the pause counter -2 -> -1", 'mem.wds16(0x832A, wait - 2, "0791:9703")', 'mem.wds16(0x832A, wait - 1, "0791:9703")'),
    ("9564: the keeper test of the holder's x inverted", "if mem.u8(ds * 16 + rec) == mem.ds8(0x82F6):", "if mem.u8(ds * 16 + rec) != mem.ds8(0x82F6):"),
    ("9564: 6188's loop to 0x15", "if k == 0x16:                      # 9695", "if k == 0x15:                      # 9695"),
    ("9564: 8AE9 called when 2956 says unavailable", "        if (mem.reg(\"ax\") & 0xFF) == 0:                    # 96BE jne 96CB", "        if (mem.reg(\"ax\") & 0xFF) != 0:                    # 96BE jne 96CB"),
    ("9564: the sweep position's slot table 0x883 -> 0x884", "set_product(mem, mem.ds8(0x883 + slot), 0x16)", "set_product(mem, mem.ds8(0x884 + slot), 0x16)"),
    ("9564: the speaker not called", "        yield go(0x96DB)                                   # 94E8 speaker\n", ""),
    ("9564: the quick flag not tested after the poll", "        if mem.ds8(QUICK) != 0:                            # 96EA jne 9708\n            return None\n", ""),
    ("9564: the stack word popped twice", 'mem.set_reg("sp", (mem.reg("sp") + 2) & 0xFFFF)                  # 95A7 pop ax', 'mem.set_reg("sp", (mem.reg("sp") + 4) & 0xFFFF)                  # 95A7 pop ax'),
    ("983F: the sprites loop's second side dropped", "            if i == 1:                                     # 98A7", "            if i == 0:                                     # 98A7"),
    ("983F: DS:9B55 not set", 'mem.wds8(0x9B55, 1, "0791:986A")', 'mem.wds8(0x9B55, 0, "0791:986A")'),
    ("98C4: the kick-off side test inverted", "behind = 1 if mem.ds8(0x9B3D) > mem.ds8(0x9B3C) else 0", "behind = 1 if mem.ds8(0x9B3D) < mem.ds8(0x9B3C) else 0"),
    ("98C4: the state 6 -> 5", 'mem.w8(ds * 16 + ((rec + 0x12) & 0xFFFF), 6, "0791:992A")', 'mem.w8(ds * 16 + ((rec + 0x12) & 0xFFFF), 5, "0791:992A")'),
    ("98C4: the sweep loop runs once", "            if (mem.reg(\"ax\") & 0xFF) != 0:                # 9948 or al, al; je 993F\n                break", "            break"),
    ("9955: the closing argument 4 -> 3", "ax = set_al(mem, 4)                            # 9979-997B", "ax = set_al(mem, 3)                            # 9979-997B"),
    ("998C: the first word left on the stack not taken back", "    mem.set_reg(\"sp\", (mem.reg(\"sp\") + 2) & 0xFFFF)\n    yield go(0x99E2", "    yield go(0x99E2"),
    ("998C: the clock's target 0x2D -> 0x2C", 'mem.wds8(0x8319, 0x2D, "0791:9998")', 'mem.wds8(0x8319, 0x2C, "0791:9998")'),
    ("998C: the code of the line 0x3B -> 0x3A", "yield go(0x99E2, first, third, 0, 0x3B)", "yield go(0x99E2, first, third, 0, 0x3A)"),
    ("9A32: the recovery +2 -> +1", 'mem.u8(energy) + 2, "0791:9A85")', 'mem.u8(energy) + 1, "0791:9A85")'),
    ("9A32: the menu shown for the wrong answer", "show = not zero_flag(mem)", "show = zero_flag(mem)"),
    ("9A32: the board not restored", "    yield go(0x9AC1, backup[1], backup[0], screen[1], screen[0], 0xFA0)    # and back\n", ""),
    ("9A32: the kick-off side not swapped", "other = 1 if mem.ds8(0x831A) == 0 else 0", "other = 0 if mem.ds8(0x831A) == 0 else 1"),
    ("F098: the winner byte > -> <", "winner = 1 if second > first else 0", "winner = 1 if second < first else 0"),
    ("F098: AX after the winner byte not set", "            set_al(mem, winner)\n            mem.w8(lin + 3, winner, at_win)", "            mem.w8(lin + 3, winner, at_win)"),
    ("F098: the draw byte 2 -> 3", 'mem.w8(lin + 3, 2, at_draw)', 'mem.w8(lin + 3, 3, at_draw)'),
    ("F098: the shoot-out winner > -> <", "winner = 1 if mem.ds8(0x9B3D) > mem.ds8(0x9B3C) else 0       # F17C-F189", "winner = 1 if mem.ds8(0x9B3D) < mem.ds8(0x9B3C) else 0       # F17C-F189"),
    ("F098: 98C4 called when the scores are level", "        if mem.ds8(0x9B3D) != mem.ds8(0x9B3C):             # F19F-F1A6", "        if mem.ds8(0x9B3D) == mem.ds8(0x9B3C):             # F19F-F1A6"),
    ("F098: extra time without the decider flag", "if mem.ds8(0x7C36) != 0 and mem.u8(record()[2] + 3) == 2:", "if mem.u8(record()[2] + 3) == 2:"),
    ("1C78: the second word compared with +2", "if v5 == mem.u16(top + 3):", "if v5 == mem.u16(top + 2):"),
    ("1C78: the side byte not compared", "differ = 0 if (ax & 0xFF) == parent.u8(0xA) else 1", "differ = 0"),
    ("1C78: AH after the first compare", "ax = (ax & 0xFF00) | code\n", "ax = code\n"),
    ("1D4A: the next record's mark 0xFF -> 0xFE", ', 0xFF, "0791:1E41")', ', 0xFE, "0791:1E41")'),
    ("1D4A: the record size 6 -> 5", "ring = (mem.ds16(RING_COUNT) * 6 + RING_BASE) & 0xFFFF           # 1D88-1D94", "ring = (mem.ds16(RING_COUNT) * 5 + RING_BASE) & 0xFFFF           # 1D88-1D94"),
    ("1D4A: the bar counter on the other side", "counter = (2 * side + BARS) & 0xFFFF\n        mem.wds16(counter", "counter = (2 * (1 - side) + BARS) & 0xFFFF\n        mem.wds16(counter"),
    ("1D4A: a repeated line written", "            proceed = False                                # jmp 1E4A", "            proceed = True"),
    ("1D4A: the side byte not written", '        mem.w8(top + 5, fr.u8(0xA), "0791:1E16")           # the side\n', ""),
    ("1E53: the delta table 0x720 -> 0x721", "FIRST_SLOT, SIDE_COUNTRY, PERF_DELTA, BARS, POSSESSION = 0x0668, 0x9B34, 0x0720,", "FIRST_SLOT, SIDE_COUNTRY, PERF_DELTA, BARS, POSSESSION = 0x0668, 0x9B34, 0x0721,"),
    ("1E53: the delta unsigned", "delta = s8(mem.ds8((s8(parent.u8(4)) + PERF_DELTA) & 0xFFFF))", "delta = mem.ds8((s8(parent.u8(4)) + PERF_DELTA) & 0xFFFF)"),
    ("1E53: the rating word +0x12 -> +0x10", "target = seg * 16 + ((off + 0x12) & 0xFFFF)", "target = seg * 16 + ((off + 0x10) & 0xFFFF)"),
    ("1EB5: the redraw includes line 0", "                if s16(i) > 0:                             # 1EF2", "                if s16(i) >= 0:                            # 1EF2"),
    ("1EB5: the redraw row 4 -> 5", "row = (4 - (n - i)) & 0xFFFF", "row = (5 - (n - i)) & 0xFFFF"),
    ("1EB5: the picture pointer copy dropped", '        mem.wds16(0x7C26, off, "0791:1F2F")\n', ""),
    ("1EB5: the rating delta skipped", "    yield go(0x1EBC, fr.bp)                                # 1EBB push bp; call 1E53\n", ""),
    ("230C: the sort order reversed", "if fr.u8(j - 0x13) < fr.u8(k - 0x13) or", "if fr.u8(j - 0x13) > fr.u8(k - 0x13) or"),
    ("230C: the unavailable code 0xE -> 0xD", 'fr.w8(j - 0x13, 0xE, "0791:237B")', 'fr.w8(j - 0x13, 0xD, "0791:237B")'),
    ("230C: DS:830C not followed", '(0x830C, "0791:24A4", "0791:24D2"),', ""),
    ("230C: the bench order reversed", "if other < held:", "if other > held:"),
    ("230C: the bench starts at slot 11", "        fr.w16(-5, 0xC, \"0791:258C\")\n        k = 0xC", "        fr.w16(-5, 0xB, \"0791:258C\")\n        k = 0xB"),
    ("230C: DS:8109 not cleared", '    mem.wds16(0x8109, 0, "0791:260E")\n', ""),
    ("230C: a bind for ten slots only", "            while True:\n                set_product(mem, j, 0x16)", "            while j < 0:\n                set_product(mem, j, 0x16)"),
    ("go: the argument count not checked", "    if len(args) != nargs:", "    if False:"),
]


def main():
    if "--list" in sys.argv:
        for i, (name, _, _) in enumerate(RULES, 1):
            print(i, name)
        return 0
    source = (ROOT / FRAME).read_text()
    bad = [name for name, old, new in RULES if source.count(old) != 1]
    if bad:
        print("rules whose text does not occur exactly once:", *bad, sep="\n  ")
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="t69-mut-", dir=os.environ.get("TMPDIR") or None))
    try:
        shutil.copytree(ROOT / "runtime", tmp / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        (tmp / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_frame.py", tmp / "tests/test_port_frame.py")
        (tmp / "static").symlink_to(ROOT / "static")

        def run():
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_frame"], cwd=tmp, capture_output=True,
                               text=True)
            tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
            return r.returncode, tail

        code, tail = run()
        print(f"control (unmutated copy): exit {code}: {tail}")
        if code != 0:
            return 1
        missed = []
        for name, old, new in RULES:
            (tmp / FRAME).write_text(source.replace(old, new))
            code, tail = run()
            print(f"{'caught' if code != 0 else 'MISSED'}: {name}  [{tail}]", flush=True)
            if code == 0:
                missed.append(name)
        (tmp / FRAME).write_text(source)
        print(f"{len(RULES) - len(missed)} of {len(RULES)} mutations caught")
        return 1 if missed else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
