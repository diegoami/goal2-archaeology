# T80a outputs

- `read_map_v1.py`, `read-map-e034-03-v{1,2}.json`: the port's inputs on E034-03's drive (v1 counted the
  kit's between-event snapshots too; v2 counts reads while the dispatcher runs, up to 4 KiB, before the
  byte is written).
- `read_map_family_v1.py`, `read-map-family-v1.chunk-*.json`, `read-map-family-v1.json`: the same over
  the 75 admitted matches (12 chunks, PyPy, all completed), and their union: 35,515 input bytes; code
  segments 590 (all equal to GOAL.EXE), initialised data 14,426 (14,425 equal; DS:7968 set before the
  match), the rest of DS 420 and elsewhere 20,079 (state and records). 4,396 of the initialised-data
  inputs lie outside build.py's measured ranges.
- The tables: `static/goal-exe/tables/` from `tools/static/port_tables.py` (the whole initialised data
  segment, and the listing's 173 data areas in the code segments, 11,572 bytes), checked with `--check`.
