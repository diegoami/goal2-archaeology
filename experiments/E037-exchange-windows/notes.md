# E037 Exchange windows (T81, issue #254)

Static only: no game was run and no savestate was written (I0). The finding is `findings/F031-*.md`.

## Files

- `predicate.py`: the rule as a function (`exchange`), the finals flag's set and clear (`finals_flag_after_route`,
  `finals_flag_after_build`), and `evaluate_row` for one row of `cases.tsv` (a `?` input is tried both ways; the
  verdict is `unknown` when they differ).
- `cases.tsv`: the 29 literal cases of F031 section 3, with the inputs by the original's field names, the verdict,
  the evidence level, the listing basis and the verdict goal2's assumed policy gives (F031 section 4).
- `test_cases.py`: visits every row and recomputes its verdict; checks the evidence levels; pins `cases.tsv`'s
  sha256; checks the flag's set/clear kinds and stages; re-decodes stage 7's friendlies (`tours.py`). Run from the
  repository root: `python3 -B -m unittest discover -s experiments/E037-exchange-windows -t experiments/E037-exchange-windows`.
- `tours.py` -> `out/tours.txt`: the stage 7 friendlies of `1771:71B2` decoded from the committed data-segment dumps
  (`static/goal-exe/data/ds_2581_0*.hex`, read through `experiments/E023-competitions-structure/dsbytes.py`), and the
  predicate at every gap of an odd and an even position's friendlies.
- `mutate.py` -> `out/mutation.txt`: rule 9: each row changed alone (its verdict; its finals flag) makes the test
  fail; `cases.tsv` is written back in a `finally` and the suite passes after.

## Hashes (sha256)

| file | sha256 |
| --- | --- |
| `predicate.py` | cec4d39e0f7eff75e99081fa3c918dfa0dbd43f8f6163b0306c577e0e04c8970 |
| `tours.py` | b6940f5b0c0f85b0ff765be92301fcc7c6d6ee59dcea08ba1e61b88b5abb702c |
| `mutate.py` | 9194bbbf23957361112b0e50bd6f8119e7b90507fe4f93d85b6c22be14368ee4 |
| `test_cases.py` | 2c70eb84d25482ccf8d577e75fd7f49dc2606e13e19ac76b23781c07cb69790e |
| `cases.tsv` | 2fbcf1cba2b2c2920b4a4b12cb8f0c03b6a92fc4ca217de2d17a5832d3221a5b |
| `out/tours.txt` | 8a9731e1a089000f6e825fad0b261888b841190be49451de43ce5584a7f46c95 |
| `out/mutation.txt` | f1c74f1c28dc204ffd54e607b3af0dffde20c38d6a0ede0d044e9a4ea096e662 |
| input `../E023-competitions-structure/dsbytes.py` | 3e733cfb5fec995ebc3b16613b6b35ae1efde8a1d942ee95de7778db19a9a40c |

## Not here

- No original bytes beyond the table values F031 quotes (the data-segment dumps were committed by earlier tasks).
- The CI suite (`python3 -m unittest discover -s tests`) does not collect this directory's test: T81 owns no file
  under `tests/` but `tests/static/*`; run the command above.
