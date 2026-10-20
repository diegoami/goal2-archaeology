# Process

[designed: owner, 2026-10-20] How a task runs; the rules are in `CLAUDE.md`. The earlier process
(review harness, family rule, worktrees, Jev, lessons register) is kept on the branch `local`;
sections keep their numbers because other files cite them.

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

The main session (Claude Code or Codex, locally or in a cloud session) plans, writes task files,
implements or spawns the `implementer` subagent, runs the checks, merges and reports. Reviews are
optional per PR (`tools/review_pr.sh`, any model) and mandatory in spirit at milestones
(`tools/milestone_review.sh`, [milestone-review.md](milestone-review.md)). Ghidra and the pinned
tools under `~/tools` are run by whoever has them; a cloud session gets DOSBox-X 2024.03.01 from
`tools/cloud_setup.sh` ([cloud.md](cloud.md)).

## 2. Task files

`docs/tasks/T<nn>.md`, 150–400 words, from `docs/tasks/TEMPLATE.md`: Kind, Evidence, Owns,
Scope, Done when, Hazards, Implementer, Reviewer, Merge after. Rules:
- **Scope** says in one line what the task protects (the claim, guard or measurement a reviewer must
  not let anything past); on a guard task it lists the forbidden actions or results. The review
  brief's "Blocking means" item 2 names the same.
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

`ready → implement → (optional review) → green CI → merge → follow-ups → report`

1. **Check** the task is ready and its Merge-after tasks are merged; its Done-when lines fail on `main`.
2. **Implement** on the work branch (below) with §4's brief; commit and push after each step and
   open the PR as a draft after the first push.
3. **Review, when warranted** (a finding, a game rule or constant, the engine port, the proof):
   `tools/review_pr.sh <pr> <cli> <model>` posts one review comment. Rework goes to the same branch;
   non-blocking findings become one `T<nn> follow-up` issue.
4. **Checks**: every Done-when line on the PR head, and green CI (`.github/workflows/ci.yml`; its
   gate, `tools/ci_gate.py`, picks what the change obliges).
5. **Merge** with a merge commit: `gh pr merge <pr> --merge --match-head-commit <sha>`; then locally
   `git switch main && git pull`, in a cloud session `git pull --ff-only origin main`.

**Branches.** [designed: owner, 2026-10-20, as in goal2 and malpaco] Locally each task has its own
branch, `task/T<nn>-<slug>` from `origin/main`. A cloud session starts on its own `claude/…` branch
and may push only there, so that branch is the work branch for every task of the session, one PR per
task, brought level with `git pull --ff-only origin main` before each. Every PR merges with a merge
commit (research PRs need their commits, rule 20; a cloud branch then fast-forwards). A PR still open
when a session ends is continued by the next session.

## 4. The implementer brief

The brief is the task file pasted in full, then this block, then on a rework round the review's URL.
The `implementer` agent file repeats the run mechanics; this block is the contract, for the main
session implementing directly as much as for the subagent. Ghidra and the pinned tools under `~/tools`
are the main session's to run where an agent cannot reach them (L57, §13).

