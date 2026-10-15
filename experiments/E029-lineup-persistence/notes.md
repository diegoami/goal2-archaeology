# E029 Does a watched match keep a copy of the lineup and restore it? (T55, Q037, F029)

Read-only over the committed run records `runs/E015/E015-r0007 .. r0010`, `r0013`, `r0017` (and `r0014 .. r0016`,
extracted but not counted). No game was run. Inputs' hashes: `out/inputs.sha256`.

Run from the repository root, in this order:

```sh
python3 -I experiments/E029-lineup-persistence/run_all.py          # out/<run>-timeline.tsv, out/<run>-<country>-changes.txt
python3 -I experiments/E029-lineup-persistence/screens.py runs/E015/E015-r0013.json experiments/E029-lineup-persistence/out/r0013-screens.tsv   # likewise r0007, r0009, r0010, r0017
python3 -I experiments/E029-lineup-persistence/substitutions.py    # out/substitutions.txt, substitutions.tsv
python3 -I experiments/E029-lineup-persistence/order_check.py      # out/order-check.txt
python3 -I experiments/E029-lineup-persistence/cprompt.py          # out/cprompt.txt
python3 -I experiments/E029-lineup-persistence/positions.py        # out/positions.txt
```

| script | what it reads | what it writes |
| --- | --- | --- |
| `timeline.py` | one record: the decoded squad words per state, the fixture index word, the stage byte | `out/<run>-timeline.tsv` |
| `changes.py` | a timeline and a country column | the states where the squad words or the fixture index changed, as membership (eleven / bench) or order only |
| `run_all.py` | the nine records | the timelines and change logs |
| `screens.py` | one record's recorded text pages | a coarse screen class per state (match board, bench screen, select screen) |
| `substitutions.py` | timelines | the placement of each managed-side change against the match windows, and the full-time / record-end / next-match check |
| `order_check.py` | records and timelines | whether the eleven and the bench are sorted by `+6`, and the screen at each order-only change |
| `cprompt.py` | the E015-r0013 timeline | Italy's squad words over the captain / kick-taker prompt where the owner typed C |
| `positions.py` | records | the incoming and outgoing players' `+6` around each managed substitution |

The match windows in `substitutions.py` (kick-off board, FULL TIME) are read off the screen classes; each is cited
in the script and in `out/substitutions.txt`. The player names in the script come from the in-match team screen of
E015-r0007 (state 85) and the owner's notes of E015-r0013. The counts quoted in F029 are the last lines of
`out/substitutions.txt`, `out/order-check.txt` and `out/positions.txt`.

How the checks can fail: `substitutions.py` answers "NO" when an incoming player is not in the eleven (or an outgoing
one still is) at the state it tests; the pre-match edits and the E015-r0013 full-time-to-record-end comparison
show it can see a difference (the eleven at kick-off, at full time and at the end of E015-r0013 are three different
lists in `out/substitutions.txt:20-22`).
