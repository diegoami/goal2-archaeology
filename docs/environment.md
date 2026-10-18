# Environment

What a session needs so the main session can delegate. Everything here is optional: each missing
piece turns one delegate off, and the main session falls back to Claude (the scripts exit 3).

## On your desktop

Locally there is no network policy and no environment settings, and the session-start hook does
nothing. You need:
- Node 20 or later.
- `gh`, logged in (`gh auth login`). It needs no `GH_TOKEN`.
- OpenCode 2 (`opencode --version`: the audited `opencode v2.0.28`), with the guard's dependencies set
  up and the reviewer's provider logged in for the v2 data directory (the next section). OpenCode 1.18
  is the explicit compatibility path only.
- Optional: the credential jail (`tools/harness/lib/jail.mjs`, #68), off by default. With
  `"jail": { "enabled": true }` in `harness.json` and bubblewrap installed on Linux or WSL
  (`sudo apt install bubblewrap`), reviewers run without your GitHub credentials; enabled where
  bwrap cannot run, the review hook and `review.mjs` print a warning. Off, only the guard stops a push.
  With OpenCode 2 the jail is not supported yet: the operand guard is pinned to the native binary's
  bytes, and a wrapped binary is refused before anything is billed (#262); use the v1 path to jail.
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

**On Windows**, the guard's byte pin is the Linux build (next section): run reviews from WSL, or use
the v1 compatibility path (`npm install -g opencode-ai@1.18`, then `HARNESS_OPENCODE_EXE`).

Then run the harness tests (`.github/workflows/ci.yml` lists them; none calls a model) and the
nonbilling preflight of the next section, then the first-session check at the end of this page.

## OpenCode 2, the default (#262)

`review.mjs`, `switch-model.mjs` and `peek.sh` use the installed OpenCode as found. `runOpenCodeWatched`
(`tools/harness/lib/opencode.mjs`) dispatches on the major it reports, through an explicit adapter
(`lib/opencode-protocol.mjs`): 2.x runs `lib/opencode-workflow.mjs`, 1.x the 1.18 runner, anything
else is refused before billing. What v2 changed, from the nonbilling capture of the installed binary
(`tests/fixtures/opencode/v2-live/run-3Ai73R`, README beside it): `run` has no `--dir` and no
`--variant` (the effort rides the model, `provider/model#variant`; the directory is the working
directory), `models` takes no provider and no `--verbose`, the export is `session export`, and a CLI
command without `--standalone` or `--server` talks to a shared background service (`serve --service`),
which it starts when none runs. Agent permissions are ordered `{ action, resource, effect }` rules with
v2's defaults first, beginning with allow-all.

A v2 review, before anything is generated: the binary must be the audited 2.0.28 (its SHA-256 is pinned
in `lib/opencode-guard.mjs`; another build is refused until the guard is revalidated); the reviewer's
permissions are translated from THIS checkout's `.opencode/agents/reviewer.md`
(`lib/opencode-policy.mjs`) and the profile the server loaded must end with exactly those rules; the
run starts its own private server (`serve --stdio`, a generated password, never the shared service);
the selected model, effort and family must be advertised, with no substitution. Then a session unique
to the run is created and `opencode run --server <ours> --session <it>` sends the brief's pointer. The
review is read from the complete session export, never the console; a rejected tool call, an
incomplete turn or any identity mismatch (session, directory, agent, model, effort) fails the run. A
limit interrupts only that session at that server and recovers its export; another session or the
shared service is never touched.

**The shell-operand guard.** OpenCode 1.18 asked for `external_directory` approval for the file operands
of `cat`, `rm`, `cp`, `mv`, `mkdir`, `touch`, `chmod`, `chown` and `cd`; 2.0.28 checks only directory
changes, so a reviewer's `cat <a file outside the worktree>` would run
(`tests/fixtures/opencode/v2-live/native-controls-7CuxTr`). `tools/harness/opencode-guard`, a trusted
plugin (goal2 PR 178's, MIT notice in `LICENSE.opencode`), restores that check with pinned Bash and
PowerShell grammars: an operand outside the worktree and the granted folders makes the shell request
`ask`, which a noninteractive run rejects. Every word of those commands, the name included, is first
evaluated as Bash would (quotes, backslashes, `$'…'`, adjacent fragments, line continuations, `~`);
a word that cannot be evaluated statically (`$VAR`, `$(…)`, backticks, `{a,b}`, `~user`, a glob that
could leave its directory) fails closed (PR 332 round 2, Sol's R1 and R2: a quoted `"cat"` or a quoted
path fragment had escaped the 1.18 code's raw-text check). Its scope is those commands' operands, as in
1.18: other readers (`head`, `sed`, interpreters), wrappers (`env cat`, `xargs`, `bash -c`) and
redirections are not checked. It is a static check of the command text, not an OS jail.
Its dependencies are exact-pinned (`package-lock.json`, `dependency-hashes.json`: 156 file hashes) and
installed once per checkout without scripts; the runs check them offline and never fetch:

```bash
npm ci --prefix tools/harness/opencode-guard --ignore-scripts --no-audit --no-fund
node tools/harness/check-opencode-guard.mjs
```

**Nonbilling checks** (none sends a prompt to a provider):

```bash
node tools/harness/probe-opencode.mjs --out <dir>             # the CLI's protocol: help, an empty session, old commands failing
node tools/harness/preflight-opencode.mjs --out <dir>         # the review transport up to generation (MiniMax key in the environment)
node tools/harness/probe-opencode-guard.mjs --complete --out <dir>       # a real run against a loopback fake model
node tools/harness/probe-opencode-guard.mjs --out <dir>                  # outside reads rejected, granted ones kept
node tools/harness/probe-opencode-guard.mjs --active-cancel --out <dir>  # cancellation spares other sessions
node tools/harness/check-opencode-guard-controls.mjs --out <dir>         # without the guard, v2 reads the outside file
```

**Receipts.** Each v2 run keeps, under `~/goal2-review-tmp-harness/<title>-*/` (outside the reviewer's
grant; review.mjs's log names `run.json`): `run.json` (binary, policy, guard and source hashes; session,
directory, model, agent, PR head; phase, usage, duration; every file's SHA-256), the raw export
response, `export.json`, `final.txt`, `assistant.txt`, stdout and stderr, the brief, the loaded profile
and model, the plugin inventory, the baseline, and the guard's scan log. They are kept on every outcome;
the only text removed is the run server's own generated password, if anything echoed it. `peek.sh`
takes a session id, a run log or a `run.json`: a finished run is read from its retained export, a
running one through a private `session export --standalone` against its own data directory.

**The v1 compatibility path.** Set `HARNESS_OPENCODE_EXE` to a 1.x binary (here
`~/.opencode/bin/opencode.1.18.32.bak`, kept, never deleted) and the harness runs the unchanged 1.18
runner with its own legacy data directory (next section); `peek.sh` then reads with the 1.x binary
(`OPENCODE_BIN` or `HARNESS_OPENCODE_EXE`). There is no automatic search for a backup any more. The
cloud session-start hook still installs `opencode-ai@1.18`, so cloud sessions use this path: the
guard's byte pin is the Linux native 2.0.28, and an npm build is a different binary until revalidated.

## OpenCode Go

**History (the owner, 2026-10-11):** this section's seats, chains and placements no longer pick a model: the main session or a Claude agent implements, and `harness.json`'s `reviewer.default` reviews unless the user names another (CLAUDE.md "Choosing models"). Kept for the logins and probes.

The MiMo v2.6 reviewers are OpenCode Go's (`opencode-go/…`), a subscription. They are not OpenCode Zen's pay-per-token `opencode/…` models. Go comes from a console
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

**History (the owner, 2026-10-11):** this section's seats, chains and placements no longer pick a model: the main session or a Claude agent implements, and `harness.json`'s `reviewer.default` reviews unless the user names another (CLAUDE.md "Choosing models"). Kept for the logins and probes.

The reviewer is GPT-5.6 Luna on the direct OpenAI route (`openai/gpt-5.6-luna`, L51), never a Luna
on Go (`opencode-go/…`): a third-party proxy behind Go's returned `Bad Request` in long agent loops
(L27). OpenAI is an ordinary OpenCode provider: log in once with `opencode auth login`, choose
OpenAI (a ChatGPT login or an API key), and check with `opencode models openai`. The login is kept in
`auth.json`, which the scripts copy into their own data directory (next section) whenever theirs is
missing or older. If OpenAI later asks for a new login, log in again in your usual OpenCode; the
next run copies it.

## Z.AI, for the GLM reviewers

**History (the owner, 2026-10-11):** this section's seats, chains and placements no longer pick a model: the main session or a Claude agent implements, and `harness.json`'s `reviewer.default` reviews unless the user names another (CLAUDE.md "Choosing models"). Kept for the logins and probes.

GLM-5.3 Flash, the default implementer (L42), and GLM-5.3, the first hard reviewer (L41), run on
Z.AI's coding plan (`zai-coding-plan/…`); both stay on watch (L35). Log in once with `opencode auth login` and choose Z.AI Coding Plan (an API
key; OpenCode also reads `ZHIPU_API_KEY`), then check with `opencode models zai-coding-plan`. The
key is kept in `auth.json`, which the scripts copy like OpenAI's. GLM-5.3-highspeed is refused by
the plan.

## Alibaba Token Plan and MiniMax, on watch

**History (the owner, 2026-10-11):** this section's seats, chains and placements no longer pick a model: the main session or a Claude agent implements, and `harness.json`'s `reviewer.default` reviews unless the user names another (CLAUDE.md "Choosing models"). Kept for the logins and probes.

Alibaba is used only when the user asks (CLAUDE.md rule 3 of "Choosing models"). On an Alibaba quota or
rate error, stop using it until the next day, tell the owner, and do not retry: its monthly pool is
small and is not monitored.

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
| `mimo-pro` | `opencode-go/mimo-v2.6-pro` | high | heavy | tested 2026-10-09 on implement, fix, review; MiMo is its own family |
| `mimo-flash` | `opencode-go/mimo-v2.6-flash` | high | light | tested 2026-10-09 on implement, fix, review |
| `mm-m3` | `minimax/MiniMax-M3` | thinking | heavy | offers only none and thinking; a new family, independent reviewer material |
| `mm-m2.7`, `mm-m2.7-highspeed` | `minimax/MiniMax-M2.7(-highspeed)` | — | light | no effort variants; a variant is ignored if sent |

Alibaba is one monthly pool for all its models (`curl -s localhost:8765/quota/alibaba`;
`pricing.discount_now` says whether the night discount is live, 22:00–08:00 UTC+8: qwen3.8 60% off,
`glm-5.3` none — prefer long alibaba runs while it is true). DeepSeek is blacklisted on any
route as of 2026-10-09. MiniMax has 5-hour and weekly windows
(`curl -s localhost:8765/quota/minimax`). Alibaba's Kimi and MiniMax models are Team-edition only
and fail; not registered.

Placements (the owner, 2026-10-09): the implementer chain runs `zai-glm-5.3-flash`, `mimo-flash`,
`mm-m2.7`, `ali-qwen-flash` (then Claude sonnet); the hard reviewer chain runs `zai-glm-5.3`,
`ali-glm`, `ali-qwen-max`, `mimo-pro`, `luna` (then Claude opus). `mm-m3` is the L38 heavy
escalation rung before the Claude fallback and the alternate for the Sol seat when openai is
exhausted. From 8 Oct 2026 `ali-glm` is the default GLM seat (zai's 3x weekday peak). From
9 Oct 2026 DeepSeek is blacklisted and MiMo replaces it on OpenCode Go. The lock bump to
`b8c6cde` awaits the owner's separate word.

## Quota: quota-tracker

**The harness no longer reads it** (the owner, 2026-10-11, CLAUDE.md "Choosing models"): `review.mjs` runs the model named whatever the quota, `lib/quota.mjs` and `choose.mjs` were removed, and no model question shows `/recommend`. The service stays useful to the user, and to the main session when a provider answers with a usage-limit error: then read `/quota/<provider>` and say when it is usable again.

Where the machine runs quota-tracker, a local service, it reports how much subscription quota is
left on each provider: `claude` (the main session and Claude agents), `openai` (Sol and Luna, via
OpenCode), `zai` (GLM-5.3 and GLM-5.3 Flash), `opencode_go` (MiMo v2.6) and `openrouter` (prepaid
credit). It is read-only, on
localhost, with no auth; results are cached 60 s, and `?refresh` bypasses the cache:
- `curl -s localhost:8765/quota`, or `/quota/<provider>` for one;
- `curl -s 'localhost:8765/recommend?tier=heavy'` (or `tier=light`): which model to use.
  `ranking` is best first, each row with `provider`, `model`, `command`, `score` (spare calls per
  day until the pool's reset; negative means the pool would run out before its reset at the current
  demand), `confidence` and `reasons`; `pick` is the first row; `skipped` lists the exhausted or
  nearly full providers, with why. OpenRouter scores 0 (prepaid); Alibaba is not ranked (occasional
  use only, in its discount hours). Right after the service restarts, `note` says the statistics
  are loading: retry after a minute or two. Do not rank by `/best` or `headroom_pct`: percentages
  are not comparable between providers, whose pools differ hugely in size, are monthly or weekly,
  and are partly used by Claude sessions running on them as their main model;
- `curl -s localhost:8765/avoid`: the providers out of quota, with when each is usable again.

Each provider has a `status`: `ok` (under 80% used), `low` (80% or more), `exhausted` (95% or
more: do not use it until `available_at` / `available_in`), `error` (it could not be checked;
`error` says why) or `not_configured`. `headroom_pct` is the percent left on its most-used window;
`windows[]` lists every limit with `used_pct` and when it resets. OpenRouter is prepaid: its
windows never reset, and `remaining_usd` is the balance. A model with a limit of its own is named
in its provider's `when_exhausted.usable_models`. Until 2026-10-09 GPT-5.6 Luna (the reviewer) ran
on a weekly pool of its own (`gpt-5.6-luna:7d`); that window is gone, and Luna is now a peer of
Sol in OpenAI's main pool. Read which pools exist from the windows the endpoint returns, not from
this page.

The models per provider, heavy and light:

| Provider | Heavy | Light |
| --- | --- | --- |
| claude | `claude --model opus` | `claude --model sonnet` |
| openai | `opencode -m openai/gpt-6.1-sol` | `opencode -m openai/gpt-5.6-luna` |
| zai | `opencode -m zai-coding-plan/glm-5.3` | `opencode -m zai-coding-plan/glm-5.3-flash` |
| opencode_go | `opencode -m opencode-go/mimo-v2.6-pro` | `opencode -m opencode-go/mimo-v2.6-flash` |
| openrouter | `opencode -m openrouter/<model>` | `opencode -m openrouter/<model>` |

GPT-5.6 Luna, the reviewer (L51), uses OpenAI's main quota like Sol. When OpenAI is `exhausted`,
Luna alone can still run while `/quota/openai`'s `when_exhausted.usable_models` lists
`gpt-5.6-luna` (the harness's L65 row).

If `curl -sf localhost:8765/health` fails where the service is installed:
1. `systemctl --user restart quota-tracker`, wait a few seconds, and check `/health` again.
2. If systemctl says `Failed to connect to bus`, the user's systemd instance is not running: ask
   the user to run `sudo loginctl enable-linger $USER`, then retry step 1.
3. If it still fails, read `journalctl --user -u quota-tracker -n 50` and tell the user what it says.
4. To run it without the service: `cd ~/projects/models_quota_tracker && uv run quota-tracker serve`
   in the background (it stops when the session ends).

`review.mjs` does not ask the service (above). *Superseded: the quota check before a chain ran
(L52), and `HARNESS_QUOTA_URL`.*

Never read or edit `~/.config/quota-tracker/config.toml`: it holds account tokens. A provider in
`error` over an expired cookie or token goes to the user, since renewing it needs their browser or
login. Where the service is not installed, go on without it, and count a usage-limit error as
`exhausted`.

## DOSBox-X 2024.03.01, for every run of the original

The project is calibrated to DOSBox-X **2024.03.01** (F001, `runtime/driver/savestate.py`): Ubuntu
24.04's apt package. Ubuntu 26.04's apt offers only 2026.01.02, whose savestates store `Vga` raw
and write a save in 3 events instead of 53-54, so no reader works on it (#117). On such a machine,
`bash setup/dosbox-x-2024.03.01.sh` unpacks Ubuntu 24.04's packages (checksums pinned in the
script; no sudo, nothing installed system-wide) into `~/tools/dosbox-x-2024.03.01`, with a
`bin/dosbox-x` wrapper that supplies the libFLAC 12 26.04 lacks. The system package stays for other
projects.
- `runtime/driver/driver.py`'s `dosbox_x()` picks the binary: `$DOSBOX_X`, else that bundle, else
  `dosbox-x` on PATH. The driver, the cycle fingerprint and the recorder (launch and version
  check) use it; `setup/goal2-runtime.sh` resolves it the same way and refuses another version.
- `experiments/E015-human-playthrough/scripted_keys.py` refuses another version before any display
  or emulator starts. `runtime/spike/` (F001's frozen spike) still runs `dosbox-x` from PATH: put
  `~/tools/dosbox-x-2024.03.01/bin` first on PATH for it.
- An OpenCode run of the original needs the same: pass `--env "PATH=$HOME/tools/dosbox-x-2024.03.01/bin:$PATH"`
  only for `runtime/spike/`; the driver and the recorder find the bundle themselves.
- The driver's keys (issue 244): `runtime/driver/xkeys.py` sends every key as a raw XTEST keycode
  with no modifier, and the driver's savestate and load are Scroll Lock and Print Screen through a
  mapper file it writes into the session folder, so the host key F12 is never pressed. On Ubuntu 26.04
  (xdotool 3.20160805.1 with Xvfb 21.1.22) xdotool sent Left Alt with every function key (F10 reached the
  game as Alt+F10) and left Left Alt held in the guest from the launch on; the 458 records made on
  Ubuntu 24.04 show none of that (34 published savestates checked), only a plain F12 pressed into the
  guest at each read. Two independent settings: `legacy_keys` is the transport (raw XTEST or xdotool),
  `mapper` is what the savestate and load keys are (`"nohost"` Scroll Lock / Print Screen, `"dosbox"` the F12
  chord, or a mapper file); the driver presses what the mapper in effect binds and refuses, when it is made, a
  mapper whose savestate, load and screenshot binds are not usable as a set (one key for two actions, an empty or
  unreadable bind, a modifier other than host, the host key F12 itself, differing duplicate lines, a key that
  is no X keysym: `ValueError`), and, before DOSBox-X starts, a key the raw transport cannot send. The old driver is `Driver(legacy_keys=True, mapper="dosbox")`. E031's `play.py` takes
  them as `--keys`, `--fkeys` (function keys and a chord's F12; default as `--keys`) and `--mapper`
  (`experiments/fix-244-driver-keys/README.md` has the table).
- **Read pace**: the savestate key is held `save_hold` seconds, default `SAVE_HOLD` = 0.52 s, so a read takes
  about 0.53 s as it did with the F12 chord (the chord held 3 steps of 0.15 s and made four xdotool calls;
  measured 0.512-0.764 s between chords in E003-r0047/r0049). Scripts whose `settle` waits for two equal
  reads stop earlier on a transient screen at 0.15 s and then do not reproduce their records (E003 d3b);
  at the default they do (`experiments/fix-244-driver-keys/README.md`). Pass `save_hold=` to change it.
- **Start states** (`.cache/states/driver/*.sav`, `main`, `title`, `e004-*`, `e006-*`) made with the old driver
  on a machine where xdotool adds Alt (Ubuntu 26.04) carry Left Alt held in their saved BIOS data
  (`0040:0017` bit 3 set; `python3 experiments/E031-play-the-game/lastkey.py <file.sav>` prints it), and a
  restore from one starts the guest with Alt held. Remake those: `python3 runtime/driver/driver.py make-state title`,
  `python3 experiments/E003-q001-inputs/run.py make-main --dos-time 10:00:00 --dos-date 10/04/2026`, and the
  experiment's own `make-state`. The published driver savestates (release assets named in `evidence/E005`,
  `E006`, `E010`, `E011`, `E013`, `E014`, `E018`) were made on Ubuntu 24.04 and show no Alt held
  (`experiments/fix-244-driver-keys/out/published-states.tsv`).
- **Do not press F1 in a driver run**: the help viewer makes every later savestate crash DOSBox-X
  2024.03.01 (buffer overflow detected, exit -6), even after Esc (E031, `docs/play-guide.md` section 2).

## Ghidra, for the decompiled and named views

`tools/static/decompile.sh` (T18; with `--annotations`, T20's named view) needs these, outside the
repository; nothing else does:
- Ghidra 12.1.4 (release `Ghidra_12.1.4_build`, unpacked to `~/tools/ghidra_12.1.4_PUBLIC`, or set
  `GHIDRA_HOME`). The script refuses another version.
- A JDK 21: Temurin 21.0.12.1 (`~/tools/jdk-21.0.12.1+1`, or set `JAVA_HOME`). The script refuses
  another major version, and the output's README records the exact one.

Ghidra refuses a project path with an element that starts with `.` ("Path element starting with '.'
is not permitted"), and the harness's isolated worktrees are under `<repo>/.claude/worktrees/`. So
Ghidra's project, input and temporary files never go under the repository or `TMPDIR`: the wrapper and
`GhidraMappingTests` make `$HOME/goal2-ghidra-work/<unit>-<random>` (`tools/static/ghidra_work.py`;
`GOAL2_GHIDRA_WORK` names another absolute base), set `TMPDIR`, `TMP` and `TEMP` to it for Ghidra, and
remove it afterwards (`KEEP_WORK=1` keeps it). A base whose resolved path has a dot element (a `HOME`
under `.something`, a link into one) stops the run with that reason (fix #315). No manual `TMPDIR` is
needed in an agent worktree.

Ghidra runs headless with `-max-cpu 2`, one instance at a time (the machine is shared). Without
them, `tests/static/test_decompile.py` skips its Ghidra tests and says why. One run takes about
six minutes on two CPUs: start it in the background.

## A shared machine

Isle-wars' sessions run DOSBox-X and Xvfb on the same machine. Use another display than `:99` (a
stray `Xvfb :99` belongs to neither project), and stop only processes you started, by PID: never
`pkill dosbox-x` or `pkill Xvfb`.

## Heavy jobs

Up to four agents and three reviews ran at once on 2026-10-17: load average 6.8 to 7, reviews of 62-match
runs took one to two hours, one hit its limits, and the idle watch fired "possibly stuck" for work that was only
slow. "At most one match process at a time" was only a line in briefs; since #318 a lock enforces it.

`tools/harness/heavy.sh <name> -- <command>` takes one of N slots (harness.json `heavy.slots`, two; why two, a 1 s poll and a 5 s stale-ticket age: measurements and sources in `notes/318-heavy/README.md`; the
environment variable `HARNESS_HEAVY_SLOTS` overrides it), then runs the command in place of itself (its exit status
and output are the command's). With every slot taken it queues, first come first served, and prints
`heavy: <name>: waiting for a slot (k ahead)` on stderr, k being the jobs queued before it. The slots and the queue
are files in `~/.cache/goal2-heavy` (`HARNESS_HEAVY_DIR`), locked with `flock`, so they are shared by every
worktree and every process of the machine, and a job that dies, even killed with SIGKILL, frees its slot at once.
`heavy.sh --status` lists the slots and the queue; `--weight K` holds K slots (a job that runs K processes).
A `heavy.sh` started inside a heavy job (`HARNESS_HEAVY_HELD` is set) runs its command at once and takes no
second slot, so `check.py` called by the unit suite cannot deadlock a full machine.

Who uses it: `experiments/E036-match-port/family.py` (weight = the match processes it runs at once: `--workers`, but at most the matches still to run, and 1 for `--find-ranges`, which runs its matches one after another), `runtime/original_match/check.py` and
`tools/ci_gate.py run-tests` queue themselves when run as scripts (`runtime/heavy_slot.py`; each reads its slot weight and whether to queue at all with the same argparse parser its `main()` uses, `heavy_slot.parsed`, so a repeated `--workers`, `--workers=2` or an abbreviation weighs what the run uses, and a command line `main()` refuses holds no slot; `check.py` is one process in every mode; the unit suite is one job, and a test of it that starts its own processes (the two-workers test, the human recorder's display stack) is not counted again; not in CI, where the
runner is not this machine, nor when `HARNESS_HEAVY_OFF` is set). The unit suite run by hand is
`tools/harness/heavy.sh unit-suite -- python3 -m unittest discover -s tests`. A review: `review.mjs` puts
`tools/harness/` of the main checkout first on the reviewer's PATH (a PR that predates the script has it too),
names the command in its rules, clears an inherited `HARNESS_HEAVY_HELD`, and sets `HARNESS_HEAVY_QUEUE_FILE`,
a file that `heavy.sh` touches at every poll while the reviewer's command waits; `lib/opencode.mjs` counts the
idle limit from the later of the session's last update and that touch, so queue time is not idle time. The
review itself holds no slot (a review that held one while its reviewer waited for another would deadlock two
reviews on two slots). `tools/harness/heavy.test.mjs` and `tests/test_heavy_slot.py` test it.

## OpenCode's agent permissions

`.opencode/agents/reviewer.md`, the one OpenCode agent since 2026-10-11 (the implementer agent went
with `implement.mjs`), allows `/tmp` and `/tmp/*` (PR 119, the owner, 2026-10-11: a model's scratch
file in `/tmp` was refused and the run ended with nothing posted) and the DOSBox-X bundle (#117).
The grant was lost twice, once by a harness bump; `tests/test_agent_permissions.py` now fails CI
without it, and `harness.lock` lists the file as adapted: carry it over on every bump. A run that
dies on another rejected path is fixed by widening the grant here, never by re-briefing.

Since 2026-10-17 (#311) it also allows `~/goal2-review-tmp` and `~/goal2-review-tmp/*`, a scratch
folder on the real disk. `/tmp` is an 11 GB RAM-backed tmpfs shared with other projects; it hit 100%
and a review of PR 300 died of ENOSPC after an hour. `review.mjs` makes `~/goal2-review-tmp/<pr>-review-<id>`
for each run, sets `TMPDIR`, `TMP` and `TEMP` to it (the path has no dot element: Ghidra rejects
temp paths with one), removes it when the run comes back and keeps it, naming it, when the run
fails. It refuses to start when `/tmp` has under 500 MB free and the scratch disk under 2 GB. Every
folder the harness writes in during and after a review is on that disk and is checked by its resolved
path and filesystem (a root that is a symlink into tmpfs, e.g. `/dev/shm`, is refused, exit 2): the
run's folder, OpenCode's output logs in `~/goal2-review-tmp-harness` (a sibling of the scratch root, outside the
reviewer's grant; every file there is created exclusively, with O_EXCL and O_NOFOLLOW, so a name the
model planted, a symlink included, is replaced as a name and never written through), and the finished review,
which `review.mjs` writes there first (`review-<run>.md`), posts from that file, and only then removes
and cleans the run's folder. A post that fails keeps the file and names it. A kept failed-run folder is
removed by hand once its cause is read. `tests/test_agent_permissions.py`
fails CI without the grant.

## The scripts' own data directory

**OpenCode 2** (#262): `HARNESS_OPENCODE_HOME` (default `~/.local/share/harness-opencode`) holds a
v2-only root, `v2/`. Provider logins and sessions live in its one database, `v2/data/opencode/opencode.db`
(set as `OPENCODE_DB`, so an inherited path cannot reach the legacy one); each run has its own cache,
state, receipt index and protocol marker under `v2/runs/run-*`. A v2 process never opens the legacy
`data/` below and never copies `auth.json`. A provider that needs a login is logged in once for that
root, in your own terminal (the harness never passes secrets on a command line); a provider whose key is
in the environment (MiniMax) needs nothing:

```bash
XDG_DATA_HOME="$HOME/.local/share/harness-opencode/v2/data" \
  OPENCODE_DB="$HOME/.local/share/harness-opencode/v2/data/opencode/opencode.db" \
  opencode auth login --standalone openai
```

Check it with the same two variables and `opencode models --standalone`. On 2026-10-18 that root (made
by goal2's runs) listed `opencode-go` and `minimax` but not `openai`: the default reviewers (Luna, Sol)
need this login before their first v2 review; until then they run on the v1 path. When a model is not
listed, the scripts exit 3 with this command and bill nothing.

**OpenCode 1.18** (the explicit compatibility path): `review.mjs` and `switch-model.mjs` run OpenCode with a data directory of their own, so OpenCode's
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
| `ANTHROPIC_BASE_URL` (with `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`) | the orchestrator itself: unset or Anthropic's for Claude; Z.AI's for GLM, MiniMax's, or Moonshot's for Kimi when Claude's tokens are out. `review.mjs` and `switch-model.mjs` read the session's family from it (CLAUDE.md "Choosing models" rule 0); pass it to a review's unit with `-E` | the session is Claude |
| `HARNESS_SESSION_FAMILY` | overrides that family when the endpoint is one the harness does not know | an unknown endpoint refuses to review until it is set |

For `GH_TOKEN`, use a fine-grained token limited to the project's repository, with read and write on
Contents, Pull requests and Issues.

OpenCode reads both `OPENCODE_API_KEY` and `OPENROUTER_API_KEY` from the environment (checked with
`opencode auth list` on 1.18.33), so those need no `opencode auth login`. Go is the exception: without
its console login, `review.mjs` exits 3: log in and run again.

## Network

A cloud environment's network policy must allow:

| Host | For |
| --- | --- |
| `opencode.ai` | OpenCode's own providers (Zen, Go) |
| `openrouter.ai` | Jev, OpenRouter models, image generation |
| `api.z.ai` | the GLM reviewers, GLM-5.3 and GLM-5.3 Flash |
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

It never fails the session. OpenCode is pinned to the 1.18 line, so cloud sessions run the v1
compatibility path (#262: the v2 guard is pinned to the Linux native 2.0.28 binary, not an npm build).
The v1 runner's assumptions were checked against 1.18:
- the `run` flags;
- `session list --format json`, with `id`, `title`, `directory`, `created` and `updated`;
- `export`, whose `info.agent` names the agent that actually ran.

Change the pin only after running the tools against the new version.

On your machine, install OpenCode 2 with its own installer (`~/.opencode/bin`), `gh`, and Node 20 or
later, and set up the guard (the OpenCode 2 section above); keep a 1.18 binary for the compatibility path.

## First session: check it works

1. The hook's report shows every key `set`, and no setup notes.
2. The hook's report says OpenAI is logged in (the default reviewer), and `opencode models openai`
   lists `harness.json`'s `luna` id. If an id differs, edit `harness.json`. On a desktop with
   OpenCode 2: `node tools/harness/check-opencode-guard.mjs` passes, `opencode models --standalone`
   with the v2 data directory's variables lists the reviewer's id, and
   `node tools/harness/preflight-opencode.mjs --out <dir>` passes (nothing billed).
3. Jev: put two lines such as `{"id": 1, "state": {"title": "Game crashes on load"}}` in
   `items.jsonl`, then run `node tools/harness/jev.mjs ask --decision breaks-play --in items.jsonl`.
   It should print `asked 2 of 2`.
4. OpenCode: run `/run-task` on a small `fix`, and watch the first review: the tail of its log and
   the posted review.

## Raw sittings and other git-ignored data (what is not in the repository, and where it lives)

The owner's recorder sittings (`scratch/human/sessions/<date-time>/`: savestates, `keys.jsonl`, `notes.jsonl`,
`meta.json`, the game copy with its saves, the video) are git-ignored by design (CLAUDE.md rule 18: a savestate is
the game's memory; the key log is the owner's typing; a sitting is about 100-400 MB). What the repository holds
instead: the run records `runs/E015/E015-r0007..r0017` (screens, game state, diffs, the owner's notes), and for
r0001-r0012 the savestates on release `E015` (manifests under `evidence/E015/`).

- **Nothing in the tests, the tools or CI needs a sitting.** A new computer needs a clone and
  `bash setup/goal2-runtime.sh` (it fetches the original game and the saved games from the private releases by hash).
- **Two jobs do need a raw sitting:** T39c's check (`python3 experiments/E022-video-screens/check.py <session folder>`,
  the sitting `20261011-161003`) and re-extracting a run record with `experiments/E015-human-playthrough/extract.py
  <session folder>` (other countries, a fixed extractor).
- **Where the raw sittings are (2026-10-16): an interim backup, one zip per sitting** in
  `~/projects/goal2-archaeology-keep/sessions/` (with `SHA256SUMS` and a README that maps each sitting to its
  record), outside the repository, on the owner's main computer. To use one on another computer, copy the folder
  (or one zip), check it with `sha256sum -c SHA256SUMS`, and `unzip` it into `scratch/human/sessions/`
  (each zip holds the session folder at its top level). **A session that needs a raw sitting and cannot find it
  in `scratch/human/sessions/` says so to the owner and asks for that backup folder; it does not guess.**
- The proper home is a release, one zip per run (issue 224, not done): then a clone and `gh` access are enough.
- Also git-ignored and not backed up: the black videos of old sittings (nothing to decode), small test sessions
  made by agents, `.cache/` (re-created by `setup/goal2-runtime.sh`).
- Released and verified: the owner's saved games (`goal2-saves`, `artifacts/saves.json`), the play-the-game
  milestone saves (`play-the-game-saves`) and its kept savestate (`play-the-game-states`,
  `experiments/E031-play-the-game/out/states.tsv`).

## Third-party tools kept outside the repository (Turbo Pascal compilers, 7-Zip)

Needed only to redo E035 (`experiments/E035-tp-version/`, which compilers built `GOAL.EXE`: Turbo Pascal 5.5) or to
check a decompiled routine by compiling a Pascal transcription of it with the same compiler. Nothing else needs them.

- **The compilers** are the owner's downloads from WinWorldPC (old DOS floppy images; the owner treats them as
  abandonware, as the game, rule 18). They are third-party software: **never committed, run only inside DOSBox-X**.
  They live in `~/projects/goal2-archaeology-keep/tools/turbo-pascal/` on the owner's main computer: `archives/`
  (the 7z files, including the 5.0 manuals), `extracted/` (the floppy images of Turbo Pascal 4.0, 5.0, 5.5, 6.0, 7.0
  and 7.01), a README, and `SHA256SUMS` (hashes the archives only). Copy the folder to another computer and check it
  with `cd tools/turbo-pascal && sha256sum -c SHA256SUMS` (7 lines, all OK); if the
  folder is missing, a session says so to the owner and asks for it; it does not download them itself (the
  WinWorldPC pages need a browser).
- **7-Zip:** the Python reader `py7zr` cannot read Turbo Pascal 7.0's archive (BCJ2 filter). The official 7-Zip
  Linux binary does: `7zz` 23.01 from `https://www.7-zip.org/a/7z2301-linux-x64.tar.xz` (sha256
  `23babcab045b78016e443f862363e4ab63c77d75bc715c0b3463f6134cbcf318`), unpacked to `~/.local/bin/7zz`, no sudo.
- **Reko** (0.12.5, a decompiler tried on a few routines and not adopted, `experiments/E035-tp-version/README.md`)
  is not a requirement; the excerpts it produced are committed.
