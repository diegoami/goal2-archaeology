# outputs/

- `20261016a`, `20261016b`, `20261016c`: runs of `run_all.py` at three stages of the probes. Their `gaps.*.txt` and
  `bytecmp.55.txt` first listed the raw bytes of the GOAL (and candidate) instructions. A review found that more than
  the short identifying patterns the project allows (rule 18), so the byte columns were removed from these files
  in place (the instruction text and counts are unchanged; the first commits of this branch still hold the bytes in
  git history, which a branch squash or rewrite would drop). Everything else in these folders is as the run wrote it.
- `20261017a`: the run the README cites. `gaps.*.txt` give, per stretch, offset, length and sha256 of GOAL's bytes
  plus the masked mnemonics, never the bytes; `startup.py`, `movecheck.py` and the routine table are in `run.log`.
  The generator (`gaps.py`, `bytecmp.py`, `movecheck.py`, `sysseg.py`) no longer prints bytes, so a rerun does not
  bring them back (`hexscan.py` counts what is left).
