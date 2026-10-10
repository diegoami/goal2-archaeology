# goal2-archaeology

An evidence-backed specification of *goal (version 2)* (New Era Software, 1993), a DOS text-mode
international football team-management game, using the method of
[game-archaeologist](https://github.com/diegoami/game-archaeologist) (decisions U14–U20). The spec
feeds a faithful rebuild and a bot that maximises the World Cup win rate, in the private `goal2`.
The process is `docs/process.md`; read it before running a task. Tasks are `docs/tasks/T<nn>.md`,
indexed in `docs/tasks/README.md`.

## Rules
1. The main session plans, runs `/run-task`, triages and talks to the user. Who implements and
   who reviews, on which model, is the user's choice ("Choosing models" below); repeated decisions
   go to Jev after a trial, and images and audio to OpenRouter or ElevenLabs models, whose ids come
   from live lists, never memory (`/delegate`).
2. Nobody works in the main checkout: the main session, when it implements, works in its own git
   worktree; OpenCode runs in the worktree the script makes; Claude agents run with worktree
   isolation. Never `git stash`.
3. Status lives in GitHub labels. No document carries a status snapshot.
4. A question is not a request to edit files. Answer it; propose any fix and wait.
5. The Done-when is not negotiable by the implementer. It stops and reports; it never weakens an
   assertion, skips a test or edits its task file. The main session amends a Done-when on `main`
   with the reason in the commit message.
6. The reviewer is never the implementer's model family. It re-runs every Done-when line itself.
7. Merge only with an approving review and green CI. Two rework rounds, then escalate. (L38's
   ladder is superseded: each round's implementer is the user's choice.)
8. Relay review findings in full. Read a run's final message before you retry or re-route it (L55).
9. A test proves behaviour only if it fails without that behaviour; re-take a claim that nothing failed.
10. A comment asserting behaviour at an edge arrives with the test that visits that edge.
11. Until the first playable build, schedule only bugs that break play; the rest are `post-playable`.
12. A bug whose fix stays in the files it names and changes no outcome is a `fix`; a blocking
    one-file mechanical fix may ride the PR that found it, declared under Scope.
13. Design decisions go to the user; nothing else waits for the user.
14. At session start: `gh issue list --label triage:needed --state open`, and any task in flight.

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
    the main session writes `spec/`, after review. Research PRs merge with a merge commit. Every
    measured output (run records, probe logs, timings) lives under a tracked path the task owns, is
    committed and pushed after each batch of runs and at least every 30 minutes, and is never deleted
    or overwritten (game-archaeologist L207).
21. **Difficulty** (U13): game rules, formulas or constants from evidence are hard work; say so in the
    question of "Choosing models" rule 1. Routing by difficulty (game-archaeologist's
    `docs/models.md`) is superseded by the user's choice. Rule 11 has no effect: this repository
    builds no playable game.
22. **Static first** (game-archaeologist U32, the owner, 2026-10-05). A research question is answered
    by reading the decompiled and disassembled `GOAL.EXE` first (the named view
    `static/goal-exe/named/`, then the raw `static/goal-exe/decompiled/` and `static/goal-exe/code/`; Ghidra as `docs/environment.md` says). Runs of the game are made only
    when static analysis cannot answer, or to corroborate a static answer (rule 19). A finding that
    rests on runs says in its Method what static analysis was tried and why it was not enough. A
    missing tool is never the reason: install it, or stop and report. A review treats runs made
    because a tool was missing as a contract defect (gate G0a): rework.

## Choosing models: the user decides (the owner, 2026-10-11)
These rules replace every other model-choice rule in this project, including issue #113's
"follow quota-tracker's /recommend and nothing else" and, here, the global `~/.claude/CLAUDE.md`
rule that quota-tracker decides. Tables, tiers, chains, substitute orders and exclusion lists in
the docs and `harness.json` that pick a model are superseded by them.

1. Before implementing anything (a task, a fix, a plan change), ask the user ONE question with the
   question tool: does the main session implement it, or a subagent, and on which model?
   - The main session: it implements itself, in its own git worktree (never the main checkout).
   - A subagent: the Agent tool with the model the user names (any model this session's backend
     offers), or an external run (e.g. OpenCode, `implement.mjs --model <name>`) with that model.
   Whoever implements works in its own worktree, keeps a short running-notes file there
   (`RUN-NOTES.md`, `docs/running-notes.md`: the plan, a progress line per commit, an END block
   before stopping), pushes after every commit, and opens the PR. When a subagent ends, the main
   session reads its final report before acting and posts its notes on the issue.
2. At every review (first review, re-review, re-check of named fixes), ask the user ONE question:
   which external model reviews? Run that review alone (one at a time, `review.mjs --reviewer
   <name>`), and relay its findings to the user in full. A PR gets one review unless the user asks
   for more.
3. With each question, show quota-tracker's recommendation as a SUGGESTION ONLY:
   `curl -s "http://localhost:8765/recommend?tier=heavy"` for heavy work, `tier=light` for small
   work; its `pick`/`pair` with rank, outlook and reliability. If it doesn't answer, ask without
   the suggestion.
4. The only fixed rules: the reviewer is never of the implementer's model family; DeepSeek is
   never used (the scripts refuse it); Alibaba only when the user asks.
5. Record each choice (who, which model, the suggestion's reasons) on the issue or PR.
6. These rules work whatever model the orchestrator itself runs on; they never name it.
7. A failed run is diagnosed and fixed, not silently re-routed: another model only when the
   provider does not answer, and the user names it.

### Monitoring OpenCode sessions (and any other background agent)
8. Start every OpenCode run in the background, with stdin from a file (never an inherited pipe:
   `opencode run` waits for stdin's end-of-file before it creates a session). Never wait on it blind.
9. Watch it with one monitor that checks every 1-2 minutes:
   - the session started (`opencode session list` in the run's directory, or the run's
     "session ses_... started" line), and the run's exit;
   - progress: the OpenCode log's size and the session's `updated` time, the worktree's changed
     files, new lines in the running-notes file, and new commits on the branch;
   - "possibly stuck" after ~10 minutes with no change; "unpushed" when a commit sits on the
     branch but not on origin for ~15 minutes (push it for the run and record it);
   - free memory, if the machine is short of it: run reviews and builds one at a time.
   For a Claude subagent, the progress signal is its transcript file's size plus its worktree.
10. Tell the user, in plain language, what each running agent is doing: the step it is on, what it
    committed, what it found (from its notes, commits and latest session messages). Never raw log
    lines or byte counts.
11. On a "possibly stuck" flag: check the process is alive, read its newest session messages
    (`opencode export <ses_...>`, or `/run-task` step 2's session reader); a long build or test step
    is not stuck. A dead or 20-minute-silent run is stuck: stop it, but only if it is ours (the
    machine is shared).
12. When a run ends, read its final message before doing anything else. A run that stopped and
    reported a blocker gets an answer (fix the brief or the setup), not a retry on another model.
13. A run interrupted by our own limits (an idle or total timeout) is resumed in its own session
    and worktree (`implement.mjs --session <ses_...> --model <same> --total-timeout-sec <longer>`,
    with a short "continue where you stopped" brief), not restarted from scratch.