```text
You implement <T<nn>>. The task file above is the contract.
- Build only what the task asks for, even inside a file it requires; say why for each changed file. (L44)
- A Done-when you cannot meet: stop and report. Never weaken an assertion, skip a test or edit the task file.
- Every new test fails before your change and passes after it; say how you checked.
- If you measure: every output a finding or the PR may cite goes under a tracked path the task owns,
  pushed per batch and every 30 min, never deleted or overwritten; originals out, hashes recorded. (L40)
- A comment that asserts behaviour at an edge comes with the test that visits that edge.
- A Done-when that names a real mechanism (a window, a chord, a device) is met by that mechanism, never by a stand-in
  for it; with only a stand-in, report the line as unverified and stop. (L106)
- Report the suites' results from the final commit; after a later code change, re-run them, or say the results are stale. (L106)
- [research] Static first (U32, CLAUDE.md rule 22): read the decompiled and disassembled code first,
  the named view `static/goal-exe/named/` before the raw `decompiled/` and `code/`; add or correct the
  annotation rows for what the task establishes and regenerate `named/` in the PR (§13);
  run the game only where static analysis cannot answer, or to corroborate. The finding's Method says
  what static analysis was tried and why it was or was not enough. A missing tool: install it, or stop.
- A defect you find outside the task: report it. A one-file mechanical fix that blocks you may
  ride this PR, declared under Scope in the PR body.
- Update any document your change makes wrong, in this PR. Never write status into a document.
- A heavy job (a match run, a family run, check.py, the unit suite) runs as `tools/heavy.sh <name> -- <command>`:
  four at a time on a machine, the rest queue and say "waiting for a slot (k ahead)"
  (docs/environment.md "Heavy jobs"). family.py, check.py and `tools/ci_gate.py run-tests` queue themselves.
- Commit and push after each step, at least every 20 minutes and before any command that runs longer
  than 5 minutes; after your first push, open the PR as a draft (`gh pr create --draft`). A crash then
  loses one step, and the branch shows where you are. (L103)
- A command that can run past 10 minutes never pipes through `tail`/`head`: an agent's tool call
  has a timeout of its own (L10). Run it detached (`nohup … > log 2>&1 &` or `setsid`), verify it
  survived the tool call with `ps`, then poll the log in short calls.
- PR body: Closes #<issue>; Scope (files and why); a fenced block with each Done-when command and
  the tail of its output; Docs changed.
```

## 5. Reviews

A review re-runs every Done-when line, proves its findings (a command, or a mutation a test fails
on) or labels them unverified, and posts one comment on the PR. Blocking means a claim false as
worded or a defect a user of the spec would hit; a theoretical bypass of tooling is a follow-up
(CLAUDE.md rule 23). For an engine task a rework review may re-run the seeded sample (F40 seeds 1-5,
2 of O8, 2 of S), the unit tests and the mutation checks, and verify committed family outputs by
sha256, instead of the full 62-match family run (#319).

## 6. Bugs, fixes, triage

Bugs and non-blocking review findings are filed with `triage:needed`: one `T<nn> follow-up` issue
per merge. Triage decides one of:
- **fix**: no ruleset value, fixture value, seeded measurement or golden line changes outside the
  bug's own reproduction. The bug issue is the contract; its Done-when is its reproduction as a
  failing-then-passing test; an optional review. (L4)
- **correction task**: anything that changes an outcome.
- **fold** into a task not yet ready, or **close**, with the reason.


Scheduling follows CLAUDE.md rule 23 (the owner, 2026-10-18): the route-C engine port comes first.
Hardening, defence-in-depth and edge-case work on the proof or the tooling is not fixed
ahead of the port, unless it blocks a port task or breaks the proof for ordinary use. It is recorded
as a follow-up issue that states the known limit and its acceptance (what would close it), and,
where the limit concerns a mechanism, as a note in the docs too. A reviewer's finding that is a
deliberate-reflection or adversarial-use route, when the port's own code does not use it, is
likewise a known limit with a follow-up issue and is not reworked again. The owner decides when a
limit is worth closing.

## 7. Escalate to the owner

A design question; a Done-when that would have to weaken; anything destructive (force-push,
rewriting `main`, deleting an issue or a release asset); a new external dependency.

## 8. Labels

`task`, `bug`, `fix`, `triage:needed`, `milestone-review`, `review`,
`status:{ready,in-progress,in-review,rework,blocked,escalated,merged}`.

## 9. Autonomous runs

[designed: owner, 2026-10-20] A session may work the backlog on its own (`docs/backlog.md`, the
engine port first, rule 23): it takes the ready tasks in order, implements, checks and merges them
without asking, and stops only for a design decision, a Done-when that would weaken, and each
milestone (milestone issue, independent review).

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
A reviewer without Ghidra (it lives under `~/tools`) does not run it; the main session regenerates
`named/` where a check needs it (L57).

## 14. Sending findings to goal2

The purpose of this repository is to explore the game and find out how it works, and to deliver findings to `goal2`, which decides and builds the remaster. What we learn reaches it by one
route, so nothing stays in a chat or a run record that goal2 needs. (L109, the owner, 2026-10-15)

**When.** After a research PR merges that adds or changes a finding or a run record, and after
every sitting of the owner is extracted (section 11). Also when the owner states a rule in play,
a correction or a wish.

**1. Sort every item** into exactly one kind, and keep the kinds apart:
- *finding*: backed by a method, reviewed, with its F-number and its evidence level (proposed, supported or corroborated; not a work status, rule 3). Source tag `finding`.
- *owner statement*: what the owner said or did in a sitting, the notes of the run record
  (`runtime/human/note.py`). Source tag `owner`, citing the sitting and the run record. It is
  never written as a finding; it names what would check it.
- *question*: open; the register row's last column names it (Q-number or issue).
- *wish or design*: not a rule. It goes in the handover only (research never decides design, L16).

**2. A branch in goal2** (goal2 works without worktrees since 2026-10-20), named
`docs/register-<topic>-<date>`. It changes `docs/assumptions.md` and adds the handover file of step 3, and nothing else: new rows, or a changed row
when a finding replaces an `assumed` one (its Source becomes `finding F<nn>`, its Replaced-by is
emptied). Each row is a rule plus its Source, Live and Replaced-by cells in goal2's own columns.
A statement that contradicts an existing row is marked on that row; its rule changes only when
the owner says so, with the date, and only after a grep shows which goal2 code cites the row.
A decision about the remaster (a rule the rebuild plays by, its UI, its plan, a deliberate difference from the
original) is the owner's and lives in goal2: it is recorded there (goal2's `CLAUDE.md` or `docs/`, its own
rule 13a, through the handover and the issue of steps 3 and 4), and the row cites it. This repository records
only what concerns exploring the original: what the original does, and its keys and prompts for automating
it. (L112)

