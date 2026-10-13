# The wide pass (the owner, 2026-10-13)

Go wide before deep: reconstruct as much of the game as possible at **low or medium precision**, with
an uncertainty on every claim, so the `goal2` rebuild and the bot can start from what is known and
say what they guess; then make further passes where the uncertainty matters. T43-T48 (exact
substitutions of single routines, 25-45 min a proof) are the deep kind. They stop at T48 until the
wide pass says which routines matter.

## The claim row

`spec/<area>.md` follows game-archaeologist's `formats/templates/spec-area.md`; each row adds three
columns, so the table is also the parameter table the goal project reads:

| ID | Claim | Status | Scope | Basis | Findings | Uncertainty | Next |
| --- | --- | --- | --- | --- | --- | --- | --- |

- **Claim**: one sentence, with the value, the formula or the constant where there is one.
- **Status, Scope, Basis, Findings**: as in game-archaeologist's `vocabulary/` (a reviewed finding makes a
  row `supported`; `corroborated` needs a behavioural and a static method).
- **Uncertainty** is one of, followed by a short detail (an interval, a count, what was not seen):
  - `exact`: a model reproduces the original bit-for-bit where tested (a substitution that stayed 98/98,
    a seed-exact model); the detail names the tests and the inputs they did not reach.
  - `read`: read from the listing and not yet run against the original (the rule is as written; the
    branches are untested).
  - `measured`: a statistical effect or a table measured in runs, with the interval or the sample.
  - `inferred`: follows from other rows, or from the help file plus one observation.
  - `documented`: only the help file says so.
  - `unknown`: nothing established; the row says what the rebuild would have to guess.
- **Next**: the cheapest step that would raise the row (one line: a task, a run, a listing to read).
  Sensitivity (how much the row moves match or campaign results) is not guessed: pass two measures it
  with a rough rebuild, then spends the deep work on the rows at the top.

## The passes

1. **Pass one (breadth).** Promote what F010-F022 already established, row by row; find the gaps per
   knowledge-map area; one cheap task per gap, a few hours at most, that reads the code or the data
   for the rule or runs a short measurement and records the value with its uncertainty.
2. **Pass two (sensitivity).** A rough `goal2` simulator uses the rows; each `read`, `inferred` and
   `unknown` row is varied over its uncertainty; the rows that move results most are ranked.
3. **Pass three (depth).** Deep work, such as the substitution milestones, goes to the top of that
   ranking and nowhere else.

Promotion stays the main session's alone (CLAUDE.md rule 20, protocol §4): drafts made by other
agents are read by the main session before they go into `spec/`.

## Status rules used at the first promotion (2026-10-13)

- A reviewed, merged finding supports its claim by one method: `supported`.
- `corroborated` only when the row cites two different findings and its Basis has both a behavioural tag (`observed`, `intervened`, `quantified`) and a static one (`static`, `parsed`). Emulation of the original code counted as static-adjacent. Rows drafted `corroborated` that failed this rule were demoted and say so in Uncertainty.
- A row with two statuses in the draft takes the weaker; the draft text is kept in Uncertainty.
- Rows that the drafting agents read out of the listing themselves, without a finding, are `hypothesis` until a finding reviews them.
