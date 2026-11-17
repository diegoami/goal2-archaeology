# Optional extended-roster planning

[designed: owner2026-11-18, goal2#777; T138a/#727]
`ExtendedRoster.from_squads(core, pool, extras)` describes the current native20
and up to4 additionally selected made-pool words. It is immutable and detached.
`bench(core)` returns the current native bench followed by selected members
outside that native twenty. A displaced ordinary bench member remains selected.
`promotion(word, core, pool, unavailable=())` returns native squad/pool indices
and the incoming/displaced words; it never executes or writes anything. It
prefers the last explicitly unavailable native bench member, otherwise the last
native bench slot, preserving the XI and total selected membership.

`replaced(off,on,current_core)` updates selected membership only for a completed
ordinary external recruitment witnessed in the current native twenty. Within
selected membership it retains the same plan. Invalid sizes, exact-ID types,
uniqueness, stale core/pool domains or replacement evidence raise before mutation.

This is a designed optional22/24-player consumer capability, not an original
larger-squad rule. The original country/pool binary layout remains20/80. Actual
Match integration must validate and record public extended-bench inputs, expose
all selected players/cards, preserve original substitution/status/budget behavior,
and support native/held entries and save/replay. No consumer may patch guest
memory or finals flags. Default Match behavior is unchanged in this planning leaf.
