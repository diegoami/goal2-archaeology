# E036 the match port: notes and provenance

Route C of [`docs/match-engine-plan.md`](../../docs/match-engine-plan.md): the watched engine translated from the listing into
Python, memory-faithful, plugged into the original-match kit (`runtime/original_match/`, issues 250 and 252) in place of the
original's routines through the same hooks, and accepted when whole matches stay identical draw for draw. The end state is a
pure-Python engine that equals the original over the seed families with no GOAL.EXE bytes needed at run time (the owner's
decision, restated in the brief of 2026-10-17). The work is the backlog `docs/tasks/T57.md` to `T80.md`; this page holds no
status (the issues' labels do).

## Layout

- The ports: `runtime/original_match/port/`, one module per task (vendored with the kit, standard library only, no byte of
  the original). Each module registers its own ports, so tasks that run at the same time own different files.
- The scripts of this experiment (T57, T59): `family.py` (run a family through the kit, with or without ports), `compare.py`
  (fail closed), `locate.py` (the first differing minute, then the first differing call), the family definitions; a
  family or scenario a later task adds is a file of its own under `families/`, with its reference.
- Each task's outputs: `out/T<nn>/`, never deleted or overwritten; each task's notes: `notes/T<nn>.md`.
- Records hold counts and digests only: no commentary text, no player name, no byte of the image (rule 18).

## The acceptance rule every porting task uses

A porting task is accepted when, with its ports hooked, every match of the families equals its declared unhooked reference
(the T57 baseline or the T73 display profile below: score, ticks, every main-RNG draw by its digest and per minute, the board, the commentary's templates, the result,
the events, the records after the post-match update), and the same holds with every port merged on `main`; and when each of
three falsifiers (a one-line mutation of a ported routine on a branch the families reach, the reach counted first, L105)
changes or stops a match. A routine that stays non-exact after an hour of locating is accepted non-exact with its
divergence recorded (the plan's one-hour rule); two such in one task go to the main session.
Each task's Done-when and the owner's strict acceptance decisions take precedence over that historical fallback.

T73 runs containing `display`, including `--ports all`, select the strict
[display profile](families/display/profile.json). Compare these runs with `--no-screen`:
the comparator uses the profile's bound unhooked reference, compares every DS block under its declared byte mask
(currently `[]`), and excludes the screen digest and only the duplicate `full_time.data.screen_sha256` event field.
Every other event field/count and every record, draw and seed remain compared. Ordinary unprofiled `--no-screen`
keeps its legacy behavior. The original-access proof and reference provenance are in [T73's notes](notes/T73.md).

The families (T57; T76 adds a set-piece scenario to S, T77 adds R): F40 (the reference fixture, Denmark v country 19 at
calendar number 21 from E006-r0001: 20 seeds as they are and the same 20 with declared edits), O8 (other country pairs),
S (the kit's scenarios from E033 and E034: decisions at pauses and half time, an injury, sendings off, quick results,
extra time, shoot-outs with sudden death, a qualifier), R (states that reach the frontier). ALL is their union; each
family names its own reference (the unhooked kit), so a family added later brings its reference with it.

## The commands (T57, T58 and T59 build them; the porting tasks use them as written here)

- `python3 -B experiments/E036-match-port/family.py --family ALL [--ports M,...|all] [--variant M.NAME]
  [--count SSSS:OOOO,...] [--max N] [--workers 1|2] --out experiments/E036-match-port/out/T<nn>/<name>.jsonl`:
  one record per match (`records.py` is the grammar); resumable (a rerun with the same `--out` adds only the matches not
  yet in it, never rewrites a line, and refuses a log that is not this run's); `--count` counts the executions of any
  instruction address, a routine's entry or a branch's target (L105's reach count), skipping the kit's replays.
  T57 builds `--family`, `--out`, `--max`, `--workers` (the default is one process; two at most), `--count`, `--only ID,...`
  (a few matches), `--time-limit S` (per match, default 300), `--stretch-limit S` (the kit's watchdog per stretch
  between two events, default 60, at most `--time-limit`; a slow machine with every port installed needs more, #357), `--checkpoint DIR`
  (each running match saved there every 10 minute events, so a run killed mid-match resumes inside it with the same
  command, to the record a straight run writes; #359), `--mask FILE` (a JSON list of `[space, start, length]`, space
  `DS` or `P`: the bytes zeroed before the memory digests are taken, none by default; the record carries it and
  compare.py refuses two masks) and `--find-ranges FILE` (the write watch that found `records.RANGES`, out/T57). T59
  builds `--ports` and `--variant` (the kit's port mode; the record then carries `ports`, `variant` and `port_calls`, and
  compare.py refuses a ported reference).
  Later: `--engine port --no-unicorn` (T78: the engine on its own, `import unicorn` made to fail first) and
  `--from-records` (T80: the start state given as records, not as an image).
- `python3 -B experiments/E036-match-port/compare.py --family ALL --candidate <file> [--reference <file>]
  [--expect differ] [--no-screen]`: against each family's reference (`--reference` names one log for all); exit 0 as
  expected, 1 not, 2 malformed or missing evidence (never a pass); names the first differing field, the minute where
  the draws first differ and the first differing 1 KiB block of memory. `--e032 --candidate <reference>` prints, per
  seed, F40's ten E032 matches against `check.py`'s `EXPECTED_FAMILY`.
- `python3 -B experiments/E036-match-port/locate.py --family ALL --candidate <file> --match <id> [--out <new file>]`:
  the first differing minute, then the first differing call of a ported routine, proved side by side (T59; the kit's
  `Match(prove=N)`, port/prove.py): the routine, its call, the byte or the register. Exit 0 located, 1 not, 2 refused.

**Heavy jobs (#318).** A match run is a heavy job: `family.py` (and `check.py`, `--find-ranges` included) waits for a
slot of `tools/heavy.sh` as its first act, so at most four run at a time on the machine, across every agent and
review (harness.json `heavy.slots`; two until 2026-10-18), and `--workers 2` holds two slots. It prints `heavy: family: waiting for a slot
(k ahead)` while it queues and then runs unchanged; inside another heavy job it runs at once. To name the slot or
run anything else in it: `tools/heavy.sh <name> -- <command>` (a review has `heavy.sh` on its PATH);
`heavy.sh --status` lists the slots and the queue. The old line "at most one match process at a time" in briefs
is this rule: do not start a second family run by hand beside the lock. docs/environment.md "Heavy jobs".

**Where a family runs (the owner, 2026-10-22; #361).** One match takes one core; a family is 62 matches, so a run's
wall time is the matches over the cores. Measured on 2026-10-22/23 (T62-T70): one port installed, about 60 s of CPU a
match on the owner's machine and 200-550 s in a cloud session (3-4x slower, and its container restarts); every port
installed, 1,500-2,200 s a match in a cloud session, about 500-1,900 s on an Actions runner.
- *GitHub Actions* (`.github/workflows/family-run.yml`, the default for full runs of the port tasks): a
  `workflow_dispatch` on the task's branch splits the selection into shards (`shards.py plan`), runs each as an ordinary
  `family.py --only <shard> --workers 2 --checkpoint ...` job, and its collector joins them in the family order
  (`shards.py collect`, which refuses a match missing or twice) and commits them with each shard's log and a manifest to
  `out/<task>/<name>-<run id>/` on that branch (a re-run of the same run: `<name>-<run id>-attempt-<n>`, #364).
  Dispatch, then pull the branch after the run and compare the joined file:

      gh api -X POST repos/diegoami/goal2-archaeology/actions/workflows/family-run.yml/dispatches -f ref=<branch> \
        -f 'inputs[task]=T<nn>' -f 'inputs[name]=all-actions' -f 'inputs[family]=ALL' -f 'inputs[ports]=all' \
        -f 'inputs[count]=<the row's addresses>'      # a falsifier: inputs[name]=falsifier-<v>, inputs[family]=O8,
                                                        # inputs[variant]=<module>.<v>; the unhooked kit: inputs[ports]=
      gh api "repos/diegoami/goal2-archaeology/actions/workflows/family-run.yml/runs?per_page=3" \
        --jq '.workflow_runs[] | "\(.id) \(.status) \(.conclusion) \(.head_sha[0:8])"'
      git pull --ff-only origin <branch>
      python3 -B experiments/E036-match-port/compare.py --family ALL --no-screen --candidate out/T<nn>/all-actions-<id>/all-actions.jsonl

  31 shards (the default) run at most 20 at a time; an integrated run took 40-50 min of wall time and 570-600
  runner-minutes, billable 0 on this public repository (each run's `GET .../actions/runs/<id>/timing`). The joined
  file stands in for the Done-when's `out/T<nn>/own.jsonl` or `all.jsonl` (the PR says so). A shard's slowest match
  (an S knockout with every port) took up to 37 min: a job over 30 min is not yet stuck (`--time-limit 6000`).
- *A desktop with more cores*: the same shards by hand. `shards.py plan --family ALL --shards <cores/2>` prints the
  `--only` lists; run each as its own `family.py ... --workers 2 --checkpoint .cache/checkpoints/T<nn> --out
  out/T<nn>/<name>-s<i>.jsonl` under `HARNESS_HEAVY_SLOTS=<cores>`, then `shards.py collect --family ALL --out
  out/T<nn>/<name>.jsonl out/T<nn>/<name>-s*.jsonl`. Only cores and their speed matter (no GPU); under WSL keep the
  checkout on WSL's own disk and give it every core (`.wslconfig`).
- *A cloud session*: samples only (`--only` a few matches); commit outputs about every 5 minutes and run long jobs with
  `--checkpoint` (#359), since its container restarts.

A family is a file under `families/` (`F40.json`, `O8.json`, `S.json`; `families.py` documents the format): its matches
(fixture, managed side, seed, declared edits of the records, answer policy) and the path of its reference log. A new
family or scenario is a new file there, found with no list to edit; a policy a scenario needs that `families.py` does
not have is a class in a `families/*.py` file (`POLICIES = {name: class}`). A match's spec digest includes its policy's
code, so a record only compares with a reference made by the same declaration.

## The rules every porting task follows

1. Static first (rule 22): the named view `static/goal-exe/named/`, then `code/`; each constant cites its listing line
   (rule 17).
2. A port reads and writes only through the port's memory view (T58): a write that bypasses it loses an event or a draw
   without an error. A routine it calls that is still the original's is called as the listing calls it, `yield
   call(target, *args, ret_to=..., far=...)` (T59, port/guest.py), with the registers the listing hands the callee. A ported routine that holds one of the kit's sites (`match.py`: key-read return addresses, the polls,
   `F2E3`, `9B15`, `9D67`, `A1EF`, the table reads) fires it at the listing's point.
2a. The stack is part of the acceptance (T60): the family digests cover the stack segment, so a retained routine writes the frame the
   listing's code writes (saved BP, locals, the pushes and return addresses of the calls it makes, and the callees'
   frames), not only the data it changes. The proof leaves the dead frame out; the family comparison does not.
   `out/T60/fuzz.py` checks a port against the original on random inputs with the frame included.
3. Accepted when ALL is identical with the task's ports and again with every port on `main` (after rebasing), and three
   falsifiers are caught, each on a branch the families reach (counted with `--count` first, L105); a branch no family
   reaches gets a unit test on a synthetic memory view with the listing's values.
4. The one-hour rule above; two non-exact routines in one task go to the main session.
5. Annotation rows for each routine read (purpose; `established` when exact on ALL, else `likely`), `check_annotations.py`,
   and `named/` regenerated last, after rebasing (two tasks at once touch the same rows file).
6. Family runs are detached (L103). Use the desktop/Actions sharding and heavy-slot capacity described in "Where a family
   runs" above, with at most two workers per shard and checkpoints. Outputs go under `out/T<nn>/`, never overwritten,
   pushed after each batch and every 30 minutes.
7. The PR states the milestone number: the routines of the task's row ported and exact, and each one's calls per match.

## The sizes of the backlog (static, no run)

`sizes.py` assigns every routine of the static call closure of run_match `0791:F1F6` and the post-match update `0791:B7FA`
(what the kit runs as the original's code) to one task or to OUT with a reason, and fails on any routine left over; it
counts each task's static instructions (`static/goal-exe/routines.tsv`) and turns them into hours at the plan's three rates
of the E032 pilot's pace, with every other figure a named assumption. E032's six coverage runs say which routines a match
reaches between kick-off and full time.

- Current: `out/backlog/sizes-20261017d.md` and `.json` (2026-10-17, on the tables of `c7e1969`): 540 routines, 37,618
  static instructions in the universe; 442 routines (33,299 instructions) in 24 tasks, 98 (4,319) OUT; 0 problems; 111.7
  hours of work at the central rate (80.9 optimistic, 173.6 pessimistic), 65.0 elapsed on two workers (49.5, 96.1).
  SHA-256 `99f6f447699ee3bd4876874df56ce2b615d54a335568792b8d259a5b6b9bef55` (`.md`),
  `abf9a5b7cf0a730690604ba7f5a770355adeaedcb4c23355f66283da8a11e534` (`.json`).
- Superseded, kept: `sizes-20261017` (`099228de…`, `c7d92f4f…`: 1829 counted as commentary, though E032 removed it as
  display; no hour for the fixture with no managed side); `sizes-20261017b` (`3f8a9723…`, `3537aee1…`: two workers taking
  the tasks in index order); `sizes-20261017c` (`612cb908…`, `cd5dbdfb…`: the longest chain first, but a worker waited
  for a task whose dependency had not finished while another could start).

What the sizing found that the plan did not count:
- The plan's steps call each other's routines (for example `2AA3` calls `emit_commentary 1EB5`, `move_ball 83A2` calls the
  dead-ball routines and `82EB`, `dead_ball_throw_in 6E11` calls `check_substitutions 8062`, which opens the team menu), so
  a port must be able to call a routine that is still the original's (T59).
- The kit runs more than kick-off to full time: the set-up's own callees (`2648`, the computer's lineup `B11F` and its
  helpers, the sorts), run_match's tail (`CAB0`, `CB7D`, `update_group_tables 1771:8757`, `D050`, `BC5D`), the post-match
  update `B7FA` and `BA4E`, the menus and prompts a decision goes through, and the quick result `D733` from a pause.
- Runtime routines the engine calls beyond the RNG, sets and longs: min and max, clamps, fills, moves, Pascal strings
  (Turbo Pascal 5.5's, E035).
- The pitch picture `[DS:7C16]` is engine state (E032 notes, "Why 8537 and 8E24 stay"); every write to it stays, whatever
  routine makes it.
