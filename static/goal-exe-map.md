# Map of GOAL.EXE's code by area

Hand-written index over the generated listing in [`goal-exe/`](goal-exe/README.md), for the unpacked
`GOAL.EXE` (sha256 `6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188`, from the packed
file `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`). The areas are the rows of
[`knowledge-map.md`](../knowledge-map.md). Nothing here changes a status there.

How to read it:
- An address is `SEGMENT:OFFSET`, the segment being the image paragraph before relocation
  ([`goal-exe/README.md`](goal-exe/README.md)); a data-segment address is `DS:OFFSET`, the data segment being `2581`.
  A routine's size and callers are in [`goal-exe/routines.tsv`](goal-exe/routines.tsv) and
  [`goal-exe/calls.tsv`](goal-exe/calls.tsv); its code is in `goal-exe/code/seg_SSSS_NN.asm`.
- **Basis** is `static:listing` throughout. **observed** means the row states only what the listing shows: a string the
  routine references or sits beside, a constant, a call, a data-segment offset it uses (cited in
  [`goal-exe/strings.tsv`](goal-exe/strings.tsv), [`goal-exe/datarefs.tsv`](goal-exe/datarefs.tsv) or by instruction).
  **inferred** means a role read from those observations; the row says from which. **not placed** means the area has
  texts or tables in the data segment but no routine is tied to them. No inferred row is a finding.
- `tests/static/test_map.py` checks that every routine start cited as an address below is a routine in `routines.tsv`,
  every quoted string occurs in the listing's strings, every row is marked, and the unit table's counts equal `routines.tsv`.
- The code is almost certainly Pascal compiled to real-mode 8086 (inferred from: length-prefixed strings, one code
  segment per unit, a start-up routine at `23E4:0000` that loads `DS` and installs INT 00h/23h/24h/3Fh through INT 21h AH=25h,
  a halt routine with INT 21h AH=4Ch at `23E4:00D8`, the text "Runtime error " at `23E4:01E0`). Which compiler and version
  is not established.

## Units (code segments)

| Segment | Image offsets | Routines found | Code bytes decoded | What it is | Marked |
| --- | --- | --- | --- | --- | --- |
| `0000` | 00000..000DF | 1 | 223 | the main program (below) | observed |
| `000E` | 000E0..0790F | 58 | 24514 | news and press text built from phrases ("WORLD CHAMPIONS!", "Assistant says:", "IS SACKED!!!!"), and `000E:7439`, the last routine the main program calls, which calls the screens | inferred |
| `0791` | 07910..16D5F | 283 | 61291 | the largest unit: screens and the in-match code (events, replay, summaries, squad checks) | inferred |
| `16D6` | 16D60..1770F | 26 | 2359 | the help viewer for `GOAL.HLP` | observed |
| `1771` | 17710..2137F | 154 | 39019 | game state: loading and saving, fixtures, squads, tactics, player status | inferred |
| `2138` | 21380..2138F | 1 | 7 | an empty start-up routine (`push bp; mov bp, sp; mov sp, bp; pop bp; retf`) | observed |
| `2139` | 21390..214AF | 1 | 277 | the start-up routine that allocates the program's heap blocks (below) | observed |
| `214B` | 214B0..235BF | 85 | 8026 | utility unit: text windows and prompts, the file API on DOS handles, printing, running `COMMAND.COM` | inferred |
| `235C` | 235C0..2381F | 12 | 600 | a call of INT 21h with a register record (`235C:0000`), a generic interrupt call (`235C:000B`), date, time and find-file calls | inferred |
| `2382` | 23820..23E3F | 17 | 820 | keyboard and screen: INT 16h, INT 10h | inferred |
| `23E4` | 23E40..2580F | 88 | 4908 | the language's run-time library: start-up, halt, string routines, memory, files | inferred |
| `2581` | 25810..2D37F | | | the initialised data segment, 31,600 bytes: its text and tables are in `goal-exe/data/` and `goal-exe/strings.tsv` | observed |

