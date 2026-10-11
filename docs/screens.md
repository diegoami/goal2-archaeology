# Screens: the catalogue and the renderer (T39a)

What a driver or a bot may press on each screen of GOAL2, with where each row comes from, and a
picture of any screen. The tools are read-only over the committed E015 records
([`runs/E015/`](../runs/E015)); no game is run.

## The catalogue

[`static/screens/catalogue.tsv`](../static/screens/catalogue.tsv), one row per screen kind and key:

| column | meaning |
| --- | --- |
| `kind` | the screen kind, named from the screen's fixed text (never a digest: a digest changes with every name and number) |
| `key`, `keysyms` | the key as the screen or the log prints it, and the X keysym(s) of the recorder's key log |
| `effect` | for a `screen` row, the screen's own words; for a `run:` row, `burst: <kind before> -> <kind after>` |
| `source` | `screen`, `run:<run id> state <n>`, `static:<path>:<line>` (none yet: later tasks fill it from the code), or `owner` |
| `quote`, `state` | `screen` rows: the hint text and the record state (`E015-r0007 state 16`) it was read in |
| `to_kind`, `to_state`, `count` | `run:` rows: the kind and first state of the screen after, and the bursts seen |
| `rule` | the kind's rule, copied from [`kinds.tsv`](../static/screens/kinds.tsv) |

Reading it:

- A `screen` row means the screen prints that key. A prompt drawn over another screen keeps the
  other screen's hints on show but not in force; such kinds list only their own line
  (`OVERLAYS` in `build.py`).
- A `run:` row is a burst: the screen before, the presses in order, the screen after (T34's rules,
  [`keymap.py`](../experiments/E015-human-playthrough/keymap.py)). It says what was seen, never
  that one key caused it; a row of many presses is one burst. Only the owner's sittings count
  (`REAL_SITTINGS` in `build.py`); the scripted acceptance sittings E015-r0004 to r0006 do not.
  `state` is the first state of the record that has the screen before; a screen no rule names
  (`unknown`) leaves its bursts out.
- A kind with no key found has one row with an empty key and `no key known`.
- The only hand rows are in [`owner.tsv`](../static/screens/owner.tsv) (`kind`, `key`, `keysyms`,
  `effect`), and get source `owner`.

`python3 tools/screens/build.py` rebuilds the file from the records (byte-identical when nothing
changed; `--check` compares). To add a hint: add an entry to `HINTS` in `build.py` (the quote and the
key as the screen prints them); it makes a row only for kinds whose recorded screens hold the quote.

## Screen kinds

`python3 tools/screens/identify.py <record|run id> [state ...] [--summary]` gives a state's kind
or `unknown`; `--savestate <file.sav>` does the same for a savestate. A kind's rule is
`+phrase ;; -phrase`: every `+` phrase occurs and no `-` phrase occurs in the screen's text (runs of
whitespace as one space). Two rules matching one screen is an error, so rules are written exclusive
(`tests/test_screens.py` checks every state of every record). Add a kind by adding a line to
`kinds.tsv` and rebuilding.

## An unknown screen

Render it, and send the PNG to the owner with the question "what do I press here, and what does it
do?". The answer goes in `owner.tsv`, with a rule in `kinds.tsv` if the screen is new.

## The renderer

`python3 tools/screens/render.py <record|run id> <state> [-o out.png]` (or `--savestate`) writes
a 640x400 PNG: 80x25 cells of 8x16 dots, the 16 standard VGA colours, blink off (attribute bit 7 is a
bright background). A record keeps only a screen's text and digest, not its attributes, so the
picture comes from the state's savestate, found by name under `--from` directories, `.cache/evidence/E015`
(`python3 tools/verify_evidence.py E015`) or `scratch/human/sessions/*/snapshots`, and checked against
the sha256 of `evidence/E015/<run>.manifest.json`. The glyphs are the font in the savestate (VGA plane
2); if it holds none, the pinned [`font-goal-8x16.bin`](../static/screens/font-goal-8x16.bin) is used
and the run says so. PNGs and screens stay in this private repository and with the owner (CLAUDE.md
rule 18): [`E015-r0007` states 16 and 76](../static/screens/png).
