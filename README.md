# goal2-archaeology

An evidence-backed behavioural specification of *goal (version 2)* (New Era Software, 1993), a DOS
text-mode international football team-management game. It follows the method of
[game-archaeologist](https://github.com/diegoami/game-archaeologist) at the commit
[archaeology.json](archaeology.json) pins. The spec feeds
a faithful rebuild and a bot that plays a country competently for idle play (the owner, 2026-10-11), in the private `goal2`. The
owner's decisions are U14–U20 there.

- **The artifact**: sets in [artifacts/known.json](artifacts/known.json): `goal2-a949da2f` and its
  successor `goal2-67cf27d6`, which declares what the runtime writes (F001, U21) — the same ten
  files, so every run stays valid against the set it names. CI, `setup/goal2-runtime.sh` and the
  driver fetch and verify the successor. The ten original files are assets of this private
  repository's release `goal2-original`, and are never committed.
- **What is known**: [knowledge-map.md](knowledge-map.md). **What is established**: [spec/](spec/README.md).
- **The plan**: [docs/plan.md](docs/plan.md). **The process**: [docs/process.md](docs/process.md); tasks
  are in [docs/tasks/](docs/tasks/README.md).
- **Playing the original** (every screen, key and setting, and driving it from a script):
  [docs/play-guide.md](docs/play-guide.md).
- **Layout**: `runtime/` (the DOSBox-X driver), `experiments/`, `runs/`, `evidence/`, `findings/`,
  `spec/`, `artifacts/`, `static/` (derived extracts).

Private: GOAL2 is treated as abandonware (U17), and nothing of it goes to a public repository.

Codex starts from [AGENTS.md](AGENTS.md); Claude starts from [CLAUDE.md](CLAUDE.md).
The harness runs the installed OpenCode 2 (audited 2.0.28) through its own private server, the
trusted reviewer profile and a shell-operand guard; `HARNESS_OPENCODE_EXE` naming a 1.x binary selects
the explicit 1.18 compatibility path ([docs/environment.md](docs/environment.md), "OpenCode 2").
