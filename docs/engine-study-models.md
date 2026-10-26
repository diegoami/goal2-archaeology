# Agent and model assignments for the engine study

[designed: owner, 2026-10-26] Record the advised Codex model/effort in each task and require a
spawned implementer using that selection. A listed Claude alternative may implement the same
contract; Claude may instead supply independent review when Codex implements. This applies to
[programme #433](https://github.com/diegoami/goal2-archaeology/issues/433), T95–T113, their future
slices and the [independent review checkpoints](engine-study-reviews.md).

## Task assignments

These are initial workload recommendations, not measured cross-provider quality equivalences.
The two effort scales are provider-specific; equal effort names do not imply equal cost or work.
Pin model IDs rather than moving aliases; verify actual access and effective effort at dispatch.

| Task | Codex implementer | Effort | Claude implementation alternative | Effort |
| --- | --- | --- | --- | --- |
| [T95](tasks/T95.md) | `gpt-6-luna` | `medium` | `claude-haiku-5-5` | `medium` |
| [T96](tasks/T96.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T97](tasks/T97.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T98](tasks/T98.md) | `gpt-6.1-sol` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T99](tasks/T99.md) | `gpt-6-astra` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T100](tasks/T100.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T101](tasks/T101.md) | `gpt-6.1-sol` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T102](tasks/T102.md) | `gpt-6.1-sol` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T103](tasks/T103.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T104](tasks/T104.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T105](tasks/T105.md) | `gpt-6-astra` | `high` | `claude-opus-5-5` | `xhigh` |
| [T106](tasks/T106.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T107](tasks/T107.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T108](tasks/T108.md) | `gpt-6-astra` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T109](tasks/T109.md) | `gpt-6-astra` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T110](tasks/T110.md) | `gpt-6-astra` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T111](tasks/T111.md) | `gpt-6.1-sol` | `xhigh` | `claude-opus-5-5` | `xhigh` |
| [T112](tasks/T112.md) | `gpt-6.1-sol` | `high` | `claude-sonnet-5-5` | `high` |
| [T113](tasks/T113.md) | `gpt-6.1-sol` | `medium` | `claude-sonnet-5-5` | `medium` |

T95's lighter model handles inventory/census work; semantic interpretation beyond that brief goes
to Sol/high or the appropriate hard task. Sol handles the implementation and synthesis work;
extra-high effort covers tightly coupled state or numerical reasoning. Astra is reserved for
contest analysis, experimental design, defect attribution and architectural decisions.

For T107, the high effort applies to code, experimental deviations and interpretation. Merely
waiting on a validated batch does not need a new reasoning-heavy run. T113's medium-effort agent
prepares the review packet and manages evidence; fixes use high effort. Its independent final
verdict comes from the separate reviewer below. T111 remains conditional on its existing gates.

## Spawn and handover contract

1. Once a task slice is ready under its existing prerequisites, the main session **must spawn a
   separate implementer agent**, with the row's Codex model and reasoning effort set explicitly.
   It coordinates scope, talks to the owner, checks acceptance and merges; it does not quietly
   implement the task using its own default model instead of the assigned agent.
2. The listed Claude alternative is authorised for the same implementation scope when selected.
   Spawn a separate Claude implementer with that exact model and effort; keep the same task,
   evidence, branch and acceptance contract. This is a choice of implementation provider, not
   permission to run two writers against the shared checkout.
3. Give the implementer the full task/slice, docs/process.md §4 brief, source/evidence paths,
   owned artifacts, branch, pinned baseline, outstanding findings and the relevant review gate.
   Slices inherit the package's model/effort and reviewer policy unless a recorded scope-based
   reassessment changes them.
4. In this Codex collaboration API, model/effort overrides require a fresh agent context:
   use `fork_turns="none"`, explicit `model` and `reasoning_effort`, and include the complete
   handover in its message. In Claude Code, use the implementer role and explicit model/effort;
   the locally installed CLI supports `--agent implementer --model <id> --effort <level>`.
   Do not infer that inherited settings select the prescribed model.
5. Record requested model/effort, provider, agent/session identity and source/candidate SHA in
   the issue/PR. Record runtime-reported effective settings when available; otherwise say they
   are requested settings rather than attested settings. If a model is unavailable, use the
   listed alternative and record that choice. If neither is available, report the constraint;
   do not silently substitute a different tier or weaken acceptance.
6. The task file's executable-contract, size-splitting, static-first, evidence, heavy-slot,
   review and CI requirements continue to apply. This update records future dispatch policy;
   it starts no research agent, match batch or review.
7. `max` is a targeted escalation for a well-scoped unresolved problem, not the default.
   Record the reason for an escalation and carry unresolved issues to the independent reviewer.

## Independent review selection

For a Codex implementation, **spawn a fresh `claude-opus-5-5` reviewer at `xhigh`** for
consequential rule claims and ES-R1–ES-R5/conditional ES-R4P. It must not be an author of the
deliverables. Kimi remains an allowed alternative through the configured review provider:
verify and pin its available model ID and supported reasoning setting at activation, rather
than assuming Codex/Claude effort names apply to it.

If Claude implements, select a fresh `gpt-6-astra` reviewer at `xhigh` or Kimi through the
same independent-review contract. Any owner-selected review model overrides these defaults.
The implementer never supplies the independent verdict, and a different conversation alone
does not remove authorship. Reviewers receive the exact candidate, primary sources and raw
evidence, rather than only the implementer's conclusions.

Main-session coordination and candidate preparation are distinct from the reviewer agent.
Activate milestones under docs/milestone-review.md and use the existing launcher; set both
model and effort explicitly. The current wrapper accepts a model but has no effort argument.
For its Claude branch, the documented environment setting reaches the spawned CLI, for example:

```bash
CLAUDE_CODE_EFFORT_LEVEL=xhigh tools/milestone_review.sh <issue> claude claude-opus-5-5
```

The same environment setting applies to tools/review_pr.sh's Claude branch. Verify effective
settings and record the receipt when actually running it; the example above is not a completed
review. Preserve AGREE/BLOCK, source-backed findings, full relay and exact-candidate tagging.

## Basis and availability

The Codex assignments preserve the owner's accepted recommendation and the session's local
Codex catalogue (2026-10-26): Luna, GPT-6.1 Sol and GPT-6 Astra support the selected efforts.
OpenAI's [model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection)
supports choosing settings by workload and checking them against actual task outcomes.

Claude model IDs and effort support were checked against Anthropic's
[model overview](https://platform.claude.com/docs/en/models/overview),
[effort reference](https://platform.claude.com/docs/en/build-with-claude/effort) and
[Claude Code model configuration](https://code.claude.com/docs/en/model-config), and the installed
CLI's help confirms explicit model, agent and effort options. Documented availability does not
prove this account can invoke a model; verify that at the first real dispatch. Recheck exact IDs
when availability changes, and record any revised assignment in the task and issue.
