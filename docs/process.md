# Process

`CLAUDE.md` holds the rules, this file how they run, `/run-task` the procedure; each rule cites its lesson.

## 0. Order of work

1. **Evidence first** (for a rebuild): decode, decompile, and write the design with every claim
   tagged `[confirmed]`, `[derived]` or `[designed]`.
2. **A walking skeleton before the fan-out**: scaffolding, the seams the rules plug into, one rule
   end to end, a CLI, and a thin screen a person can use. (L1)
3. **The fan-out**: rules behind the seams, best-evidenced first.
4. **The first playable build**: once the skeleton exists, the UI chain goes before more rules.
   Until it ships, only a bug that breaks play is scheduled (crash, stall, unwinnable game, save
   that will not load, order that can never succeed). (L1)

Tag capability jumps, not phases. Release notes come from GitHub when the tag is cut.

## 1. Roles

| Role | Who | Does |
| --- | --- | --- |
| Main session | Claude, the session the user talks to | Plans, writes task files, runs `/run-task`, triages, merges, reports |
| Implementer | The user's choice (CLAUDE.md "Choosing models" rule 1): the main session in its own worktree, a Claude agent, or OpenCode via `tools/harness/implement.mjs --model <name>`. *Superseded: the GLM-5.3 Flash → DeepSeek V4.1 Flash → Sonnet chain (L42) and L46's heavier-model rule.* | One task, one branch, one PR, in its own worktree |
| Reviewer | The external model the user names (rule 2), via `tools/harness/review.mjs --reviewer <name>`; never the implementer's family (L27). Exit 3: ask the user for another; exit 4: the main session reads the flagged review and decides (L28). *Superseded: the quota-checked Sol / Luna / Opus order (L50, L51, L101).* | Re-runs the Done-when, audits scope and evidence, posts one PR comment, applies the label |
| Decider | Jev via `tools/harness/jev.mjs` (the `/jev` skill) | Repeated yes/no decisions over many items, at the confident ends only (§12) |
| Generator | Models on OpenRouter (images, other families) and ElevenLabs (speech, sound, music) | Assets, each committed with a sidecar naming provider, model, prompt, date and cost |

The user names who implements and who reviews, on which model (CLAUDE.md "Choosing models"
rules 1-2); model ids come from `models.mjs` or `opencode models`, never memory (L25). Quota-tracker's
`/recommend` is shown with each question as a suggestion only; a model whose provider is exhausted
or does not answer goes back to the user, who names another (rule 7). *Superseded: "skip an
exhausted one for the next with quota, saying so" (L50).*
The main session runs `implement.mjs` itself: a wrapper agent would spend tokens watching it.
It watches each background job as CLAUDE.md rules 8-13 say, never with `pgrep -f` (L48).

## 2. Task files

`docs/tasks/T<nn>.md`, 150–400 words, from `docs/tasks/TEMPLATE.md`: Kind, Evidence, Owns,
Scope, Done when, Hazards, Implementer, Reviewer, Merge after. Rules:
- **Owns** names directories or files. Go finer only when two tasks run at once in one file: function-level Owns made one project open 27 PRs that only widened a list. (L5)
- **Done when**: each line is one check a command can run. The main session runs each line before dispatch: it fails on `main` and passes on a mock fix. (L45)
- The main session edits task files directly on `main`, the reason in the commit; the reviewer sees it. (L6)
- **Milestones.** A task likely to outlast one implementer run (about an hour), or whose Done-when is all
  or nothing (an exact match, a whole model), is split into tasks that each merge on their own: the
  static reading (a finding's first part), any tool that produces ground truth, then the deliverable
  piece by piece. A milestone's Done-when measures progress as a number (the first divergent minute,
  the records matched), committed with each push, so a resumed run starts from it. (L102)
