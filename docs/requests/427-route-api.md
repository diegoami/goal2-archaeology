# Sealed round consumer seam

[designed: main,2026-11-07, within owner-authorized T123/#427 scope] This fixes the technical interface before implementation so goal2T170 can keep one round continuation in its existing engine process. It adds no player selection policy or annual-rollover support.

`play_round(state, tables, keys)` returns a `RoundStep` (a public immutable container with attributes):

| Field | Meaning |
|---|---|
| `status` | `match`, `complete`, or `deferred-rollover`. |
| `state` | Current real state/2 value, with no opcode bytes; usable through `Image.from_state`. Input state/tables are not mutated. |
| `played_fixtures` | Ordered completed fixture/result records accumulated during this round call, including across its resumes. An unfinished match is not counted. |
| `news_pages` | Ordered actual `NewsPage` captures accumulated during the call, including repeated equal-looking pages and pages overwritten later. |
| `match` | Only for `match`: an actual ordinary `Match` using the port engine with `tail=False`, not the comparison harness's `RouteMatch`. Its normal `events`, `answer`, `result` methods are the player's match interface. |
| `continuation` | Only for `match`: opaque in-process round continuation, owned by the existing engine worker. |

`resume_round(continuation, match)` accepts only that continuation's completed pending match, restores its exact returned effects and advances to the next `RoundStep`. An incomplete/foreign/repeatedly consumed match refuses before route-visible mutation. An unfinished match's continuation is in-process; this task does not claim serialization/migration of an active round. Completed states remain real state/2 values. Other observational fields may be added without changing these meanings.

`keys` follows the existing Route key-policy contract, including queued/pushed-back context. Unknown reads and unsupported pool-list operations refuse explicitly. Production never invokes the harness legal-eleven policy. The E040 comparison runner may explicitly supply T124t's original-menu policy to both arms; this is proof input, not a player-flow default.

The managed match enters at the real F1F6 far-call frame (SP3EC0/BP3EDE, callerSS), with no repeated fixture/setup/RNG changes. Its result must return the exact effects at6F1D/SP3EC8. Original route post-match updates remain route-owned and occur once. All constructor/return invariants must be checked against the actual incoming frame, not normalized away.

After final results/8757/news, cursor=count/rounds1/stage4or8 yields `deferred-rollover` BEFORE70E6. Round/stage and all final effects remain intact; a fresh call on that terminal state returns the same boundary before any new route/kit write. The guard also covers70B9's Python guest-call path, which bypasses ordinary guest hooks. Supported2→3/6→7 transitions still execute real ageing/builders.

T123's consumer document `427-route.md` explains the delivered API and proof limits. Main owns process§14's separate goal2 register/handover/issue delivery; the upstream implementer does not change the active goal2 UI checkout. Whole combined upstream milestone validation and owner-run review precede T170 adoption.
