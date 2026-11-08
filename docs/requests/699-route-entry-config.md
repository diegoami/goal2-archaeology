# Upstream request from goal2 T170/#566: configure the actual held route Match

Suggested title: Support strict pre-execution configuration of a sealed round's held Match
Task: T127; upstream #699.
Importance high: required consumer compatibility for accepted round delivery427/681, downstream goal2T170. Cost bounded: one facade/lifecycle slice plus focused proof and documentation. The main-authored T127 task governs implementation and validation.

[confirmed by accepted source c6a5e113] route.play_round/resume_round already preserve the actual ordinary Match at F1F6 and route-owned return processing. Match.from_route_entry(image,fixture,context,*,managed=None,timeout_s=600) hardcodes captainNone/substitutionsNone/ticksFalse/record_drawsFalse, omits set_piece/live_players/substitution_control and offers no supported configuration method. Goal2 must preserve its existing chosen captain, declared substitution budgets, prompt interface and BOTH live-player/substitution-control flags without constructing another Match or replaying F1F6 setup.

[confirmed by match.py:_hooks] record_draws is construction-sensitive: its RNG write recorder is conditionally installed by _hooks. Setting opts after construction does not install it. _hooks also installs unrelated sites/watchers and must never run again to solve this. Most other requested flags are read dynamically at later original sites. This is an API/configuration correction, not new original rules or a new formula investigation.

## Proposed exact API (one surface, no play_round signature change)

    step = play_round(state, tables, keys)
    assert step.status == 'match'
    step.match.configure_route_entry(
        captain=chosen_word_or_none,
        substitutions=budget_or_pair_or_none,
        ticks=True, record_draws=False, set_piece=True,
        live_players=True, substitution_control=True,
    )
    # Drive THIS object through normal events()/answer(), then:
    step = resume_round(step.continuation, step.match)

The method accepts keyword-only fields. It is valid exactly ONCE on an unstarted object created by from_route_entry. It returns None, changes Python configuration only, and leaves the route's pending object identity intact. An ordinary constructor Match(tail=False), subclass, foreign object or loaded match is not an entry-configuration target. Initial factory creation stays byte-for-byte/default-option compatible. Immediate configuration after creation and delayed configuration while the caller selects a captain are equivalent if no guest/replay execution intervenes. There is no separate creation-kwargs or late-captain API; all final choices arrive together just before the first event iteration. This avoids passing season-wide captain words into future different squads and avoids mutable option dictionaries stored on the round controller.

Calling events() merely constructs a lazy generator; define start at its first advancement, before _replay_start captures an origin, even if no event has yet been yielded. After any guest advancement, replay-origin capture/start, decision, live frame, completion or accepted configuration, configure_route_entry refuses before changes. The guard must bind the real original entry identity/frame and ownership, not only st['fresh'], event/tick counts or overFalse. Reading memory/result accessors is not guest execution; active-round save/load remains unsupported. If a public operation captures a replay origin before execution, configuration after that capture refuses; never rewrite an existing replay origin to hide different options. Do not add a checkpoint/round-serialization contract.

## Strict fields and atomicity

- Boolean fields ticks, record_draws, set_piece, live_players, substitution_control accept exact bool only; reject0/1/None/string. Preserve legacy optionalFalse omission; existing ticks/record_drawsFalse keys remain as factory defaults.
- captain is None or exact int in1..3060 belonging to the CURRENT managed XI, with a managed participant; reject bool, out-of-XI/foreign/zero words. Use the existing constructor's membership rule, not a new availability/player-selection policy.
- substitutions is None, exact int0..255 for both sides, or a two-element list/tuple of exact ints0..255. Normalize to a detached two-item list. Reject bool, negative,256+, bad length/type; external mutation cannot change accepted options. None retains the original's budget. Actual override still occurs only at the existing on_play setup-complete hook; configuration itself writes no budget bytes.
- No seed, reference_seed, delay_byte, players, countries, managed, fixture, index, engine, tail, ports, prove, arbitrary opts or unknown keys. In particular no tailTrue or setup reseed. Existing ordinary constructor/default behavior remains unchanged.
- Validate ALL arguments, target/lifecycle/frame and captain membership before changing opts, configuration marker, replay bookkeeping, handlers/listeners, CPU or memory. A failed call consumes nothing and leaves a valid later configuration possible. A second call (including identical/no-op) rejects atomically. A successful all-default call consumes the one supported configuration opportunity without changing default opts/events/memory.
- Extract the existing draw-recorder installation into a deduplicated helper shared by initial _hooks and this method. For the route defaultFalse→configuredTrue path, install exactly one recorder before execution; never rerun _hooks, add duplicate RNG/tick/event listeners or replace the machine. One-shot configuration avoids needing later recorder removal or flag toggling. Preserve existing ordinary constructor recording/checkpoint behavior.

## Required evidence and delivery

Controls must fail on696 before implementation. They cover every invalid field and mixed valid+invalid arguments, no target changes on rejection, immediate/delayed valid configuration equality, lazy-generator versus first-advancement boundary, repeat/ordinary/started/completed/loaded targets, captain current-XI validation, caller-list detachment and legacy omitted/default profiles. Compare complete incoming memory, all16registers, opts/state/inputs and installed-handler counts for purity/duplicate detection.

A fresh actual route entry, not a fabricated frame, runs through the configured object with real captain, budget and prompt/decision behavior. At least one recorded run uses record_drawsTrue and independently observes the actual ordered7B62 writes through the existing recording interval, proving no missing/duplicate draws/digest; a matching false/default arm proves no recorder/event extension accidentally enabled. Use the same options and original-key answers in original and port reference arms; all previous result/events/RNG/full-memory/ALL16 return and route update assertions remain. Enabled read-only fields must match actual decision memory. Exercise BOTH flags together, requestTrue→False and actual timed opportunity acceptance without an early player pair; retain original legal-stop rules and full result equality. Seed/timing overrides are forbidden for these route configuration inputs.

Use a real denied PyPy route worker with positive Unicorn/original-file tripwires and source-bound receipts; production invokes no RouteMatch legal-eleven policy. An explicit original-menu selection script may be shared by both proof arms and must remain a declared test input. Preserve foreign/incomplete/consumed resume purity and actual6F1D/SP3EC8/ALL16 transfer before route-owned B7FA/8757; no duplicate updates. Retain immutable failed calibrations separately from passing final-source records. No new memory mask or weaker old assertion.

Own runtime/original_match/match.py, tests/test_route_entry_config.py, docs/requests/427-route-api.md and427-route.md (plus README only if directly made wrong), and experiments/E040-route-fixture-writes/out/T127/. No goal2 consumer source or port body/table/formula changes. Upstream697/698 live TEAM context is Track A's independent work: preserve its eventual accepted fields, do not implement/duplicate/adopt its unaccepted head. Normal merge conflicts in match.py need exact-head focused revalidation, not overwriting its other changes.

Main supplies contract, clone/branch release and issue509/upstream status. Implementation commits/pushes each evidence batch, records actual model, leaves full suite to CI, starts no reviewer. Goal2 adoption happens only after live accepted merge/head/check/blob verification and deliberate byte-copy/provenance update; this request alone is not acceptance of new source.