- **Orthogonal layers.** A task file's **Owns** and **Scope** sections name the layers it touches.
  Two layers are orthogonal if they can be merged independently: each is testable in isolation, the
  other layer's tests still pass without it, and the other layer is still useful in the field. When
  a task touches more than 3 orthogonal layers, **split it into T<nn>a, T<nn>b, ...** before
  dispatch. Each sub-task is its own mergeable PR with its own Done-when, reviewer, and merge
  cycle. T34 (recorder 2) is the canonical case: 5 orthogonal layers (privacy & nested-display key
  logger; burst detection; scheduler timing; keymap & acceptance guard; CI apt step & latency
  probe) sat on one PR; the rework rounds each surfaced a defect in a different layer, the L38
  / family-rule bind fired per-round for the whole ticket, the 900 s idle limit per round had to
  cover all 5 layers, and the r3 round died without pushing. Per-layer splits would have closed
  each layer in 1 round. Defensive check: when reviewing a task file, ask "could this be two or
  three tasks instead?" If yes, split. The cost of splitting is small (more task files, more
  PRs); the cost of not splitting is what we saw on T34. The retrospective is at
  `goal2-archaeology-work/lessons/T34-too-big-split-by-orthogonal-layer.md`. (L104)
- **Numbering.** Before writing a task file, `git pull` and take the next free number in
  `docs/tasks/`: another session may have written one (T14 was overwritten once, 2026-10-05).

## 3. The loop

`ready → implement → review → approved + green CI → squash merge → follow-up → unblock → report`.
Rework sends the full review back to the same branch, at most two rounds (one for a fix), then
escalates. The implementer script resumes a pushed branch; it never starts over. Before a merge the
main session re-runs the check the approval rests on most; a different result is rework. (L46)

What the implementer script guarantees, and why:
- OpenCode starts with stdin closed; without it a run hangs before it starts. (L10)
- No session in 180 s, no progress in 900 s, or no exit in 3 h kills the run's process tree. (L10)
- The agent is checked on OpenCode's session record (L11); a rejected tool call fails the run. (L26)
- The brief passes by file: the runner writes it to `.harness-brief-<title>.md` at the run
  worktree's root and the command line carries only a pointer, so a long brief cannot exceed the
  command-line limit; the file is never committed, and on failure it is kept with the logs. (L60)
- Each light OpenCode model runs at effort high; a heavy one (Sol, GLM-5.3, DeepSeek V4 Pro) at
  effort low, medium only when justified, never high, except where the provider offers nothing
  lower (DeepSeek V4 Pro: high is its lowest). All run in the scripts' own data directory (L27, L29). The model is the user's,
  passed as `--model` (a harness.json key or `provider/model[@variant]`); the chain (L12) runs only
  without it, which the main session no longer does.
- Exit 0: a PR is open. 1: the main session reads the log (a stop and report, or an early end).
  2: a refused model (DeepSeek, an unknown name). 3: OpenCode unavailable, its model not listed, or
  not logged in; the user names another (rule 7).
- A run our own idle or total limit killed is resumed, not restarted: `--session <ses_...>` with the
  same `--model` and a longer `--total-timeout-sec`, in the kept worktree (rule 13).

How the main session launches and watches a run (L103):
- Detached from its own session, so a restart of Claude Code does not kill the run: `systemd-run --user
  --unit=goal2-<task> --collect -E PATH="$PATH" -p WorkingDirectory=<repo> bash -lc '<implement.mjs or
  review.mjs command> > <log> 2>&1'` (`bash -lc` loads the keys of `~/.profile`).
