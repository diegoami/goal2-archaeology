# Agent instructions

This repository's project rules live in [`CLAUDE.md`](CLAUDE.md). Every agent
working on the repository (Claude Code sessions and subagents, OpenCode
sessions, third-party harnesses, or the main session acting directly) reads
and applies those rules before taking any action. Where these files would
otherwise diverge, `CLAUDE.md` wins — it is the single source of truth, and
this file is here only so a non-Claude agent that only looks for
`AGENTS.md` still finds its way to the project's rules.

The roster (who implements, who reviews, who is blocked, how the question is
asked) is `harness.json`, changed only through `tools/harness/switch-model.mjs`
and the `/switch-model` skill. The implementer kind and the reviewer kind are
the project's, the names of the models are not in any rule.
