# goal2-archaeology

An evidence-backed specification of *goal (version 2)* (New Era Software, 1993), a DOS text-mode
international football team-management game, using the method of
[game-archaeologist](https://github.com/diegoami/game-archaeologist) (decisions U14–U20). The spec
feeds a faithful rebuild and a bot that plays a country competently for idle play (the owner,
2026-10-11), in the private `goal2`.
The process is `docs/process.md`; read it before running a task. Tasks are `docs/tasks/T<nn>.md`,
indexed in `docs/tasks/README.md`.

## Rules
1. The main session plans, runs `/run-task`, triages and talks to the user. A subagent it spawns
   implements (or it does itself), and OpenCode reviews, asking the user before each ("Choosing
   models" below); repeated decisions
   go to Jev after a trial, and images and audio to OpenRouter or ElevenLabs models, whose ids come
   from live lists, never memory (`/delegate`).
2. Nobody works in the main checkout: the main session, when it implements, works in its own git
   worktree; OpenCode runs in the worktree the script makes; Claude agents run with worktree
   isolation. Never `git stash`.
2a. **Never remove a worktree** (the owner, 2026-10-11, after the main session removed a running
    review's worktree mid-run): not after a merge, not in a cleanup, not one that looks finished.
    The harness scripts' removal of their own worktree at the end of their own run is theirs.
    Old worktrees go only through the **sweep**, at session start (rule 14) and at least once a
    day: a worktree is old when ALL hold — no process has its cwd or an open file in it
    (`ls -l /proc/*/cwd`, `lsof +D`), no systemd unit or monitor of this or another session uses
    it, its newest file and last commit are more than 7 days old, its branch is merged or gone
    on origin, and it is clean (else its diff is saved as a patch beside it first). Keep its
    savestates under `.cache/kept/` before removing it. Anything in doubt stays, and the sweep
    lists what it removed and what it kept, and why.
3. Status lives in GitHub labels. No document carries a status snapshot.
4. A question is not a request to edit files. Answer it; propose any fix and wait.
5. The Done-when is not negotiable by the implementer. It stops and reports; it never weakens an
   assertion, skips a test or edits its task file. The main session amends a Done-when on `main`
   with the reason in the commit message.
6. The reviewer is never the implementer's model family. It re-runs every Done-when line itself in a
   task's first review. In a rework round it re-runs the seeded sample the brief names (for an engine
   task: F40 seeds 1-5, 2 of O8, 2 of S), all unit tests and the mutation checks, and verifies the
   committed full-family outputs by sha256 against the implementer's manifest and by a compare.py run on
   the committed files; a sample difference or a hash mismatch sends it to the full run. Reason: a full
   62-match family run is about 15 CPU minutes and reviews took 1-2 hours each round (the owner,
   2026-10-18, #319; `docs/review-brief.md`, "Rework rounds").
7. Merge only with an approving review and green CI. Two rework rounds, then escalate. (L38's
   ladder is superseded: the same implementer fixes the class of the findings, not each instance.) With both, merge at once
   without asking (the owner, 2026-10-04): research PRs `--merge` (rule 20), the rest `--squash`.
   The main session may grant a third, narrow round itself when the remaining findings are small
   and change no result (the owner, 2026-10-05). When it escalates over small exact corrections,
   it offers "small fix + delta review": it applies the corrections in the task's worktree and
   the reviewer checks only `git diff <old>..<new>`.
8. Relay review findings in full. Read a run's final message before you retry or re-route it (L55).
9. A test proves behaviour only if it fails without that behaviour; re-take a claim that nothing failed.
9a. Undo a mutation or scratch edit by writing back the file's saved contents (read it first, restore
    it in a `finally`), or commit first; never `git checkout`, `git restore` or `git reset` a file with
    uncommitted work: they return the last commit and destroy the rest (PR 114 round 1).
10. A comment asserting behaviour at an edge arrives with the test that visits that edge.
11. Until the first playable build, schedule only bugs that break play; the rest are `post-playable`.
12. A bug whose fix stays in the files it names and changes no outcome is a `fix`; a blocking
    one-file mechanical fix may ride the PR that found it, declared under Scope.
13. Design decisions go to the user; nothing else waits for the user.
13a. A lesson or a decision of the owner goes into this file or `docs/` in a commit, never only
    into Claude's memory, which stays on one computer (the owner, 2026-10-11). Memory holds nothing
    the repository needs.
14. At session start: `gh issue list --label triage:needed --state open`, any task in flight, and
    the worktree sweep (rule 2a).

## Token economy
15. A brief carries the task file pasted in full, never a pointer to it.
16. Keep every file an agent must read under ~20k tokens. Scope searches to the source and test
    directories; keep terminal output quiet; show diffs, not files.

## Conditional
17. [evidence-driven] Every constant in driver or parser code (an offset, a timing) traces to a finding
    or a representation claim; a guessed value says so and what was searched.

## This project
18. **The artifact comes by hash** (U17: GOAL2 is treated as abandonware). The original files are
    assets of a release of this private repository, verified against `artifacts/known.json`; they are
    never committed to the tree. Derived extracts (data tables, the unpacked executable's listings)
    may be committed, under `static/`. Nothing of GOAL2 goes to a public repository.
19. **Behavioural and static methods** (U16). The original runs in DOSBox-X in WSL; `GOAL.EXE` may be
    unpacked and decompiled. `corroborated` needs both a behavioural and a static finding.
20. **Research follows game-archaeologist ADR-007/008 and `method/research-protocol.md`.** Run records
    are raw and immutable, evidence bundles are release assets, and findings start `proposed`. Only
    the main session writes `spec/`, after review. Research PRs merge with a merge commit (never squash: tag `research/T02`
    keeps the commits `runs/E001` cites, from #12's mistaken squash; never delete it). Every
    measured output (run records, probe logs, timings) lives under a tracked path the task owns, is
    committed and pushed after each batch of runs and at least every 30 minutes, and is never deleted
    or overwritten (game-archaeologist L207).
21. **Difficulty** (U13): game rules, formulas or constants from evidence are hard work; a hard
    task's file names `sol-6.1` as its reviewer ("Choosing models" rule 2). Routing the implementer
    by difficulty (game-archaeologist's `docs/models.md`) is superseded: Claude implements. Rule 11 has no effect: this repository
    builds no playable game.
22. **Static first** (game-archaeologist U32, the owner, 2026-10-05). A research question is answered
    by reading the decompiled and disassembled `GOAL.EXE` first (the named view
    `static/goal-exe/named/`, then the raw `static/goal-exe/decompiled/` and `static/goal-exe/code/`; Ghidra as `docs/environment.md` says). Runs of the game are made only
    when static analysis cannot answer, or to corroborate a static answer (rule 19). A finding that
    rests on runs says in its Method what static analysis was tried and why it was not enough. A
    missing tool is never the reason: install it, or stop and report. A review treats runs made
    because a tool was missing as a contract defect (gate G0a): rework.
23. **The engine migration comes first** (the owner, 2026-10-18): "As a rule, work toward the engine
    migration first and document reflection or hardening issues." The route-C engine port (the port
    of the watched match engine, T57-T80 in `docs/backlog.md`) has priority over everything else.
    Hardening, defence-in-depth and edge-case work on the proof, the harness or the tooling (for
    example the reflection routes to the raw Unicorn engine, #333; refusals that wait for a slot,
    #328) is not fixed ahead of the port, unless it blocks a port task or breaks the proof for
    ordinary use. It is recorded as a follow-up issue that states the known limit and its acceptance
    (what would close it), and, where the limit concerns a mechanism, as a note in the docs too. A
    reviewer's finding that is a deliberate-reflection or adversarial-use route, when the port's own
    code does not use it, is likewise a known limit with a follow-up issue and is not reworked
    again. The owner decides when a limit is worth closing.

## Choosing models: who implements, who reviews (the owner, 2026-10-11 and 2026-10-12)
These rules replace every other model-choice rule in this project: the morning of 2026-10-11's
"the user decides, with /recommend's suggestion" (L104), issue #113's "follow quota-tracker's
/recommend and nothing else", and the global `~/.claude/CLAUDE.md` rule that quota-tracker
decides. What worked: a subagent spawned inside Claude Code implements (or the main session does, when
it cannot spawn one), and a separate OpenCode process of another family reviews. The roster is the owner's and changes often: the
defaults and the blocked list live in `harness.json` and change through `/switch-model`, never by
a rule that names a model. No quota, tier or difficulty table picks a model.

0. **The orchestrator is set by the Anthropic environment variables alone** (`ANTHROPIC_BASE_URL`,
   `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`): Claude by default; when Claude's tokens are out, GLM-5.3
   through Z.AI's Anthropic-compatible endpoint, or MiniMax, or Moonshot's Kimi, which then work
   like Claude. These
   rules never name the orchestrator's model. The harness reads the orchestrator's **family** from
   that environment (`lib/common.mjs` `sessionFamily`: Claude when the base URL is unset or
   Anthropic's, GLM for Z.AI, MiniMax, Kimi for Moonshot; `HARNESS_SESSION_FAMILY` overrides, and an unknown endpoint refuses
   to review until it is set), because every subagent the session spawns, whatever its model,
   runs through the same endpoint and is of that provider's family. Pass `ANTHROPIC_BASE_URL` and `HARNESS_SESSION_FAMILY` to
   a review's systemd unit (rule 9).
1. **Before each implementation, ask the user ONE question** with the question tool: which
   **subagent** implements, or does the main session implement directly? The implementer is
   normally a subagent spawned inside Claude Code with the Agent tool
   (`subagent_type: "implementer"`, `.claude/agents/implementer.md`, worktree isolation) on a
   model of its own, not the orchestrator's: Opus orchestrates and spawns Sonnet. The model is a
   Claude Code alias (`sonnet`, `opus`, `haiku`, `fable`) or any model id the session's provider
   serves; under another Anthropic-compatible provider (Z.AI's GLM, MiniMax, Kimi) the same alias
   resolves to whatever that provider maps it to (GLM-5.3 Flash for `sonnet` on Z.AI), or the id
   names its model outright. When the provider cannot spawn a subagent (one model only, or the
   Agent tool's model is not honoured), the main session implements directly, in its own git
   worktree (never the main checkout). Propose `harness.json`'s `implementer.default` first.
   Whatever the model, a subagent runs through the session's endpoint, so its family for the
   reviewer rule is the session's (rule 0). OpenCode never implements: `implement.mjs` was
   removed, because its runs died on rejected paths, resets and early ends and did not follow the
   brief (L104). Whoever implements keeps `RUN-NOTES.md` in its worktree (`docs/running-notes.md`:
   the plan, a progress line per commit, an END block before stopping), pushes after every
   commit, and opens the PR. When a subagent ends, the main session reads its final report before
   acting and posts its notes on the issue.
2. **Before each review, ask the user ONE question:** which OpenCode model reviews? Propose
   `harness.json`'s `reviewer.default` first (GPT-5.6 Luna today; `sol-6.1`, GPT-6.1 Sol at
   `low`, for hard research, rule 21), and list the registered models that are neither of the
   session's family nor blocked. Then `tools/harness/review.mjs --pr <n> --brief <file> --issue
   <n> --apply-label [--reviewer <name>]`, one review per PR unless the user asks for more; its
   findings are relayed in full (rule 8). OpenCode's models do not always follow the brief: the
   script posts what came back, flags what it cannot read (exit 4), and the main session reads a
   flagged review and decides rather than paying for another. Record the answers to both
   questions on the issue or PR.
2a. **Asking is a setting** (the owner, 2026-10-13: the answers were the same every time). `harness.json`'s
   `dispatch.ask` is `true` (rules 1 and 2 as written: one question each) or `false`: the main session then
   proposes `implementer.default` and the reviewer for the work's kind (`dispatch.reviewerByKind`: `fix` for a
   fix or docs, `research` for a task whose Done-when is evidence from the game), says the pair in one line,
   records it on the issue and PR, and proceeds. It asks anyway when it wants another model, when the default
   is blocked or cannot run, or when the user has said to ask. The setting changes through
   `switch-model.mjs --ask on|off` and `--review-kind KIND --model NAME`, never by editing a rule.
3. **The fixed rules:** the reviewer is never of the session's family (`review.mjs` refuses it
   from the environment; a `/code-review` or the `reviewer` agent, which are that family, run
   only when the user asks); a model on `harness.json`'s `blocked` list never runs (DeepSeek
   today; `/switch-model --block` and `--unblock` change it); Alibaba only when the user asks.
4. **Permissions, not briefs:** an agent gets the permissions its work needs, in its agent file
   (`.opencode/agents/reviewer.md`: all of `/tmp` and the DOSBox-X bundle; `.claude/agents/*.md`:
   the guard hook refuses only a force-push, `git stash`, `git worktree`, a merge and, for the
   reviewer, every write). A run that dies on a rejected path is fixed by widening the grant,
   never by re-briefing.
5. A failed run is diagnosed and fixed, not silently re-routed: another model only when the
   provider does not answer, and the user names it. The PR records who implemented and which
   model reviewed.
5a. **OpenCode 2.x is permitted when it works** (the owner, 2026-10-13, T174 round 3). The
   harness's `runOpenCodeWatched` refuses any non-1.x CLI with `OpenCode gave no version ...
   desktop app's 2.x CLI differs (#26)`; that is a harness-compatibility check, not a
   correctness one. When the wrapper refuses 2.x but `opencode run` itself runs the brief
   end-to-end and produces a readable review (the way Malpaco did for T10: `opencode run
   --model provider/model#variant --title ... --auto -f <brief>` invoked directly, bypassing
   `runOpenCodeWatched`), trust the run, not the version check. Two ways in: call the wrapper
   with `HARNESS_OPENCODE_EXE=<a 1.18.x binary, e.g. /home/diego/.opencode/bin/opencode.1.18.32.bak>`,
   or call `opencode run` directly and replicate what `review.mjs` does (detached worktree at
   the PR head, reviewer agent, post the result, apply the label). Do not silently re-route to
   a different model because of the version check.
6. These rules work whatever model the orchestrator itself runs on; they never name it.
7. **Still in force:** the effort rule (a heavy model, Opus, GPT-6.1 Sol, GLM-5.3, MiMo v2.6 Pro
   or MiniMax-M3, at `medium` at most and `low` when medium is not needed; a light model at
   `high`); every model id comes from a live list (`opencode models <provider>`), never memory;
   the main session runs Ghidra and the lines an OpenCode reviewer cannot reach (L57).

### Monitoring OpenCode sessions (and any other background agent)
8. Start every OpenCode run in the background, with stdin from a file (never an inherited pipe:
   `opencode run` waits for stdin's end-of-file before it creates a session). Never wait on it blind.
9. Watch it with one monitor that checks every 1-2 minutes. Test a job's life by its systemd unit
   (`systemctl --user is-active <unit>`: start every long job as its own unit, L103) or its PID
   (`kill -0 <pid>`), never with `pgrep -f`, which matches the watching shell's own command line
   and never sees the job end (L48; isle-wars lost 1.5 h to it, 2026-10-11). A unit gets only the
   environment it is given: `systemd-run --user --unit=goal2-<name> --collect -E PATH="$PATH"
   -E MINIMAX_API_KEY -E ANTHROPIC_BASE_URL -E HARNESS_SESSION_FAMILY -p WorkingDirectory=<dir> -p StandardInput=null -p StandardOutput=file:<log>
   -p StandardError=file:<log> <command>` (without the key a MiniMax run stops with "minimax lists
   no models", 2026-10-11; never a `bash -c` script). It covers:
   - the session started (`opencode session list` in the run's directory, or the run's
     "session ses_... started" line), and the run's exit;
   - progress: the OpenCode log's size and the session's `updated` time, the worktree's changed
     files, new lines in the running-notes file, and new commits on the branch;
   - "possibly stuck" after ~10 minutes with no change; "unpushed" when a commit sits on the
     branch but not on origin for ~15 minutes (push it for the run and record it);
   - free memory, if the machine is short of it: run reviews and builds one at a time.
   For a Claude subagent, the progress signal is its transcript file's size plus its worktree.
10. Tell the user, in plain language, what each running agent is doing: the step it is on (as "step k
    of n" where the brief has steps), what it committed, what it found (from its notes, commits and
    latest session messages). Never raw log lines or byte counts. As soon as an OpenCode run's log
    shows `session ses_… started`, give the user the session id and the command to follow it,
    `tools/harness/peek.sh ses_… [-n 20]` (or the run log's path), and repeat the id in every update
    (the owner, 2026-10-11, after isle-wars-archaeology d1e0082).
11. On a "possibly stuck" flag: check the process is alive, read its newest session messages
    (`opencode export <ses_...>`, or `/run-task` step 3's session reader); a long build or test step
    is not stuck. A dead or 20-minute-silent run is stuck: stop it, but only if it is ours (the
    machine is shared).
12. When a run ends, read its final message before doing anything else. A review that stopped on
    a rejected path or an unreadable output gets its cause fixed (a wider grant, a brief line), not
    a retry on another model.
13. A review our own idle or total limit killed is run again with a longer limit
    (`review.mjs --total-timeout-sec <longer>`); a Claude agent our limits interrupted is resumed
    with a short "continue where you stopped" brief, never restarted from scratch.
