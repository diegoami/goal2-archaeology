# T129p: the SELECT TEAM pool pane, 0791:E2E6

[confirmed: original `named/seg_0791_12.c:806`, `code/seg_0791_22.asm` E2E6-E44C, task #703] E2E6 is ported in `runtime/original_match/port/selection.py` as `draw_pool_view` (`ret 2`, 14-byte frame, 138 instructions). It draws the three templates, the 21 rows top..top+20 through 1771:2F37 (`A927[DS:6D18[manager] + row - 1]`), the retained-mark row highlight (214B:00DB), the two footer templates when DS:0C20 is clear, the selected pool card (DDCB, DE51, 1771:42BC) and the cursor bar (214B:13C5). All seven callees are the already registered routines; nothing else was added, and `tests/test_port_pool_view.py` is the only new test file.

[derived] The listing's arithmetic flags are tracked at each guest call (`add di,ax` before 214B:0329, 1771:2F37, 214B:00DB; `cmp byte [0C20],0` before DDCB/the footer templates; `add ax,2` before 214B:13C5), so helper-entry ALL16 includes EFLAGS.

## What the tests prove

`tests/test_port_pool_view.py` (11 tests, about 40 s):

- **Primitive, 32 cases** (16 pool-pane states x DS:0C1E in 0,1): first page, mid/last row highlight, mark above/below the window, no mark, managers 2 and 6 with bases 81 and 401, a base that wraps, empty selected word, empty row word, `top` wrapping past 0xFFFF (the `ja` skips all rows), `top` ending exactly at 0xFFFF (21 rows, wrapped indexes), `top`=0, DS:0C20=1 (no footer), a country product above 16 bits. Original (CPython/Unicorn) against the candidate in verified PyPy3.11, Unicorn and GOAL.EXE positively denied. Every original helper entry is compared first on complete memory (`MEM_SIZE`, HMA included) and ALL16, then the helper's original effects replay privately. Final complete memory, ALL16 and ordered live byte writes (outside the order-boundary frame of `docs/requests/701-order-boundary.md`) are equal. No memory mask. Complete original and candidate traces are retained in ignored `.cache/t129p-private-traces/` and bound by hash in `primitive-v1.jsonl`.
- **Falsifiers** (5, primitive and 5 again in the real flow): row index off by one, base omitted, highlight omitted, cursor bar +1, AX clobbered at return.
- **Unknown callees fail**: E2E6 alone stops at 214B:0329 (`no registered port/return`); removing DDCB, 1771:42BC or 214B:13C5 from the registry stops the real flow.
- **Code-free sealed primitive** (5 cases), exact helper replay on sealed memory.
- **Sealed REAL registered E44F pool flow** (5 flows, positively denied Unicorn/GOAL.EXE, every callee a registered port, nothing replayed): keys Right, Down, Down, Enter (marks a pool player), Down, Left, Down, Enter (swaps squad and pool), Right, Esc, Esc, for DS:0C1E 0 and 1; the same with DBFA refusing; and C1F=1 (pool unreachable, E2E6 never called). Against the original Unicorn run with identical keys: counts of E2E6 (6), DDCB (8), DE27, DE51, DEA6 (2), DBFA (1), 4E22, 42BC, 2F37, 00DB, 13C5; every DDCB return value; per key state (DS:0C1B, pool top/cursor words, E44F frame including pane and mark, the 20 squad words, pool hash); at each E2E6 return ALL16 registers and the **complete 4000-byte screen buffer**; at exit records, RNG, frame, squad, buffer, video and every register except EFLAGS.
- **Historical zero counters**: the unused E2E6 counter must be 0 before `accepted_default_fields` (T127 profile) and the T117 E034-03 drive omit it from a detached copy; any call is refused; every other field stays hashed.

## Findings to report

1. **The one registered stub reached is 1771:3947** (11 calls per flow). The reference for the buffer comparison is the original with exactly that routine returning at its entry (the registered stub). The pure original differs from it in 189 attribute bytes of the screen buffer, the same 189 in video memory (12 attribute runs on rows 11-22, 0x70 against 0x05) and 26 dead-stack bytes, **nothing else** (`stub_boundary` in `auxiliary-v1.jsonl`, `outside: 0`): the established "twelve attribute writes" boundary, here visible in the buffer after E2E6. No gameplay record, cursor, frame or RNG differs.
2. **EFLAGS at the final return of the whole E44F flow differ** (port 0x202, original 0x246); EFLAGS at every E2E6 return are equal. The difference comes from the existing E44F/1771:5532 port, outside this leaf, and is not masked: the exit comparison names the other fifteen registers.
3. Not exercised: the opponent viewer 1771:50F1 and the F2 name editor (stubs / absent, `docs/requests/701-prematch-closure.md`).

## Red before, green after

- `pool-view-before-v1.log`: first draft of the tests on the pre-change `selection.py` (calibration; later strengthened). `pool-view-before-v2.log`: final tests on origin/main's `selection.py`: 64 failures/errors, no new test passes (`KeyError: '0791:E2E6'`, `no registered port/return at 0791:E2E6`). `historical-before-v1.log` and `-v2.log`: with origin/main's T117/T127/selection tests the unused counter changes the immutable T117 digest (`d33896d9... != b08217df...`) and the inventory test fails. `focused-v1.log`: all 58 focused tests pass with the change (`tests.test_port_pool_view`, `test_port_pool_swap`, `test_port_selection`, `test_port_counter_compat_t128`, `test_port_pre_match_swap`, `test_port_assistant`). `historical-after-v2.log`: T117 drive, T127 profile and counter controls pass.
- `primitive-v1.jsonl`, `auxiliary-v1.jsonl`: receipts. `verify.py` (`verification-v1.json`) rechecks source digests, the 32 private trace pairs, that `draw_pool_view` is the only new function of `selection.py` with every other function AST-identical to the T128 merge `1bbbc2cf`, and that the T128 tests are untouched.

Reproduce: `source .cache/cloud.env`, then `T129P_RECEIPTS=<new file> T129P_AUX_RECEIPTS=<new file> tools/heavy.sh t129p -- python3 -B -m unittest tests.test_port_pool_view`, then `python3 -B experiments/E040-route-fixture-writes/out/T129p/verify.py --primitive <file> --auxiliary <file> --out <new file>`.

Model: Claude Sonnet 5.5 (claude-sonnet-5-5).
