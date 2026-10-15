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
| Implementer | The **`implementer` subagent** spawned inside Claude Code (worktree isolation) on a model of its own, not the orchestrator's (Opus spawns Sonnet; under Z.AI `sonnet` is GLM-5.3 Flash), or **the main session** directly, in its own worktree, where the provider cannot spawn one; asked before each implementation (CLAUDE.md "Choosing models" rule 1). *Superseded: OpenCode via `implement.mjs` (removed), the GLM/DeepSeek/Sonnet chain (L42), L46's heavier-model rule, the user asked before each run.* | One task, one branch, one PR, in its own worktree |
| Reviewer | **One OpenCode run** via `tools/harness/review.mjs`, on the model the user names at the question before the review, `harness.json`'s `reviewer.default` (GPT-5.6 Luna) proposed first (`sol-6.1` for hard research, rule 21); never the session's family (L27), never a blocked model. Exit 3: read the final message, fix the cause, run again; exit 4: the main session reads the flagged review and decides (L28). *Superseded: the quota-checked Sol / Luna / Opus order (L50, L51, L101), the Claude fallback, the user asked at every review.* | Re-runs the Done-when, audits scope and evidence, posts one PR comment, applies the label |
| Decider | Jev via `tools/harness/jev.mjs` (the `/jev` skill) | Repeated yes/no decisions over many items, at the confident ends only (§12) |
| Generator | Models on OpenRouter (images, other families) and ElevenLabs (speech, sound, music) | Assets, each committed with a sidecar naming provider, model, prompt, date and cost |