- The watch follows the unit (`systemctl --user is-active goal2-<task>`), and when a run's worktree holds
  uncommitted work more than 20 minutes newer than its last commit, it archives it outside the worktree,
  read-only (it never touches the run's index).
- An implementer's PR may be a draft; the main session runs `gh pr ready <pr>` before the review.

## 4. The implementer brief

The brief is the task file pasted in full, then this block, then on a rework round the review's URL. The
OpenCode agent file repeats the run mechanics; this block is the contract. A brief never asks an OpenCode
implementer for anything outside its worktree: a line that needs it (a TMPDIR outside every checkout, the
user's install, `.git/info`) is one the main session runs itself (L57).

```text
You implement <T<nn>>. The task file above is the contract.
- Build only what the task asks for, even inside a file it requires; say why for each changed file. (L44)
- A Done-when you cannot meet: stop and report. Never weaken an assertion, skip a test or edit the task file.
- Every new test fails before your change and passes after it; say how you checked.
- If you measure: every output a finding or the PR may cite goes under a tracked path the task owns,
  pushed per batch and every 30 min, never deleted or overwritten; originals out, hashes recorded. (L40)
- A comment that asserts behaviour at an edge comes with the test that visits that edge.
- [research] Static first (U32, CLAUDE.md rule 22): read the decompiled and disassembled code first,
  the named view `static/goal-exe/named/` before the raw `decompiled/` and `code/`; add or correct the
  annotation rows for what the task establishes and regenerate `named/` in the PR (§13);
  run the game only where static analysis cannot answer, or to corroborate. The finding's Method says
  what static analysis was tried and why it was or was not enough. A missing tool: install it, or stop.
- A defect you find outside the task: report it. A one-file mechanical fix that blocks you may
  ride this PR, declared under Scope in the PR body.
- Update any document your change makes wrong, in this PR. Never write status into a document.
- Commit and push after each step, at least every 20 minutes and before any command that runs longer
  than 5 minutes; after your first push, open the PR as a draft (`gh pr create --draft`). A crash then
  loses one step, and the branch shows where you are. (L103)
- A command that can run past 10 minutes never pipes through `tail`/`head`: the run is killed at
  900 s of session silence (L10), before any bash timeout. Run it detached (`nohup … > log 2>&1 &`
  or `setsid`), verify it survived the tool call with `ps`, then poll the log in short calls.
- PR body: Closes #<issue>; Scope (files and why); a fenced block with each Done-when command and
  the tail of its output; Docs changed.
```

## 5. The reviewer brief

```text
<T<nn>> review (<model>)
You review PR #<n> at <sha>. You did not write it. The task file follows.
0. Prove the tree: HEAD is <sha> and the diff against origin/main is the PR's; findings name its files.
1. Re-run every Done-when line yourself, and account for each (L32). The PR's evidence is no proof.
2. [evidence-driven] Every constant traces to a fixture, report or investigation; a [designed] one says what was searched.
3. [seeded] No wall clock, unseeded random or order-dependent iteration in rule code.
4. Every changed file and behaviour is one the task asks for (L44); docs it makes wrong are updated.
5. Sweep the diff: tests that pass with the behaviour deleted (mutate, rebuild clean, re-take any
   negative result), branches no input reaches, edge comments without a test, <project classes>.
6. <docs/review-brief.md in full: "Blocking means" for this task, then its one-pass section (L47, L49)>
Prove each finding (run it, or delete the behaviour and name the test that fails) or label it
unverified. Your final message is the review: the header; the verdict (approve | approve after
named fixes | rework | user decision); per Done-when line `DW<k>: ran <command> → <result>` or
`DW<k>: not run — <reason>`; the findings R1..Rn (file:line, blocking or not); the verdict again
last. Never post it: the script posts it and applies the label.
```

Research briefs here also add, under "Blocking means": G0a (U32, CLAUDE.md rule 22) — runs made
because a static tool was missing, or a finding resting on runs whose Method does not say what
static analysis was tried, is a contract defect: rework.

Run mechanics, added to every brief here: the session is killed after 600 s without activity; keep
every shell command under 5 minutes, and work only inside the review worktree. Undo a mutation by
writing back the file's saved contents (read it first, restore it in a `finally`), never with
`git checkout`, `git restore` or `git reset` of the file: those return the last commit and destroy
any uncommitted work in it (PR 114 round 1). If a reviewer still
reports one blocker per round, stop after the second such round: the main session goes through the
whole diff for the same class of problem before the next review, and records the pattern in
`docs/model-trials.md` (L101).

Practical, not theoretical (the owner, 2026-10-05, after T12 took 4 rounds over a bypass no run
showed): a theoretical bypass is blocking only if it makes a claim false as worded, not merely
unproven. Accept what is about 80-90% likely, worded with its confidence and what remains
possible; narrow a claim's wording rather than add runs or rounds, and file stronger evidence as
a follow-up.

For a Claude reviewer, the main session also runs `/code-review <pr>` on architecture tasks,
always with the PR number: a bare invocation from an agent reviews the wrong tree. (L8)

## 6. Bugs, fixes, triage

Bugs and non-blocking review findings are filed with `triage:needed`: one `T<nn> follow-up` issue
per merge. Triage decides one of:
- **fix**: no ruleset value, fixture value, seeded measurement or golden line changes outside the
  bug's own reproduction. The bug issue is the contract; its Done-when is its reproduction as a
  failing-then-passing test; one review round. (L4)
- **correction task**: anything that changes an outcome.
- **fold** into a task not yet ready, or **close**, with the reason.

Once `breaks-play` is trialled (§12), Jev settles the gate's confident ends; the main session the middle.

## 7. Escalate to the user when

A design question; a Done-when would have to weaken; a third rework round; anything destructive
(force-push, rewriting `main`, deleting an issue); a new external dependency.

## 8. Labels

`task`, `bug`, `fix`, `triage:needed`, `post-playable`,
`status:{ready,in-progress,in-review,rework,approved,blocked,escalated,merged}`,
`review-round:{1,2}`, and `model:<name>` on a PR whose implementer was not the default.

## 9. Measure

After each merge, one PR comment records each Claude agent's token total (from its completion
notice), each OpenCode run's model and duration, and the review rounds. After 10–20 tasks, compare
the rework rate with the baseline in `docs/lessons.md` before changing models. (L13)

## 10. Adding a rule

A rule enters `CLAUDE.md` or this file only with a lesson in `docs/lessons.md`: a failure in a real
run, or the owner's decision with its basis. Plausible rules without either stay out. (L14)

## 11. For a reverse-engineering project

- Transcribe every number from the research into one fixtures corpus with provenance, and assert
  against it: each re-read of a report is another chance to misread it. (L15)
- New evidence runs in two stages: findings to the research repository, then a check of every
  document claim it touches. Each finding is a doc fix, a bug, a task-file edit, or a question for the user; research never decides design. (L16)
- The original files never enter the repository. CI fetches them from a private fixtures
  repository holding the whole corpus; tests find fixtures by name; local tests skip without them. (L17)
- A start state a run record names by sha256 outlives the worktree that made it: it is published
  to the experiment's release as an evidence bundle (`tools/publish_evidence.py`: asset
  `<sha256[:16]>-<name>`, manifest under `evidence/E<nnn>/`, re-verified by
  `tools/verify_evidence.py`; ADR-008). A savestate holds the game's memory: release assets of
  this private repository only, never in the tree; an asset is never deleted or replaced.