## The main program and the heap

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `0000:0000` | the main program | far calls to the units' start-up: `23E4:0000`, `2382:0000`, `214B:206A`, `2139:0000`, `2138:0000`, `0791:F3F2`; then `1771:080C` (the saved-game question), `214B:179C`, `1771:9B85`, `1771:2D15`, a loop for `i` = 1 to the byte at `[A923]` that calls `000E:68A4` with the byte at `[A91F] + (i + 0x80) * 3`, `1771:76B1`, a second loop of the same form that calls `000E:60CB`, `000E:7439`, and `23E4:00D8` (halt); when `1771:080C` returns non-zero the main program jumps straight to `000E:7439` | observed |
| `2139:0000` | allocates the program's heap blocks | 16 calls `mov di, <pointer>; mov ax, <size>; call far 214B:0A62` (`214B:0A62` has 19 callers; the text "Insufficient memory to run program" precedes it) for `[9B68]` 0x810, `[9B6C]` 0x8387, `[9B70]` 0xBF5, `[9B74]` 0x6DB, `[9B78]` 0x87, `[A917]` 0x603F, `[A91B]` 0xEF24, `[A91F]` 0x195, `[A923]` 0x10E, `[A927]` 0x3C2, `[A92B]` 0x4B48, `[A92F]` 0x2448, `[A933]` 0x1C00, `[A937]` 0x348, `[A93B]` 0x348, `[A93F]` 0x1E0: the first five are the `GOAL.DAT` blocks, the next eleven the saved game's | inferred (allocation) |
| `000E:7439` | the top-level screens | called last by the main program; calls `0791:112C`, `0791:E44F`, `16D6:0945`, `1771:090F`, `1771:09A0`, `1771:1981`, `1771:26B9`, `1771:4D8A`, `1771:5BF6`, `1771:958D` | inferred |

