# Country TEAM panels: skills, performance and characteristics (#432)

goal2 shows three country-card placeholders as "not decoded yet". This report hands over
the original TEAM panel (`1771:157D`) contract for each, one task and finding per panel.
Manager name, Status and Skill (T93/T94, F034/F035, [428-country-labels.md](428-country-labels.md))
are unchanged. Ranking-top and strips stay open on #432.

| Panel | Task | Finding | Decoder |
| --- | --- | --- | --- |
| Team skills, rows 15..18 | T114 | [F036](../../findings/F036-team-skills-bars-are-0bc4-side-one-line-sums-scaled-by-11e1.md) | `runtime/decoders/team_skills.py`, `team_bars.py` |
| Performance, rows 20..23 | T115 | [F037](../../findings/F037-team-performance-bars-sum-the-match-sides-performance-words-by-role-after-the-first-in-match-menu.md) | `runtime/decoders/team_performance.py`, `team_bars.py` |

Findings start `proposed`. The probes are original code run on genuine memory, plus genuine DOSBox
screens of the owner's sitting E015-r0007. That is static-adjacent corroboration, not a new
behavioural campaign.

## Reading the original memory

Every decoder takes read callbacks over the current original memory, and none bundles original
bytes. goal2 supplies these, each returning exactly the bytes asked for:

| Callback | Bytes |
| --- | --- |
| `read_country(n)` | 191 bytes at `far(DS:A917)+191*n` |
| `read_player(w)` | 20 bytes at `far(DS:A91B)+20*w` |
| `read_manager(m)` | 3 bytes at `far(DS:A91F)+3*m`, including m = 0 and human slots 129..134 |
| `read_ds(off, n)` | n bytes at `DS:off` |
| `read_code(seg, off, n)` | n bytes at image paragraph `seg` (relocated), offset `off` |

The panel recomputes everything on every draw. Call the decoders whenever goal2 draws the card,
never from a cached copy. Host checks (record sizes, line-table bytes above 5) raise `ValueError`.
They are consumer bounds, not original behaviour. The original follows such inputs outside its
tables.

## Team skills (T114, F036)

`team_skills(country_record, read_player, read_country, read_manager, read_ds, read_code)`
returns `bars` (four dicts: `line`, `row`, `column`, `value`, `cells`) and `line_sums`.

- **Inputs**: squad words 0..10 of the country record (slots 1..11 only; zero words are skipped).
  For each player it reads strength bytes +2, +4, +5, form +0xC, energy +0xE, position +6, side +7,
  tactics +0xF, status +0x10, and its own country byte +0, whose record's +0x2D tactics byte it
  reads. It also reads the country's manager selector +0x2E and that manager's ability byte +1
  (manager 0 included), the tables `DS:0D4E`, `DS:0E60` and `DS:0E7C`, and the sets at
  `1771:0BA4`, `1771:3139` and `1771:3159`.
- **Rendering**: rows 15 keeper, 16 defence, 17 midfield, 18 attack. Each template row holds 25
  cells of `■` from column 10. Give the first `cells` (0..25) of them attribute 0x70 (black on
  grey); leave the rest in the template colour (0x05). The characters never change, so there is
  no number and no label. `value` (1..256) is for debugging only.
- **Do not** substitute goal2's existing line-strength bars, raw sums or percentages. Lines 1..3
  are divided by 4 and the keeper is not; the clamp is 1..256 and the scale `v*25 idiv 256`.
- **Side effect**: the original leaves the scaled values in side 1's quick-engine words. Every
  reader recomputes them first, so goal2 need not reproduce it.

Regressions to carry into goal2: Denmark 21/25/25/9, Holland 25/19/24/16, Scotland 23/19/25/12,
Russia 23/17/20/17, Yugoslavia 23/18/21/17, R.C.S 21/24/22/12 and Italy 23/20/18/10 (computer
managers, country selection). In-match Italy shows 22/20/20/7 and 22/19/20/8 after a tactic toggle,
with the human manager E Go at ability 0 (bonus 16). Add boundary cases for the clamps (keeper 10
gives 0 cells, defence 44 gives 1 cell, 1027 gives 25), an unavailable player, a zero squad word,
manager 0 and the tactic override.

