# E018 Q016 confidence

Static-first investigation of the result-relative player byte +0C. The
original-routine probe uses E011-r0002's hash-verified half-time guest image
and Unicorn, following E017's method. It is not a complete played match or
a DOSBox run; no DOSBox runs have been taken. Probe batches and their
declared input changes are retained. No original guest image is committed.

## Immutable records and supersession

| Record | Superseded by | Reason |
| --- | --- | --- |
| `fixture-probe-002.json` | `fixture-probe-003.json` | The probe mistakenly injected squads at country +47 instead of +0 and status at player +7 instead of +10. It did not execute the declared player/role cases. All six cases require replacement. |

`fixture-probe-001.log` is a pre-execution failure (wrong manifest filename);
no guest execution or comparison record was produced.

## Commands

```sh
python3 experiments/E018-q016-confidence/probe_fixture.py scratch/t32/9820b47814dd9670-E011-r0002-halftime.sav experiments/E018-q016-confidence/fixture-probe-003.json
python3 -m unittest -v tests.test_model_confidence
```

The model's new tests were run without the module first
(`model-red-001.log`: import failure), then with it (`model-green-001.log`:
four tests passed). The expanded test suite's baseline and mutations are
retained in `mutations-001.log`.

## Retrospective extraction records

`register_probes.py` registered both immutable probe traces under
`runs/E018/`, retaining the complete input, draw and per-player result
objects as observations. Its timestamps are extraction times, not guest
execution times. `E018-r0001` records the defective first probe;
`E018-r0002` records its replacement.

The first schema check (`run-validation-001.log`) rejected both records:
the script recorded the literal host name `WINDOWS-BJ0PUMB`, whereas
`run/1` requires `^[a-z0-9][a-z0-9-]*$` for `machine`. These outputs are
retained unchanged. A replacement cannot make the task's directory-wide
`validate_runs.py runs/E018` command pass: that validator still validates
the retained originals. Editing/deleting them would violate the immutable
record contract. No evidence release was published for these records.

## Recorded model checks

`comparison-001.log` reports the explicit first-probe supersession and
`match: 240/240` for the replacement's six cases. No E015 match pair was
used (the available sitting is the four-state scripted recording).
`mutations-001.log` records the baseline and each in-place mutation:
all thirteen declared numeric constants were shifted by both +1 and -1,
then seven input/branch/persistence operators were changed independently;
33/33 mutations failed the literal-output tests. Source restoration ran
in `finally` after the sweep.