## Data files and saves

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:011B` | opens a named file; on failure shows a message and ends the program | strings "Cannot load file" and "program terminated" beside it; calls `214B:1BF5` (open) | inferred |
| `1771:018A` | loads `GOAL.DAT` | the string "goal.dat" at `1771:0181`; ten consecutive calls to `214B:1B47` (read) whose sizes `0x810 0x8387 0xBF5 0x6DB 0x87 0x183 0x81 0x81 0x81 0xA14` add up to 44,040, the size of the file; destinations `[9B68] [9B6C] [9B70] [9B74] [9B78]` (far pointers allocated by `2139:0000`), then `DS:9D80 DS:9B7C DS:9BFD DS:9C7E DS:9F03` | observed |
| `1771:027B` | writes or reads a saved game | its byte argument picks the message: `mul 0xB`, `add di, 0xC22` selects "Saving" or "Loading" (11 bytes apart); then 22 transfers through `1771:0232`, which calls `214B:1B47` (read) when the argument is not zero and `214B:1AD1` (write) when it is: the ten arrays of `GOAL.DAT` with the same sizes, then `[A917]` 0x603F, `[A91B]` 0xEF24, `[A923]` 0x10E, `[A927]` 0x3C2, `[A91F]` 0x195, `[A92B]` 0x4B48, `[A92F]` 0x2448, `DS:9CFF` 0x81, `[A933]` 0x1C00, `[A937]` 0x348, `[A93B]` 0x348, `[A93F]` 0x1E0, then `214B:1A36` (close); the 22 sizes add up to 169,553 bytes; the extension is the 3-character string ".GL" in the bytes just before `1771:03FF` | observed |
| `1771:0480` | finds saved games | strings "Finding saved games..." and "*.GL"; "SAVED" at `DS:0C72` | observed |
| `1771:03FF` | saved-game file naming | references "SAVED" (`DS:0C72`); the 3-character string ".GL" is in the bytes before it | inferred |
| `1771:0657` | saved-game selection | references "SAVED" (`DS:0C72`) | inferred |
| `1771:080C` | the first question of a session | the string "Do you want to load a saved game? (Y/N)" beside it | observed |
| `1771:090F` | quitting | strings "Are you sure you want to quit" and "Do you want to save this game" beside it | observed |
| `1771:101A` | refuses to overwrite a file | string " already exists" beside it | inferred |
| `0791:0C65` | action replay: offers to save a goal | strings "an action replay" and "to save this goal" beside it; `DS:06D6` is ".HIL" | inferred |
| `0791:F1F6` | saves the match summary | string "to save the match summary to disk" beside it; `DS:06DB` is ".SUM" | inferred |
| `214B:1BB7` | creates a file | `mov ax, 0x3C00` then `call 0x1A5F` (a DOS call by name, through `235C:0000`) | observed |
| `214B:1BF5` | opens a file for reading and writing | `mov ax, 0x3D02` then `call 0x1A5F` | observed |
| `214B:1B47` | reads a block from the open file | sets AH to `0x3F`; the handle is `DS:AAA4` | observed |
| `214B:1AD1` | writes a block | sets AH to `0x40`; the handle is `DS:AAA4` | observed |
| `214B:1A36` | closes the file | sets AH to `0x3E` | observed |
| `214B:1869` | DOS error texts | strings "Illegal file name or file not found", "Path not found", "Read only/hidden file", "No such drive" | observed |
| `16D6:08C5` | opens `GOAL.HLP` | strings "GOAL.HLP" and "not found" beside it; calls `214B:1BF5` | observed |
| `16D6:0910` | checks free memory before showing help | compares the result of `23E4:038C` with 0x9C40 (40,000); string "not enough memory" | observed |
| `16D6:04C3` | prints the help | strings "Do you want a print out of the help" and "Printing...." | observed |

## Countries, continents and their strength

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:9A40` | builds the 128 country records (called from `1771:9B85`) | records of 0xBF (191) bytes at `[A917]` (`mul 0xBF`): for each position 1..128 it reads a country number from `DS:9BFD` and stores the position at field +0x2B; reads `DS:9C7E`, stores `(position-1) mod 32 + 1` at +0x2A and `(position-1) div 32 + 1` at +0x2C; copies `DS:9B7C` into +0x2D; stores the country number at +0x2E and as byte 0 of the 3-byte record at `[A91F]`; fills the first 20 words of the record with the player numbers `(country-1)*20 + 1 .. country*20` | observed |
| `1771:9B85` | starts a new game | calls `1771:9A40`; stores `DS:A9FD` + 1 (made even) at `[A923]` +0x3A, and sets byte +0x40 to 1 when that value mod 4 is 2 | inferred (a four-year cycle) |
| `DS:6E9A` | continent names | strings "Europe", "America", "Africa", "Asia" | observed |
| `DS:690A` | continent adjectives | strings "EUROPEAN", "AMERICAN", "AFRICAN", "ASIAN" | observed |
| `0791:1073` | picks two teams' display colours | reads bytes 0 and 2 (and 1 when they coincide) of the 3-byte records at `DS:9D80` of the two countries in `DS:9B34` and `DS:9B36`, into `DS:832E..8331` | inferred (colours) |

How strong each country is, and where the 128 differ, is **not placed**: no routine reads a strength table by name or string.

