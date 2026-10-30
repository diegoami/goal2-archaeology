# T80b step 1: the port's inputs outside GOAL.EXE's tables

[derived: `out/T80/a/read-map-family-v1.json` (the 75 admitted matches), `classify_elsewhere_v1.py`,
`who_reads_v1.py` (E034-03's drive, which port routine reads each byte); 2026-10-29] Of the 35,515
bytes the port reads before writing them, 15,016 are GOAL.EXE's (T80a's tables: the code segments'
data areas and the initialised data segment, less DS:7968). The rest is the game's state when the
match starts, which goal2 holds:

| Where | Bytes (family) | Read by (E034-03) | What |
| --- | ---: | --- | --- |
| DS:7968 | 1 | | set by the game before a match |
| the rest of DS (DS:7B70..FFFF) | 420 | | the game's variables |
| the player records (`DS:A91B`, 0x14 each) | 5,451 | | the players |
| the country records (`DS:A917`, 0xBF each) | 2,347 | | the countries |
| the text page (B800:0000) | 4,000 | | what the screen shows before the match (display only) |
| from the fixtures (`DS:A92B`) on, about 6.1 KB | ~5,000 | 1771:8322 (the post-match update) | the fixtures and the competition's tables |
| 26-byte strided rows above 0x64ABE | | 1771:8322 | the competition's table rows |
| the game record (`DS:A923`) and around it | ~350 | 0791:9372, 0791:BB05 | the game record's fields |
| two blocks of 220 bytes below the countries | 440 | 23E4:062A/06B7 (Pascal string helpers, from display and menus) | the two squads' player names, built from the player records |
| a 48-byte buffer | 48 | 214B:003C (display) | an empty text buffer |

So the sealed engine's input is GOAL.EXE's tables plus the game's state: no constant outside the
tables is read in the admitted family. The packed screens and commentary templates T80 names are
not read from the heap here (the commentary's texts are in the initialised data, inside the tables).
Open for T80b: which of these goal2 passes as records (players, countries, fixtures, the game record,
the variables) and which the engine builds itself (the squads' name lists from the player records;
the screen and buffers blank, as no result depends on them: the comparisons exclude the screen).

## The probe: tables plus state only

`minimal_image_v1.py`: a memory image that is zero except T80a's tables (43,172 bytes at their image
positions) and the read map's 20,500 state bytes, taken from the reference image (52,297 non-zero
bytes in all, of 1.1 MB). E034-03's straight drive from it equals the drive from the full image in its
831 events (the same digest), the score, the 110,835 draws and every field of the result; the only
field that differs is `image_sha256`, the result's digest of its own input image
(`minimal-image-v1.json`), so v2 compares the result without it: `equal: true`
(`minimal-image-v2.json`). The build guard is bypassed in the probe only, because it zeroes the code
on purpose. Still to show: the family (T80b's Done-when runs the kit's check from records).

## The family probe: the input contract

[derived: `probe_family_v1.py` .. `probe_family_v5.py`, their parts and `probe-family-v*.compare.log`;
2026-10-29] Every admitted match (the 75 of `ALL` less A700), played on the port (PyPy, one worker per
chunk) from its own source image reduced to the tables plus state, then checked by compare.py's
`identical` check under the strict display profile against its bound reference
(`families/display/reference-with-finals-20261024-v1.jsonl`), the image binding left out (each record
names its reduced input image by digest).

| Version | State kept from the source image | Result |
| --- | --- | --- |
| v1 | the read map's bytes, DS:7968 | events, scores and draws identical in all 75; post-match digests differ (regions v1 had zeroed outside the bytes read) |
| v2 | + DS:7B70..FFFF and records.RANGES whole | DS+0x7800, the records and w5c8a0 still differ |
| v3 | + the 26 initialised bytes (DS:7966..7B68, the RNG word DS:7B62 among them) the game changed after start-up | the records and w5c8a0 still differ |
| v4 | records.RANGES at load*16 + start (v2/v3 placed them at absolute addresses, a probe bug) | 74 of 75; FS/public-stage8-holland-belgium differs at records+0x16C00 |
| v5 | each source's own records extent (`records.ranges_for_source`: E031-stage8 and T86-stage8 carry 106,640 bytes, not 93,648) | **75 of 75 identical** (v5 reran the one match its change touches; the other 74 are v4's, whose reduction v5 leaves byte-identical) |

So the sealed engine's input contract, for the admitted family, is:
- **from GOAL.EXE** (T80a's tables, built from the player's own file, never shipped): the initialised
  data segment DS:0000..7B6F and the listing's 173 code-segment data areas (11,572 bytes);
- **from the game** (goal2's state when the match starts): DS:7B70..FFFF; DS:7968; the initialised
  bytes the game has changed since start-up (26 in the family's sources, DS:7966..7B68); the record
  ranges at load*16 + start, the records with the source's own extent; and the remaining bytes the
  read map lists outside those (the text page, the name-list blocks, the 48-byte buffer: display
  inputs, which the engine can build or blank).
Nothing else in the 1.1 MB image is read: GOAL.EXE's code and the rest of memory are zero in the
probe. The build guard (Image.build_problems) and the source's memory digest
(image_sources.validate_image) are bypassed in the probe only.
