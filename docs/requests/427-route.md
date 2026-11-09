# Sealed round continuation

The consumer interface is pinned in [427-route-api.md](427-route-api.md).
`original_match.route.play_round(state, tables, keys)` accepts an existing
`original_match.state/2` value and verified `Tables`. It returns a frozen
`RoundStep`. The caller retains ownership of its input state and tables.

| Status | Caller action |
|---|---|
| `match` | Drive the ordinary `Match` through its existing `events()` and `answer()` interface, then pass that completed object and the supplied continuation to `resume_round`. |
| `complete` | The current original70B9 call returned. Persist `state`; the calendar may contain further fixtures for later calls. |
| `deferred-rollover` | Persist the terminal state. The annual transition is outside this interface's supported scope. |

`played_fixtures` contains completed fixtures in execution order, including
silent results before a managed match. It excludes the pending match until its
result and original route updates complete. `news_pages` contains immutable
`NewsPageMemory` snapshots at actual05F6 entries, preserving every page in order,
including equal-looking pages and pages later overwritten. Decode their text
through `original_match.news.news_pages`; the original cells retain attributes.

A `match` step supplies an ordinary `Match(engine="port", tail=False)` at the
actual F1F6 entry. Its incoming memory, manager identities, RNG and complete CPU
context are retained. The caller decides its team and match actions through
normal Match operations. The legal-eleven policy used by the comparison harness
is an explicit proof input. Production installs no automatic player-selection
policy. Unsupported pool-list operations refuse through the existing squad-menu
boundary.

Keep the continuation in the same engine process. `resume_round(continuation,
match)` accepts only its own completed pending object, validates its actual
6F1D/SP3EC8 return frame, and executes the remaining original route updates once.
Incomplete, foreign and already-consumed requests refuse before route-visible
changes. Active round continuations have no serialization contract.

The key mapping uses the established Route key sites and waiting-key semantics.
A `Keys` object can carry one waiting key across calls. Unknown reads refuse.
Completed news snapshots preserve queued/pushed-back context. The route owns
post-match result, confidence, news, fixture advancement and8757 finalization.

When the finalized cursor equals the calendar count, rounds is1 and stage is4
or8, the interface yields `deferred-rollover` before70E6 calls stage_end. It
preserves final fixtures, pages, rounds and stage. A fresh call on that terminal
state returns the same boundary before new route or delay-calibration writes.
Required2→3 and6→7 transitions execute their in-season ageing and builders.
Year rollover remains outside the supported production route.

Task-owned comparison sources and immutable measurements live under
`experiments/E040-route-fixture-writes/out/T123/`. Raw original game memory stays
in ignored private caches. The production backend consumes state and tables
through `PortMachine`; original reference executions belong to the comparison
harness.

## Configure the held Match before execution (T127)

`step.match.configure_route_entry(*, captain=None, substitutions=None, ticks=False, record_draws=False, set_piece=False, live_players=False, substitution_control=False)` configures the same actual F1F6 object exactly once. Supply final choices together before the first event-iterator advancement or replay-origin capture. Creation itself retains the old defaults; failed validation consumes nothing. Exact booleans, a current managed-XI captain and detached0..255 budgets are validated before changes. No guest memory, register, fixture, setup or RNG write occurs during configuration. A deduplicated draw recorder is installed independently of existing hooks when requested. Ordinary/loaded/changed/started/already-configured targets refuse. No seed, delay, player-record, engine or tail option is accepted; no active-round serialization is supplied. Drive normal events/answers and return this exact completed object to resume_round.

## The manager menu's Play action as a route entry (T130, #705)

`Route(image, entry="play_action")` is a third entry of the comparison harness (`ENTRIES = ("route_fixture",
"play_round", "play_action")`; the first two are unchanged). One `call()` is one press of the manager menu's Play action,
run by `main_menu_loop` 000E:7439's own code: the Enter branch of item 6, from 000E:772A to 000E:77CB. The entry site is
neither 57E5 nor 77BF: 77BF is the branch's last step and 57E5 its second. The branch is, in the original's order:
`7072` (always 0 in this build); when the manager's byte `[A923]+0x47+m` is clear, `57E5(country)`, whose return of 1
ends the press, then `5CF4(country)`, likewise; then `play_round` 70B9 when the current manager `[A923]+1` is the last
(`[A923]+0`), else the next manager. The frame, the BP chain and every address are in `route.py`'s docstring, with the
disassembly lines they rest on.

**One press is not "pre-step, then play_round".** In the original a press whose 57E5 replaces a retiree (000E:56F3: the
retiree's 20 bytes zeroed, a fresh record in his slot, the flag `+0x4D+m` set) returns 1 and ends there, with no
`play_round` and no fixture routed; the next press finds the flag set, 57E5 returns 0 and the round is played (checked
by `tests/test_play_action_entry.py`). The harness makes no decision of its own: `call()` is one press, `round()` repeats
presses until one reaches the round's end, and the record carries `("action", name[, AL])` at each decision of the
original's code ("retirements", "finals_news", "play_round", "next_manager") and `("return", "000E:77CB")`.

**Not in the sealed API.** `play_round()` and `resume_round()` are unchanged and there is no sealed play-action: the
`PortMachine` refuses an unregistered address, and 000E:57E5, 56F3, 54F0, 544D, 50D4, 5CF4, 5AC5 and 1771:1B2E, 4CF7
have no port (`tests.test_play_action_entry.PortGap`). The entry exists for the comparison harness, on the original under
Unicorn.
