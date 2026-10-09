# Running notes — `RUN-NOTES.md`

> A per-worktree file where the implementer tracks its own progress in real time. If a
> run is interrupted (wall clock, process kill, orphan collision, owner intervention),
> the next implementer reads this file as the authoritative handoff.

## File

- **Path**: `RUN-NOTES.md` at the worktree root.
- **Git**: per-worktree ignored (`.git/info/exclude`). Never committed to any branch.
- **Created**: by the agent on its first step (Plan section filled in; Progress and
  Notes empty until the agent appends).

## Sections

```
# RUN-NOTES — <task id>

## Plan
1. <step one>
2. <step two>
3. ...

## Progress
- <timestamp> <one-line: what was done>

## Notes
- <timestamp> <one-line: anything the next session needs>

## END
- last commit: <sha>
- PR state: <open / draft / ready / merged>
- deferred: <bullet or "none">
```

Three live sections + one terminal block:

- **Plan** — what the agent intended to do. Written once at the start, from the brief's
  step list. Not edited after.
- **Progress** — what the agent actually did. Append a `## <step>` bullet after each
  commit (or after each meaningful tool-call cluster). Append-only.
- **Notes** — abandoned approaches, decisions made, surprise findings, blockers hit.
  Append-only.
- **END** — the last block the agent writes, before `git -C <worktree> checkout --detach`
  on exit. Last commit hash, current PR state, what's deferred.

## Implementer's three rules

1. **Read it first.** At the start of every run, `cat RUN-NOTES.md` at the worktree root.
   If it exists (a previous round left it), read it in full before anything else. It
   carries the design rationale and the deferred TODO.
2. **Append, don't rewrite.** After every commit (or every meaningful tool-call cluster),
   append a `## <step>` bullet to **Progress**. Never edit earlier entries. **Never
   `git add` or `git commit` `RUN-NOTES.md`** even if it ends up tracked.
3. **Final state on exit.** Before the agent exits (or before any detached `git
   checkout`), append a `## END` line to **Notes**: last commit hash, current PR state,
   what's deferred for the next round.

## Reviewer's one rule

Read `RUN-NOTES.md` before the diff. It tells you the design rationale and the deferred
items — the review grades against the *design*, not just the final state.

## Why this concretely helps

- **Implementer interrupted by wall clock / orphan / process kill** — the next round
  reads `RUN-NOTES.md` and knows exactly what was tried, what landed, and what didn't.
- **Long implementer run** — anyone with read access can `cat RUN-NOTES.md` mid-run to
  see where it's stuck (alternative to reading the live opencode db).
- **Reviewer context loss** — the reviewer's first read is `RUN-NOTES.md`, which
  carries the design rationale and the deferred items the implementer surfaced.

## Hazards

- **Append-only.** A `Progress` entry that turned out wrong gets a new entry saying
  "the previous approach was reverted because X" — never an edit.
- **Never `git add` / `git commit`** the file, even if it ends up in `git status`. The
  `.git/info/exclude` line keeps it out; the rule keeps it from being staged by
  accident.
- **Per-worktree ignore** — the agent adds it once on first touch:
  `printf 'RUN-NOTES.md\n' >> .git/info/exclude` from the worktree root.
- **Don't put the file in the PR body.** The PR carries the *result*; the notes file
  carries the *narrative of getting there*.
