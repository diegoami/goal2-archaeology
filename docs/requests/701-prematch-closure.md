# T129 static closure audit

**Recommendation:** add one bounded **E2E6 pool-view state/ABI leaf before interactive pool actions**. T128 closes swaps/indexing, not the E44F pool screen. Explicitly bound original-name/opponent-view behavior before releasing T129 leaves; do not infer those paths are implemented from existing stubs or fake-call tests.

Sources: accepted main `763a5f744447bd33f971c0a25a93f235e83b72b2`; tested, still-unmerged T128 candidate `97f4f4958b73a1f3870539418bca380a5dec0e90` supplies DDCB/DEA6. `git diff --name-only <main> <candidate> -- runtime` shows only `port/selection.py`, so other inspected port bodies/stubs are byte-identical to that accepted main. Primary reference remains `46e0043e89de2799272addad2b99017cb259302c`. Inspection used source/listings and Python-B registry loading only: no engine, gate, source/ref/evidence edit or review. Snapshot aids: `/tmp/t129-registered-entries.json`, `/tmp/t129-static-call-closure.json`, `/tmp/t129-missing-static.json`. These are static dependency aids, not execution receipts. Model: Codex GPT-6 family; exact variant unavailable.

## Required action map

All `port/` citations below refer to `runtime/original_match/port/`.

| Path | Registration and closure | Consequence |
|---|---|---|
| Managed players: ED8A→E949→E44F | All real (`menus.py`, `selection.py:160–284`). Squad view4E22 is real and calls real42BC/cards/row helpers. | Entry/squad view is implemented; this does not close the pool branch. |
| Pool toggle/browse: E44F E4D4→E2E6 | **E2E6 is absent, not a stub.** Original `named/seg_0791_12.c:806`; `code/seg_0791_22.asm:E2E6–E44C`.138 instructions,14-byte frame, `ret2`. | First pool redraw fails in a real PortMachine before any pool Enter/DEA6 can run. Cannot bypass it as “only UI”: templates, rows, card/cursor attributes, stack and return effects are real guest state. |
| E2E6 direct callees | Seven distinct targets:214B:0329,1771:2F37,214B:00DB,0791:DDCB,0791:DE51,1771:42BC,214B:13C5. All real under97f; **DDCB is only supplied by pending T128**. | One bounded missing body; reuse these callees. Preserve21 visible rows(top..top+20), actual manager pool base/top/cursor, retained mark highlight, current card and ABI. |
| Pool exchange | E44F→DEA6→DBFA/DE27/DDCB/DE51/007B/re-sort. Real in97f, bounded primitive/real-helper proofs in T128. | Still cannot reach it through the actual pool UI until E2E6 exists. DBFA/DC7E remain accepted main bodies. |
| Play validation: ED8A→EA09 | Real. Actual availability3216, manager0B77, count/keeper checks and real1765 message/key machinery (`selection.py:363–423`). | No new missing entry found. Actual pre-match key/ownership/refusal iteration remains a T129 proof requirement. No auto-XI repair. |
| R/C | Real4952→4925 (R) or record+7 restore(C); setup-context3EF8 refresh is real (`menus.py:185–208`). | Preserve original refresh/global writes, not only the changed position byte. |
| Personal T/marking | Real4B61→42BC/1560, bit-set helpers,49B8; dynamic0C79/0CA1 targets are real (`menus.py:454` onward). | Pool/squad and eligibility gates still come from original caller/context. No new missing required entry found; card path retains the3947 stub limitation below. |
| Team tactics | Real1981→157D/13D0,1560,0CF4 and setup refresh3EF8 (`menus.py:313`; `display.py:2100` onward). | Eight-bit editing is implemented. Status/rating output stubs below remain a bounded display boundary, not a claim of full original screen equivalence. No Track A projection change proposed. |
| Ins recommendation | RealDC7E→DBFA/377E/007B; E44F gates managed/squad/C1F before calling it (`selection.py:270`, `assistant.py:150`). | Reuse original recommendation, including tie/order/window behavior; no harness/legal-XI policy replacement. |
| Initial captain | Real20E3→1F3C/CC7B, CC2E,3216,6B65/1FDD and key/wait entries; `takers.py:147`, `positioning.py:516–616`. Delay1E09 and speaker1E8D are **real retained-state entries**, not stubs. | No missing core guest entry found. Existing host adapter automatically supplies initial captain; it does not expose a public late live-XI captain decision. T129c is still an API/interaction requirement. |

Source-call scanning also checked literal helper calls and the existing conditional text/clamp/bit helper targets; unresolved wrapper parameters were inspected at their callers. This is static inspection, not a proof that every dynamic menu branch has executed.

## Existing stubs: keep their limits visible

