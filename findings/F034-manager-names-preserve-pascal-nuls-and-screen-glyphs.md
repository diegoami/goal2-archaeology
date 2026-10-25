# F034 Manager names preserve Pascal NULs; the screen writes cells

- **Status**: proposed.
- **Artifact**: goal2-67cf27d6 (identical executable/data to goal2-a949da2f).
- **Question**: #429: manager-name record boundaries and the trailing glyph after B Vogts.
- **Method**: static first, named formatter, callers and Pascal/screen helpers, checked against the assembly; then isolated original-code execution to corroborate exact payloads. No behavioral game session was run. These probes are static-adjacent, not independent behavioral corroboration.
- **Max intervention**: synthetic call frames, scratch result/screen buffers; five explicitly synthetic name controls in a private copy. Genuine manager records remain unchanged for their observations. No executable edits or behavior hooks.

## Answer

- `1771:0947(m)` makes one initial byte (including zero), a single space from CS:0945, and exactly the surname's Pascal length, then stores at most14 bytes. The name record has width13 (length plus twelve payload bytes), F002 R005/R006. No C-string terminator or formatting byte is consumed. The original trusts the length; the host decoder rejects malformed widths/lengths rather than claiming the original validates them. static:static/goal-exe/code/seg_1771_01.asm:1036 static:static/goal-exe/code/seg_23E4_01.asm:746 static:static/goal-exe/code/seg_23E4_01.asm:803 static:static/goal-exe/code/seg_23E4_01.asm:900

- Germany's manager12 has declared surname length6, although only five letters spell Vogts: its sixth character is NUL. The original formatted payload has eight cells: `B Vogts` plus NUL. This agrees with F002's pre-existing anomaly inventory. The current downstream algorithm returns `B Vogts` plus U+0000; the standard DOS text-cell projection yields `B Vogts `, with a final blank. This is a demonstrated decoding discrepancy and a source-backed explanation for the owner's symptom; the screenshot's exact Unicode character/font/rendering path is not established here. static:static/goal-dat/checks.txt:6 static:notes/429/original-r1.json:1 static:notes/429/original-r2.json:1

- TEAM draws the result with `214B:026D`, which copies the Pascal payload and calls `00FF`. That primitive writes each byte as the character half of one text cell; low values are not interpreted as string termination, newlines, colors or escape sequences. In all135 original name records and five synthetic controls, the actual original writer's character cells equal the formatter payload byte for byte. The font's glyph interpretation is a separate projection: the pure decoder uses the standard IBM PC text glyphs, with zero blank and1..31/127 represented by their glyphs, not Unicode controls. static:static/goal-exe/code/seg_214B_01.asm:155 static:static/goal-exe/code/seg_214B_01.asm:353 static:notes/429/original-r2.json:1


## Observations and checks

The producer first ran without the decoder (receipt r1), then compared it with the decoder (r2). Both are retained. It verifies the full E010-r0001 half-time hash against the immutable run record and checks original code/data identity with the existing build guard. Every call must return to its sentinel with the source-declared stack cleanup within2seconds/500000 instructions. `0947` and its string helpers and `026D/00FF` run unmodified. Screen buffers use a sentinel immediately after the expected cells to detect extra output. No original record, executable, save or screenshot bytes are exported; receipts contain decoded observations, counts and hashes. static:notes/429/probe.py:1 static:notes/429/original-r1.json:1 static:notes/429/original-r2.json:1

Five independent tests include Vogts's trailing NUL, a Pascal length shorter than a printable run (Olsen), an interior NUL followed by a character, empty surname/zero initial, twelve-character maximum, low/high glyphs, preserved whitespace, and host rejection of invalid records. The module fails to import before implementation; changing NUL handling, separator, record width, maximum length or C-style termination fails assertions. Exact validation and downstream instructions are in the report. static:tests/test_manager_decoder.py:1 static:docs/requests/429-manager-name.md:1

## Alternatives and limits

1. **Overreading beyond the13-byte record** is excluded for the shipped German record: declared6 fits, and original and independent bounded extraction agree. Overreading malformed runtime lengths is possible in the original and deliberately rejected by the host.
2. **A hidden formatting command consumed by the writer** is excluded for this path by unhooked writer execution: the NUL becomes a character cell, and a synthetic interior NUL does not stop the following character.
3. **The screenshot box is a different byte/font defect** remains possible without its exact stopped memory and displayed string/codepoints. No inference from a tofu box establishes a specific encoding byte.

This does not establish every possible font's glyph appearance, the exact private playtest memory, arbitrary corrupt records, other releases or manager editing behavior. No guessed stripping or transliteration is recommended. F024's period separator description is corrected; its other claims are unchanged.

## Inferences

- The reusable consumer correction is to project the existing Pascal payload as screen glyphs, not terminate at NUL or strip arbitrary characters. Screenshot attribution remains conditional on the private stopped input and rendering path. static:notes/429/original-r2.json:1
