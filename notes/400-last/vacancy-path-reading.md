# Existing vacancy-path contracts and the limit of further campaign collection

This is a scoped reading of already named/listed routines, not a new finding or a
claim of global unreachability. T89's immutable17-save/12-core-input inventory remains
the available-source observation; all managed100 entries were nonzero.

- `1771:9A40` initializes each country's20 squad words with positive consecutive IDs.
- `0791:DEA6` marks a nonzero first selection, then swaps it with the second selected
  squad/pool entry through `214B:007B`. It can move an **already existing** empty entry,
  but that is not a way to derive one from the inspected full sources.
- `0791:E022` checks an empty first-selected squad word before marking, producing E062;
  its normal successful substitution is a swap, not a player-ID deletion. The sent-off
  status check at E19F is a different guard, already delivered by T88.
- `000E:56F3` calls `1771:4CF7`, stores the fresh ID in the retiring member's squad/pool
  slot and creates the replacement before clearing the old player record. `4CF7` scans
  positive IDs in1..3060; its fallback loops until finding a free record rather than
  returning zero. This is the existing F017 reading, not new campaign evidence.
- `0791:EA09` increments its vacancy counter only for a zero squad word. The earlier
  `214B:0018` fill includes that counter byte; it is not justified to treat the decompiled
  local as an uninitialized way to reach EC60. EC60 is also after the earlier checks.

The reviewed paths do not establish a cheap path from these full inputs to the two requested
empty-slot warnings. The reading is not an exhaustive write/alias audit. It therefore does
not justify an unattended multi-year run, and it does not justify manufacturing a zero
entry or claiming the warning callers were visited. Their conditional static contracts
remain the explicit assumption until a genuinely closer input is identified.

Sources: named `seg_1771_07.c`9A40, `seg_1771_04.c`4CF7,
`seg_0791_12.c`DEA6/E022, `seg_000E_04.c`56F3 and
`seg_0791_13.c`EA09; corresponding original listings; F017/F029/T84/T89.
