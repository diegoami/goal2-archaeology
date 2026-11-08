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