Pinned for vendoring: `team_bars.py` sha256 `4631ccf2c135a151800d0cddd6a84819aaf7ef0ce7b1c646fc746a2bb94582cf`,
`team_skills.py` sha256 `1f530c1f7a9bad85af350343f222f8b702f508244ab7c7abd776da0dac858c6a`, with the
reviewed commit recorded on #432.

Reproduction:

```sh
/home/diego/.local/bin/python3.12 -B -m unittest tests.test_team_skills_decoder
/home/diego/.local/bin/python3.12 -B notes/432/skills/mutations.py /tmp/T114-mutations-<new>.json
tools/heavy.sh T114-original -- /home/diego/.local/bin/python3.12 -B notes/432/skills/probe.py --output /tmp/T114-original-<new>.json
```

The probe needs the cached E006-r0001, E010-r0001..r0010 and E011-r0001 savestates and the 19
E015-r0007 snapshots (release assets, verified by hash against their run records and manifest).
Missing inputs are prerequisites, not permission to skip the comparison.

## Performance (T115, F037)

`team_performance(country, match_set_up, in_match_menu_used, sides, read_country, read_player, read_ds)`
returns None when the original draws no performance bars. Otherwise it returns `side`, `team`,
`bars` (as for skills, rows 20..23) and `role_sums`.

- **Gate**: pass `DS:0C1E` as `match_set_up`, `DS:0C1F` as `in_match_menu_used`, and the words
  `DS:9B34` and `DS:9B36` as `sides`. The bars exist only when both bytes are nonzero: during a
  match, after the first (pre-match) visit of the in-match menu has returned. In goal2's terms, a
  fixture is set up and the in-match menu has been left at least once. On the country list, the
  main menu and the pre-match menu, leave rows 20..23 as the template: 25 unhighlighted `■` per
  row. That is not a bar of zero, and not "no data".
- **Which team**: side 1 when `DS:9B36` is the panel's country, else side 0. In a match the panel is
  reached for either side. A non-participant would show side 0's bars. Keep that rule; do not
  substitute the panel's own country.
- **Inputs**: the chosen side's eleven squad words (slots 1..11, a zero word included as player 0).
  For each, the player's `+0x12` performance word and `+6` position, plus the table `DS:0D7C`.
  Each word becomes `((p - 0x37), minus 10000 when signed above 5000) + 100` in 16-bit
  arithmetic, so a fresh starter or substitute is 100 and a blank 0x7FFF is 22812. Roles 4 and 5
  give a signed, truncating half to two lines. Sums wrap at 16 bits.
- **Rendering**: identical to skills, at rows 20..23 from column 10, with attribute 0x70.

Regressions: in-match Italy (side 1 of 29 v 16) gives role sums 99/497/600/204 and cells
9/12/14/4. The gate is closed (None) on every country-selection screen. Add the substitute word
10055, the blank, raw 5055 against 5056, odd negative hybrid halves on a cell boundary, a
non-participant country, and each gate byte alone.

Pinned for vendoring: `team_performance.py` sha256
`cd65009941455e7a0c1bd98a7d920ad3e57782f47e4940ccfe949c1a3e17200a` with `team_bars.py` as above.

```sh
/home/diego/.local/bin/python3.12 -B -m unittest tests.test_team_performance_decoder
/home/diego/.local/bin/python3.12 -B notes/432/performance/mutations.py /tmp/T115-mutations-<new>.json
tools/heavy.sh T115-original -- /home/diego/.local/bin/python3.12 -B notes/432/performance/probe.py --output /tmp/T115-original-<new>.json
```

No original executable, data, savestate or screenshot bytes cross repositories. No goal2 change is
part of this delivery.
