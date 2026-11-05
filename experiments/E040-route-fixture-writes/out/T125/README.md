# T125 assistant evidence

Method: read named 0791 DAF8/DB38/DBFA/DC7E and 1771 55FC first, then their complete assembly listings. Static analysis establishes exact control flow, record offsets, call frames, the unsigned comparison and two passes. The original-backed runs corroborate that transcription with real original callees and entry frames on explicitly synthetic records over a hash-verified published image. No guest bytes are published.

`baseline/unit-red.log` is the missing-module preimplementation failure. `ports-v1`/`ports-v2` are retained failed calibration runs; the latter exposed an incorrect synthetic expected pool order, corrected only after original `oracle-v2` established pool `[1,2,...]`. `ports-v3` passes the six focused tests.

`oracle-v1` is **not acceptance evidence**: its outer return did not dispatch the Prover completion hook, and its refusal keyboard boundary was absent. `oracle-v2` adds the return handler and real key boundary service; each accepted outer routine must have `proved: 1`. No earlier attempt is overwritten.

The sealed consumer API is documented in `runtime/original_match/assistant.py`. It installs only real existing port entries (no display stubs), runs DC7E on copied state/tables, and reports the original finals/tour refusal. Full suites/gates remain CI work under the owner's instruction.
