# Codex entrypoint

Read `CLAUDE.md` and `docs/process.md` before working. Their research, evidence,
worktree, review and merge rules also apply to Codex. The following adaptations
apply to a native Codex session and take precedence over Claude-specific routing:

- Codex is the main session and implements directly in its own worktree. Claude
  aliases and the Claude Agent tool do not select a Codex model. Keep the Claude
  defaults in `harness.json` for Claude sessions. Delegate only when requested.
- Follow the existing `dispatch.ask` setting for reviews. Codex belongs to the
  `openai` family: never select an OpenAI reviewer, including Luna or Sol. If the
  configured reviewer is OpenAI, ask for an eligible registered reviewer from
  another family; do not silently change the shared defaults.
- Set `HARNESS_SESSION_FAMILY=openai` for review commands and detached systemd
  units. The harness also detects `CODEX_THREAD_ID` or `CODEX_CI=1`; an explicit
  family override takes precedence. Unknown custom endpoints require an explicit
  family. Pass the family through to detached processes.
- Read `.claude/skills/run-task/SKILL.md` for the task workflow, and the applicable
  repository skill files for brief creation and model switching. Use shell and
  available Codex tools for Claude-specific slash commands.
- Keep `RUN-NOTES.md` as described in `docs/running-notes.md`. Respect the current
  session's filesystem permissions; Claude hook grants do not grant Codex access.

The harness automatically selects a verified OpenCode 1.x backup when the default
executable reports 2.x. It tries `opencode.bak`, `opencode.exe.bak`, and
`opencode.1.*.bak` beside the resolved executable and in `~/.opencode/bin`.
`HARNESS_OPENCODE_EXE` pins an executable and disables automatic replacement.
The harness retains its isolated XDG data directories to protect against the
incompatible desktop database. Use the selected executable printed in the review
log for manual commands and `OPENCODE_BIN` when inspecting a run with `peek.sh`.
