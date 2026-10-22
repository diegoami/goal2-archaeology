# Working in a cloud session

[designed: owner, 2026-10-20] goal2-archaeology runs from any fresh checkout, a Claude Code on the
web session included, with the original game running in DOSBox-X 2024.03.01 headless.

## Secrets of the cloud environment

- `GH_TOKEN`: a fine-grained GitHub token for `diegoami/goal2-archaeology` with read and write
  access to contents, issues and pull requests. Without it `gh` cannot open or merge PRs.
- `GOAL2_RCLONE_TOKEN` (optional): the whole JSON after `token = ` of the `goal2drive` remote in a
  configured machine's `~/.config/rclone/rclone.conf`, the same secret as goal2's. With it, the setup
  copies the newest `goal2-archaeology/checkpoint-<date>` folder of the owner's Drive into `.cache/`:
  the non-git state (start states) a local session handed over. Everything a result
  rests on is in git already (rule 20).
- Optional, for reviews by other model families from the cloud: the API keys of the CLI that
  `tools/review_pr.sh` or `tools/milestone_review.sh` calls.

The original game needs no secret: its files are assets of this repository's public releases
(CLAUDE.md rule 18), fetched and verified by hash.

## Network

`archive.ubuntu.com` (the pinned DOSBox-X packages) and the image's own apt mirrors, `pypi.org`
and `files.pythonhosted.org`, and GitHub (`github.com`, `api.github.com`, `codeload.github.com`,
`objects.githubusercontent.com`, `release-assets.githubusercontent.com`, `uploads.github.com`) for
the code and the release assets.

## What happens at session start

The session-start hook (`.claude/hooks/session-start.sh`, cloud sessions only) runs
`tools/cloud_setup.sh`, which mirrors CI: Xvfb, Xephyr, xinput, xdotool, ffmpeg and the
distribution's `dosbox-x` (for its libraries) from apt; DOSBox-X 2024.03.01 from
`setup/dosbox-x-2024.03.01.sh` when apt offers another version; the Python requirements; the
artifact sets `goal2-67cf27d6` and `goal2-a949da2f`; and an **emulator probe**: the game boots to
its title screen, whose digest must equal the one in `runs/E001/E001-r0001.json`, then two
driver cycles (`runtime/driver/cycle.py --dry`) run end to end. It reports the branch, gh's login
and the DOSBox-X version; its log is `.cache/cloud-setup.log`. Elsewhere run `tools/cloud_setup.sh`
and `source .cache/cloud.env` by hand.

## Handing work over from a local session

The local session stops at a checkpoint: it pushes every commit and measured output (rule 20),
posts a checkpoint comment on each open PR (head SHA, what is done, what remains, the next command),
then copies its non-git state to Drive:
`rclone copy .cache/states goal2drive:goal2-archaeology/checkpoint-<YYYY-MM-DD>/states` (start states only; the caches of
old review runs are not handed over, 2026-10-21).
The cloud session's setup pulls the newest checkpoint; it continues each PR from its pushed head.
A checkpoint may keep states per task (`states/T<nn>/driver/…`, with a `manifest.json`): before
working on task T<nn>, copy its folder into place (`cp -rn .cache/states/T<nn>/* .cache/states/`), so
the driver finds `.cache/states/driver/` as the local session left it.

## GitHub from a cloud session

[designed: owner, 2026-10-21, after the first goal2-archaeology cloud run] The session's proxy lets
only GitHub's REST API through: `gh`'s GraphQL commands (`gh pr create`, `gh pr merge`, `gh pr view`,
`gh issue list`, `gh release download`, `gh auth status`) fail with 403. Use the session's built-in
GitHub tools, or `gh api` (REST), for example:

- merge with the merge commit process.md §3 asks for, pinned to the checked head:
  `gh api -X PUT repos/diegoami/goal2-archaeology/pulls/<n>/merge -f merge_method=merge -f sha=<head sha>`
  (goal2 squashes only locally; a cloud session always merges like this);
- open a PR: `gh api repos/diegoami/goal2-archaeology/pulls -f title=... -f head=<branch> -f base=main -F draft=true -F body=@<file>`
  (`-F`, not `-f`: only `-F` reads a file after `@`; `-f body=@<file>` posts the path as the text, 2026-10-22);
- the login check: `gh api user --jq .login`.

Release assets come over plain HTTPS from the public release (the setup falls back to it); their
downloads redirect to `release-assets.githubusercontent.com`, which the network settings must allow.

## Branches

The session starts on its own `claude/…` branch, the work branch for every task of the session;
every PR merges with a merge commit (process.md §3).

## Limits

- Runs are CPU-bound; a cloud session has few cores, so heavy jobs queue through `tools/heavy.sh`.
- [designed: owner, 2026-10-22] A cloud container restarts often, killing every running job (the first
  restart came mid-run on 2026-10-22, T63). There, measured outputs are committed and pushed about **every
  5 minutes** while runs go (CLAUDE.md rule 20's "at least every 30 minutes" is the local floor): a small
  loop that commits only the task's output folder is enough. Files on disk survived that restart; a
  family run resumes with the same `--out` and a fresh log.
  A family run there takes `--checkpoint .cache/checkpoints/T<nn>` (#359): a match killed mid-way resumes
  inside it, not from its start. Keep the folder on disk; it is the non-git state a Drive checkpoint carries.
- Ghidra is installed on demand, not at session start: a task that regenerates `static/goal-exe/decompiled/`
  or `named/` (process.md §13) first runs `bash setup/ghidra-12.1.4.sh` (Ghidra 12.1.4 and Temurin
  21.0.12.1, sha256 pinned, about 780 MB), then `tools/static/decompile.sh` as the views' READMEs say,
  in the background (about 6 minutes on two CPUs).
- A probe failure means the emulator differs here: no run made in that session counts until it is
  understood.
