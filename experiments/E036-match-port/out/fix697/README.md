# Live TEAM context snapshot (#697)

[confirmed: F037; original1771:157D 1892–18AE] Performance visibility uses
both raw DS:0C1E/0C1F bytes; side selection reads DS:9B34/9B36. The existing
live_players opt-in now includes team_context {match_set_up, in_match_menu_used,
sides}, with raw byte integers and two country words. The default/False profile
is unchanged. Saved old waiting packets can omit context; consumers must retain
an explicit fallback until a newly produced decision supplies it. No new option,
formula, port body, guest write or table change.

Baseline c6a5e113. before-v1.log retains an invalid decoder import calibration
and duplicated imported test collection, not acceptance. before-v2.log uses the
correct decoders import and five own tests: the new packet/freshness/checkpoint/
visibility controls fail; legacy omission passes. after-focused-v1.log runs29
controls (five own plus unchanged682/695/663) successfully. Synthetic raw flag
corners and swapped side words are boundary controls, not natural game claims.
The first cheap synthetic run used a private limiter directory; subsequent tests
use the repository shared heavy limiter. No overlapping match job was started.

proof-v1.py extends the accepted682 producer without deleting its oracles. It
independently reads context at every real decision in each backend, compares
legacy and opt-in full results/full physical memory and exact event streams
with only independently sampled record/context additions, and verifies actual
checkpoint load equality. Original/port comparison retains the existing display
profile and accepted state ranges; raw hashes remain visible and are not claimed
cross-backend identical when they differ. Original data is private; public
receipts contain only filtered identities/hashes and small context fields.

Natural producer receipts, final source identity and hosted CI are still required
before merge. Historical682/695 proof outputs remain immutable. Full suites are
left to integrated milestones; focused proof is required for this addition.
