# Environment

What a session needs so the main session can delegate. Everything here is optional: each missing
piece turns one delegate off, and the main session falls back to Claude (the scripts exit 3).

## On your desktop

Locally there is no network policy and no environment settings, and the session-start hook does
nothing. You need:
- Node 20 or later.
- `gh`, logged in (`gh auth login`). It needs no `GH_TOKEN`.
- OpenCode 1.18 (`opencode --version`), logged in to OpenCode Go (next section).
- Optional: the credential jail (`tools/harness/lib/jail.mjs`, #68), off by default. With
  `"jail": { "enabled": true }` in `harness.json` and bubblewrap installed on Linux or WSL
  (`sudo apt install bubblewrap`), reviewers run without your GitHub credentials; enabled where
  bwrap cannot run, the review hook and `review.mjs` print a warning. Off, only the guard stops a push.
- The other keys below, as user environment variables. On Windows, in PowerShell:
  `[Environment]::SetEnvironmentVariable("ELEVENLABS_API_KEY", "<key>", "User")`.
  Then restart the terminal and Claude Code, so they see it.

**In WSL** (Claude Code, or the desktop app, working in a WSL folder), use OpenCode's Linux binary.
OpenCode's own installer puts it in `~/.opencode/bin`; the release tarball `opencode-linux-x64.tar.gz`
works too. Avoid `opencode upgrade`, which may reach for the Windows npm. The `opencode` that WSL
finds on PATH is often the Windows npm shim under `/mnt/c`. That shim runs the Windows OpenCode,
which cannot use the run's Linux paths and survives the kill of a timed-out run: both real-OpenCode
tests failed through it. The runner skips the shim and falls back to `~/.opencode/bin/opencode`;
`HARNESS_OPENCODE_EXE` overrides both. WSL and Windows keep separate logins: log in from WSL.

**On Windows**, `npm install -g opencode-ai@1.18`.

Then run `npm test` in the harness repository. The tests against the real OpenCode run wherever
`opencode` is installed. Then do the first-session check at the end of this page.

## OpenCode Go

The second implementer, DeepSeek V4.1 Flash, is OpenCode Go's (`opencode-go/…`), a subscription. They are not OpenCode Zen's pay-per-token `opencode/…` models. Go comes from a console
(organisation) login, not from a key; `opencode auth login` and `OPENCODE_API_KEY` reach only Zen
(IC2 #551):
1. `opencode console login`, then approve the URL and code it prints in the browser;
2. `opencode models opencode-go` lists the models; without the login it lists none, although
   `opencode console orgs` still exits 0 ("No accounts found"). If a login lists none, run
   `opencode models --refresh`.

The login is stored in the database of OpenCode's data directory, not in `auth.json`. Another data
directory, another machine, WSL beside Windows, or a new cloud session each needs its own
`opencode console login`.

## OpenAI, for the reviewer

The reviewer is GPT-5.6 Luna on the direct OpenAI route (`openai/gpt-5.6-luna`, L51), never a Luna
on Go (`opencode-go/…`): a third-party proxy behind Go's returned `Bad Request` in long agent loops
(L27). OpenAI is an ordinary OpenCode provider: log in once with `opencode auth login`, choose
OpenAI (a ChatGPT login or an API key), and check with `opencode models openai`. The login is kept in
`auth.json`, which the scripts copy into their own data directory (next section) whenever theirs is
missing or older. If OpenAI later asks for a new login, log in again in your usual OpenCode; the
next run copies it.

## Z.AI, for the implementer and the GLM models

GLM-5.3 Flash, the default implementer (L42), and GLM-5.3, the first hard reviewer (L41), run on
Z.AI's coding plan (`zai-coding-plan/…`); both stay on watch (L35). Log in once with `opencode auth login` and choose Z.AI Coding Plan (an API
key; OpenCode also reads `ZHIPU_API_KEY`), then check with `opencode models zai-coding-plan`. The
key is kept in `auth.json`, which the scripts copy like OpenAI's. GLM-5.3-highspeed is refused by
the plan.

## Alibaba Token Plan and MiniMax, on watch

Registered 2026-10-05/06 (the owner), all on watch in `harness.json`, no chain seats. The key is the
env var `ALIBABA_TOKEN_PLAN_API_KEY` (or `MINIMAX_API_KEY`) from `~/.config/ai-keys.env` — never
`opencode auth login` for these (an `auth.json` entry overrides the variable). All probed
2026-10-06 19:39–19:40 (`switch-model.mjs --probe --dry-run`, answered; first probes 2026-10-05).
`opencode models <provider> --verbose` lists no effort ladders for these providers; the variants
below are the owner's live checks.

| Entry | Id | Variant | Heavy/light | Notes |
| --- | --- | --- | --- | --- |
| `ali-glm` | `alibaba-token-plan/glm-5.3` | low | heavy | GLM-5.3 on the monthly pool; no night discount; zai relief (and its 3x weekday-peak price from 8 Oct 2026) |
| `ali-qwen-max` | `alibaba-token-plan/qwen3.8-max` | low | heavy | new family; offers low, medium, xhigh |
| `ali-qwen-flash` | `alibaba-token-plan/qwen3.8-flash` | medium | light | offers low, medium, xhigh (no high); medium since 2026-10-06 (xhigh before) |
| `ali-deepseek-pro-0813` | `alibaba-token-plan/deepseek-v4-pro-0813` | high | heavy | only the dated `-0813` id gets the 50% night discount |
| `ali-deepseek-flash` | `alibaba-token-plan/deepseek-v4.1-flash` | high | light | same model as `deepseek-flash` on Go |
| `mm-m3` | `minimax/MiniMax-M3` | thinking | heavy | offers only none and thinking; a new family, independent reviewer material |
| `mm-m2.7`, `mm-m2.7-highspeed` | `minimax/MiniMax-M2.7(-highspeed)` | — | light | no effort variants; a variant is ignored if sent |

Alibaba is one monthly pool for all its models (`curl -s localhost:8765/quota/alibaba`;
`pricing.discount_now` says whether the night discount is live, 22:00–08:00 UTC+8: qwen3.8 60% off,
`deepseek-v4-pro-0813` and `v4.1-flash` 50% off, `glm-5.3` none — prefer long alibaba runs while it
is true). MiniMax has 5-hour and weekly windows (`curl -s localhost:8765/quota/minimax`). Alibaba's
Kimi and MiniMax models are Team-edition only and fail; not registered. This repo's pinned
`lib/quota.mjs` predates alibaba/minimax window knowledge — see `harness.lock`'s bump note.

Placements (the owner, 2026-10-06): the implementer chain runs `zai-glm-5.3-flash`, `deepseek-flash`,
`mm-m2.7`, `ali-qwen-flash` (then Claude sonnet); the hard reviewer chain runs `zai-glm-5.3`,
`ali-glm`, `ali-qwen-max`, `deepseek-pro`, `ali-deepseek-pro-0813`, `luna` (then Claude opus).
`mm-m3` is the L38 heavy escalation rung before the Claude fallback and the alternate for the Sol
seat when openai is exhausted. `ali-deepseek-pro-0813` and `ali-deepseek-flash` are the
explicit-model reliefs when opencode_go is out. From 8 Oct 2026 `ali-glm` is the default GLM seat
(zai's 3x weekday peak). The lock bump to `b8c6cde` awaits the owner's separate word.

## Quota: quota-tracker

Where the machine runs quota-tracker, a local service, it reports how much subscription quota is
left on each provider: `claude` (the main session and Claude agents), `openai` (Sol and Luna, via
OpenCode), `zai` (GLM-5.3 and GLM-5.3 Flash), `opencode_go` (DeepSeek) and `openrouter` (prepaid
credit). Check it before choosing, recommending or delegating to a model (L50). It is read-only, on
localhost, with no auth; results are cached 60 s, and `?refresh` bypasses the cache:
- `curl -s localhost:8765/quota`, or `/quota/<provider>` for one;
- `curl -s localhost:8765/best`: the providers with quota left, most headroom first;
- `curl -s localhost:8765/avoid`: the providers out of quota, with when each is usable again.

Each provider has a `status`: `ok` (under 80% used), `low` (80% or more), `exhausted` (95% or
more: do not use it until `available_at` / `available_in`), `error` (it could not be checked;
`error` says why) or `not_configured`. `headroom_pct` is the percent left on its most-used window;
`windows[]` lists every limit with `used_pct` and when it resets. OpenRouter is prepaid: its
windows never reset, and `remaining_usd` is the balance. A model with a pool of its own has its
own window, named after it: today GPT-5.6 Luna (`gpt-5.6-luna:7d`), which can be usable while
OpenAI's main `7d` window, the one GPT-6 Luna and Sol draw on, is exhausted. Read which pools exist
from the windows the endpoint returns, not from this page.

The models per provider, heavy and light:

| Provider | Heavy | Light |
| --- | --- | --- |
| claude | `claude --model opus` | `claude --model sonnet` |
| openai | `opencode -m openai/gpt-6.1-sol` | `opencode -m openai/gpt-5.6-luna` |
| zai | `opencode -m zai-coding-plan/glm-5.3` | `opencode -m zai-coding-plan/glm-5.3-flash` |
| opencode_go | `opencode -m opencode-go/deepseek-v4-pro` | `opencode -m opencode-go/deepseek-v4.1-flash` |
| openrouter | `opencode -m openrouter/deepseek/deepseek-v4-pro` | `opencode -m openrouter/deepseek/deepseek-v4.1-flash` |

GPT-5.6 Luna, the reviewer (L51), has its own weekly limit: for light work OpenAI is usable while
the `gpt-5.6-luna:7d` window in `/quota/openai` is under 95%, even when OpenAI's main window is
exhausted.

If `curl -sf localhost:8765/health` fails where the service is installed:
1. `systemctl --user restart quota-tracker`, wait a few seconds, and check `/health` again.
2. If systemctl says `Failed to connect to bus`, the user's systemd instance is not running: ask
   the user to run `sudo loginctl enable-linger $USER`, then retry step 1.
3. If it still fails, read `journalctl --user -u quota-tracker -n 50` and tell the user what it says.
4. To run it without the service: `cd ~/projects/models_quota_tracker && uv run quota-tracker serve`
   in the background (it stops when the session ends).

`implement.mjs` and `review.mjs` ask the service themselves before their chain runs (`lib/quota.mjs`,
L52): a model with a window of its own (GPT-5.6 Luna's `gpt-5.6-luna:7d`) is judged by that window
alone, skipped at 95% or more even when its provider is not exhausted, and run under 95% even when
it is; any other model is skipped when its provider is `exhausted`. A provider in `error` or
`not_configured` skips nothing. Each skip is logged with its reason, and with none left the script
exits 3. `HARNESS_QUOTA_URL` names another
address. Where the service does not answer, they skip nothing and log `quota: not checked`.

Never read or edit `~/.config/quota-tracker/config.toml`: it holds account tokens. A provider in
`error` over an expired cookie or token goes to the user, since renewing it needs their browser or
login. Where the service is not installed, go on without it, and count a usage-limit error as
`exhausted`.

## Ghidra, for the decompiled and named views

`tools/static/decompile.sh` (T18; with `--annotations`, T20's named view) needs these, outside the
repository; nothing else does:
- Ghidra 12.1.4 (release `Ghidra_12.1.4_build`, unpacked to `~/tools/ghidra_12.1.4_PUBLIC`, or set
  `GHIDRA_HOME`). The script refuses another version.
- A JDK 21: Temurin 21.0.12.1 (`~/tools/jdk-21.0.12.1+1`, or set `JAVA_HOME`). The script refuses
  another major version, and the output's README records the exact one.

Ghidra runs headless with `-max-cpu 2`, one instance at a time (the machine is shared). Without
them, `tests/static/test_decompile.py` skips its Ghidra tests and says why. One run takes about
six minutes on two CPUs: start it in the background.

## The scripts' own data directory

`implement.mjs` and `review.mjs` run OpenCode with a data directory of their own, so OpenCode's
desktop app (2.x) can never migrate their database to a schema the 1.x CLI cannot read (IC2 #540,
"no such column: project_id"). It is `~/.local/share/harness-opencode`, with `data/`, `cache/` and
`state/` set as `XDG_DATA_HOME`, `XDG_CACHE_HOME` and `XDG_STATE_HOME` for OpenCode's processes only.
`HARNESS_OPENCODE_HOME` moves it (a relative path is made absolute). `auth.json`, the API-key
providers, is copied in from `~/.local/share/opencode` (or `HARNESS_OPENCODE_AUTH_SOURCE`) when the
copy is missing or older; it is never read or printed.

Go's login does not travel with `auth.json`, so log in once for this directory. In bash (WSL, Linux):

```bash
XDG_DATA_HOME="$HOME/.local/share/harness-opencode/data" opencode console login
```

In PowerShell (Windows), in a new window afterwards:

```powershell
$env:XDG_DATA_HOME = "$HOME\.local\share\harness-opencode\data"; opencode console login
```

Check it with the same `XDG_DATA_HOME` and `opencode models opencode-go`. Before any run, each script
checks that OpenCode lists its model there; if not, it exits 3 with the command that fixes it (this
one for Go, `opencode auth login` for OpenAI), and nothing is billed. The scripts never change their
own process's environment, only that of the OpenCode processes they start, so nothing needs
restoring afterwards.

## Keys

In **Claude Code on the web**, set these in the environment's settings: the cloud environment menu
in the session's title bar, then **Edit**, then the environment variables (or API credentials, where
that section is offered). A new session picks them up. On **your machine**, set them in your shell.
Never paste a key into a chat, and never commit one.

| Variable | Used by | Without it |
| --- | --- | --- |
| `OPENCODE_API_KEY` | OpenCode Zen's `opencode/*` models, if `harness.json` names any. The default models are Go's, which need `opencode console login` instead (above) | nothing, while `harness.json` names only Go models |
| `OPENROUTER_API_KEY` | Jev, through OpenRouter (`jev.mjs`); also OpenCode's `openrouter/*` models, if `harness.json` names any | `jev.mjs` exits 3; the main session decides every item itself |
| `ELEVENLABS_API_KEY` | ElevenLabs: speech, voices, sound effects, music (`/delegate`, `models.mjs elevenlabs`) | no generated audio; the main session says so |
| `GH_TOKEN` | `gh`, inside the tools and inside OpenCode's runs: finding the PR, `gh pr create`, posting a review, labels | the scripts cannot find or post to PRs |

For `GH_TOKEN`, use a fine-grained token limited to the project's repository, with read and write on
Contents, Pull requests and Issues.

OpenCode reads both `OPENCODE_API_KEY` and `OPENROUTER_API_KEY` from the environment (checked with
`opencode auth list` on 1.18.33), so those need no `opencode auth login`. Go is the exception: without
its console login, `implement.mjs` and `review.mjs` fail over and exit 3, and Claude agents take the work.

## Network

A cloud environment's network policy must allow:

| Host | For |
| --- | --- |
| `opencode.ai` | OpenCode's own providers (Zen, Go) |
| `openrouter.ai` | Jev, OpenRouter models, image generation |
| `api.z.ai` | the implementer, GLM-5.3 Flash, and the hard reviewer, GLM-5.3 |
| `api.elevenlabs.io` | ElevenLabs |
| `registry.npmjs.org` | installing OpenCode |
| `api.github.com`, `github.com` | `gh` and git |
| the Ubuntu package archive | installing `gh` with apt |
| `models.dev` | OpenCode's model list. Optional: runs worked without it, but allow it if `opencode models` shows stale ids. |

## The session-start hook

`.claude/hooks/session-start.sh`, registered in `.claude/settings.json`, runs at the start of every
session on the web (and does nothing locally). It:
- installs `opencode-ai@1.18` with npm and `gh` with apt, if they are missing;
- reports which keys are set, as the session's first context.

It never fails the session. OpenCode is pinned to the 1.18 line because the runner's assumptions were
checked against it:
- the `run` flags;
- `session list --format json`, with `id`, `title`, `directory`, `created` and `updated`;
- `export`, whose `info.agent` names the agent that actually ran.

Change the pin only after running the tools against the new version.

On your machine, install the same things yourself: `npm install -g opencode-ai@1.18`, `gh`, and
Node 20 or later.

## First session: check it works

1. The hook's report shows every key `set`, and no setup notes.
2. The hook's report says OpenCode Go is logged in for the scripts' data directory (above), and
   `opencode models opencode-go` there lists the ids in `harness.json`. If an id differs, edit
   `harness.json`.
3. Jev: put two lines such as `{"id": 1, "state": {"title": "Game crashes on load"}}` in
   `items.jsonl`, then run `node tools/harness/jev.mjs ask --decision breaks-play --in items.jsonl`.
   It should print `asked 2 of 2`.
4. OpenCode: run `/run-task` on a small `fix`, and watch the first run: the tail of its log and the
   `implemented by:` line.
