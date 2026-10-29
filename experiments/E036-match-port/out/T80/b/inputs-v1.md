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
