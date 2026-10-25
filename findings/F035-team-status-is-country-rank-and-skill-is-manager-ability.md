# F035 TEAM Status is country rank; Skill is manager ability

- **Status**: proposed.
- **Question**: #428 / T94: original country TEAM Status and Skill, source fields, bounds and contexts.
- **Artifact**: goal2-67cf27d6; same original code/data as predecessor goal2-a949da2f.
- **Method**: static first: named TEAM 157D,1527,10E7,0AF8, their callers, tables and listings; corroborating isolated unmodified original-code calls and complete original TEAM draws under Unicorn. These are static-adjacent probes, not a new behavioral campaign or independent behavioral corroboration.
- **Intervention**: synthetic call frames and scratch screen buffers. Genuine-country records are unchanged for the two-state observations. Boundary/context cases explicitly edit copied country/manager fields; original instructions and callees are unchanged, with no behavior hooks. Each call must return with its specified stack cleanup within 2 seconds/500000 instructions.

## Answer

- **Status is the country label at TEAM row 8/column 25**, drawn by 1527, called at 15C1. The literal original template says `status` there. The value is `((5-continent)*(33-continental_rank)+129-world_rank) idiv2` from country+0x2C,+0x2A,+0x2B (10E7, already F007/C-TEAM-01). In the normal rank domain (continent1..4, continental place1..32, world place1..128), value 1..128 selects `DS:7884[(value-1) idiv8]`; that byte selects a 16-byte Pascal slot at `DS:6EB4+16*index`. No player skill, XI, tactic or current-match field enters this label. static:static/goal-exe/code/seg_1771_03.asm:76 static:static/goal-exe/code/seg_1771_03.asm:6 static:static/goal-exe/code/seg_1771_02.asm:698 static:notes/428/original-r3.json:1

- **Skill is the manager label at TEAM row 10/column 24**, drawn by 0AF8 and called at 15F8; the original template says `skill` there. Country+0x2E selects manager m; byte+1 at `[DS:A91F]+3*m` supplies its ability. For m=0 the original draws nothing. Otherwise ability 0 selects the code Pascal string `unknown` at 1771:0AF0; nonzero ability selects `DS:7894[(ability-1) idiv8]`, then the same 6EB4-rooted descriptor slots. The byte is zero-extended: no signed interpretation and no clamp in this routine. All256 byte values match;129..255 deliberately read neighboring table entries, not a new invented rating scale. F025 describes normal rating updates clamped 1..128; that writer bound is distinct from this display's behavior. static:static/goal-exe/code/seg_1771_02.asm:39 static:static/goal-exe/code/seg_1771_03.asm:96 static:notes/428/original-r3.json:1 static:findings/F025-sacking-and-end-of-the-game.md:18

- **Germany at both supplied states displays Status `giant`, Skill `eclectic`**, country rating 126 and manager 12 ability 126. Albania is `poor` / `very bad` (34), Sweden `major` / `exceptional` (113), Yemen AR `very small` / `negligible` (31). The six full original TEAM panels confirm the positions/labels, not only decoded values. Four explicitly synthetic Germany/human-manager 129 full panels preserve Status `giant` while Skill becomes `unknown`, `none`, `eclectic`, `ok` for ability 0,1,128,255 respectively. The country selects current manager memory; a computer-country-index shortcut would fail that context. static:notes/428/original-r3.json:1

- **Host bounds are explicit, not original guards**: the pure decoder requires a 191-byte country record, selected manager 0..134 and a 3-byte manager record when nonzero; normal rank bounds above; ability 0..255; complete 16-byte Pascal slots with length<=15. Invalid/truncated inputs raise ValueError, never a clamped/guessed label. The original trusts memory and can read outside semantic tables on corrupt inputs. Labels are read from caller-supplied original memory and projected as F034 screen glyphs; original data is not bundled. static:runtime/decoders/country.py:1 static:tests/test_country_decoder.py:1

## Observations and interpretation correction

Receipts use hash-verified original E010-r0001 half-time and E006-r0001 new-game savestates, with the existing original build guard. All128 countries of each state are read; the same three contrasting countries12/27/128 are fully drawn in each. These two snapshots have the same rank-derived labels; this is not a claim of campaign evolution or independence of the snapshots. The complete renderer runs unmodified, including template unpacking and its normal string writers. Private inputs are cached, never committed or exported as bytes.

The first producer named its JSON keys from the misleading existing `draw_manager_status` annotation. Receipt `original-r1.json` has its semantic `status`/`skill` keys **reversed**; its raw row 8/row 10 observations are correct and immutable. Do not consume r1's semantic keys. The actual original template exposed the reversal. Producer b73a3a1f corrected the interpretation, r2 retains the corrected output before decoder cross-checks, and r3 additionally matches the pure decoder and four explicit manager contexts. No earlier receipt was overwritten. In r2/r3 the legacy key `status_byte` still means the selected manager ability byte (+1), not the visible country Status; use the corrected visible `status`/`skill` fields and the explicitly named synthetic arrays. The local producer variables retain that historical naming too. The task's interpretation was corrected on main at 85496181 without weakening its Done-when.

Most genuine manager ability bytes equal their country ratings, so agreement over the genuine rows alone does not distinguish the two dependencies. The source reads, separate descriptor tables and four manager-only synthetic full-panel edits are the discriminating evidence.

The decoder's seven independent tests fail to import before implementation and pass afterward. Eleven in-memory mutations are all rejected, including swapped labels, wrong tables, off-by-one bands, reading manager confidence instead of ability, manager 0/unknown changes, an unjustified128 clamp, wrong rating formula and unbounded label length. The full original country ratings1..128 and manager bytes0..255 provide separate comparison coverage. Source/producer/helper hashes are pinned in the receipts.

## Alternatives and limits

1. **Skill is an average of the XI's skills** is excluded for these labels by source reading and manager-only context edits; it may describe other team bars, which are separate placeholders.
2. **The existing routine name means the panel fields should be reversed** is refuted by actual original row 8/row 10 templates and full renders. Names are annotations, not ground truth; relevant annotations are corrected.
3. **Zero means the lowest normal band or manager 0 means unknown** is refuted by the original0AF8 branches and explicit sentinel controls. Zero ability and missing manager are separate cases.

This does not establish natural reachability of arbitrary edited ability values, the original's behavior on every corrupt rank tuple, the exact private Windows playtest state, all screen/font variants, a complete country-card decoder, or the meanings of ranking-top/strips/bar displays. Evidence for remaining placeholders is audited, with concrete follow-ups in #432 and the delivery report.

## Inferences

- Goal2 can replace only these two placeholders using current country and selected manager records plus the pinned original descriptor tables. Use `team_labels` with a read-only adapter and preserve manager selection and original screen glyphs. Other placeholders need their separate accepted contracts; no runtime/vendor/UI change is made here. static:runtime/decoders/country.py:1 static:docs/requests/428-country-labels.md:1
