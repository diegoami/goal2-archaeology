"""The player screen of GOAL.EXE, read from the text page (T16, Q009).

The screen is drawn by `1771:42BC` (the card at the top), `1771:3947` (the twelve bars of the left
panel) and `1771:3BD3`; the template it starts from is the byte string at `DS:486E` (`seg_1771_06.asm`
`42C3`; the data bytes `DS:486E..4BBD` in `static/goal-exe/data/ds_2581_02.hex`, the team panel's template following
at `DS:4BBE`). The coordinates are
the ones the routine passes, 1-based (row, column) on the 80x25 text page, so a 0-based cell is one
less; the bars are cells whose attribute is 0x70, painted by `214B:00DB` (`seg_214B_01.asm:00DB`:
`inc di / stosb`, the attribute byte of each cell) over the template's filler cells.

Every constant below is read off the listing or the screen of E007's records:
- row 7 (`2EE5` at (8, 2): the name; (8, 0x13) the age; (8, 0x18) caps; (8, 0x1E) goals; (8, 0x21) and
  (8, 0x24) the height as feet and inches; (8, 0x28) the foot; (8, 0x3C) the performance),
- row 9 ((0xA, 2) the position byte +6; (0xA, 0x15) the position byte +7; (0xA, 0x3D) the status),
- the left bars: `3947(player, 0xB, 0xB)` paints row 0xB + i, column 0xB, for i = 1..12: 0-based rows
  11..22, columns 10..35 (the template's 0x19-wide filler plus the cells around it, 26 in all, as the
  records show), the length being the number of cells with attribute 0x70,
- the right panel: rows 0x13..0x17 (0-based 18..22), column 0x30 (0-based 47), 14 cells (the bars of
  `214B:13C5` are at most 14 long: `value * 14 div 32`, `* 14 div 16`, `* 14 div 7` in `42BC`),
- the squad list beside the card (T16 rework, R1): `1771:4E22` draws it with `1771:4D8A(country)`
  (`seg_1771_07.asm:4D8A`-`4E1F`) before the card: the template `DS:15A4`, the header `0F58(country, 1, 0x41)`, then
  `2F37(country word i - 1, i + 2, 0x41)` for i = 1..11 and `2F37(..., i + 3, 0x41)` for i = 12..20 (`4DC2`-`4E1A`).
  `2F37` prints the name at (row, 0x41) (`2EE5`: at most 12 characters, `1771:2E93`'s `23E4:0644` with 0xC) and one
  glyph at (row, 0x41 + 0xD) (`2F92`-`2FA2`). `214B:02C8` writes at (row - 1) * 160 + (col - 1) * 2 (`02E9`-`0306`:
  `mul 0xa0`, `shl`, `add di, 0xff5e`), so the 0-based cells are rows i + 1 (i <= 11) and i + 2 (i >= 12), columns
  64..75 (the name) and 77 (the glyph); row 0, columns 64..78 the header (`0F58`: the 15 '-' of `DS:0D6A`, then the
  country's name over them). `4E22` then paints the 12 name cells of row `[DS:0C1B]` at 0x70 (`4F45`-`4F67`:
  `214B:13C5(0xC, 0x41, [DS:0C1B] + 2 + ([DS:0C1B] > 11))`), the list position of the player on the card.
"""
import re

import savestate

ROWS, COLS = 25, 80
LEFT_ROWS = range(11, 23)      # the 12 skill rows
LEFT_COLS = range(10, 36)      # the bar field
RIGHT_ROWS = range(18, 23)     # hardness, fitness, energy, morale, leadership
RIGHT_COLS = range(47, 61)     # the word and its bar
TACTIC_ROWS = range(11, 16)    # position, possession, passing, tackling, mark (the player's tactics)
TACTIC_LABELS = ("position", "possession", "passing", "tackling", "mark")
BAR_ATTR = 0x70
FILL = "■"                # CP437 0xFE
SQUAD_COL = 0x41 - 1           # 2F37's column 0x41, 0-based
SQUAD_NAME_LEN = 12            # 1771:2E93 cuts the name to 0xC characters
SQUAD_GLYPH_COL = 0x41 + 0xD - 1
SQUAD_ROWS = tuple(i + 1 + (i > 11) for i in range(1, 21))   # 4D8A: rows i + 2 and i + 3, 1-based
HEADER_ROW, HEADER_LEN = 0, 15                               # 0F58 at (1, 0x41); DS:0D6A is 15 '-'