Registry declares each of these “display/sound/wait body omitted; listing return cleanup and incoming result registers preserved”. That is not a complete memory/frame/key implementation. Accepted state-access audit: `experiments/E036-match-port/out/m4-408/removal-state-audit-2.md:15–18`; profile limits: `notes/T73.md:5–37`.

| Stub | Real effects omitted / accepted proof limit |
|---|---|
|1771:0AF8 `retf6`|Manager-status text through DS:A96E, own locals. Frozen audit saw21 entries and bounded status bands; caller157D reloads its next country expression. Output elision, not state-free.|
|1771:1527 `ret6`|Rating label/buffer and frame writes. Frozen21-entry scope;157D reloads the manager byte. Not general full-buffer equivalence.|
|1771:3947 `ret6`|DS:AAB2=70h plus twelve attribute writes and locals. Frozen638-entry argument says42BC later supplies explicit attributes/AAB2=15 before further reads. Do not reinterpret as “no global writes”; new stop placement must respect that boundary.|
|1771:50F1 `retf4`|Unmanaged/opponent player viewer from E949. Original uses1560 to change DS:0C1B/key state and loops until Esc; conditional F2 invokes4859/name effects. Frozen audit:zero entries, **unreached-stateful, not generally proved removable**. `named/seg_1771_04.c:438`; raw `seg_1771_07.asm:948–1012`.|

Thus an original **guest** opponent-view round trip is not established. Do not enqueue arbitrary original viewer keys against a stub that consumes none. Existing Qt read-only views can remain detached canonical-data views if that boundary is explicitly retained; do not describe them as an executed original50F1 flow.

## Conditional F2 gap and false dependency to avoid

Managed E44F F2 and original50F1 F2 call real1771:4859, but it calls **missing214B:1086**. Its original input-editor closure also needs missing **214B:0D90**(67 instructions,ret6), **214B:0E41**(149,ret2) and **214B:0FB5**(61,ret4);1086 is310 instructions,retf12. D90 blinks/restores a screen cell while polling0723 and reads BIOS tick0040:006C; it is not just a string helper. Source: named `seg_214B_01.c:1061`, `seg_214B_02.c:4,35`, raw `code/seg_214B_02.asm`0D90–1363; `menus.py:668–705`. Cursor, editing mode/DS:7A24, string restoration on Esc, keys and caller buffers are stateful. This is not a tiny display stub. If T129 claims actual guest F2, split editor helpers/editor/viewer closure into independent bounded prerequisites. If names remain the accepted designed UI overlay, keep that control usable and explicitly exclude a DOS-name-editor fidelity claim; do not silently remove it.

1771:4FAA has no registered entry but is **not** an extra required viewer dependency:50F1's only static call at516D is skipped by `mov AL,1; or AL,AL; jne5174` at5166–516A. Do not schedule dead code merely because a raw call-graph lists it.

## Why existing coverage did not establish this

`tests/test_port_selection.py:30–70`'s synthetic Rig delegates replies or falls back to AX=0 for unknown callees. Its tests explicitly intercept edits/read-only viewers; the C1F-mode test at306–315 asserts E2E6/DEA6/etc are *not called*. Those tests are valid dispatch/guard checks, not real closure proofs of pre-match pool/name/viewer paths. T128's real-helper proof starts at DEA6, so it likewise never draws E2E6.

## Bounded next release

1. Before T129b activation, release **only E2E6** as a separate state/ABI leaf after accepted T128. Original-backed pool top/cursor/mark/country/zero-word frames compare complete effects under the declared existing proof boundaries, followed by denied-PyPy **real E44F Right→browse→swap→back/Esc** controls; assert actual E2E6/DDCB calls and original caller/key/stack/RNG effects. Keep failures; no new display stub, guessed UI policy or private memory patch.138 instructions with real existing callees is one coherent leaf, plausibly one implementer run.
2. Author T129a/b/c around the already-listed managed semantic edits and late captain, with actual real-registered path tests. Keep the accepted display-profile limits explicit; any newly observable stub effect must be reported for a bounded prerequisite, not masked.
3. Declare the opponent-view/name boundary before claiming closure: retain current detached Qt views/designed name overlays, or separately port/prove the original50F1 and F2 editor path. The latter exceeds a single hour-sized pre-match interaction leaf and must not be hidden inside T129.

No task IDs were reserved or tasks released by this audit; no frozen T128 code/evidence was changed.

## Main release boundary

[designed: main] T129p/#703 is authored but remains dependency-blocked until T128/#701 is actually accepted. It owns only E2E6 pool-view state/ABI. The later pre-match/action/captain contracts remain drafts and require their own live dependency checks. Existing detached Qt information views and designed name overlays keep their accepted boundary; no executed original50F1/F2-editor fidelity is claimed. Preserve those controls and their visible behavior when connecting the held worker; a timing/representation gap must be solved explicitly, never hidden by disabling the action.
