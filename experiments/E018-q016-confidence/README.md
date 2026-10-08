# E018 Q016 confidence

Static-first investigation of the result-relative player byte +0C. The
original-routine probe uses E011-r0002's hash-verified half-time guest image
and Unicorn, following E017's method. It is not a complete played match or
a DOSBox run; no DOSBox runs have been taken. Probe batches and their
declared input changes are retained. No original guest image is committed.

## Immutable records and supersession

| Record | Superseded by | Reason |
| --- | --- | --- |
| `fixture-probe-002.json` / `E018-r0001` (defective) | `fixture-probe-003.json` / `E018-r0002` | The probe mistakenly injected squads at country +47 instead of +0 and status at player +7 instead of +10. Its own consistency check fails: `declared slot disagrees with injected squad`. It did not execute the declared player/role cases. All six cases require replacement. The checker executes this check before setting the record aside, and refuses to set aside a consistent record. |

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
the script recorded the literal host name `WINDOWS-BJ0PUMB` (`platform.node()`), whereas
`run/1` requires `^[a-z0-9][a-z0-9-]*$` for `machine`. Those two files were never valid run
records, and they are not measurements: `register_probes.py` derives them from the retained probe
traces `fixture-probe-002.json` / `-003.json`, which stay unchanged. The main session (2026-10-09)
fixed the script to write the project's machine id `ubuntu-24-04-wsl2`, as every other record
does, and regenerated both records from the same traces before the PR merged; `validate_runs.py
runs/E018` now passes. The rejected originals remain in git history at 110476c, and
`run-validation-001.log` keeps the rejection.

## Recorded model checks

`comparison-001.log` reports the explicit first-probe supersession and
`match: 240/240` for the replacement's six cases. No E015 match pair was
used (the available sitting is the four-state scripted recording).
`mutations-001.log` records the baseline and each in-place mutation:
all thirteen declared numeric constants were shifted by both +1 and -1,
then seven input/branch/persistence operators were changed independently;
33/33 mutations failed the literal-output tests. Source restoration ran
in `finally` after the sweep.

The continuation's `checker-red-001.log` shows the consistent-record rejection
test failing before the guard was added. `checker-green-001.log` passes;
`checker-mutations-001.log` removes each of the consistency, empty-set and
kept-mismatch guards independently and kills 3/3. The latter two guards
already existed: their tests fail with those guards removed, not on the
unmodified continuation baseline. `comparison-002.log` prints each defective
case's failed consistency check and matches 240/240 kept player words.
`mutations-002.log` repeats the bidirectional sweep; `mutations-003.log`
includes literal boundary cases for clipping, signed interpretation,
expected-margin truncation, saved-form clipping and bounded draws. Each
sweep kills 33/33 in-place mutants. These boundary assertions fail when the
relevant constants are shifted, and pass after source restoration.

The two E018 manifests publish the original E011 half-time state again under
release E018, by its unchanged SHA256. Registration/probe traces remain
tracked separately; no new guest execution was needed to publish evidence.
