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
four tests passed). Further acceptance and mutation checks are required.
