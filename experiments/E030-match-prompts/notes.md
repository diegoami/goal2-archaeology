# E030 Prompts around a match (T56, issue #226)

Read-only over the committed records `runs/E015/E015-r0013.json` and `runs/E015/E015-r0017.json` (the owner's
sittings of 2026-10-15). No game was run and no savestate was written (I0). The finding is
`findings/F030-*.md`.

## Files

- `prompts.py`: for each record, the text screen of every snapshot (a screen the extractor did not list keeps the
  previous text, as in E029's `screens.py`), the snapshot's UTC time from its file name, and the byte
  `[A923]+0x41` of the game-state block; tags the screen with a prompt class; writes
  `out/<run>-prompts.tsv` (one line per snapshot) and `out/prompts-summary.txt` (per prompt: the snapshots that hold
  it, the runs of consecutive snapshots, the class of the snapshot that follows and the seconds to it, the scoring
  side before each replay or save-the-goal prompt). Usage from the repository root:
  `python3 -I experiments/E030-match-prompts/prompts.py`.
- `out/inputs.sha256`: the sha256 of the two records read.
- `out/session-folder.txt`: a directory listing of the owner's git-ignored session folder (outside the repository;
  a listing, not a record), kept because question 5 of F030 asks which file the game wrote. It is an observation
  of this machine on 2026-10-15; the file contents are not read.

## How to read the logs

- The recorder takes a snapshot every 5 s (its `DEFAULT_CADENCE_S`, `runtime/human/recorder.py:107`) and 0.05 s
  after a key burst settles, so a gap of 1-5 s to the next snapshot may have been cut short by a key and a gap of
  15-20 s is a stretch with no tick. A prompt that is on two snapshots lasted at least the time between them; a
  prompt that is on one snapshot lasted less than the time from the previous snapshot without it to the next one
  without it.
- Counts are over the snapshots of one record (865 in r0013, 297 in r0017). A prompt that was on screen between
  two snapshots is not counted; the logs say what the snapshots hold, not how often the game asked.