## The player pool and the squad

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:97CC` | creates the 20 players of one country | first writes the country number into the seed word `DS:7B62` (`seg_1771_14.asm:18`–`20`; F007), then calls `1771:96D3` for slots 1..20 with the player number, the country, a byte of `DS:9F03` (`mov al, [di-0x60FE]` after `mul 0x14`) and 1 | observed (F007) |
| `1771:98C4` | makes the managed country's 80 extra players (2561..2640) | through `1771:9873` → `1771:96D3(…, 0)`: positions 0..13 four times, one per squad slot 1..20 (age redrawn), then slots 6..9 again (`seg_1771_14.asm:146`–`253`; F007) | observed (F007) |
| `1771:10E7` | a country's rating | `((5 − [+0x2C]) · (0x21 − [+0x2A]) + (0x81 − [+0x2B])) idiv 2` over the country record (`seg_1771_02.asm:710`–`733`); player field +3 is it + 0x7F (F007) | observed (F007) |
| `0791:BC5D` | sets up a country's team | clears field +0xF of its 20 players, calls `0791:BBFF` with the country and `DS:9B7C[country]`, calls `1771:52CC`, then copies the byte of `DS:9F03` of slots 1..11 into field +6 of the 20-byte record at `[A91B]` | observed |
| `0791:DBFA` | refuses a change of squad | strings "cannot alter squad" (`DS:0A9C`), " during finals" and " whilst on tour" | observed |
| `0791:E022` | refuses a substitution | strings "There is no player here", "Illegal substitution", " cannot play", "Nice try" | observed |
| `1771:4FAA` | checks the first team | strings " has too many ", "s in 1st team", " has no keeper in 1st team" | observed |
| `0791:EA09` | checks the first team (another screen) | strings " has an ineligible player in the first team", " has too many ", " has no " | observed |
| `1771:42BC` | the status of a player | strings "two footed", "suspended", "injured", "booked", "sent off", "substituted", "ready to play", "selected", "on the bench" | observed |
| `000E:544D` | press text on a player | strings "SHOWS PROMISE", "DESERVES A CAP", "NEEDS" | observed |
| `000E:50D4` | retirement news | strings "retires from the", "international scene", "is to retire", "at the age of " | observed |

The player record is 20 bytes, 3061 of them (`[A91B]`, 0xEF24 = 3061 * 0x14, allocated by `2139:0000`); `1771:97CC`, `1771:98C4` and `1771:9873` index it with `mul 0x14`. The names come from `[9B6C]` and the initials from `[9B70]` with the same player number (`0791:0106` reads both with `DS:7C3A`).

## Player attributes and skills; fitness, energy, confidence and morale; ageing

Not placed in code. The vocabularies are in the data segment (**observed**, strings only): the attribute and skill names around `DS:4979`
("keeping", "kicking", "possession", "tackling", "passing", "heading", "marking", "crossing", "feinting", "hardness", "control", "fitness", "dribbling",
"energy", "shooting", "morale", "penalties", "leadership", "height", "foot", "performance", "caps", "goals", "cards", in `DS:4979..4E78`); the words for confidence and mood
(`DS:6ED4..6FF4`: "demoralised" ... "acceptable"; "confident", "over-confident"); for fitness and energy (`DS:74D4` "unfit", "very fit", "match fit"; `DS:7624` "very tired").
The names are two screen templates (control bytes `FF attr`, `00 n`, filler `FE`): `DS:486E..4BBD` is the player screen, drawn by `1771:42BC` (the card and the right panel; `1771:3947` draws the 12 skill bars as `DS:6DCD[12 * +5 + DS:6D25[12 * +7 + i]] * (+4 + 1) div 256`; `1771:3BD3` the tactics rows; `1771:2FAD` height, `1771:3088` foot, `1771:3041` two footed, `1771:2FFB` hardness, `1771:30D9` leadership, `1771:3827` performance; the squad list beside it is `1771:4D8A`'s, template `DS:15A4`), and `DS:4BBE..4EB1`, which follows it, is the team panel drawn by `1771:157D`. Fields and ranges: F008 (inferred, corroborated by E007's screens).

## Team analysis and rankings

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:377E` | a player's value | reads fields +4, +0xC and +0xE of the 20-byte record at `[A91B]`, adds `0xFFC2`, subtracts one sixteenth when field +0xC is 0x20 or more and adds field +0xC otherwise, clamps to 0..0x100, and returns 0 when `1771:3216` reports the player unavailable | inferred (current playing strength) |
| `0791:BD03` | compares two teams | sums `1771:377E` over the first 11 player numbers of each of two countries (`mul 0xBF`, `[A917]`) and returns 1 when the first sum is larger | inferred |
| `DS:4C50` | text "ranking", "rankings" and the caption tables `DS:6605`, `DS:678C` | `strings.tsv` | observed |

How a ranking is set (the world and continental tables) is **not placed**.

