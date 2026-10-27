# Tactics and manager controls: from choice to field action

A tactic is a branch input, with personal overrides, role gates and refresh timing. Its label
does not guarantee an action or a better result. The [20-row control matrix](../../notes/engine-study/T103/T103a-v1.json)
records writes, readers, effects, refresh, persistence and limits; the [source calculator](../../notes/engine-study/T103/controls.py)
checks four worked cases and six altered-rule alternatives. These remain proposed interpretations
pending ES-R2. No original/port routine, UI keys or matches were executed for this chapter.

## The control-to-code matrix

Country+2D is the **current** eight-bit team set; immutable R008 is its default source. Pascal
element k is mask `1<<(k−1)`. Team editor1981 displays elements in order **5,6,7,1,2,3,4,8**.
It edits only a managed country outside replay. The same country byte is interpreted differently
by watched action rules and quick aggregate rules.

| Element, clear / set | Readers and immediate consequence | Limits and interactions |
| --- | --- | --- |
| 1 stay back / push forward | 42CB line class;4532 advance;4A28 defensive destination;4E28 selected roles' pass/dribble choice | Effective personal override can shadow it; role and possession decide whether a branch reads it |
| 2 keep ball / quick pass | 5049 holder action gate adds a coin opportunity alongside energy-dependent chance | It does not directly raise passing skill or guarantee a pass rather than another action |
| 3 short / long passes | 3111 initial cutoff2/24 plus a precomputed table value, comparison and candidate replacement | Own-half nonkeeper can force long mode; fallback ignores distance, so neither option guarantees pass length |
| 4 avoid injury / go in hard | 4DA9 watched foul-opportunity gate;D5C1 quick foul gate | Hardness comparison, later cards/injury and loss cap remain conditional; label is not immunity from injury |
| 5 half / full pitch | 4649/4B64 defensive depth tables;4A28 follow guard | The guard's arithmetic effect requires the direction/target qualification in marking.md; no universal full-pitch chase benefit |
| 6 sag / stand ground | 4649/4B64 depth and5729 defending approach-to-ball gate | Changes shape and conditional response; some contexts can move in different directions |
| 7 safe / offside trap | 4532/4B64 advance and depth limits while holding possession | Offside8CF5 reads geometry, not element7 directly; the name is not a separate offside-rule switch |
| 8 zonal / man to man | 1771:3EF8 automatic role-based opponent identities;47C5 consumes the resulting word | Protected manual words survive; a zero marking word can still select/follow an opponent through zonal fallback |

Quick aggregate0BC4 reads effective1 and team5/6 to allocate contributions between attack and
defence. It does not run all watched positioning/holder branches to generate its line sums.
D5C1 separately reads4. Thus a watched effect should not be transferred to a silent/quick
simulation merely because both display the same tactic label.

Keeper labels for1 and3 are stay/leave box and throw/kick from hand. They are the same stored
elements, interpreted by role and event context. There is no extra keeper tactic byte.
[Positioning](positioning.md), [marking](marking.md), [possession](possession.md),
[ball play](ball-play.md) and [discipline](discipline.md) give the actual branch order and tables.

The remaining manager controls are also present in the matrix:

| Choice | Write/refresh and resulting mechanism | Important boundary |
| --- | --- | --- |
| Four personal tactics1..4 | 4B61 edits value bits1..4 and enable bits5..8;26D7/0BC4 consume effective values | Three states per row: inherit, forced off, forced on; no personal override for team5..8 |
| Played position | 4952 cycles player+6 through0..13, or C restores natural+7; marking refresh and9B55 flag | Rebind affects posts, placement/foot penalty, line class, pairing and formation label; natural role remains distinct |
| Manual marking | 49B8 cycles inherited/default, protected zero, then available opposing slots2..11 | Status element7 is protection0x40, not team tactic7; only eligible roles and setup expose this editor row |
| Captain | CC7B returns player identity;20E3 adds twice leadership to rebound pitch extra | Normal230C rebuild resets cache before addition; not an unconditional bonus to every skill |
| Four set-piece identities | CC7B roles2..5;6B65 resolves identity to current squad slot | Restart kind/location/availability can use fallback; shootout full-order9B93 is a different selection |
| Selection/substitution | E44F/E022 with availability/budget/replay gates;EA09 validates XI | Prematch pool exchange and in-match replacement have different admission and role rules |
| Pace | 9372 edits game+3F; shootout changes/restores it | Delay setting is not a stored player speed/pace attribute; nominal timing differs from host wall time |
| Watched/quick mode | 9372,97D0,D733;A10A forces watched kicks | Outer silentD47E is a distinct route from choosing quick within run_match |
| Managed/controller context | Country+2E mapping via0B77 affects setup,AI and editors | Configuration boundary, not a normal mid-match tactical toggle; edits must keep manager mapping coherent |

