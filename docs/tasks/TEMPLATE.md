# T<nn> <Title>

- **Kind**: feature | correction (of T<nn>, bug #<n>) | slice | infrastructure
- **Issue**: #<n> · **Branch**: `task/T<nn>-<slug>` · **Merge after**: T<nn>, …
- **Implementer**: the main session, or the `implementer` Claude agent (CLAUDE.md "Choosing models"); say which, and why, only when it matters (Ghidra and the pinned tools need the main session, L57).
- **Reviewer**: `reviewer.default` (`luna`, GPT-5.6 Luna), or a `harness.json` key with the reason: `sol-6.1` for hard research (rule 21); never the implementer's family.
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
