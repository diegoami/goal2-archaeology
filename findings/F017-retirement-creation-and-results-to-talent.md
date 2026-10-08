# F017 Old players retire at the ageing gate (computer countries) or one at a time between fixtures (managed ones); every new player comes from make_player with ten draws per re-create; results reach the replacements through the country's ranks

- **Status**: proposed
- **Question**: How do retirements happen, how are new players made, and do results feed new
  talent? (Q014, Q04.3-Q04.7, `docs/backlog.md`; T30)
- **Tests claims**: F016's retirement test and re-create context (both kept; the re-create is now
  modelled completely, its draws included); F007's make_player and country rating (reproduced by
  an independent model, all 2560 squad and 80 pool players of a new game); F004's seeding (made
  narrower: the DOS time seeds the RNG word once per game, section Answer 4); the help file's P38
  (`GOAL.HLP` 196-205): "if you do better than expected (from your country's skill ratings),
  talented new players will gradually appear" — yes for "results feed new talent", not established
  for "better than expected".
- **Experiment and runs**: E016 (`experiments/E016-q014-retirement/`): the static map `notes.md`,
  the model `runtime/model/recreate.py`, `check_recreate.py` over the committed E014 records
  (`runs/E014/E014-r00{01..06}.json`, F016) and the tests' use of the committed E006 records
  (`runs/E006/`, F007). No new run.
- **Artifact**: set `goal2-a949da2f` for the listing; the records are E014's and E006's (set
  `goal2-67cf27d6`, variant none).
- **Max intervention**: none new (the records used were taken at I1/I2).
- **Tier reached**: V1 (rules read from the listing, corroborated on recorded games).
- **Confidence**: unreviewed (status `proposed`). Static: every claim below with its listing lines;
  `notes.md` maps them claim by claim. Behavioural: E014's 38 re-creates (every capturable byte of
  the contract; every drawn byte exactly from a recovered RNG word, one word per pair) and E006's
  new games (every byte of 2640 players). The managed path and a re-create's exact +3 are static
  only (Method).

## Answer

1. **Computer countries: at the ageing gate.** `000E:70B9` calls `1771:8208` when a stage's
   fixtures are done (seg_000E_09.asm:492), and 8208 calls the ageing `1771:80DA` on entry to a
   stage in CS:81E8 = {2, 3, 5, 7} (seg_1771_12.asm:161-163). 80DA runs `1771:7FDF` for countries
   1..128 (:20); 7FDF ages the squad, then, for a computer country only (`1771:0B77`,
   seg_1771_11.asm:1048-1050), tests each slot with `1771:7F40` (:1098) and re-creates a retiree
   in place with `1771:7E80` (:1106). 7F40 (F016): `(DS:110E[gk] < +1 AND caps word == 0) OR
   +1 > +2 + 5`, 30/33 (ds_2581_01.hex:143), strict (`7F78 jae`, `7F9D jg`), on the aged record.
   Confidence: high (static, and E014: every flagged player re-created, none other).
2. **Managed countries: one at a time, between fixtures.** 7FDF runs no test for them
   (:1050-1080). Instead the main menu's Enter on item 6 (`000E:7439`, seg_000E_09.asm:1210) calls
   `000E:57E5`, which from year 1 on (`580C`, seg_000E_07.asm:397), unless the manager's
   +0x4D flag is set (`5824`), tests squad slots 1..20 with the same 7F40 (`587C`) and else the 80
   pool players from a random start (`58AB`-`58DC`), and replaces the first retiree at once through
   `000E:56F3` (`5897`, `591B`): no step asks the user. 56F3 sets the flag (`570D`), shows the news
   when announced, takes a fresh record from `1771:4CF7` (`5745`), puts its number in the
   retiree's slot, makes it with `000E:54F0` (`57A6`) and zeroes the retiree's 20 bytes (`57C0`).
   `000E:6CA7` clears the flags at every fixture (seg_000E_09.asm:67-74): at most one per manager
   between fixtures. Confidence: medium (static only).
3. **Every new player is `1771:96D3` make_player**, with four callers (calls.tsv): `1771:97CC`
   (new-game squads, RNG word := country, flag 1, club position from DS:9F02), `1771:9873` from
   `1771:98C4` (the manager's 80 pool players, flag 0: +3 lowered by 10 + rand(10); the squad-slot
   copies' +1 = DS:118C[gk] + rand(3)), `1771:7E80` and `000E:54F0`. make_player writes +0, +7,
   +6 = +7, +5 = rand(16), +1 = DS:118A[gk] - b + a (rand(7) each), +2 = DS:0E80[gk] + b - a
   (rand(3) each, `1771:3291`), +3 = country_rating + 0x7F (flag 1), +4 (`32EB`), +0xC = rand(32),
   +0xF's bits (`1771:3431`, never cleared first), +0xD/+0xE (`1771:3558`: T = DS:0E82[+1 > +2 + 4]
   = 16/13, computer T + rand(2T), managed T + rand(3T) - rand(T + 1), capped 32, energy before
   the floor of 1) and +0x12 = 0x7FFF (seg_1771_13.asm:1107-1201, seg_1771_05.asm:243-633). It
   writes no name byte and not +8..+0xB, +0x10, +0x11. Confidence: high (static, and E006: all
   2560 squad and 80 pool players byte for byte).
