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

The harness uses the installed OpenCode as found and dispatches on its major
(#262): 2.x (audited 2.0.28) runs through a private server of its own, the
reviewer profile translated from this checkout and the shell-operand guard
(`npm ci --prefix tools/harness/opencode-guard --ignore-scripts --no-audit --no-fund`
once per checkout); 1.x runs the unchanged 1.18 path, which is now chosen only
explicitly with `HARNESS_OPENCODE_EXE`. There is no automatic backup search.
v2 keeps its logins and sessions in its own data root, and the legacy v1 data
directory is never opened by a v2 process. `peek.sh` takes a session id, a run
log or a v2 `run.json`; `OPENCODE_BIN` selects the binary it reads with. See
`docs/environment.md`, "OpenCode 2".
