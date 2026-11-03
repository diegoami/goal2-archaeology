# E040 route-fixture-writes

Copied from the research task's contract when the experiment is created. After the first record this file is
append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T119b (#427; goal2 #509, Track B), T118c folded in.
- **Question**: does one call of route_fixture `000E:6CA7`, run from published states, write and draw exactly what
  the static write-set says (`notes/427/writeset/writeset.json`, `sack.json`, `news.json`; T118a, T118b1, T118b2;
  F039)? Static first (rule 22): the tables are the answer; these runs only corroborate it (rule 19).
- **Hypotheses** (from the tables and F039):
  - H1: every write of the call lies in a row of the tables: its own store site, a push of a scoped routine, or the
    callee of a call row; and the row's class admits where it lands (frame: the stack; game, countries, players,
    managers, fixtures: that record; screen: the text pages; rng: `DS:7B62`; pure: nothing but the callee's frame).
    The string operations' destinations (news.json's declared limit) are checked here: a `frame` call row's callee
    writes the stack only.
  - H2: every write and visit falls in route_fixture's phase order of F039, and a sack.json or news.json row is
    reached only under the route_fixture row that calls the news (`6FD8`) or 6685's helpers.
  - H3: every row in a basic block the call entered is visited, as often as the block; no other row is.
  - H4: each rng row draws one step of `DS:7B62` per visit; no row of another class but port-owned and unread
    subtrees steps `7B62` or `8336`; the crowd animation's colour draw `04B2` follows exactly the seat tests that
    found a byte below 7.
  - H5: per fixture, F039's paths: a managed fixture is played (`6F18`), with the confidence term (`6F80`, `6F86`,
    twice each) only when its kind is not 1, the news once per managed side and `B7FA` once; an unmanaged one goes
    to `6970`, with the score page (`6A84`, `E929`) exactly when its first byte is 0xFE; 319B's win, draw and defeat
    rows follow the managed side's result; no sack where `0B77` returns 0 (season word +0x38 below 2, or kind 1).
- **Artifact**: set `goal2-67cf27d6` (the states' GOAL.EXE), read against the listings of `goal2-a949da2f`.
- **Runtime**: the route harness `runtime/original_match/route.py` (T119a) on the kit's Unicorn machine (unicorn
  2.1.4), its default key policy (a key at the first poll, Enter; N at the watch prompt; the owner, goal2 4368fac),
  the managed match by `Match(tail=False)`.
- **Design**:
  - The cases, `runner.CASES`: published states at the manager menu ("play next game" on the screen their run record
    keeps), with the next managed fixture ahead of the cursor: E006-r0001..r0004, r0006, r0007, r0009, r0010
    (friendlies after 0 to 8 silent fixtures), E015-r0007 states 26 and 213 and E015-r0009 state 3 (17 silent
    fixtures, one with first byte 0xFE, then a friendly; three silent friendlies then a qualifier, kind 2), E014-r0006's
    input (stage 3, cursor 769: 15 silent fixtures, then a friendly). Each state is fetched from its release (`--fetch`) and verified against its evidence manifest's sha256
    before it runs; the record names the hash. No state, screen or original byte is committed.
  - `runner.py --run`: one call per case, one record `runs/E040/<run id>.json` (run/1), refused on a dirty tree. The
    harness records every write, RNG step and key visit; the runner adds code hooks at every basic-block leader,
    store and call site and call return of the scoped routines (from the raw listings, with check.py's own site
    reader) and keeps the stack of active scoped calls. The record holds, per call: the visits of each site and
    leader, the route_fixture-scope sites in order, every write aggregated by (outer site, route_fixture-level site,
    innermost site, how, region), the harness's own bytes likewise, the steps of `7B62` and `8336` per visit of each
    call row and in order (runs), 045D's seat tests, the key visits, the fixtures' bytes before and after and both
    sides' country +0x2E, the harness record's counts and sha256, and whether the record replayed over the start
    memory gives the memory the call left.
  - Regions: the stack (SS = load + 0x3052, 0x4000 bytes), DS below the stack segment (`ds:<offset>`), and the
    records the far pointers `A923` (game, 0x10E bytes), `A917`, `A91B`, `A91F`, `A927`, `A92B`, `A92F`, `A933`,
    `A96A` (the video page) and `A96E` (the back page) point to, with the allocated sizes globals.tsv gives.
  - The check, `runner.py --check` (check_records.py), with no emulator: rules 1-3 are H1-H2 (the match's write-back
    lies under `6F18`, port-owned, any region), rule 4 is F039's phase order, rule 5 is H3, rules 6-7 are H4, rule 8
    is H5. Rule 2's screen class also admits the CRT unit's text attribute `DS:AAB2`, which the text routines
    `214B:0205` and `02C8` store (seg_214B_01.asm `02E6`; routines.tsv): a development run of the E006-r0001 case,
    not recorded, found news.json's screen rows' callees writing it, and their row text does not name it.
  - `--report` also writes `out/coverage.json`: per record the fixtures, their paths and the managed result, and the
    rows no record visits.
  - Stopping rule: one completed record per case; an aborted run is kept and repeated once under the next run id,
    except a case `runner.CASES` marks with a harness limit: its record must abort with that limit, once.
- **Harness limits** (found by development runs, not recorded, before the first record; route.py and match.py are
  T119a's and are not changed here):
  - Every non-friendly fixture of these calendars has its round number in fixture +1 (1..8 in E006, 6..8 at E015's
    cursor 19; 0 in every friendly), and `Match`'s fixture builder (`match.py` `_write_fixture`) writes
    `FE 00 kind 00 ...`, so the harness refuses the call at `6F18` ("Match's set-up wrote what route_fixture had not
    left there"). No managed non-friendly can be played: the E015 qualifier cases r0010 and r0011 are kept as that
    limit's records, and the confidence term is not corroborated.
  - route.py's `DEFAULT_KEYS` does not name the group-table reads `214B:157C<1771:9022`, `<1771:91BE` and
    `1771:9567` that `6970`'s score page reaches through `E929` for a 0xFE fixture; the case that reaches one
    (r0009) answers them Enter, as `Match` does (`match.py` TABLE_READS, TABLE_KEY), and its record says so.
- **Outputs**: `runs/E040/`; `experiments/E040-route-fixture-writes/out/`; F039's corroboration section.
- **Limits known before the runs**: no published state reaches a season word +0x38 of 2 or more, so no sack can
  run; none reaches the finals' kinds 0x67 or 0xCB (6685, the crowd animation's win flag) or kind 0; the cases'
  managed sides are single managers.