**3. The handover**: `docs/handover-<date>-<topic>.md` in the same branch, saying what the
branch holds, the evidence (run record ids, finding numbers, PRs of this repository), what the
goal2 session does (check the rows against its code and tasks, open a docs-only PR, ask the
owner for the reviewer), the owner's wishes, and what this repository does next.

**4. An issue on goal2** with the prompt for the goal2 session pasted in full, label
`triage:needed` (remote sessions have no clipboard, and the goal2 session's start-of-session
check finds it). The issue number goes on the finding or the research PR here.

**5. goal2 merges it, this repository does not.** The goal2 session opens the PR and gets the
review; this repository never pushes to goal2's `main`.

**What never goes across**: the original files, savestates, and bytes of the original beyond the
identifiers a row needs (CLAUDE.md rule 18). Both repositories are private; the rule still holds.

**Check**: a register row that cites a run record or finding must cite one that is merged here.

## 15. Requests from goal2

goal2 asks for decompilation or exploration by an issue in this repository (goal2's `docs/process.md` section 11),
labelled `triage:needed` and `from-goal2`; rule 14 lists it at the start of every session. (L114, the owner,
2026-10-16)

- **Grade it** by importance and cost (`docs/wide-pass.md`, "Grading the unknowns"), and answer **on the issue in the
  same session**: *investigate* (it becomes a task `T<nn>`, labelled `task`, with the issue linked), *assume* (state
  the assumption that stands and its risk, and close the issue as assumed; goal2's own assumption is a valid answer,
  so goal2 never waits), or *return it* (it is a remaster design decision: goal2's to make, L112).
- Ask the requester on the issue when the question is unclear; do not guess what blocks them.
- A request needing a long run or an expensive proof is answered *assume* unless goal2 shows it is of high importance
  (then it comes to the owner with the proposed assumption).
- The answer travels by section 14: a finding, a register branch and handover, and an issue in goal2. Static first
  (rule 22); nothing of the original goes across beyond the identifiers a row needs (rule 18).
