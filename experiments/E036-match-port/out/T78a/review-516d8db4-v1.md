PR #563 review (Codex, GPT-6)
approve after named fixes — R1

DW1: ran `PYTHONPATH=runtime tools/heavy.sh review563-dw1-literal -- python3 -B -m unittest tests.test_port_machine` → 10 PASS. Independently reran all 10 against aa928292: 1 failure/9 errors. Temporary source mutations detected 7/8 regressions; saved contents restored.
DW2: ran the existing guest/proof/runtime controls → 143 PASS; `unittest discover -s tests -p 'test_port*.py'` → 700 PASS; `tools/ci_gate.py run-tests --modules=test_e036_compare` → 1924 PASS, 17 environment skips. All ran through tools/heavy.sh; regressions used Python 3.12. Exact-head [CI 40509724056](https://github.com/diegoami/goal2-archaeology/actions/runs/40509724056) succeeded.
DW3: ran `git diff --name-status origin/main...HEAD`, audited both commits' output histories and scanned tracked original-file extensions → all changed paths owned; all 11 output files newly added, never subsequently edited; no original-game files committed. Checkout unchanged at 516d8db4e0add877d97b358b1b995c431bc6f8ec.

R1 runtime/original_match/port/engine.py:86 — IP/FLAGS aliases differ from the existing Machine register API. Independently reproduced on both backends: `set_reg('eip', 0x12345678); set_reg('ip', 0x9abc)` leaves EIP=0x12349abc here versus 0x9abc in Machine. Likewise `set_reg('eflags', 0x200002); set_reg('flags', 0x202)` leaves EFLAGS=0x200202 here versus 0x202. The generic merge retains upper bits these two reference setters clear, contradicting the promised register-contract preservation and producing different snapshots. Match those setters and add independently labelled representation controls. (blocking)

R2 tests/test_port_machine.py:85 — Deferred-return replay coverage misses the destination callback. Removing engine.py's `no_replay_at` assignment still passes all 10 tests. Adding a handler at 0791:0110 exposes the difference: current code reports replay=False; the mutant reports True. Add that assertion so this stop/resume guarantee is protected. Current implementation passes the stronger control. (not blocking)

Final pass done
approve after named fixes — R1
