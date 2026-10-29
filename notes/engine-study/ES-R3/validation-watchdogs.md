# Full-match verification allowances

[designed: #605] The knockout regression explicitly allows 600 seconds for one
stretch in each compared engine. The positive-Unicorn-denial child allows 1800
seconds for its entire reference match. Both remain bounded. Production Match
keeps its public 60-second stretch default.

The two full-CI attempts at b46ce1e0 recorded in
validation-watchdog-failures-v1.json did not complete under the inherited 60-second
knockout stretch limit. The second also exceeded the complete-match child's
600-second limit. Earlier local T78b controls completed the knockout pair in
1346.3 seconds and the denial match in 317 seconds. These observations justify
explicit allowances for slower CI hosts; 600 and 1800 are designed verification
budgets, not performance guarantees or scientific measurements of engine effects.

The fix changes only those two test allowances. It preserves the admitted
fixture, policy, event/result/whole-memory comparisons, required extra time and
shootout, positive import denial, and exact score/tick/draw assertions. It adds
no test skip, retry loop, engine change or scientific invocation. The inherited
600-second Machine/family allowance is an existing verification precedent, not
proof that this test will finish within it. A continued timeout remains a failure.

Local logs and source/exit receipts use new filenames and the existing T78b
run_control.py harness. Its job prefix is historical; these are #605 regression
checks. GitHub remains authoritative for task, PR and milestone status.
