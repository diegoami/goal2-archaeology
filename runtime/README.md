# runtime/

The GOAL2 driver (G1): DOSBox-X in WSL, headless, driven by keystrokes; screens read from text-mode video memory; savestates, and memory read from them (DOSBox-X 2024.03.01 — apt's on Ubuntu 24.04, `setup/dosbox-x-2024.03.01.sh` elsewhere, picked by `driver.dosbox_x()`, docs/environment.md — has no debugger: G1's spike reads the screen and memory from savestates). It drives the released original as a black box.

- `spike/`: T02's spike (F001), kept unchanged; its probes wrote measurements, not run records.
- `driver/`: the reusable driver (T07, F003). `driver.py` is the library (`Driver.launch(start_state)`, `keys(...)`, `screen()`, `memory(addr, n)`, `save_state()`, `restore(state)`, `terminate()`; `StartState`, `make_state`) and a CLI (`make-state title`, `read <file.sav>`); `savestate.py` parses a DOSBox-X 2024.03.01 savestate (text page and guest memory, offsets from F001; `Savestate.program()` finds GOAL.EXE's MCB, PSP and data segment, and `ds_word(off)` reads a word at `DS:off`, T08; `with_memory(data, addr, bytes)` returns a copy of a savestate with guest memory edited at `addr`, an I3 intervention for the record that loads it, T19); `cycle.py` runs restore → key → screen read → reset and writes one `run/1` record per cycle to `runs/E002/`. `match.py` plays one match from the captain screen as a quick result or watched (the starting keys in one burst, then an Enter only where the game waits for a key, until a stable full-time screen; T10, F005), and `commentary.py` reads the match commentary ring, its counter, the score bytes and the speed byte from a savestate (T10). `players.py` reads the player array at the far pointer `DS:A91B` (3061 records of 20 bytes) and the country array at `DS:A917` (129 records of 0xBF bytes) from a savestate, and `players.check` places them on known values (each country's first 20 words name its squad, each squad player holds its country in byte 0) before any field is used (T15); `players.full_name` builds the name `1771:2E93` prints from the arrays at `[DS:9B6C]` and `[DS:9B70]`, and `playerscreen.py` transcribes the player screen (name, card values, the 12 skill bars and the right panel's words and bars, which are the cells with attribute 0x70, and the tactics rows, the squad list beside the card with its colours and glyphs, and the country header) from a savestate's text page (T16).

Start states live in `.cache/states/driver/` (git-ignored) with the folder drive C: was mounted from and the drive layout the driver mounted (`drive_layout`, e.g. `mount c <game>`, `mount d <work>/dosclock`); kept copies of the states run records name live in `.cache/kept/E<nnn>/` until published. A start state a record names by sha256 is an evidence bundle (ADR-008): `python3 tools/publish_evidence.py E<nnn> --run <run_id> --file <state.sav>` uploads it to release `E<nnn>` as `<sha256[:16]>-<name>` (creating the release, never replacing an asset) and writes `evidence/E<nnn>/<run_id>.manifest.json`, which `python3 tools/verify_evidence.py E<nnn>` re-checks against the release — so the state stays fetchable after the worktree that made it is gone. A savestate holds the game's memory: release assets of this private repository only, never in the tree. `Driver.restore()`, which every restore passes through, refuses before copying the state or sending Host+L (and `launch()`, `cycle.py` and E003's `run.py` refuse earlier, before any record), a state whose layout is not the driver's or that has none (every state made before T08 rework round 4: restoring one under a driver that mounts D: stalled DOSBox-X), with a `StateLayoutMismatch` naming the state and the command that remakes it (`python3 runtime/driver/driver.py make-state title`; for E003's `main`, `run.py make-main`), after the old `.sav` and `.json` are moved out of the folder; every session mounts `scratch/driver/game`, recreated from the verified release copy. Each wait is a bounded poll or a logged key hold, and each record carries the host UTC and local time of every read. The guest clock starts from the host's unless the config sets `dos_date` (MM/DD/YYYY) and `dos_time` (HH:MM:SS), which the autoexec sets with DOSBox-X's `date` and `time` before GOAL runs (I3, T08); every launch, clock option or not, writes DOS's own `date /t` and `time /t` to a drive D: in the session folder before GOAL runs (so savestates have the same drives either way), `Driver.clock_applied` holds that read-back, and a launch whose set clock DOS did not apply raises `ClockNotApplied`; a restored savestate brings its own BIOS tick count, hence its own DOS time (F004). `terminate()` SIGTERMs the two process groups the driver started and SIGKILLs any group still alive `TERM_GRACE` (0.5 s) later — DOSBox-X ignores SIGTERM after a restore (F003) — logging each process's end method and time, which the record's log carries. `verify_release` checks `.cache/goal2` against the registered set the driver names in every record's `artifact.set`, `goal2-67cf27d6` — the successor that declares the runtime writes F001 observed; its predecessor `goal2-a949da2f` stays in `artifacts/known.json` and earlier records keep naming it (the ten files are identical). `bash setup/goal2-runtime.sh` first; then `python3 runtime/driver/cycle.py --runs 10 --start-state title`.
- `human/`: the recorder around a human sitting: `play.sh` runs windowed DOSBox-X on its own nested Xephyr display (`--res WIDTHxHEIGHT`, default 1280x800), shown on the player's display. `--self-test` checks Xephyr, xinput and stdbuf as well as the release and emulator. An XInput2 raw-key logger attaches to **only the nested display** and is started *before* the emulator is launched (no key between the two launches is lost); it flushes press/release events to `keys.jsonl` with UTC, monotonic time, keycode and the base keysym. Other applications on the outer display are not observed — the restriction is structural (the logger never opens the outer display), not a content filter; a key typed into another application while it holds the outer focus is never read, while a key typed on the outer display while the Xephyr window holds the focus is forwarded by Xephyr and is game input. A watcher stages a timestamped savestate every 20 s and 0.05 s after each settled key episode
(the scheduling quiet `EVENT_SETTLE_S`; the 0.5 s `BURST_QUIET_S` is the grouping quiet the map
reads), on a capture pipeline off the loop whose fast path takes the kernel's inotify
write-event count as the write-completed evidence when burst requests overlap — every other
gate check (fresh signature, no open write session, event-count bracket, zip validation) is
unchanged. Each request owns its savestate bytes: a job whose live savestate advanced by more
than one save's write events since its request was sent (one real save is ~53-54 events,
`evidence/E015/T34-probe-closes-20261009-01.log`) is marked superseded at every poll, accepted
bytes are re-read from a per-request path (`requests/rq-<n>.sav`, the single staging source),
and a fast job never stages a merely stable live file; the acceptance guard requires that
write accounting (`pre_events`/`accept_events`) on every staged request line. Save keys use explicit window-targeted XSendEvent, so they cannot recursively trigger raw-input bursts. All captures use T29's same stability, zip and inotify gate, with one staging writer; a snapshot's screen is bracketed by its save-request window (`request_s`..`sent_s` + 50 ms delivery margin, see `experiments/E015-human-playthrough/T34-probe-20261009-05.log`), not by its staging time. Optional video films the game window on the nested display (mkv, `-flush_packets 1`, SIGTERM-finalized). Sessions live in `scratch/human/sessions/` (git-ignored; keys and savestates never enter git). `experiments/E015-human-playthrough/extract.py` creates one new immutable `run/1` record per sitting, carrying the screen/key map as a JSON observation; `keymap.py <session>` only prints the map's summary and readable table (one record per sitting: extract.py's). `--scripted-keys` is an explicit opt-in for acceptance sittings only, never for the owner's play. See `experiments/E015-human-playthrough/protocol.md` for the protocol and coverage map.
- `model/`: the engines as read from the listing, each constant with its listing line. `quick_engine.py` models the quick-result engine seed-exactly (T23/T24, F012); `ratings.py` models the performance ratings (T26, F014); `keeping.py` is where keeping and penalties are read (T27, F015): the twelve-skill derivation `1771:3A06` (the screen's `3947` with divisor 32 instead of 256), the engine's one skill reader `0791:278A` with its form/energy blend and the element-12 penalties bonus, and the I3-edit predictions the E013 records check (`experiments/E013-q012-keeping/check_keeping.py`); `ageing.py` models the yearly ageing loop (T28, F016): the per-player writes of `1771:7FB1`/`7E4A` (+1 age, +4 ability through `1771:32EB`'s five-age maximum around the peak age, +0x11 cleared), the deterministic retirement predicate `1771:7F40` on the aged record, the derived-skill consequence, with the E014 records checked by `experiments/E014-q013-ageing/check_ageing.py`; `recreate.py` (T30, F017) models every new player: `make_player` (`1771:96D3`, each byte and draw in order through the RNG word `214B:0688`/`06B1`), its four callers (`new_game_squad` `1771:97CC`, `managed_pool` `1771:98C4`, `recreate` `1771:7E80`, `managed_replacement` `000E:54F0`), `country_rating` (`1771:10E7`), the re-create's complete contract in range form (`recreate_contract`, with what year-apart captures cannot show in `NOT_IN_CAPTURES`) and F016's reduced `recreate_constraints`, which `ageing.py` re-exports for both import styles; `experiments/E016-q014-retirement/check_recreate.py` checks the E014 records' 38 re-creates, exactly from a recovered RNG word.
- `emul/`: the Unicorn emulation harness (T25, F013). `watched.py`'s `WatchedHalf(savestate_bytes).run()` emulates one watched half from a half-time team-screen stall savestate as real guest code — `0791:983F` whole: its head, the tick loop `0791:97D0` with the watched engine `0791:9564`, `8CF5`, `9119` and the clock — with the `9A32` tail's two resume writes applied first (the kick-off slot as a ONE-byte `9AFC` store, its side base read from `DS:0668`), interrupts swallowed, the BIOS key thunk `214B:0723` stubbed "no key" and the unreachable-from-the-match `000E` wait family skipped behind a stray log that must stay empty (T24's `emu_full_loop.py` mechanics, generalised). `draws` records every main-seed `214B:0688` call with the match minute and sub-tick (`DS:831F`, `DS:831D`); `tick_values()` turns them and the `970C` entry marks into the (minute, sub-tick) → seed-value sets the ground-truth reads are checked against tick-exactly (`experiments/E011-q010-watched-engine/emu_check.py`, E011 notes.md §6). `watched_match.py` (T38, M0) runs whole watched matches: `Guest` is a Unicorn machine resumed from a savestate's own CPU state (registers, flags and segments from its `CPU` component, layout calibrated in E021 notes.md §1) with `hook(address, fn)`, which substitutes a routine — `fn(guest)` runs instead, the guest returns as the routine's own `ret`/`retf n` (read from its listing block), the routine's code never runs, and each call is counted in `hook_counts`; `WatchedMatch(watchstart_bytes).run()` resumes an E011 captain-screen state before the kick-off and runs the original to the full-time board as guest code (both halves, the half-time board and team screen answered with E004's Enters at their declared reads, any other key read voids the run), with declared input writes (`set_seed`, `set_country_tactics`, `set_player_bytes`, `set_squad`, `set_delay`; recorded in `inputs`), every write of the seed word with the clock (`draws`, `tick_values()`), and `outputs()` (score, scorers, man of the match, the board's raw counters, the commentary ring, the board screen). `experiments/E021-m0-whole-match/check.py` checks it against E011's every read (E021 notes.md).

- `original_match/`: the kit for goal2 (issue 250, E033): the original's watched friendly played interactively
on an image of the original outside a match (goal2's own savestate form), self-contained (the standard library
and unicorn, no byte of the original; goal2 vendors the folder). `Match(image, Fixture(first, second, index),
managed=...)` enters `run_match` `0791:F1F6` with route_fixture's own frame and then the post-match update
`0791:B7FA`; `events()` yields the match as it happens (minutes, the original's commentary lines, goals, cards,
injuries, substitutions, the boards) and stops at the original's own decision points (half time, the substitution
notice after an injury or a request, a pause asked for with `pause()`), where `answer()` takes substitutions,
tactics, positions, man-marking, a player's own tactics, the quick result and the speed and presses the original's
keys for them (screens.py, closed-loop on the screens' state); `save()`/`Match.load()` stop and resume a match
exactly. `python3 -m original_match.check` is the check (E011-r0001's match as E021 recorded it; `--family` E032's
ten seeds); `README.md` there is the page for the goal2 session.

`model/energy.py` supplies instruction-path transformations for the player record's
+0xC/+0xD/+0xE: one quick slot visit, one watched activity-counter tail, the
post-match copy, and 1771:3651's draw-dependent fitness update. It requires the
actual activity counter, ordered recovery draws and DS:0E84 cap bytes; it does
not simulate movement, substitutions, complete quick matches, injury causes or
morale outcomes. Its form-delta and injury-store helpers account for already
established stores when replaying a watched-half transcript. The E017 checker
compares all three bytes by player word and rejects absent draws, unknown stores,
missing final players and an empty comparison set. E017's notes describe the
transcript formats and their evidential limits.

F018 settles fitness as +0xD and expendable energy as +0xE. The watched
counter measures active updates (direction <5), not a role/marking weight;
substitutions reset the pitch counter but do not refill the incoming player's
energy. The pre-half +2 step precedes E011's team-screen input. The helper's
recovery path is 1771:3651, not 3558's separate redraw selected by other caller
branches. See `findings/F018-energy-is-expended-in-matches-and-restored-from-fitness.md`
and E017's reader/writer inventory for the exact gates and limitations.

`model/confidence.py` (T32, proposed F019) models the country-rank-derived
result term, signed per-call confidence clipping, exact or draw-dependent
bench outcomes, and live/saved watched form writes. It does not infer a
watched event sequence from the final score: callers supply that sequence,
pool draws and silent-route scorer bonuses in order. E018 checks original
B7FA probes by player word, retaining its defective probe only after its
own declared-input consistency check fails. See
`findings/F019-confidence-follows-result-relative-to-country-ranks.md`.

`model/morale.py` (T33, proposed F020) models the writers outside
F019's result rule: `0791:7CC5 adjust_player_form` (named `event_clamp`
with a [1, 255] clamp on the live byte and an optional DS:9B07 write
when the persist flag is non-zero) and its five callers — the scorer
`0791:6443` (s8(DS:0x7920[side_of_credit]), persist True), the team
reaction `0791:65FE` (s8(DS:0x7920[side_of_ball]), persist False), the
sending-off `0791:7B77` (the sent-off player push 0xfffe with flag 1,
the OTHER team's available pitch slots push 2 with flag 0), the injury
`0791:7D56` (push 0xfffe with flag 1; the +0xE := 0 injury store is
F018's), and the team aggregate `1771:13D0 team_panel_aggregate`
(`team_panel_morale(starters)` = `max(1, ((6 + sum_of_min(32, s8(+0xC)))
over the 11 available starters) & 0xFFFF) // 11)` — no lower clamp on
the per-starter contribution (a -128 signed byte contributes -128; the
`add word ptr [0x9B5A], ax` at `code/seg_1771_02.asm:1067` wraps mod
0x10000; the `div cx` at line 1093 is the 16-bit unsigned divide) —
recomputed every `1771:157D draw_team_panel` render and never
persisted. The yellow-card routine `0791:798D booking` does **not** call
`7CC5` and so does not write +0xC by these lines — the help claim
"booking damages confidence" is not established by the listing; the
help claim "injury and sending-off damage confidence" is established.
The helper does not choose call order: callers pass the events in
match order. E019 checks 22 literal-input probe cases by player word
(13 `7CC5` cases covering the named deltas, clamp boundaries and
signed-byte edges; 9 `1771:13D0` cases covering the seed, divisor,
floor and signed-byte clamp); the probe generator does NOT import
`runtime.model.morale` — `expected_*` are LITERAL ints (hand-traced
from the listing, R1) and `got_*` come from a separate call to the
module's listing-arithmetic helper; the checker verifies the model's
output equals both. `mutations_morale.py` shifts each of the 9 numeric
constants by +1 and -1 and deletes each of the 5 named helpers,
rerunning the unit suite in a fresh subprocess — 23/23 mutants
killed. See `findings/F020-events-change-confidence-and-team-morale-aggregates-it.md`
and E019's `notes.md` for the inventory, listing lines and the booking
limitation.
