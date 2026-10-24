# T85 / goal2 request #396: mutable DS:066A in the kit guard

[confirmed: registered GOAL.EXE listing, `static/goal-exe/code/seg_0791_15.asm` 941A–9448;
`static/goal-exe/named/seg_214B_02.c` 1D6F] Original Up/Down passes the address DS:066A to
214B:1D6F with limits 0..4. That helper reads the byte, wraps the requested change, and writes
it back. This is a live display-mode variable, not immutable initialized data. E033's sampled
read/write scenarios did not include these keys. Static analysis answers the question; no new
playthrough or guest execution was needed.

[confirmed: T84/#392, E031 g1 checkpoint 3874] The unchanged private input
`3ea57029282b849f-g1-03874-shootout-start.sav`, SHA-256
`3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc`, was rejected before the
correction. `before.json` records that refusal and the original generated-module digest.
Its private retrieval location remains `notes/390/inventory.json` / the #392 delivery; place
it in `.cache/dl/` locally. Do not publish another copy. Its absence skips only the real-image
controls in CI; the static/generator coverage tests always run.

[derived: the original writer above] `build_guard.MUTABLE_DATA` records the writer so that a
future regeneration cannot reintroduce the sampled mistake even without this input. The
runtime checker is unchanged. The generated coverage removes exactly one additional byte,
DS:066A, leaving both adjacent bytes covered; all code metadata and every other covered data
byte are unchanged. `baseline.json` fingerprints the pre-fix coverage and code metadata; the
regressions reconstruct that coverage by adding this byte back. This is a byte exclusion,
not a data-block exemption.

The registered packed executable is verified as
`a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`, and its unpacked form as
`6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188`.
Both `guard-regenerated-r1.json` and `guard-regenerated-r2.json` record zero listing/extract
differences, all 14 original images accepted, and identical generated-module hashes. They
name every image by hash and the unchanged E033 `ds-reads-20261016f2.json` input report.
No original bytes are stored in these receipts.

Reproduce from the registered private/local inputs (use a fresh log filename):

```sh
python3 -B experiments/E033-original-match-kit/build_guard.py \
  --exe .cache/artifacts/goal2-a949da2f/GOAL.EXE \
  --reads experiments/E033-original-match-kit/out/ds-reads-20261016f2.json \
  --log notes/396/guard-regenerated-r3.json
python3 tests/test_build_guard_mutable.py -v
```

`before-regressions.log` fails on the old guard; `after-regressions.log` passes all five tests.
Corruptions operate only on copies as refusal controls: no corrupted image is executed or
advertised as a real state. Goal2 must consume the merged generated module through a declared
re-vendor and provenance pin. This change alone does not implement its shootout screen.
