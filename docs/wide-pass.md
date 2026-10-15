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

## Grading the unknowns: importance AND cost, and assume when it is cheaper (the owner, 2026-10-15)

Findings must be practical. An unknown is not investigated because it exists: it is graded, and the
grade decides. "If a finding requires you to play 2 years of game, that is unpractical and it is better
to assume" (the owner).

- **Importance to the remaster and the bot**: **H** a wrong assumption changes the playable loop or the
  results the player sees (a rule of the match, the competition path, the squad); **M** it shapes play but
  not the loop (a tactic's size, a discipline detail); **L** a detail, a rarely reached branch, a screen or
  file nobody builds (highlights, the commentary scroll).
- **Cost to evaluate**: **S** a few hours of static reading, or one driver run of minutes; **M** about a day,
  or a driver campaign of hours; **L** game time of years, many repeated matches for a statistic, new
  tooling, or a session of the owner.
- **Decision**: investigate when importance is H and cost is S or M, or importance is M and cost is S;
  **assume** (state the assumption and its risk in the register row, mark it `assumed`) when cost is L and
  importance is not H, or when importance is M and cost is M; drop when importance is L and cost is not S.
  An H with cost L is raised to the owner with a proposed assumption.
- **A question never waits for a long session.** A finding whose only evidence would be a long run is
  replaced by an assumption now, and the run is made only if the assumption proves wrong where it matters.
- **Static first stays** (rule 22); a corroborating run is made when it is cheap (S), not as a rule.

Applied 2026-10-15 to what is open (the remaster's register rows and our issues):

| Unknown | Importance | Cost | Decision |
| --- | --- | --- | --- |
| Ageing dynamics over years (Q013, A-COMP-8) | M | L (years of game time) | **Assume F016's reading**; no run |
| Competition calendar corroboration (Q030, F023) | H | L (two years of game per check) | **Assume the read (F023)**; corroborate only the first stage if a run is cheap |
| Computer lineup and tactics (Q035, F024) | M | L | **Assume F024** |
| Home advantage (Q028, A-MATCH-5) | M | M (a statistic over many matches) | Static read of `0BC4` with the host flag only (S); else **assume none** |
| Offside: which side, and a team-mate's offside cancelling a goal (#227) | M | S-M (static) | **Investigate, static only**, one task |
| Man-marking target byte and the sending-off flag values (#228) | M / L | M | **Assume**: default marking; flags from F027 |
| Does a sweeper in a centre-back slot cost the halving (#231) | M | S (F028 data) | **Assume from F028**, one paragraph |
| Duplicate names across countries (#232) | L-M (the owner's wish) | S (a script) | **Do it**, minutes |
| Shoot-out arm `A10A` (cups) | M | M (set up a drawn cup match) | **Assume** F015's taker ranking and F023's kinds; run only if cheap |
| Watched-match engine exactness (the M-chain, T47 onward) | M | L (each routine 25-45 min of proof) | **Stop**: the stand-in quick engine stays (goal2 A-WATCH-1); resume only if the owner asks for exact watched matches |
| `.HIL` file layout (#229), the commentary scroll size (#230), the keeper gate (#164), exact commentary identity (#40) | L | S-M | **Drop** (post-playable) |
| Prompt waits and keys for automating the original (#226) | M | S | **Done** (F030) |
| Recorder, video, flaky tests, the evidence store | support | M | **Frozen** unless one blocks a run the project needs |

A new question gets its row here when it is filed, with the grade and the decision; the register row it
feeds says `assumed` and what the assumption is.