- The owner's sittings (E015, `runtime/human/play.sh`) are normal play, not a scenario for a bot
  (the owner, 2026-10-07: "Do not treat me as your playing bot"): every sitting is mined. Run
  `experiments/E015-human-playthrough/extract.py` on it, publish its savestates, update the
  coverage map in that experiment's `protocol.md`, and report what filled and what remains, sorted
  into "any normal play fills it" and "needs a specific moment". Ask for a moment by name only
  when nothing else covers it.

## 12. Delegating decisions to Jev

Jev takes a decision only when it recurs over many items, its answers are known up front, and a
trial against labels has set its cutoffs, recorded in `harness.json` with the numbers. It answers
the confident ends and the main session the middle; a person's decision outranks both. Without its
key it is off. `/jev` has the procedure. (L24)

## 13. The named view

`static/goal-exe/named/` is `decompiled/` with names: routines, the `player` and `country` records
typed on their array pointers, globals. The names live as tracked rows in `static/goal-exe/annotations/`
(`routines.tsv`, `records.tsv`, `fields.tsv`, `globals.tsv`), each with its purpose, confidence
(`established` for a finding's claim, `likely`, `guess`) and basis (a finding id, or `read <file>`
for the lines read). Names are claims: no name without reading the routine; a name read from one
routine without its callers is at most `likely`; no row beats a wrong one. `decompiled/` stays the
raw baseline; where the two views disagree, the listing decides.

Each research task adds or corrects the rows for what it establishes, with its finding as basis,
runs `python3 tools/static/check_annotations.py`, and regenerates `named/` in its PR with the command
in `static/goal-exe/named/README.md`. Only rows change by hand; `named/` never does.
OpenCode runs cannot run Ghidra (it lives under `~/tools`, outside their worktree): an OpenCode
brief says "do NOT run Ghidra; the main session regenerates named/ after you push (L57)", and
its review brief says the same for the reviewer. Claude agents and the main session can run it.
