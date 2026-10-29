# Repository model policy

[owner instruction, 2026-10-29] This repository is model-agnostic. It fixes no model,
provider, model-specific effort tier, allowlist, denylist or named fallback chain for
implementation, helpers, handoffs or review.

## Selection belongs to the caller

- Use the model and supported settings configured for the running session, unless the
  caller explicitly selects others. A handoff can continue with another configured model
  without rewriting the task or asking for a model-policy exception.
- Helpers inherit caller configuration or receive an explicit choice at dispatch. Delegate
  on the task's needs; no named model or automatic per-task spawning is required.
- Review launchers forward the required caller-supplied model identifier unchanged. That
  argument is explicit configuration, not a repository default or catalogue restriction.
  Interactive clients and agent definitions use their configured selection.
- Do not silently substitute another model/provider or escalate settings. Respect the caller's
  explicit selection and resource limits; report effective settings when the runtime exposes them.

## Review and evidence

Model-agnostic selection does not relax review independence: the reviewer must not have authored
or helped implement the deliverables, and the repository's cross-family review requirement remains.
Choose an appropriate configured reviewer without naming a required model or provider here.
Pinned candidates, checks, reproduced findings and the AGREE/BLOCK process remain unchanged.

Recorded model names in historical run, assistance and review evidence describe what actually ran.
They are provenance, not defaults or future assignments. Preserve immutable evidence and Git
history; never rewrite measurements merely to remove a historical identifier. When inspecting an
older checkout, its retired model assignments do not override this owner instruction.

All task readiness, scope, static-first research, immutable-output, compute-budget, CI, prototype
and milestone gates remain in force. Model choice does not authorise a blocked task, new
experiment, weaker assertion or production/default change.
