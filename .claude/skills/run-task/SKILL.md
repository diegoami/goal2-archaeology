---
name: run-task
description: Run goal2-archaeology tasks or fixes end to end on the work branch in the checkout at hand - implement (the main session or the implementer subagent), optionally review with tools/review_pr.sh, wait for green CI, merge with a merge commit and report. Main session only.
---

Engine port stage exception: see `docs/process.md` section 3 (owner, 2026-10-21;
L123). Port PRs use their checks plus green CI and one milestone review for the stage;
skip the individual port PR review dispatch and approval gates in this workflow.


# /run-task [T<nn> | #<issue> ...]

Follow `docs/process.md` §3 for each id in order (none given: the first `status:ready` task in
`docs/tasks/README.md`, the engine port first, CLAUDE.md rule 23). For `#<issue>` of a bug labelled
`fix`, the issue body is the task file and the branch is `fix/<issue>-<slug>`.

1. **Check**: Merge-after tasks are merged; each Done-when line fails on `main`. A line that cannot
   be run is amended on `main` first, the reason in the commit.
2. **Implement** on the work branch (process §3: locally `task/T<nn>-<slug>` from `origin/main`; in
   a cloud session the session's own branch, after `git pull --ff-only origin main`): yourself, or
   `Agent(subagent_type: "implementer")` with the task file pasted in full and process §4's block
   (on rework, the review's URL). Label `status:in-progress`. Read the subagent's final report
   before acting.
3. **Review, when warranted** (a finding, a game rule or constant, the engine port, the proof, or the
   owner asks): `tools/review_pr.sh <pr> <opencode|claude|codex> <model>`, any model. Relay findings
   in full; rework on the same branch; non-blocking findings become one `T<nn> follow-up` issue
   (`triage:needed`).
4. **Checks**: re-run every Done-when line on the PR head; CI must be green on that head.
5. **Merge**: `gh pr merge <pr> --merge --match-head-commit <sha>` (always a merge commit), label
   `status:merged`, then `git switch main && git pull` locally or `git pull --ff-only origin main`
   in a cloud session; unblock dependants, report.

Escalate (process §7) with options and a recommendation, and stop. Never weaken a Done-when,
relay part of a review, force-push or rewrite `main`.
