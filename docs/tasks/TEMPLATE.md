# T<nn> <Title>

- **Kind**: feature | correction (of T<nn>, bug #<n>) | slice | infrastructure
- **Issue**: #<n> · **Branch**: `task/T<nn>-<slug>` · **Merge after**: T<nn>, …
- **Implementer**: the main session or a scoped helper using caller-configured model/settings; no fixed model or automatic per-task spawning. See [model policy](../model-policy.md).
- **Reviewer**: independent under the repository review rules; caller-configured model/settings, without a named-model requirement.
- **Evidence**: the reports, fixtures or investigations this task rests on, with links.
- **Owns**: directories or files, e.g. `src/Calendar/**`, `tests/Calendar/**`. A task that measures
  owns a tracked path for its outputs, e.g. `runs/E<nnn>/**` or `spike/measurements/**`: they are
  pushed after each batch and every 30 minutes, never deleted or overwritten; originals stay out,
  their hashes recorded (L40).
- **Scope**: what to build, in a few sentences. What is out of scope, if it is easy to confuse. A task
  likely to outlast one implementer run (about an hour), or whose Done-when is all or nothing (an exact
  match, a whole model), is split into milestone tasks first, each merging on its own with a Done-when
  that measures a number (L58).
- **Done when**:
  1. One check a command can run, with the expected result. Before dispatch, each line fails on
     `main` and passes on a mock fix (L45).
  2. …
  3. The build and the test suite are green.
- **Hazards**: the mistake an implementer is most likely to make here, and how to avoid it.