Before each implementation and each review the main session asks the user one question, with
`harness.json`'s default proposed first (CLAUDE.md "Choosing models"); no quota, tier or chain picks a model, and the
roster changes through `/switch-model`. The implementer's family is the session's, read from the
Anthropic environment variables (`lib/common.mjs` `sessionFamily`; the orchestrator is Claude, or GLM
through Z.AI, MiniMax or Kimi when Claude's tokens are out), and the reviewer is never of it. Model ids come
from `harness.json`, `models.mjs` or `opencode models`, never memory (L25).

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

`ready → implement → review → approved + green CI → squash merge → follow-up → unblock → report`.
Rework sends the full review back to the same branch, at most two rounds (one for a fix), then
escalates. The implementer script resumes a pushed branch; it never starts over. Before a merge the
main session re-runs the check the approval rests on most; a different result is rework. (L46)
CI (the owner, 2026-10-12, to save minutes): no run on a draft PR, so a PR is marked ready before
its review; a new push cancels the run it supersedes; a push that changes only measured outputs
(`*.log`, `experiments/**/out/**`) runs nothing, so "green CI" is the newest run that covered the
PR's code; a push to `main` runs only the quick checks (links, citations, no original file).

What the review script guarantees, and why:
- OpenCode starts with stdin closed; without it a run hangs before it starts. (L10)
- No session in 180 s, no progress in 600 s, or no exit in 1 h kills the run's process tree (L10);
  `--idle-timeout-sec` and `--total-timeout-sec` lengthen them for one run.
- The agent is checked on OpenCode's session record (L11); a rejected tool call fails the run (L26),
  and the fix is a wider grant in the agent file, not a re-brief (CLAUDE.md "Choosing models" rule 4).
- The brief passes by file: the runner writes it to `.harness-brief-<title>.md` at the review
  worktree's root and the command line carries only a pointer, so a long brief cannot exceed the
  command-line limit; the file is never committed, and on failure it is kept with the logs. (L60)
- The model runs at the effort its `harness.json` entry names (a heavy model at low, a light one
  at high), in the scripts' own data directory (L27, L29). One model, one run; no chain. The model
  is `reviewer.default`, or `--reviewer` (a harness.json key or `provider/model[@variant]`).
- Exit 0: posted and labelled. 2: a refused model (DeepSeek, an unknown name). 3: no review, nothing
  posted: read the final message ("Choosing models" rule 12), fix the cause, run again. 4: posted under a note, no
  label: the main session reads it and decides.

How the main session launches and watches a run (L103):
- Detached from its own session, so a restart of Claude Code does not kill the run, in the form of
  CLAUDE.md "Choosing models" rule 9: `systemd-run --user --unit=goal2-<task> --collect -E PATH="$PATH"
  -E MINIMAX_API_KEY -E ANTHROPIC_BASE_URL -E HARNESS_SESSION_FAMILY -p WorkingDirectory=<repo> -p StandardInput=null -p StandardOutput=file:<log>
  -p StandardError=file:<log> <review.mjs command>`. A unit gets only the
  environment it is given, so each key a run needs is passed with `-E`; never a `bash -c` or
  `bash -lc` script (the safety check flags it).
- The watch follows the unit (`systemctl --user is-active goal2-<task>`). A Claude implementer
  agent is watched by its transcript file's size and its worktree; when its worktree holds
  uncommitted work more than 20 minutes newer than its last commit, the main session archives it
  outside the worktree, read-only (it never touches the run's index).
- An implementer's PR may be a draft; the main session runs `gh pr ready <pr>` before the review.

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
- Commit and push after each step, at least every 20 minutes and before any command that runs longer
  than 5 minutes; after your first push, open the PR as a draft (`gh pr create --draft`). A crash then
  loses one step, and the branch shows where you are. (L103)
- A command that can run past 10 minutes never pipes through `tail`/`head`: an agent's tool call
  has a timeout of its own (L10). Run it detached (`nohup … > log 2>&1 &` or `setsid`), verify it
  survived the tool call with `ps`, then poll the log in short calls.
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

Write the brief with `tools/harness/make-brief.mjs` (usage in its header), never by hand: it fills this block and `docs/review-brief.md` and refuses a brief `review.mjs` would refuse.

Every review brief states the timezone and timestamp convention (L108): include the owner's
supplied timezone and use UTC ISO 8601 for evidence logs unless the task needs local time. A
harmless metadata read the owner has authorized does not need another permission question. Grant
only the read the tool can enforce, test sibling reads and writes as denied, and describe the
boundary accurately. On OpenCode 1.18.32, `external_directory` checks the parent `/*` for a file
read, while `grep` and `glob` permission requests omit the target path; where path-specific rules
are needed, deny those tools and use a path-bearing tool. These are tool-layer controls, not OS
isolation.

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

Before merging an approval that carries non-blocking findings, the main session reads them: a
proven way past what the task protects is rework whatever the reviewer rated it; it says so on the
PR and records it in `docs/model-trials.md` (L47: GLM-5.3 proved three guard bypasses, rated them
non-blocking and approved).

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

A design question; a Done-when would have to weaken; a third rework round, except the narrow one
the main session may grant itself when the remaining findings are small and change no result
(CLAUDE.md rule 7); anything destructive (force-push, rewriting `main`, deleting an issue); a new
external dependency.

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
An OpenCode reviewer cannot run Ghidra (it lives under `~/tools`, outside its worktree): the review
brief says "do NOT run Ghidra", and the main session regenerates `named/` where a check needs it
(L57). Claude agents and the main session can run it.

## 14. Sending findings to goal2

The purpose of this repository is to feed `goal2`, the rebuild. What we learn reaches it by one
route, so nothing stays in a chat or a run record that goal2 needs. (L109, the owner, 2026-10-15)

**When.** After a research PR merges that adds or changes a finding or a run record, and after
every sitting of the owner is extracted (section 11). Also when the owner states a rule in play,
a correction or a wish.

**1. Sort every item** into exactly one kind, and keep the kinds apart:
- *finding*: backed by a method, reviewed, with its F-number and status. Source tag `finding`.
- *owner statement*: what the owner said or did in a sitting, the notes of the run record
  (`runtime/human/note.py`). Source tag `owner`, citing the sitting and the run record. It is
  never written as a finding; it names what would check it.
- *question*: open; the register row's last column names it (Q-number or issue).
- *wish or design*: not a rule. It goes in the handover only (research never decides design, L16).

**2. A branch in goal2**, made in a worktree of goal2, never in its main checkout, named
`docs/register-<topic>-<date>`. It changes `docs/assumptions.md` and adds the handover file of step 3, and nothing else: new rows, or a changed row
when a finding replaces an `assumed` one (its Source becomes `finding F<nn>`, its Replaced-by is
emptied). Each row is a rule plus its Source, Live and Replaced-by cells in goal2's own columns.
A statement that contradicts an existing row is marked on that row; its rule changes only when
the owner says so, with the date, and only after a grep shows which goal2 code cites the row.
The owner's decision is first written in this repository, in a commit that changes `CLAUDE.md` or
`docs/` (rule 13a: never only in a chat, a memory or goal2's branch), and the row cites it.

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
