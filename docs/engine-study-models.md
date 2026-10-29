# Model policy for the engine study

[designed: owner, 2026-10-29] **No model is fixed.** The main session works on whichever model the
owner runs it on (CLAUDE.md rule 1), implements itself or spawns a helper on its own judgment, and
the owner names a model only when they want a specific one. This supersedes the owner correction of
2026-10-26 (all work on `gpt-6.1-sol` at `high`, rare `xhigh` helpers, Claude implementation
excluded) for [programme #433](https://github.com/diegoami/goal2-archaeology/issues/433) and every
other task. Model lines in earlier task files and assistance records are history, not instructions.

## Helpers

- Give a helper the exact question, relevant source and evidence, expected output and scope
  boundaries; a fresh context does not inherit the conversation.
- Record the reason and scope in the issue/PR, with the actual model, effort and agent identity.
  The main session keeps responsibility for the task and for shared-checkout writes.
- All readiness, splitting, static-first, immutable-evidence, compute-budget, CI, prototype and
  milestone gates remain in force. A model choice does not authorise starting a blocked task or an
  unbudgeted experiment.

## Independent reviews

The [review milestones](engine-study-reviews.md) stay independent: the reviewer did not author the
deliverables and is of another model family than the author's; the actual model and setting are
selected and pinned at activation. The reviewer receives the pinned candidate, primary sources and
raw evidence. The main session prepares the packet and handles fixes; the reviewer supplies
AGREE/BLOCK. Use the existing milestone-review process: source-backed findings, full relay,
rechecking MUST-FIX corrections and tagging only the accepted candidate. Help given to the author is
not independent review.
