# T80c: the whole family from records (the sealed engine)

[derived: this folder, 2026-10-30; PyPy 3.11.15, the head the chunks name]
`family.py --engine port --no-unicorn --from-records`: every match played from goal2's state in its
registered source (Image.state_of: the memory without GOAL.EXE's load module) and GOAL.EXE's tables
(static/goal-exe/tables), never the image; Unicorn imports denied.

- `chunks_v1.py start --family ALL ... --chunks 24 --tag sealed-v1`, started before T79's fix that took the
  A700 sheet out of ALL, so the run holds all 775 matches (the 75 admitted and A700's 700). The first
  start ran 24 at once: 32 A700 matches went over the unchanged 300 s limit (median 283 s CPU at that
  load; T79's port arm: 120 s). Stopped, resumed with 12 slots (`part-*.r1.log`), and the 32 rerun alone
  (`family-sealed-v1.rerun-1.part-*.jsonl`, all completed, at most 124 s): the join replaces each failed
  record and lists it (`family-sealed-v1.joined.json`).
- **Done-when**: `sealed.jsonl` (the 75 of ALL, joined), `compare.py --family ALL --no-screen --candidate`
  it → exit 0, **75 matches expected identical, 75 pass** (`compare-sealed-v1.log`).
- Beyond it: `sealed-A700.jsonl` (700) against T79's oracle arm with `out/T79/compare_a700_v1.py`
  → **699 of 699 identical**; A700/ref-121 left out, not completed in either arm (#623)
  (`compare-sealed-A700-v1.log`).
