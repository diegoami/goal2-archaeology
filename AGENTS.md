# goal2-archaeology — Codex entrypoint

Read [CLAUDE.md](CLAUDE.md): its rules apply to every client (Codex, Claude Code, OpenCode), and
[docs/process.md](docs/process.md) for how a task runs. Claude Code's skills and agents under
`.claude/` are Claude-specific; Codex follows the same steps with its own tools. Since 2026-10-20
there is no review harness and no worktree: work on a branch in the checkout at hand, merge with a
merge commit on green CI. Only milestones mandate a review; no session starts one, the owner runs
it from the prompt the main session gives (owner, 2026-10-29).

## Resuming the engine port

Read the [latest shutdown checkpoint on #386](https://github.com/diegoami/goal2-archaeology/issues/386#issuecomment-6375808145)
before selecting the next task. It supersedes that issue's historical opening status; GitHub labels remain authoritative.

## Resuming the engine anatomy study

For the owner-authorised engine anatomy study, read the [current study checkpoint on #433](https://github.com/diegoami/goal2-archaeology/issues/433#issuecomment-6442284469) and the accepted T105 design linked from #444 before selecting a study task. Live labels, PR checks and newer checkpoint comments remain authoritative. The owner clarified on2026-10-27 that the goal session handles standalone delivery independently in a cloned repository; this session continues engine analysis. ES-R2 is accepted at its pinned tag;the owner resumed the next study steps. Follow executable task contracts and stop at the next independent-review milestone. The owner deferred the current T107 batch under #571 until T106 results inform a better design;prepare a revised proposal before match spending.

ES-R3 is accepted at `m7-engine-study-probes-and-integration`, exact f55ef8314c1da390eb96091efe2bdab7b73fa534.
The owner resumed T110's design assessment through [ES-R4 #457](https://github.com/diegoami/goal2-archaeology/issues/457).
Prepare/check executable slices before dispatch, then stop at #457's exact-candidate independent-review
prompt. This authorises assessment and documentation, not a T111 prototype or production rewrite.
T106/T109 evidence and [T107 revision notes](docs/engine-study/t107-revision-proposal.md) stay distinct:
T107 has no match results or approved replacement batch. Never substitute a later standalone-delivery
commit for a reviewed SHA or rerun completed probes to regenerate reports.