4. **The re-create `7E80` exactly** (seg_1771_11.asm:872-947): make_player(1, old +7, old +0)
   (`7EA6`-`7EC0`), then +1 = DS:110C[gk] + b - a with a, b = rand(6) (`7EC7`, `7ED1`, `7EF9`;
   25/28 +- 5), `32EB` (`7F01`), +8..+0xB and +0x10 zeroed (`7F09`-`7F19`), a new initial
   DS:0C38[rand(21)] (`1771:0000`: one of "ABCDEFGHIJKLMNOPRSTVW", seg_1771_01.asm:12-17,
   ds_2581_01.hex:104-105) at `[DS:9B70]+player` (`7F2D`), and the old +6 restored (`7E9D`,
   `7F36`). The surname, +0x11 and +0xF's other bits are kept. Ten draws per re-create, in that
   order. Confidence: high (static; E014: 38 of 38, see Method).
5. **The managed replacement `54F0`** (seg_000E_07.asm:85-283) is make_player(1, retiree +7,
   country) into the fresh record with the managed fitness branch, then +1 = **DS:0x78**[gk] + b -
   a (rand(6) each; DS:0078 = 19 1C: 25/28 +- 5, `5561`), `32EB`, caps/goals/status zeroed, a new
   initial; then if fewer than 20 of the squad and pool (the new record included) have +1 <
   **DS:0x76**[gk] + 4 (DS:0076 = 11 14: 21/24, `5609`/`5689`, `56AC`), +1 = DS:0x76[gk] +
   rand(3) (18..20 / 21..23, `56D2`-`56DD`). Confidence: medium (static only).
6. **The RNG.** One 16-bit word, the one DS:A978 points to (`214B:206A` sets it to DS:7B62, F004),
   stepped by `214B:0688` as w := w * 0x7ABD + 0x1B0F and returning hi16(w * n) + 1 through
   `214B:06B1` (seg_214B_01.asm:880-911). `1771:6730` calls `23E4:11D7` (DS:7B62 := hour·256 +
   minute, DS:7B64 := seconds/hundredths) only when the year word is 0 (`675B`, seg_1771_09.asm:
   1111), and 80DA raises it at every {2, 5} gate before that transition's 6730: the DOS time
   seeds the word once per (new) game. The gate draws nothing but the re-creates' ten each, in
   country and slot order. A savestate at 80DA's entry holds the word; the E014 records hold
   none, but it is recovered from them: for each of the five pairs exactly one of the 65536
   words reproduces all the pair's re-creates (countries 1..3 draw first). Confidence: high.
7. **Results feed new talent: yes, through the ranks.** Points: +0x2F gathers weighted group
   points (`1771:61F8`, (5 - k) x points), placement bonuses 800/600/400/200 (`602D` world, `6103`
   continents, through `5FD1`) and 200 per knockout fixture (`5E3A`), reset at each recompute
   (seg_1771_09.asm:125-639, :964). `1771:63A4` (from 6730 at stages 2 and 5) sorts by +0x2F with
   `5EE1` (largest first) and writes +0x2B = world place (stage 2) or +0x2A = place in the
   continent (stage 5) (:883, :888). `1771:10E7` = ((5 - continent)(33 - continent rank) + (129 -
   world rank)) idiv 2, larger for better ranks, 1..128 in the game's domain; +3 = that + 0x7F
   for every replacement (7E80, 54F0) and +4 follows. The manager byte 63A4 also writes,
   clamp(rating + signed delta, 1, 128) (`6582`-`65ED`; delta from `0791:B6CC`), feeds match
   strength (`1771:0AA7`, F012), not make_player. Which recompute a replacement reads, by gate:
   entry to 2: both ranks from the previous cycle; entry to 3 and 5: the world rank of this
   cycle's stage 2, the continent rank of the previous cycle's stage 5; entry to 7: both from
   this cycle; a managed replacement reads the latest. Confidence: high for the chain (static),
   medium for its effect (no record shows a rank change move a +3).
8. **"Better than expected" is not in the chain.** No step reads a skill rating or an expected
   value: a country's ranks come from its points against the others' (Q04.4's "better than
   expected" and Q04.7 are not established; Q04.6's points, placements and knockout success are,
   as the inputs of +0x2F).

## Method

Static first (rule 22). The named view, then `code/`, answered every question: the gate and the
retirement path (`80DA`, `7FDF`, `7F40`, `57E5`, `56F3`, `6CA7`), every byte and draw of
make_player and its four callers, the RNG's state, writers and seeding, the readers and writers
of the ranks, and the results chain to +3 (`notes.md` sections 1-7). The listing could not say
whether the draw map is complete in its order (a missed draw anywhere would shift everything),
so the committed records were used: `check_recreate.py` compares all 300 squad words of E014's
five pairs, requires the capturable contract of every re-create (+0, +7, zeroed caps/goals/
status/+0x11, performance 0x7FFF, +1/+2/+5/+0xC/+0xD ranges, +0xE = +0xD, 3431's bits, +4 of its
own bytes, the initial's letters, the surname kept, one +3 per country) and, because countries
1..3 draw first at the gate, searches the 16-bit word at 80DA's entry: one word per pair
reproduces every drawn byte of all 38 re-creates. tests.test_model_recreate reproduces E006's
new games. Not in the records, so static only: the managed path; the exact +3 of a re-create (no
country record is captured); +6 and +0xF's kept bits of a re-create (the retiree's own bytes at
the instant, which a year of matches between captures changes: listed by the checker as not in
captures). No run was taken: a run could add a managed retirement and a captured country record,
but no claim above needs it to answer the question.

## Defects and corrections

- F004's row "6730 re-seeds DS:7B62 from the DOS time" holds for the new game only (answer 6);
  E014's notes (section 3) say "on entry to stages 2/5" (not this task's files).
- The earlier annotation of `1771:0000` ("one byte of the LCG") and round 1's chain (602D/6103 as
  sorts, a manager byte min(prior, rating), DS:0x76 as the managed age base, a user acceptance)
  are replaced here and in the annotations.
