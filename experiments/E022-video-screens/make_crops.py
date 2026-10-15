#!/usr/bin/env python3
"""Make the three committed crops tests/test_screens_video.py decodes.

    python3 experiments/E022-video-screens/make_crops.py <session folder>

SYNTHETIC STAND-INS, not video frames: the sitting's video holds no game pixels (notes.md), so each crop
is a 25x3-cell piece of a snapshot's text screen (T39a's renderer, the savestate's own font and attributes)
drawn at 2x like the window the recorder films, then every channel of every pixel moved by a fixed
pseudo-random amount of at most +-12 (a stand-in for h264 noise; the decoder maps to the nearest VGA colour).
GOAL2 material: private repository only (rule 18).
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "screens"))
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import render  # noqa: E402
import savestate  # noqa: E402

CROPS = [("crop-a.png", 101, 0, 0), ("crop-b.png", 101, 6, 0), ("crop-c.png", 150, 7, 0)]
COLS, ROWS, SCALE, NOISE = 25, 3, 2, 12


def main(session):
    session = Path(session)
    index = [json.loads(line) for line in open(session / "index.jsonl")]
    rng = random.Random(20261015)
    out = Path(__file__).parent / "crops"
    for name, seq, row0, col0 in CROPS:
        ss = savestate.Savestate(session / index[seq - 1]["file"])
        glyphs, _ = render.font_for(ss)
        scr = ss.screen()
        cells = [(r, c) for r in range(row0, row0 + ROWS) for c in range(col0, col0 + COLS)]
        chars = bytes(scr.chars[r * savestate.COLS + c] for r, c in cells)
        attrs = bytes(scr.attrs[r * savestate.COLS + c] for r, c in cells)
        rows = []
        for text_row in range(ROWS):
            for y in range(render.CELL_H):
                line = bytearray()
                for c in range(COLS):
                    ch, at = chars[text_row * COLS + c], attrs[text_row * COLS + c]
                    fg, bg = render.attribute_colours(at)
                    bits = glyphs[ch][y]
                    for x in range(render.CELL_W):
                        px = fg if bits >> (7 - x) & 1 else bg
                        line += bytes(px) * SCALE
                for _ in range(SCALE):
                    rows.append(bytes(min(255, max(0, v + rng.randint(-NOISE, NOISE))) for v in line))
        (out / name).write_bytes(render.png(rows, COLS * render.CELL_W * SCALE, ROWS * render.CELL_H * SCALE))
        print(name, seq, row0, col0)
        print("\n".join(scr.lines()[r][col0:col0 + COLS] for r in range(row0, row0 + ROWS)))


if __name__ == "__main__":
    main(sys.argv[1])