# The cells parse reads, as (row, first column, last column + 1). Every other cell is the template's, the same on
# every player screen (summarise.py checks it over the records).
TRANSCRIBED = ((7, 1, 61), (9, 1, 61),
               *((r, 37, 61) for r in TACTIC_ROWS), *((r, 1, LEFT_COLS.stop) for r in LEFT_ROWS),
               *((r, 37, 61) for r in RIGHT_ROWS),
               *((r, SQUAD_COL, SQUAD_GLYPH_COL + 1) for r in SQUAD_ROWS),
               (HEADER_ROW, SQUAD_COL, SQUAD_COL + HEADER_LEN))


def screen_of_raw(raw):
    """A savestate.Screen from the 4000 bytes B800:0000 holds (chars and attributes interleaved)."""
    if len(raw) != ROWS * COLS * 2:
        raise ValueError(f"a text page is {ROWS * COLS * 2} bytes, not {len(raw)}")
    return savestate.Screen(raw[0::2], raw[1::2])


def is_player_screen(screen):
    lines = screen.lines()
    return lines[6].startswith("┌name") and lines[10].startswith("├skills") and lines[8].startswith("├position")


def _bar(attrs, row, cols):
    return sum(1 for c in cols if attrs[row * COLS + c] == BAR_ATTR)


def parse(screen):
    """Every value the player screen shows, as a dict of strings and integers; ValueError when the
    screen is not a player screen or a numeric cell is not a number."""
    if not is_player_screen(screen):
        raise ValueError("not a player screen")
    lines, attrs = screen.lines(), screen.attrs
    card = lines[7]
    height = re.fullmatch(r"\s*(\d+)'\s*(\d+)\"\s*", card[31:38])
    if not height:
        raise ValueError(f"height cell {card[31:38]!r}")
    out = {"name": card[1:15].strip(), "age": int(card[16:19]), "caps": int(card[20:24]), "goals": int(card[25:30]),
           "height_in": 12 * int(height.group(1)) + int(height.group(2)), "bias": card[39:49].strip(),
           "performance": card[50:61].strip()}
    low = lines[9]
    out.update({"position": low[1:19].strip(), "club_position": low[20:38].strip(),
                "cards": low[39:44].strip(), "status": low[45:61].strip()})
    # the tactics panel (1771:3BD3 and 1771:3AE2): rows 11..15, the label then the text, right-aligned to col 60
    out["tactics"] = {}
    for r, label in zip(TACTIC_ROWS, TACTIC_LABELS):
        cell = lines[r][37:61]
        if not cell.startswith(label):
            raise ValueError(f"tactics row {r} starts {cell[:12]!r}, not {label!r}")
        out["tactics"][label] = cell[len(label):].strip("─ ")
    out["skills"] = {lines[r][1:10].strip("─ "): _bar(attrs, r, LEFT_COLS) for r in LEFT_ROWS}
    out["panel"] = {}
    for r in RIGHT_ROWS:
        label = lines[r][37:47].strip("─ ")
        cell = lines[r][47:61]
        out["panel"][label] = {"word": cell.split(FILL)[0].strip(), "bar": _bar(attrs, r, RIGHT_COLS)}
    out["squad"] = [_slot(lines[r], attrs[r * COLS:(r + 1) * COLS]) for r in SQUAD_ROWS]
    head = lines[HEADER_ROW][SQUAD_COL:SQUAD_COL + HEADER_LEN]
    name = head.rstrip("-")
    ha = attrs[HEADER_ROW * COLS + SQUAD_COL:HEADER_ROW * COLS + SQUAD_COL + HEADER_LEN]
    out["country"] = {"name": name, "name_attrs": tuple(ha[:len(name)]), "fill": head[len(name):],
                      "fill_attrs": tuple(ha[len(name):])}
    return out


def _slot(line, attrs):
    """One row of the squad list: the name (trailing blanks off), the attribute of each of its cells, the
    background (attribute bits 4..7) of the blank cells after it to column 75 (only the background of a blank
    shows), the glyph and its attribute."""
    name = line[SQUAD_COL:SQUAD_COL + SQUAD_NAME_LEN].rstrip(" ")
    a = attrs[SQUAD_COL:SQUAD_COL + SQUAD_NAME_LEN]
    return {"name": name, "name_attrs": tuple(a[:len(name)]), "tail_background": tuple(x >> 4 for x in a[len(name):]),
            "glyph": line[SQUAD_GLYPH_COL], "glyph_attr": attrs[SQUAD_GLYPH_COL]}
