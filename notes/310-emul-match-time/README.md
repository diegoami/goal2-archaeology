# #310 items 1 and 2: the time of test_emul_match

Machine: Intel Core i9-14900HX, 32 threads, WSL2 (the author's); each run through `tools/harness/heavy.sh`, one at a time.
Logs here are raw and never overwritten.

| file | what |
| --- | --- |
| before-proved-test.log | the old test's body (now `test_the_gate_falsifier_proves_on_e011`), alone: 172.8 s. A first run of the same test on the unchanged `main` file, 229.5 s (printed in the session, not kept), the machine being busier. CI's runner: 361 s (notes/T304) |
| after-fast-test.log | the new `test_the_gate_falsifier_is_not_reached_by_e011`, alone: 33.2 s |
| after-module-pull_request.log | the whole module with `GITHUB_EVENT_NAME=pull_request` (the proved test skipped): 67 tests, 45.0 s |
| mutation1-fast-gate-reached.log | `KEEPER_EVENTS` = {1, 3, 4} in runtime/model/keeping.py (a gate E011 does reach): the new test FAILS (event 1 is in the set) |
| mutation2-proved-gate-1.log | the proved test with gate {1} instead of {0x18}: ProofError at call #6685 of 0791:278A (AX original 0x44, model 0x82) |
| mutation3-observer-sees-nothing.log | the new test's observer looks for element 99 instead of 1: FAILS (`{}` != `{1: 13}`), so the test is not vacuous |
| ci-run-39112415524-emul-test-lines.txt | the CI run of PR 329 (first push of the change): the module's lines with the runner's timestamps; the new test took 28 s there, the module about 36 s (08:43:44.6 to 08:44:20.9), against 361 s and 376 s |

Also measured (not kept as a log, scratchpad scripts): the whole E011-r0001 match unhooked takes 4149 ticks; the 278A calls of the
first 3000 ticks are 28,055 (elements 5 and 8: 13,529 each); element 1 is called 7 times in them (first at tick 710) and 13 times
in the whole match, always with DS:8327 = 1 and a non-zero pitch +0x11; the plain 3000-tick run takes 35.5 s, the same run with
the hook substituting without a proof 35.6 s: the proof, not the run, is the 195 s.
