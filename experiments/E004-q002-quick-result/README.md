# E004 q002-quick-result

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T10 (#26)
- **Question**: Does the quick result (`R`) run the same engine as a watched match? (G5 Q002)
- **Hypotheses**:
  - H0: from one seeded start state, the quick result and the watched match give the same final score, the same commentary events (goals, own goals, bookings, sendings off, injuries, substitutions) and the same `DS:7B62` at full time — distinguished by the pairs' full-time reads
  - H1: they differ; then each arm is still deterministic from one state (its replays identical), and whether their goal, booking, sending-off and injury distributions differ is tested on 100 matches per arm over 100 DOS minutes — distinguished by the replays and the sample
  - static: `r` reaches a routine that computes the result by the step routine of the watched match with the display off (H0), or by another routine (H1) — distinguished by tracing `0791:9372` → `0791:92FC` and the readers of the flags it sets
- **Artifact**: set `goal2-a949da2f`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on Ubuntu 24.04 in WSL2, `cycles=30000` (fixed: the guest's timing does not follow the host's speed; F001 M:match-speed's fastest fixed setting; Q003 asks whether cycles change a match); maximum intervention level I3 (the DOS date and time set in the autoexec before GOAL runs, verified by DOS's read-back, F004)
- **Design**:
  - start states (`run.py make-state`): a fresh launch at DOS time 10:00, 10:01, 10:02 and 13:37 on 10/04/2026 (I3), F001's keys to the main screen (`n Enter Enter b o b Enter Enter Enter Enter`), then `Esc Up Enter Enter` (main menu, next game, the other results, the captain screen), and an Enter on the team screen where it comes before the captain screen (10:02, 13:37); Host+S at the captain screen; stored as `e004-HHMM` in `.cache/states/driver/` with the drive layout (git-ignored; sha256 in every record). Four fixtures: Denmark v Sweden, Denmark v England, Denmark v Wales, Sweden v Denmark (all friendlies)
  - arms (`runtime/driver/match.py`): `quick`: Enter and `r` in one burst (F004's d3b); `watched`: Enter and Right ×5 in one burst (the game's speed to its top, as F001 M:match-speed). Then, in both, an Enter only on a stable screen that shows `hit any key` before full time or the team screen; no other key; the match ends at the first stable screen whose commentary rows hold `FULL TIME`. Every key, its moment and its reason are in the record
  - pairs (`run.py pairs`): per start state 5 pairs, each a quick result and a watched match, each from a fresh process and a Host+L restore of the state; the 5 runs of an arm from one state are replays of each other (Done-when 3)
  - sample (`run.py sample`, only if a pair differs): 100 quick results and 100 watched matches, one per DOS minute 10:00 … 11:39 on 10/04/2026, each a fresh launch at that minute (I3) with the keys of the start states (plus the team screen's Enter where needed) to the captain screen, then the arm's match; the two arms over the same 100 minutes
  - stopping rule: those records written; an aborted run is kept and its minute or pair repeated once
- **Measurements**: per read during the match (a savestate, polled without sleep): host UTC time, screen digest, the commentary rows, the commentary counter `DS:80EE`, `DS:7B62` and the score bytes `DS:9B3C`, `DS:9B3D` (memory, I1); the commentary records added since the previous read, from the ring `DS:7C38` (`runtime/driver/commentary.py`); at the restore or title, the main screen, the captain screen and full time: the full screen, the BIOS mode byte and tick count, `DS:7B62`, `DS:7B64`, `DS:8336`, `DS:A9FD`, the score bytes and the delay byte at `[DS:A923]+0x3F`. Per record: launch time, config and its sha256, the DOS clock read back, the keys sent in the match, the number of reads and the seconds, DOSBox-X output lines, process exit, every wait (log).
- **Analysis** (`summarise.py`): per pair, the final score (screen), the events, `DS:7B62` at full time, and whether the pair is identical; per state and arm, whether each replay equals the first; for the sample, goals, bookings, sendings off and injuries per match per arm, with a two-sided permutation test of the difference of means (label shuffle, 20000 permutations, fixed seed) and a paired sign-flip test over the same minutes, per measure.
- **Outputs**:
  - run records: `runs/E004/`;
  - evidence manifests: none (savestates hold the game's memory and stay in `scratch/` and `.cache/`);
  - `findings/F005-*.md`, status `proposed`.

## Scripts

```
bash setup/goal2-runtime.sh
python3 experiments/E004-q002-quick-result/run.py make-state --dos-time 10:00:00   # and 10:01, 10:02, 13:37
python3 experiments/E004-q002-quick-result/run.py pairs --state e004-1000 --pairs 5 --batch p1   # each state
python3 experiments/E004-q002-quick-result/run.py sample --arm quick --minutes 10:00-11:39 --batch s1 --slot 1
python3 experiments/E004-q002-quick-result/run.py sample --arm watched --minutes 10:00-11:39 --batch s1 --slot 2
python3 experiments/E004-q002-quick-result/summarise.py
```

## Amendment 1 (2026-10-04, after E004-r0007)

The first watched sample (`sample --arm watched --minutes 10:00-11:39`) was stopped by hand (SIGINT) during its first run, because one invocation of 100 watched matches would outlast the 2-hour bound of the session that runs it; the driver terminated its DOSBox-X and Xvfb, and no record was written. Its run id E004-r0008 was reserved and is not used. The watched sample is run in chunks of minutes instead (10:00-10:39, then the rest); the design is unchanged.

## Amendment 2 (2026-10-04, after E004-r0242)

- **The match bound.** E004-r0200 (watched, DOS minute 11:36, run while three sessions ran at once) was still in its second half when `runtime/driver/match.py`'s first bound, 300 s, ran out (531 reads; its last screen a computer substitution notice, `press any key`); the record is kept, status aborted. The bound is now 900 s, about three times the longest completed watched match, 288.7 s (E004-r0133). The minute was repeated once, alone: E004-r0242 (batch `s1-repeat`, completed).
- **E004-r0200's keys.** Its observation "keys sent from the key that starts the match" reads `[]`, though the starting burst `Enter Right Right Right Right Right` was sent: that field was filled only when `play` returned. Its `log` observation (`match watched: starting keys Enter Right Right Right Right Right sent in one burst`) shows the burst. From commit `c3bfb59` the keys and the read count are held by the runner as they happen, so an aborted match's record carries them.
- **E004-r0231's script hash.** Its `actions.sha256` (`77b6e12c…`) is the hash of a working-tree `run.py` edited while that process ran (the edit of `c3bfb59`); the process ran `run.py` of its `code_commit` `6ed687a` (sha256 `68cc4f44…`, as every other record of that invocation). From `c3bfb59` the hash is taken when the script loads.
- **Artifact set.** T11 registered the successor set `goal2-67cf27d6` (the same ten files) while E004 ran, and origin/main was merged at `b6f1c96`. Records of invocations started before the merge name `goal2-a949da2f`: E004-r0001 … r0085 and the quick sample and the first watched chunk up to r0230 (170 records: pairs of e004-1000, e004-1001, e004-1002; the quick sample; the watched sample 10:00-10:39). Records of invocations started after it name `goal2-67cf27d6` (71 records: pairs of e004-1337, r0089 … r0119; the watched sample 10:40-11:39, r0093 … r0241; r0242). `summarise.py` does not depend on the set.
- **Analysis, added before the sample was summarised.** (1) Goals per match are the score bytes `DS:9B3C` + `DS:9B3D`, not the goal lines: `0791:1D4A` does not write a record equal to the newest one (`0791:1C78`, seg_0791_03.asm:817-835, 849-855), so two goals by one player with no line between are one line (E004-r0053, r0198, both quick); the score bytes equal the scoreboard in every record. (2) A goal line followed by `… is OFFSIDE` does not count (24 lines; the score bytes count them out in every case). (3) Bookings and red cards of the watched matches' full-time statistics screen are compared with the commentary's.
- **A commentary gap flag.** E004-r0232's first match read found 101 new lines, at the flag's limit (half the ring of 200); fewer than 200 lines lose none, and its bookings, red cards and goals agree with its statistics screen and score bytes.
- **Seeds of the sample.** The DS:7B62 word at the captain screen takes 29 values over the 100 minutes (most often `0x8101`, 27 records); with the fixture, 93 distinct start conditions per arm: some minutes repeat another minute's match exactly.