## Positions and formation

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `DS:69B6` | the 14 position names, 19 bytes apart | strings "goalkeeper", "sweeper", "centre back", "left back", "right back", "defensive midfield", "central midfield", "left midfield", "right midfield", "forward midfield", "left winger", "right winger", "centre forward", "striker" | observed |
| `DS:69A8` | a table of 14 one-byte codes, directly before the names | "GSCBBD", 0x80, "MMFWW", 0x9B, 0x24: read by `0791:05C6` and `1771:2F37` as `[di + 0x69A8]` with `di` the position field | observed |
| `0791:05C6` | maps a player's position field to one of those codes | reads field +6 of the 20-byte record at `[A91B]` (the field `0791:BC5D` sets from `DS:9F03`) and indexes `DS:69A8` | observed |
| `1771:26B9` | picks players for the posts | string "post unavailable" beside it; 1,628 bytes, 106 direct data references | inferred |
| `1771:6730` | an option menu with position names | references `DS:68C5` "option", `DS:68D9` "play next game", `DS:69B6` "goalkeeper", `DS:69CA` "sweeper" | inferred |

## Tactics

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:3BD3` | player and team tactic choices | references `DS:6AC0` "stay back", `DS:6B00` "short passes", `DS:0EA6` "stay in box", `DS:0EC6` "throw the ball" | observed |
| `1771:3AE2` | choice of a marking zone | string "Protect zone" beside it | inferred |
| `1771:3B3F` | the same for a player | string "Protect zone P" beside it | inferred |
| `DS:6AC0` | the tactic names, 16 bytes apart | "stay back", "push forward", "keep ball", "quick pass", "short passes", "long passes", "avoid injury", "go in hard", "half pitch", "full pitch", "sag back to box", "stand ground", "play safe", "offside trap", "zonal", "man to man" | observed |

## The match engine

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `0791:1829` | builds one line of match commentary | for event `n` it reads the record at `DS:7C38 + 6n` (`shl 1`, times 3), takes byte 0 as the text number (0xFF = none), copies the string at `DS:0xBE + 0x15 * number` (`mul 0x15`, `add di, 0xBE`), and inserts the player's name from `[9B6C] + 11 * word at +1` | observed |
| `DS:00C0` | the commentary texts, about 21 bytes apart | "on for", "pass by", "makes a pass", "tackle by", "dodged by", "shot from", "hits the post", "saved by", "**** GOAL **** by", "** OWN GOAL ** by" | observed |
| `0791:A10A` | the penalty shoot-out | string "penalty shoot out" beside it | observed |
| `0791:97D0` | the per-tick loop of a match | calls the watched engine `0791:9564`, or `0791:D733` when the quick-result flag `DS:9A3E` is set; the clock `0791:970C` (F005) | observed |
| `0791:0C65` | action replay | strings "an action replay", "to save this goal"; 1,038 bytes | inferred |
| `0791:A4A1` | the set-up at the start of every match (F005; earlier read as one step of a match) | zeroes the commentary counter, draws the kick-off side, clears `DS:9A3E`; called once by `0791:F1F6` before `0791:F098`; calls `0791:1073`, `0791:230C`, `0791:2FB1`, `0791:A2E6`, `0791:A375`, `0791:A3B6`, `0791:A3DE`, `0791:A841` | inferred |

The match state lives in `DS:80E8..8337` and `DS:7B7E..7C3E` (`datarefs.tsv`: 59 routines refer to `DS:830B`, 27 to `DS:82F6`, nearly all in `0791`),
so the in-match code is in `0791`, but the moving simulation itself (positions of the players and the ball, marking, passing, tackling,
shooting) is **not placed**: no routine is tied to those words by a string or a constant.

## Discipline, injuries and substitutions

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:42BC` | player status words | see the squad rows: "suspended", "injured", "booked", "sent off" | observed |
| `0791:E022` | substitution rules | see the squad rows: "Illegal substitution" | observed |
| `000E:0C3A` | press text on a dismissal | strings "HACKER", "SENT OFF", "MARCHING ORDERS", "RED CARD FOR" | observed |
| `DS:04DA` | event texts | "BOOKED", "SENT OFF", "INJURED", "FOUL by", "is OFFSIDE" | observed |

Injury and suspension rules (how long, how often) are **not placed**.

