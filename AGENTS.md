# goal2-archaeology — Codex entrypoint

Read [CLAUDE.md](CLAUDE.md): its rules apply to every client (Codex, Claude Code, OpenCode), and
[docs/process.md](docs/process.md) for how a task runs. Claude Code's skills and agents under
`.claude/` are Claude-specific; Codex follows the same steps with its own tools. Since 2026-10-20
there is no review harness and no worktree: work on a branch in the checkout at hand, merge with a
merge commit on green CI, and use `tools/review_pr.sh` when a PR needs an independent review.

## Resuming the engine port

Read the [latest shutdown checkpoint on #386](https://github.com/diegoami/goal2-archaeology/issues/386#issuecomment-6375808145)
before selecting the next task. It supersedes that issue's historical opening status; GitHub labels remain authoritative.

## Resuming the engine anatomy study

For the owner-authorised study through ES-R2, read the [current study checkpoint on #433](https://github.com/diegoami/goal2-archaeology/issues/433#issuecomment-6442284469) and the draft design notes on #444 before selecting a study task. Live labels, PR checks and newer checkpoint comments remain authoritative. The owner clarified on2026-10-27 that the goal session handles standalone delivery independently in a cloned repository; this session continues engine analysis. Keep T106/T107 gated by accepted ES-R2 and stop at its pinned independent-review prompt.
