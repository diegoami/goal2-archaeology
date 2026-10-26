# Main-session model policy for the engine study

[designed: owner correction, 2026-10-26] Implement all work in the **main session on
`gpt-6.1-sol` at `high`**. Use a **`gpt-6.1-sol` / `xhigh` agent sparingly, only for the
hardest bounded subproblems**. This supersedes the earlier per-task spawned-implementer
assignments and Claude implementation alternatives for
[programme #433](https://github.com/diegoami/goal2-archaeology/issues/433).

## Assignment for every task

| Tasks | Implementer | Effort | Targeted help |
| --- | --- | --- | --- |
| T95–T113 and their slices | Main session, `gpt-6.1-sol` | `high` | A separate `gpt-6.1-sol` / `xhigh` agent only for an exceptionally hard, narrowly scoped part |

The main session reads sources, writes the implementation and explanations, designs experiments,
runs checks, handles findings and merges. T113's review-packet preparation and follow-up fixes
also use the main session at high; its independent verdict remains a separate review.

Do not assign whole tasks to extra-high effort merely because they are labelled hard. First
work the question in the main session at high. When a specific unresolved difficulty warrants
help, isolate it: for example, a signed-arithmetic contest derivation, a subtle original/port
discrepancy or a difficult RNG/state-continuation dependency. Return the result to the main
session for integration and verification. No task automatically requires an agent.

## Limits and handover

- Astra is excluded from implementation and review. The allowed Codex implementation model is
  `gpt-6.1-sol`; `high` is the default and `xhigh` is the ceiling. No max/ultra escalation.
- Retire the previous requirement to spawn an implementer for every task. Claude implementation
  alternatives and silent model/provider fallbacks are not part of this plan.
- For exceptional help, spawn one fresh Sol/xhigh agent with the exact question, relevant source
  and evidence, expected output and scope boundaries. In this collaboration API, explicitly set
  `model="gpt-6.1-sol"`, `reasoning_effort="xhigh"` and `fork_turns="none"`; include the complete
  handover because a fresh context does not inherit the conversation.
- Record the specific reason and scope in the issue/PR, plus the requested model/effort and
  agent identity. Record effective settings when the runtime reports them. Keep shared-checkout
  writes coordinated; the main session retains responsibility for the task.
- All readiness, splitting, static-first, immutable-evidence, compute-budget, CI, prototype and
  milestone gates remain in force. A model correction does not authorise starting a blocked task
  or an unbudgeted experiment.

## Independent reviews

The existing [review milestones](engine-study-reviews.md) remain independent **Claude or Kimi**
reviews. Select and pin the actual reviewer model and supported reasoning setting at activation;
do not impose the retired automatic Opus/xhigh or Codex-reviewer defaults. The reviewer must not
have authored the deliverables and must receive the pinned candidate, primary sources and raw
evidence. The main session prepares the packet and handles fixes; the reviewer supplies AGREE/BLOCK.

Use the existing milestone-review process, including source-backed findings, full relay,
rechecking MUST-FIX corrections and tagging only the accepted candidate. These review checkpoints
are distinct from the rare Sol/xhigh helper: implementation assistance is not independent review.

This file records the owner's execution and spending preference. It makes no claim that a more
expensive model is necessary for a task or that raising effort is a substitute for clear scope
and evidence.