## Competitions and fixtures

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:580B` | names a fixture type from its code | a chain of compares: 0 "CANCELLED"; 1 "friendly"; 2 or 5 "qualifying"; 6 "play-off"; 3 or 7 "group stage"; 0xC8 "qtr-final"; 0x65 or 0xC9 "semi-final"; 0x67 or 0xCB "final"; 0x66 or 0xCA "3rd place"; 8 "last 16"; 0xFC "fourth"; 0xFD "third"; 0xFE "runners-up"; 0xFF "winners"; any other "final round" | observed |
| `000E:60CB` | press text on hosts and groups | strings "IS TO HOST", "GROUPS ARE ANNOUNCED", "QUALIFIES FOR", "THE FINALS OF" | observed |
| `000E:5AC5` | press text on preparation and hosting | strings "PREPARE TO", "GET READY TO", "GET ORGANISED TO", "HOST" | observed |
| `1771:7A9A` | a limit on the number of games | string " have too many games arranged" | observed |
| `DS:0F5E` | competition captions | "QUALIFYING" and "FINALS" | observed |
| `DS:2D98` | tables and captions | " Qualifying ", " Finals ", " Championship ", "winner:group A", "second:group H" | observed |

## Friendlies and tours

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:7BA2` | fixture-list actions | references `DS:2020` inside " cancel match   "; the neighbours " arrange match  ", " watch match  " and " auto result  " are at `DS:203F`, `DS:206F`, `DS:209E` | observed |
| `000E:5DAF` | press text on a tour | string "TO TOUR" beside it | observed |

## The other managers

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:09A0` | a manager's name | reads and writes the 13-byte records at `[9B74]` and the initials at `[9B78]` (`mul 0xD`); a record that starts with 0 gets the text "Player" (`1771:0999`) | observed |
| `000E:0868` | the assistant, physio and coach speak | strings "Assistant says:", "Physio says:", "Coach comments:" | observed |

How the computer-run teams choose their squads and tactics is **not placed**.

## Sacking and the end of the game; the shareware limit

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `000E:5E6C` | press text on a failure and a dismissal | strings "FAIL TO QUALIFY FOR", "BOO HISS", "SACK", "GET RID OF" | observed |
| `000E:68A4` | appointment of a manager | strings "APPOINT A NEW", "MANAGER", "WELCOME", "ABOARD" | observed |
| `000E:2071` | press text on a manager's fate | strings "GET RID OF", " AND", "TRY ", "MUCH BETTER THAN" | observed |
| `DS:19E8` | the shareware notice | " GOAL  ", " NE'92 ", " On shareware. ", " register this ", " for unlimited ", " seasons with  ", " load and save ", " game facility " | observed |
| `DS:59C9` | dismissal captions | " SACKED  " and " incompetence " | observed |

Which routine shows the shareware notice, and which decides a dismissal, are **not placed**.

## Several human players

| Address | Entry | Evidence | Marked |
| --- | --- | --- | --- |
| `1771:09A0` | the manager-name table has 135 records: 128 filled in the file, 6 empty | the empty case gives "Player"; the main program reads `[A91F] + (i + 0x80) * 3` for the first `[A923]`-byte-0 values of `i` (`0000:0000`) | inferred (six human slots, records 129..134) |
| `DS:1B1C` | the player-count prompt | "How many players", "1 2 3 4 5 6  ?", "Player ", ": PLEASE SELECT YOUR COUNTRY " | observed |

## Customisation (`ALTER.EXE`) and `Y.HIL`

Not in `GOAL.EXE`. `ALTER.EXE` (25,622 bytes) is also LZEXE 0.91; `tools/static/unlzexe.py` unpacks it to 49,888 bytes
(sha256 `21f97b9d50ac89aa346dfb3de74935aa33422efce45adc1479737464d851ebc8`). Its strings include "ALTER : customisation utility", "goal.dat" and
"Do you want to save changes", and texts that are in `GOAL.EXE` ("Cannot load file", "Protect zone", "two footed", "CANCELLED").
So it is, probably, the editor of `GOAL.DAT`, built from the same units. `Y.HIL` (3,989 bytes) begins with the byte `0xFE`; its extension
is the string ".HIL" at `DS:06D6` of `GOAL.EXE`, next to the "save this goal" prompt (`0791:0C65`): it is, probably, a saved goal from the action replay.
Neither is read further here.
