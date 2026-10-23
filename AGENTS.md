# goal2-archaeology — Codex entrypoint

Read [CLAUDE.md](CLAUDE.md): its rules apply to every client (Codex, Claude Code, OpenCode), and
[docs/process.md](docs/process.md) for how a task runs. Claude Code's skills and agents under
`.claude/` are Claude-specific; Codex follows the same steps with its own tools. Since 2026-10-20
there is no review harness and no worktree: work on a branch in the checkout at hand, merge with a
merge commit on green CI, and use `tools/review_pr.sh` when a PR needs an independent review.

## Resuming the engine port

Read the [latest shutdown checkpoint on #386](https://github.com/diegoami/goal2-archaeology/issues/386#issuecomment-6375808145)
before selecting the next task. It supersedes that issue's historical opening status; GitHub labels remain authoritative.
