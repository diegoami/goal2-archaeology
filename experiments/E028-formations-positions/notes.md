# E028 formations and positions (T54, Q021, Q022, Q023)

Static first (CLAUDE.md rule 22). Every output a finding cites is under `out/` (never overwritten). Run with
`python3 -B <script>` from the repository root; the artifact paths are the main checkout's `.cache/goal2/` (the release assets
verified by hash; nothing of GOAL2 is committed). Packed GOAL.EXE SHA-256
`a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664` (the harness prints it; it equals `artifacts/known.json`).

| script | what it does | output |
| --- | --- | --- |
| `ds.py`, `text.py` | read ranges of the data-segment image (`static/goal-exe/data/ds_2581_0*.hex`) | stdout |
| `tables.py` | decode every table the position code indexes (posts, depth offsets, kick-off, label classes, heights, foot rows, marking pairs, bench roles) | `out/tables-20261013T14*.txt` |
| `readers.py` | list the routines that read +6 / +7 of a player, in the named view and in the listing (syntactic sites) | `out/readers-named.tsv`, `out/readers-asm.tsv` |
| `foot_truth.py`, `foot_summary.py` | run the ORIGINAL bytes of `1771:3179`, `3088`, `3041` in Unicorn for every (played, club, n mod 3, two-footed) and compare with the rule read | `out/foot-truth-20261013T142802Z.tsv` |
| `posts.py` | group GOAL.DAT block 10 into formations; run the ORIGINAL `0791:419C` per formation; compare with a Python port | `out/formations-20261013T142949Z.tsv` |
| `posts_synthetic.py`, `posts_falsifier.py` | the same comparison on 3056 synthetic elevens; and the port made wrong on purpose | `out/posts-synthetic-*.log`, `out/posts-falsifier-20261013.log` |
| `mdtable.py` | the markdown table of the formations for F028 | stdout |

Runs of the game: none (no DOSBox-X run was taken: the listing answered, and the emulation of the original bytes corroborated).
The emulations run the unpacked image's own code, with a bare memory image (load segment 0, DS = 2581) and only the bytes
the routine reads written by the harness; no hook, no substitution.

## Checks of the checks

- `foot_truth.py`: 2352 cases, 0 differences between the original `3179` and the rule as read. `foot_summary.py --swap-sets`
  (left and right sets exchanged) gives 660 differences, so the comparison can fail.
- `posts.py`: 52 of 52 formations equal the port; `posts_synthetic.py`: 3056 of 3056 elevens equal; `posts_falsifier.py`: a port
  with the separation step changed by +2 differs on 287 of 328 elevens, with the outer-branch sign flipped on 231, with the
  previous record's y step dropped on 231, so the comparison can fail. The branch threshold (`cmp ax, 4` at 425C) cannot be
  separated from 3 by any eleven: no post has |x| in 1..4 (the falsifier "threshold-3" differs on 0 of 328).
- The branch for |x| > 4 (two adjacent players of code 3, 4, 7, 8, 10 or 11) is reached by no block-10 eleven; it is
  exercised only by the synthetic elevens (2308 of 3056 reach it).

## Outputs and their SHA-256 (originals; none overwritten)

| file | SHA-256 |
| --- | --- |
| `out/foot-truth-20261013T142802Z.tsv` | `4af9b20db56b3c6bcb126600e7e1804a18d1e89dd67b557d4935b84f1c0210b7` |
| `out/formations-20261013T142949Z.tsv` | `44a4466cfc48aa0fcf63b5ddaceab2ed6138e360131988d8b99e851d11a156eb` |
| `out/posts-synthetic-20261013T143525Z.log` | `666be552acac9d6eaf12f37e469609be404e1cb686601b0cc194dfa6867688a7` |
| `out/posts-falsifier-20261013.log` | `fcd130dc292d4de4fb4a499aed128bf896b111d05c74ea82b9404ddb90397dde` |
| `out/tables-20261013T143429Z.txt` | `f4915d1b8217d15d8f7e5962e79789d28ee11b71bd4bcf5f0a3accc75149970e` |
| `out/readers-named.tsv` | `c88e3f88883a8294c02b0689dbbd9f7b35d7b56592d9a489236df092384662d9` |
| `out/readers-asm.tsv` | `e7caaa64dc41dfebcd2d7cc25f57012f54ac926ac6f705d00733cee85a6397e9` |

`readers-named.tsv` was taken against the named view as it stood at commit 434bc08, before this task regenerated
`static/goal-exe/named/`: its file and line columns refer to that version, and a few routine names in it
(`replace_first_back_four`) have since been renamed. `readers-asm.tsv` refers to the listing, which did not change.
`readers.py` writes fixed file names, so re-running it would overwrite these two files: give it another OUTDIR.