## Overrides, edits and refresh

For k<=4,26D7 reads the player's own value when enable element k+4 is set; otherwise it
reads the current country byte for the pitch record's **side**, resolved by2974 and9B34/36.
The older annotation says “country in player's byte0”; the listing273B–2752 instead follows
the side binding. Normal coherent records agree, but mismatched synthetic identities must
not silently substitute one rule for the other. 0BC4's separate persistent-player path uses
its own country resolution.

With team element1 on and own byte0, three Enter transitions give bytes **0→16→17→1**:
inherit/on, forced off, forced on, inherit/on. The last state copies the team value into the
unused low bit while clearing enable; it is not the same stored byte as the initial0.
Changing team1 thereafter changes the effective value only while enable is clear.
For element5, own255 cannot override team0: effective5 remains false.

`3431` derives overrides from player fields. Hardness `(profile−(ability&1)) mod256` below4
forces tackling off. Played roles0,1,3,4 set enable/value1. Centre back2 sets enable1 when
profile<14, then enable/value2. It leaves existing other bits in place. `34E7` clears first;
`BBFF` re-derives without clearing. With role2/profile10/ability100, fresh byte0 becomes50;
old17 becomes51, retaining the old push-forward value. Treating every derivation as a fresh
reset changes the effective control. The calculator also checks fresh keeper17, centre-back
profile14→34, soft role5→128 and soft centre-back→178.

Ordinary effective readers see a changed persistent bit on their next call. Layout/cached
state has explicit refresh: ED8A records changed tactics in9B55 and normally exits through230C;
position edits rebuild marking when setup and request refresh in match menus. The team editor
rebuilds marking on the element8 row while setup. These mechanisms do not make an arbitrary
raw record edit retroactively refresh every pitch cache.

Managed choices can survive F1F6; explicit BC5D/reset routes restore defaults. AI setup/after-goal
policy can replace current tactics and derive overrides. The [lifecycle](lifecycle.md) chapter
shows why persistence depends on the route and controller, not merely the field name.

## Formation and marking choices

There is no selected formation ID controlling the engine. The XI's played roles, their order,
availability and feet determine posts and role effects.0E6C counts **available** XI players by
DS:0D5C: keeper0, defence1..4, midfield5..11, attack12..13, then prints the last three counts.
For roles `[0,2,2,3,4,5,6,7,8,12,13]`, the label is4-4-2. Making slot2 unavailable changes the
label to3-4-2 with no played-role change. Different role multisets can share a label and have
different posts/skills/pairings. F028's historical52 formations/nine labels describe its source
roster census, not a menu of52 selectable IDs.

Automatic marking is positional assignment, not maximising marking skill.3E2F considers opposing
strikers12..13, attacking midfield/wings9..11, midfield5..8, sweeper1, defenders2..4; within each
range four preference rows and opposing slots11 down to2 choose the first free own matching role.
Keeper is outside the loops; own sweeper, unavailable and protected players are excluded from
new automatic choices. Explicit protected targets are removed from the opposing candidate pool.

A protected player retains its word even when team8 is off: valid old opponent identity205 remains205
rather than becoming zero.49B8's protected-zero state is deliberate zonal override; its other states
choose available opposing outfield identities. The fifth row requires setup, played role>=2,
availability and the caller's enable flag. Role<2 clears protection in the cycling primitive.
Invalid explicit identities and automatic fallback follow resolver rules documented in marking.md.

## Predictions and limits

Local changes can falsify a source interpretation cheaply: exercise override precedence/cycle,
re-derive with and without clearing, preserve a protected identity under team-zonal, and recompute
an availability-dependent formation label. The four retained examples and six alternatives do
that as **source projections**. Genuine UI input remains separately evidenced; #400 gaps stay open.

No local mechanism proves a tactic improves goals or win rate. Quick-pass changes opportunity
frequency; long-pass changes candidate preference with fallback; line settings interact with role,
possession and occupancy. T105 must define which boundary is changed, which branch actually sees
it, independent randomness and meaningful outcomes before a new sensitivity batch. Historical
F026 measurements retain their original fixture/intervention limits, including its now-qualified
half-pitch interpretation. Source integrity/coverage checks are not match-effect measurements.
