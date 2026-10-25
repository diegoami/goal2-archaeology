# Manager-name decoder delivery (#429, T93)

F034 is proposed until independent review. The reusable implementation is
`runtime/decoders/manager.py`; it imports no emulator, binary or mutable goal2 code.

The manager record is 13 bytes: Pascal length followed by twelve payload bytes. The
initial lives separately. Format initial + space + declared surname, bounded to 14;
then project bytes as DOS screen glyphs. Preserve leading/interior/trailing blank
cells. Do not split at NUL, strip controls, replace unknown glyphs or use a guessed
transliteration. The host rejects width/length violations explicitly; the original
does not have that guard.

Germany manager 12 yields `B Vogts ` on the original text-cell projection, with a
last blank; current `Memory.manager_name` yields U+0000 in that last position.
The original writer copies NUL to the character cell unchanged. The shipped
surname's declared length 6 is pre-existing evidence in F002, not a newly guessed
terminator. The screenshot's exact codepoint remains unverified: if the downstream
fix does not remove the symptom, supply the private stopped state, actual formatted
Unicode codepoints, source commit and font/rendering path. The screenshot alone
cannot identify a byte.

The TEAM call site is `1771:157D`: the formatter call at `15D5` is followed
by `214B:026D` at `15E3`, row 10/column 2. See
[the original listing](../../static/goal-exe/code/seg_1771_03.asm) lines 88–95.
The isolated probe uses row 1/column 1 to verify the same cell-copy primitive;
it does not claim to have navigated naturally to the TEAM screen.

## Adoption

In a separate goal2 consumer task, deliberately vendor the reviewed pure decoder
and record its reviewed commit and file SHA256 in provenance. `Memory.manager_name`
must read exactly 13 bytes from `far(MANAGER_NAMES)+13*m` and the byte at
`far(MANAGER_INITIALS)+m`, then call `manager_text`. Validate manager index 0..134
at the host boundary. Keep manager-country lookup and screen construction as is.
Use the runtime record, rather than the original GOAL.DAT, because human names can
change. Include independent German, truncated-length, interior-NUL, maximum-width
and low/high glyph regressions in goal2. Do not change the generic `pstr` globally
without auditing its other contracts.

## Validation

`/home/diego/.local/bin/python3.12 -B -m unittest tests.test_manager_decoder`:
5 tests pass. Before implementation: ModuleNotFoundError, so no false baseline pass.
Original replay (new output path each time):

```sh
tools/heavy.sh T93-original -- /home/diego/.local/bin/python3.12 -B notes/429/probe.py --output /tmp/T93-review-unique.json
```

The fixture is the existing private/released E010-r0001 half-time input cached at
the producer's `BASE` path; its full hash is verified against `runs/E010/E010-r0001.json`.
Receipts pin producer, source files and original input, run 135 genuine names and
five explicit synthetic controls, assert exact formatter payloads, actual character
cells and call returns. These isolated executions do not claim a naturally reached
TEAM screen or independent behavioral corroboration. No original bytes are committed.

The final Git commit and file hashes are recorded on the delivery issue after review
and merge; recompute with `sha256sum runtime/decoders/manager.py`.
