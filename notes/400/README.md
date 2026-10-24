# T86: genuine nearby machine input for G13

[confirmed: T84 inventory / E031 saves.tsv at 3cf746abec51dd11dadc695a65f4fb32df7701c8]
G4C.GL is Holland immediately before the World Cup 2030 last16 against Belgium. It avoids
starting another multi-year campaign. Its SHA-256 is recorded in every attempt and verified
before launch, after copying into each private game directory, and after collection.

[derived: static-first F015/F030 readings in notes390] The earlier extra-time/taker decisions
need pre-input machine states; the supplied shootout announcement is already past extra time.
A .GL is not a CPU checkpoint, so static analysis cannot supply this machine input. `collect.py`
uses the pinned original DOS loader, original keys and read-only savestate observations, with
no guest-memory edit, CPU rewind or fixture construction. Its private Xvfb and game copy are
separate from the active port checkout. The DOS date/time intervention is explicit and saved
in the record. A newly loaded .GL is not claimed seed-equivalent to E031's old run.

Raw attempts `load-r1` and `load-r2` are retained as aborted. The first escaped the title before
the filename prompt; the second reached the editor with a carried title Y, producing Yg4c and
a file-not-found response. `load-r3` cleared the original 80-character editor through actual
Backspace keys, typed g4c and Enter, and captured the real ensuing manager menu. The driver
key/events and every observed screen are append-only records, including both aborts.
`collect.py` is the final collector version; the attempts' base Git head identifies the unchanged
original driver. The recorded original keys, rather than a claim that the three collector
revisions were identical, identify each intervention.

The accepted machine input is named and hashed in `delivery.json`. It passes the corrected
upstream build guard and has one saved original read frame returning to 000E:75D1. The frame
and file hashes are verified by `python3 notes/400/verify.py`. Upload to the existing private
Drive was read back and verified by hash. The private source and savestates are never tracked.

This delivery captures **only the original-loaded manager menu**, not yet a taker, extra-time
menu or vacancy warning. It supplies a cheap starting point for a short original-key core
continuation. Do not call the missing decision cases completed or use the .GL as their CPU
state. Their original contracts remain the T84 static evidence until reached.

Review supplements (raw attempts remain untouched): `collector-provenance.json` pins the
unchanged r3 collector as committed after that run. The earlier two aborted revisions were
not pinned and are not retroactively claimed identical. Future attempts now record the
collector's own hash and archive it before launch. The delivery verifier checks the manifest,
local private readback, delivered name/hash and the actual post-load RNG words (F004).
The wider request #400 remains open; this PR references it and supplies only a starting input.
