# #695 source-first request and timed opportunity audit

Base4fe3a973e22c2f7fa37475bfed2b6b5a71db8f08. Model: inherited Codex GPT-6
family; exact variant unavailable. This note is a static reading, not a promoted
finding or behavioral corroboration.

- `named/seg_0791_13.c` E44F and raw `code/seg_0791_22.asm` E66B–E6B5:
  while in a match, Enter invokes E022 only with DS9B41 and a remaining budget.
  Otherwise it toggles DS9B40, setting it only if a substitution remains. No
  off/on pair is necessary. Port `selection.py` preserves these writes.
- `named/seg_0791_08.c`8062 and raw `code/seg_0791_13.asm`80A9–8108:
  managed side, request latch set, and either unavailable keeper or nonzero
  minute+added time with remaining substitutions cause7FCF. Budget permits9B41.
  After7FCF, non-Esc opensED8A; an unavailable keeper forces it even forEsc.
- `named/seg_0791_07.c`7FCF, raw `code/seg_0791_13.asm`8033–8057:
  timeout comes from DS087C+2*keeper; ordinary400polls, keeper1000, as read from
  `static/goal-exe/tables/ds.hex` via the existing from_hex parser.
  A key is read if waiting; otherwise8052 writesEsc toA977. The bottom line is
  saved/restored; it is not a mandatory permanent notice.
- `named/seg_0791_11.c`CC2E, raw `code/seg_0791_20.asm`CC39–CC6B:
  each poll tests214B0723 then, if no key, calls214B1E09(10). Thus4000/10000
  nominal calibrated milliseconds, not a measured real-time2s display.
  Portmenus.timed_notice and discipline.check_substitutions retain the same
  branches/call arguments. The original opcode proof must still corroborate it.

LiteralEsc and timeout skip an ordinary opportunity's menu. The owner's desired
UIEsc-to-bench is an explicit designed2026-11-08 adaptation: the downstream UI
maps its command to the original accepting Enter. Upstream still distinguishes
accept(Enter), dismiss(Esc), timeout(no key), and keeper-forced behavior.

The old facade stops before7FCF as a legacy substitution decision; its change
plan synthesizesEnter to proceed. Preserve that default stream/replay shape.
The new single strictboolean substitution_control profile exposes a separate
substitution_opportunity, then a legal substitution decision only if the actual
original opensED8A. request_substitution is a desiredboolean paused edit through
SELECT TEAM, independent of pairs. No direct latch write or fake pair is added.

Before-v1 is a retained invalid test-import calibration. Before-v2 has eight new
controls failing against old behavior; after-unit-v1 passes29new+existing focused
controls. These synthetic coordinator cases are not natural opcode evidence.
