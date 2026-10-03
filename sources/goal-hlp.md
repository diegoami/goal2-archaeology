# GOAL.HLP passages (G4)

Source: the help file of *goal (version 2)*, quoted passage by passage. Every quotation is verbatim, with its
line numbers in the file (CR LF line ends read as one line end; CR dropped).

- **Artifact**: `GOAL.HLP` of set `goal2-a949da2f` (release `goal2-original`, [artifacts/known.json](../artifacts/known.json)), 32569 bytes, sha256 `2f3be8648a52045b6f7af1f41cba020d6a662229e5db499e203c5d0957308f60`.
- **Check**: `python3 sources/check_quotes.py <path to GOAL.HLP>` compares every quotation below with the file at its
  cited lines, checks the sha256 above, and checks the links in [knowledge-map.md](../knowledge-map.md).
- **Basis**: `doc`. A passage records what the help file *says*. Nothing here says the game does it.
  The candidate research questions (for G5) are predictions the help file implies, each worded as something
  observable, with no judgment of whether it holds.
- **Layout**: one section per knowledge-map area. A passage is quoted once, under the area it mainly informs,
  and referenced ("Also informs") from every other area it informs. Line numbers count from 1 at the banner.
  Section headings, the banner and blank lines are not passages.

## A01 Countries, continents and their strength

#### P01
Lines 10

```text
128 countries to choose from, incorporating most of the membership of FIFA. Your
```

#### P03
Lines 22

```text
- choose to be any of 128 countries, from 4 continents
```

#### P34
Lines 161–169 · also informs: A11

```text
We have four continents:

1 - Europe
2 - America (ie Concacaf and South America)
3 - Africa
4 - Asia (and Oceana)

Each has 32 nations eligible for its continental championship and for World Cup
qualifying matches.
```

#### P35
Lines 171–173

```text
European teams are on the whole better then American teams, which in turn are
better than African teams, with Asian teams being the most lowly (simply a
reflection of soccer reality and not a political statement).
```

#### P36
Lines 179–185 · also informs: A11

```text
At the start of the game you must choose a country from the 128 offered. Factors
to consider are principally the skills of the players and the continent the team
is in:

The Asian championship is the easiest, followed (of course) by the African, then
the American, with the European championship being the most difficult (arguably
even more difficult to win than the World Cup since qualification is harder).
```

#### P37
Lines 187–190

```text
Each country has its own quirks, so essentially you have 128 different games to
choose from, offering varying degrees of challenge, from what we consider to be
too easy (eg Germany) to virtually impossible! What is more, not one of these
games will ever be the same twice.
```

**Also informs this area** (quoted under another area): [P38](#p38) (lines 196–205), [P41](#p41) (lines 229–233).

**Not stated by the help file**: no list of the 128 countries, no number for any team's strength, and no ranking of individual countries beyond the one example (Germany, "too easy").

**Candidate research questions**

- **Q01.1** The country-selection screen offers 128 countries. ([P01](#p01), [P03](#p03), [P36](#p36))
- **Q01.2** The 128 countries fall into 4 continents of 32 teams each, numbered Europe, America, Africa, Asia. ([P03](#p03), [P34](#p34))
- **Q01.3** Concacaf and South American teams are listed under America, and Oceania teams under Asia. ([P34](#p34))
- **Q01.4** Averaged over each continent's teams, the team-info skills are highest for Europe, then America, then Africa, then Asia. ([P35](#p35))
- **Q01.5** For teams of equal skill, the rate of winning the continental championship is highest in Asia, then Africa, then America, lowest in Europe. ([P36](#p36))
- **Q01.6** Germany's team-info skills are among the highest of the 128 teams, and a human-managed Germany wins the World Cup more often than the average team does. ([P37](#p37))
- **Q01.7** Two games started from the same country with the same selections and tactics do not produce the same results in every match. ([P37](#p37))

## A02 The player pool and the squad

#### P07
Lines 34–36

```text
- squad of 20 players for each country

- select your team from a pool of the 100 best players in your country.
```

#### P22
Lines 106 · also informs: A13

```text
assistant auto-squad selection
```

#### P46
Lines 247

```text
SELECT TEAM - select your team from the pool of players.
```

#### P57
Lines 318–322 · also informs: A05, A10, A12

```text
You should regularly scan through your pool of national players on the lookout
for emerging talent. Your main squad should be updated between every match
(though this, obviously, is not allowed during the finals of a competition or
while on tour abroad), to remove injured, suspended, unfit or less skillful
players.
```

#### P58
Lines 324–325 · also informs: A07

```text
If you're feeling lazy you can ask your assistant to recommend his favoured
squad -  his selection will be based on the team's current formation.
```

**Also informs this area** (quoted under another area): [P38](#p38) (lines 196–205), [P48](#p48) (lines 254–259).

**Not stated by the help file**: how the 100 pool players are chosen or ordered, and how often the pool changes.

**Candidate research questions**

- **Q02.1** The player pool of the chosen country shows 100 players. ([P07](#p07))
- **Q02.2** The squad of the chosen country holds 20 players. ([P07](#p07))
- **Q02.3** The squad can be changed between any two matches, except during the finals of a competition and while on tour abroad, where changes are refused. ([P57](#p57))
- **Q02.4** Players who are injured, suspended or unfit can be taken out of the squad and replaced from the pool between matches. ([P57](#p57))
- **Q02.5** The assistant offers a recommended squad on request, and the recommendation changes when the team's formation changes. ([P58](#p58))
- **Q02.6** New players appear in the pool over the years, and some are better than any player in the squad. ([P38](#p38))
- **Q02.7** Substitutions during a match are taken from the squad of 20 and never from the pool. ([P48](#p48))

## A03 Player attributes and skills

#### P08
Lines 38–49 · also informs: A04, A05, A07

```text
- detailed analysis of each player, includes
          - skills - 12 skill categories
          - fitness and energy
          - hardness
          - age
          - caps (experience)
          - confidence
          - position (from choice of 14)
          - leadership
          - height
          - left/right/two footed
          - performance
```

#### P18
Lines 92–97 · also informs: A05, A07

```text
player info - number of skills increased (8 to 12)
            - extra fitness and confidence categories
            - leadership
            - number of positions increased (13 to 14)
            - performance rating
            - two footed players
```

#### P63
Lines 360–361 · also informs: A09

```text
KEEPING: specific goalkeeping skills. Relevant only to goalkeepers. These cover
such skills as shot stopping,one on one,handling crosses and penalty stopping.
```

#### P64
Lines 363 · also informs: A09

```text
GOAL KICKING: ability to punt a dead ball accurately up-field.
```

#### P65
Lines 365 · also informs: A09

```text
KICKING: used for defensive clearances and goal kicks.
```

#### P66
Lines 367–372 · also informs: A08, A09

```text
TACKLING: ability to take the ball off a player cleanly and legally. A
tackler must match the agility of the player on the ball with his own tackling
skill. Tackling success can be enhanced by 'going in hard' (see tactics below),
but this is related to hardness rather than tackling skill. Vital for defenders.
Also covers blocking, the ability for an outfield player to get in the way of a
shot.
```

#### P67
Lines 374–376 · also informs: A09

```text
HEADING: ability to intercept high balls and to accurately pass and shoot with
the head. Especially important for attackers receiving crosses into the box and
for defenders trying to beat them to it.
```

#### P68
Lines 378–380 · also informs: A08, A09

```text
MARKING: ability to man-mark an opponent. This skill is compared with the
feinting skill of the man being marked. A good man-to-man marker will be
practically on top of his markee whenever his team are defending.
```

#### P69
Lines 382 · also informs: A09

```text
PASSING: accuracy of passing. Of most importance to midfielders.
```

#### P70
Lines 384–385 · also informs: A09

```text
CROSSING: ability to cross the ball into the penalty area (high or low) from the
wings. Naturally useful for a winger, wide midfielder or over-lapping fullback.
```

#### P71
Lines 387–389 · also informs: A09

```text
FEINTING: not the ability to fall over in a dead swoon (though certain strikers
do have the uncanny knack of doing this once they reach the penalty area!), but
the ability to make penetrating runs and shrug off markers.
```

#### P72
Lines 391 · also informs: A09

```text
CONTROL: ability to collect passes and immediately have the ball under control.
```

#### P73
Lines 393–394 · also informs: A09

```text
DRIBBLING: ability to shield the ball from tackles and get round opponents
without losing possession.
```

#### P74
Lines 396–398 · also informs: A09

```text
SHOOTING: ability to put the ball in the net in the course of play. Includes
power and also accuracy, though even the best players will often shoot wide of
the mark when under pressure.
```

#### P75
Lines 400–401 · also informs: A09

```text
PENALTIES: ability to score from the penalty spot. Compared with the keeper's
penalty stopping skill.
```

#### P109
Lines 606–608

```text
You must select a captain for your team. The computer will select the player it
considers best. Press enter if you agree (look at leadership ability), or select
some one better.
```

#### P111
Lines 616–620 · also informs: A06, A09

```text
Each player is given a performance rating, updated for every tackle, shot,
dribble, etc he makes during the game. The highest rated player is given man of
the match. This rating is a reliable guide as to relative performances of your
players (obviously the quality of the opponents should be taken into
consideration).
```

**Also informs this area** (quoted under another area): [P59](#p59) (lines 327–332), [P60](#p60) (lines 334–340), [P61](#p61) (lines 342–350), [P88](#p88) (lines 465–466).

**Not stated by the help file**: the scale or range of any attribute, how hardness, caps, leadership or confidence are measured, and any attribute called agility (named under tackling, line 367, but not listed among the attributes).

**Candidate research questions**

- **Q03.1** A player's detail screen shows skills, fitness, energy, hardness, age, caps, confidence, position, leadership, height, foot and performance. ([P08](#p08))
- **Q03.2** A player's skills are shown as 12 values. The help file counts 12 skill categories (lines 39 and 92) and describes 13 skills by name (keeping, goal kicking, kicking, tackling, heading, marking, passing, crossing, feinting, control, dribbling, shooting, penalties); which names appear on the screen decides which description is not a separate category. ([P08](#p08), [P18](#p18), [P63](#p63))
- **Q03.3** Keeping skill matters only for goalkeepers: changing an outfield player's keeping value changes no match outcome. ([P63](#p63))
- **Q03.4** A tackle's outcome depends on the tackler's tackling skill against the agility of the player on the ball; which displayed attribute plays the part of agility is observable by varying each. ([P66](#p66))
- **Q03.5** Raising hardness, with tackling skill held fixed, raises the success rate of tackles made while going in hard; raising tackling skill alone does not. ([P66](#p66))
- **Q03.6** A man-marker's marking skill is compared with the marked player's feinting skill: a marker with higher marking than the opponent's feinting stays closer to him (practically on top of him) while the team defends. ([P68](#p68), [P71](#p71))
- **Q03.7** A penalty's outcome depends on the taker's penalties skill against the goalkeeper's penalty stopping, which belongs to his keeping skill. ([P63](#p63), [P75](#p75))
- **Q03.8** Players with higher heading skill win more high balls, and are more accurate with headed passes and headed shots. ([P67](#p67))
- **Q03.9** The computer's default captain is the player it considers best, and that choice is predicted by the leadership value: it is the highest-leadership player, or the choice does not follow leadership. ([P109](#p109))
- **Q03.10** A player's performance value on the detail screen changes after each fully watched match, being updated for each tackle, shot and dribble he makes. ([P111](#p111))
- **Q03.11** Version 2 shows 12 skills, 14 positions, leadership, a performance rating and a two-footed foot value, where version 1 showed 8 skills and 13 positions. ([P18](#p18))

## A04 Ageing, peak age and new talent

#### P19
Lines 99

```text
player skills now vary over the lifetime of a player
```

#### P38
Lines 196–205 · also informs: A01, A02, A06, A11

```text
Success or failure in the competitions (measured in terms of points achieved in
the qualifying and final groups, as well as major success in the final knockout
stages) will affect the growth/decline of footballing talent in your country:
ie if you do better than expected (from your country's skill ratings), talented
new players will gradually appear in your pool, often better than any in your
squad; but if you fail to match expectations, you will be lucky to find
replacements up to the standard of players who retire. So the route to success
with a lowly team is to persevere and consistently triumph over those teams who
are supposedly better than you, thus encouraging the growth of footballing
talent in your country. In short, success breeds success.
```

#### P59
Lines 327–332 · also informs: A03, A05

```text
Player skills change with age: each player has a maximum skill he will attain
at his "peak" age. His skill improves till he reaches that age and then tapers
off till he retires. Each player has his own peak age. Skills should be
considered in conjunction with fitness and confidence when selecting players.
Fitness and confidence can be taken together to represent form, and thus can be
seen as a player's ability to utilise his skill.
```

**Also informs this area** (quoted under another area): [P08](#p08) (lines 38–49).

**Not stated by the help file**: any peak age, any rate of growth or decline, the retirement age, and how large the effect of results on new talent is.

**Candidate research questions**

- **Q04.1** A player's skills rise with age up to his peak age and fall after it until he retires, so the sum of a player's skills, followed year by year, is non-decreasing up to a peak and non-increasing afterwards. ([P19](#p19), [P59](#p59))
- **Q04.2** Players have different peak ages. ([P59](#p59))
- **Q04.3** Players retire, and leave the squad and pool when they do. ([P38](#p38), [P59](#p59))
- **Q04.4** After years in which a country's results beat expectations drawn from its skill ratings, talented new players appear in its pool more often than after years in which results match the expectations. ([P38](#p38))
- **Q04.5** After years in which a country falls short of expectations, the new players who replace retirees are worse than the retirees. ([P38](#p38))
- **Q04.6** Success is measured in points in the qualifying and final groups and in how far the team goes in the knockout stage; two histories with the same points and different knockout results lead to different talent changes. ([P38](#p38))
- **Q04.7** A strong country and a weak country with identical results change differently, because the comparison is with the country's own skill ratings. ([P38](#p38))

## A05 Fitness, energy, confidence and morale

#### P60
Lines 334–340 · also informs: A03, A08, A09

```text
Player fitness is very important: keep a close watch on fitness and energy:
player energy will decline during a match in direct proportion to the activity
of the player. Unfit players should be reserved for last minute substitutions,
or not played at all. Exhausted players should be substituted, if possible.
Tactics can be adjusted to minimise the movement of a player, thus preserving
his energy. Fresh players, put on towards the end of a game, can often run
circles round the opposition.
```

#### P61
Lines 342–350 · also informs: A03, A10, A12

```text
Player confidence is also a significant factor in performance: winning or even
drawing matches can boost the confidence of the players involved, and thus the
team morale, as will scoring goals. The opposition is taken into account when
making changes to player confidences: eg Germany may be expected to beat India
by 3 goals, so any margin greater than 3 will improve the Germans confidence,
any margin less than 3 will decrease their confidence. Accordingly, given the
same fixture, India will boost their confidence by only losing by two goals.
Injuries, bookings and sendings off will damage player confidence. Thus the
result of every match, including friendlies, is important.
```

**Also informs this area** (quoted under another area): [P08](#p08) (lines 38–49), [P09](#p09) (lines 51–56), [P18](#p18) (lines 92–97), [P57](#p57) (lines 318–322), [P59](#p59) (lines 327–332), [P76](#p76) (lines 412–414), [P95](#p95) (lines 504–513), [P98](#p98) (lines 532–536).

**Not stated by the help file**: the size of any change, the difference between fitness and energy beyond the text, and how confidence turns into team morale.

**Candidate research questions**

- **Q05.1** During a match a player's energy declines in direct proportion to his activity, so players with more movement lose energy faster. ([P60](#p60))
- **Q05.2** Tactics that reduce a player's movement reduce his energy loss. ([P60](#p60))
- **Q05.3** A substitute brought on late has more energy than the players who started, at the same minute. ([P60](#p60))
- **Q05.4** Winning or drawing a match raises the confidence of the players involved; scoring a goal raises it too. ([P61](#p61))
- **Q05.5** The confidence change depends on the margin compared with the margin expected from the two teams: if Germany are expected to beat India by 3, a German win by more than 3 raises their confidence and a win by fewer than 3 lowers it. ([P61](#p61))
- **Q05.6** In the same fixture, India's confidence rises when they lose by 2. ([P61](#p61))
- **Q05.7** Injuries, bookings and sendings off lower the confidence of the player concerned. ([P61](#p61))
- **Q05.8** Friendlies change player confidence in the same way competition matches do. ([P61](#p61))
- **Q05.9** Team morale rises when the confidence of the players rises. ([P09](#p09), [P61](#p61))
- **Q05.10** At equal skill, a player with higher fitness and confidence performs better in a match (fitness and confidence together stand for form). ([P59](#p59))

## A06 Team analysis and rankings

#### P09
Lines 51–56 · also informs: A05

```text
- analysis of each national team, includes
          - formation
          - skills - attacking,midfield,defence, and keeping
          - average fitness,hardness,age,caps,performance
          - morale
          - world and continental rankings
```

#### P20
Lines 101–102

```text
team info - performance rating
          - history for all teams
```

#### P41
Lines 229–233 · also informs: A01, A07

```text
TEAM INFO - lets you see information for every team. World and continental
rankings given indicate the team's performance in the last World Cup/Continental
championship and are not directly related to the actual skill of that team.
Skills shown are based on the current team of 11 players, not the entire squad,
and allow for the formation chosen.
```

#### P112
Lines 622–623 · also informs: A09

```text
The team performances are based on the performances of the 11 players on the
pitch.
```

**Also informs this area** (quoted under another area): [P38](#p38) (lines 196–205), [P55](#p55) (lines 308–309), [P111](#p111) (lines 616–620).

**Not stated by the help file**: the formula that derives team skills from the eleven and the formation, and the rule that sets the rankings after a competition.

**Candidate research questions**

- **Q06.1** The team-info screen shows the formation; attacking, midfield, defence and keeping skills; average fitness, hardness, age, caps and performance; morale; and world and continental rankings. ([P09](#p09))
- **Q06.2** The team skills shown follow the current team of 11: changing one of the eleven changes them, changing a player who is not among the eleven does not. ([P41](#p41))
- **Q06.3** The team skills shown change when the formation changes with the same eleven players. ([P41](#p41))
- **Q06.4** The world and continental rankings show how the team did in the last World Cup or continental championship: the last winner has the best ranking whatever its skills. ([P41](#p41))
- **Q06.5** The rankings change only when a competition finishes. ([P41](#p41))
- **Q06.6** The team-info screen shows a performance rating, and a team's performance is based on the performances of the 11 players on the pitch. ([P20](#p20), [P112](#p112))

## A07 Positions and formation

#### P76
Lines 412–414 · also informs: A05

```text
STRIKER (dollar sign): a small agile attacker, with a tendancy to roam around
looking for shooting opportunities. Move around a lot in an effort to avoid
markers, so fitness helps.
```

#### P77
Lines 416–418

```text
CENTRE FORWARD (cent): a taller attacker, able to reach high crosses into the
box, and good at heading. Generally less agile than strikers (and with a less
accurate shot), and tend to play through the middle.
```

#### P78
Lines 420–424

```text
LEFT/RIGHT WINGER (W): agile forward midfield player, specialising in runs up
the wings, with the aim of putting a cross into the box or occasionally cutting
inside and having a shot himself. Generally reasonable goal scorers, with
particular abilities at dangerous set pieces. Similar in skills to strikers,
though better at passing.
```

#### P79
Lines 426–428

```text
FORWARD MIDFIELDER (F): like wingers this is a combination midfield/attack
player, though a forward midfielder has a central role. His speciality is the
short incisive pass through to an attacker. Not bad at shooting.
```

#### P80
Lines 430–432

```text
LEFT/RIGHT MIDFIELDER (L/R): in many ways a cross between a fullback and winger,
also with similar skills to central midfielders (see below). Prefers running
with the ball to passing, but is nonetheless adept at passing.
```

#### P81
Lines 434–436

```text
CENTRAL MIDFIELDER (C cedilla): a player specialising in passing and control of
the ball - particularly useful for slowing down play and keeping possession.
Usually the best player in the team.
```

#### P82
Lines 438–441

```text
DEFENSIVE MIDFIELDER (D): plays in midfield behind the central midfielder.
Reasonable passer but used for his ball-winning abilities in midfield. A bridge
between defence and midfield and thus can make an adequate stand-in for a
sweeper. Always willing to have a crack at goal.
```

#### P83
Lines 443–446

```text
LEFT/RIGHT BACK (B): a defender specialising in controlling the left or right
flank of the pitch, so particularly important for countering wingers. Like all
defenders, good at tackling and marking. When pushing forward (overlapping),
will attempt to get to the by-line and send a telling cross into the box.
```

#### P84
Lines 448–449

```text
CENTRE BACK (C): stoppers. Their primary function is to releave their opponents
of the ball. Adept at marking, blocking, clearing, tackling, etc.
```

#### P85
Lines 451–454 · also informs: A08

```text
SWEEPER (S): an agile defender, acting as the last line of out-field defence
against break-aways. The use of a sweeper implies that man-to-man marking is
being practised, thus the sweeper cannot be assigned to mark anyone. He will
often move into a midfield role when the defence is not under pressure.
```

#### P86
Lines 456–457

```text
GOALKEEPER: the specialist who gets the blame whenever a goal is lost. His sole
aim in life is to keep the ball out of his own net.
```

#### P87
Lines 459–463 · also informs: A10

```text
Playing positions can be altered for any player. Their first position may NOT be
the one for which they are best suited, although, it is generally the case.
Repositioning of players during a game is a very useful tactical ploy.
Repositioning also allows you to get around the loss of key players through
injury/suspension/lack of fitness,etc.
```

#### P88
Lines 465–466 · also informs: A03

```text
A two footed player can play equally well on either flank, otherwise it is not
advised to play a left footer on the right flank or vice versa.
```

**Also informs this area** (quoted under another area): [P08](#p08) (lines 38–49), [P18](#p18) (lines 92–97), [P41](#p41) (lines 229–233), [P58](#p58) (lines 324–325), [P95](#p95) (lines 504–513).

**Not stated by the help file**: any list of formations, and any numeric effect of a position or of playing out of position.

**Candidate research questions**

- **Q07.1** The position choice offers 14 positions: striker, centre forward, left winger, right winger, forward midfielder, left midfielder, right midfielder, central midfielder, defensive midfielder, left back, right back, centre back, sweeper, goalkeeper. ([P08](#p08), [P76](#p76))
- **Q07.2** Any player can be placed in any position, and his first (original) position is usually but not always the one that suits him best. ([P87](#p87))
- **Q07.3** Players can be repositioned during a match. ([P87](#p87))
- **Q07.4** A two-footed player plays equally well on either flank, while a left-footed player on the right flank (or the reverse) plays worse. ([P88](#p88))
- **Q07.5** A sweeper cannot be assigned an opponent to mark, and moves into midfield when the defence is not under pressure. ([P85](#p85))
- **Q07.6** Centre forwards have higher heading and lower shooting accuracy and agility than strikers, and strikers move around more. ([P76](#p76), [P77](#p77))
- **Q07.7** Wingers have skills similar to strikers, with better passing. ([P78](#p78))
- **Q07.8** The central midfielder is usually the best player in the team. ([P81](#p81))
- **Q07.9** Full backs that push forward (overlap) go to the by-line and cross. ([P83](#p83))

## A08 Tactics

#### P10
Lines 58–59

```text
- setting of detailed tactics at both team and individual player level before
  and at any point during each match
```

#### P89
Lines 472–475

```text
Tactics can be set both at an overall 'team' level, (for certain tactics)
or individual player level, giving you an enormous amount of flexibility,
especially when taken in conjunction with selection of players and playing
positions.
```

#### P90
Lines 477–481 · also informs: A13

```text
Be prepared to adjust your tactics to suit those of your opponent. What destroys
one team may simply not work with another.

Your opponents may change tactics and positioning as required during the course
of a match - be vigilant.
```

#### P91
Lines 483–486

```text
POSITIONING: stay back/push forward: this tactic adjusts the willingness of
players to press forward when attacking. Push forward to go for goals, stay back
to retain possession and maintain a strong defence. This tactic can be set for
each player, giving you a lot of control over your team's coverage of the pitch.
```

#### P92
Lines 488–491

```text
POSSESSION: stay on the ball/one touch passing: choice depends on the relative
agility and passing skills of your players. Passing may be more favourable if
the opposition are marking man to man. Again, this tactic can be set for each
player.
```

#### P93
Lines 493–495

```text
PASSING: short passes/long passes: long passing is riskier than short passing,
but the rewards are more immediate. The long ball game gains territory whereas
short passing retains possession. Again can be set individually.
```

#### P94
Lines 497–502 · also informs: A09

```text
DEFENCE: half/full pitch: half pitch defence requires less overall ability than
full pitch defence, as the team will drop back into their own half when under
attack, and defend from there. Full pitch defence implies holding ground and
defending immediately possession is lost, from any position on the pitch: if your
team is up to it, full pitch defence can achieve overall dominance of the entire
pitch, but it leaves much more space for the opposition to exploit.
```

#### P95
Lines 504–513 · also informs: A05, A07, A09

```text
SYSTEM: zonal system/man to man marking: marking options are extensive: zonal
system implies that each player will defend his own 'zone' (based on his playing
position), while the man-to-man option assigns each player to an opposing player
(except for the sweeper and goalkeeper). The choice of system will radically
affect the nature of the play, with man-to-man requiring more movement (hence
fitness) from the players, and generally stifling the opposition more
effectively, while the zonal system allows your players to operate with more
space and freedom particularly when switching from defence to attack.
Man-to-man marking will override any of the other tactical options, when there
is a conflict (eg full/half pitch and sag back/stand ground).
```

#### P96
Lines 515–522 · also informs: A13

```text
Assignment of men to mark is done automatically and will be updated whenever
you or your opponents change the team. These assignments can be overridden for
individual players: this allows you to try any combination of man-to-man marking
and zonal, for example, assigning more than one player to a key opposing
attacker. This option requires more work from you, as marking assignments must
be set for each game, and altered whenever either team makes a substitution or
alters player positioning. However, it also allows you to optimise the marking
and gives you more control over your players than (probably) any other option.
```

#### P97
Lines 524–530

```text
Note the following when setting marking assignments manually:
1 - players assigned manually (both your players and any opposing players they
are assigned to) will be excluded from the automatic assignments for the rest of
the team.
2 - marking assignments will be cleared (ie set to 'zonal') for such players, at
the end of the match, so you must remember to set their new assignments at the
start of the next match.
```

#### P98
Lines 532–536 · also informs: A05, A09

```text
PROTECTION: sag back to box/stand ground: sag back is the safer defensive option,
where your players will head towards the box whenever your goal is under threat,
but they will have to rebuild any renewed attack from scratch, and will get
exhausted more quickly than those standing firm in their zonal
defensive positions.
```

#### P99
Lines 538–540 · also informs: A09

```text
OFFSIDE: defensive safety/offside trap: playing offside trap will encourage your
defenders to move forward in the hope of catching the opposing attackers offside,
but if it doesn't work you had better have a very good goalkeeper!
```

#### P100
Lines 542–549 · also informs: A09, A10

```text
TACKLING: avoid heavy tackles/go in hard: players will try to tackle cleanly
unless you tell them through this option (which can be set individually) to do
otherwise. Note, however, the harder the player, the more difficulty he will
have in copping out of heavy tackles, even if he has been instructed to do so.
'Going in hard' improves the chances of winning a tackle, but do not advise
weaker players to 'go in hard' for tackles as they are likely to get injured.
Hard players on the other hand are more likely to injure the opposition and/or
get sent off.
```

#### P101
Lines 551–554

```text
When setting individual player tactics (other than marking assignments - see
above), there are always three options: the two options for that tactic (as per
team tactics,followed by the letter P) and the third option of using the default
team tactic.
```

**Also informs this area** (quoted under another area): [P60](#p60) (lines 334–340), [P66](#p66) (lines 367–372), [P68](#p68) (lines 378–380), [P85](#p85) (lines 451–454), [P103](#p103) (lines 583–585).

**Not stated by the help file**: any numeric effect of a tactic, and which of the team tactics other than positioning, possession, passing and tackling can be set for a single player.

**Candidate research questions**

- **Q08.1** The tactics screen offers eight tactics, each with two options: positioning (stay back or push forward), possession (stay on the ball or one touch passing), passing (short or long), defence (half or full pitch), system (zonal or man to man), protection (sag back or stand ground), offside (defensive safety or offside trap), tackling (avoid heavy tackles or go in hard). ([P91](#p91))
- **Q08.2** At the individual level each tactic that can be set has three options: the two options (with the letter P) and the team default. ([P101](#p101))
- **Q08.3** Tactics can be set before the match and at any point during it, at team and at player level, and only some tactics can be set per player. ([P10](#p10), [P89](#p89))
- **Q08.4** Pushing forward raises the number of players in the attacking half; staying back keeps possession and holds a stronger defence. ([P91](#p91))
- **Q08.5** Long passing completes fewer passes than short passing, gains territory faster, and short passing keeps possession longer. ([P93](#p93))
- **Q08.6** Full pitch defence gives the team more of the possession and territory but concedes more space to the opposition than half pitch defence. ([P94](#p94))
- **Q08.7** Man-to-man marking costs players more movement (energy) and restricts the opposition more than the zonal system does; the zonal system gives players more space and freedom when switching from defence to attack. ([P95](#p95))
- **Q08.8** Under man-to-man marking, every player except the sweeper and the goalkeeper is assigned an opponent. ([P85](#p85), [P95](#p95))
- **Q08.9** Under man-to-man marking, the half or full pitch and the sag back or stand ground options are overridden where they conflict. ([P95](#p95))
- **Q08.10** Marking assignments are made automatically and are updated when either team changes its team. ([P96](#p96))
- **Q08.11** A manually assigned player and his opponent are left out of the automatic assignments for the rest of the team, and the manual assignments return to zonal at the end of the match. ([P97](#p97))
- **Q08.12** Sag back sends players towards the box when the goal is under threat, and they tire more quickly than players who stand ground. ([P98](#p98))
- **Q08.13** The offside trap moves the defenders forward and catches more opponents offside, and exposes the team to more chances when it fails. ([P99](#p99))
- **Q08.14** Hard players have difficulty avoiding heavy tackles even when told to; going in hard raises the chance of winning a tackle; weaker players who go in hard are more often injured; hard players more often injure opponents and are sent off. ([P100](#p100))

## A09 The match engine

#### P25
Lines 112–113

```text
match statistics now include possession, territory, shots on target and
 man of the match
```

#### P26
Lines 115

```text
improved zonal marking
```

#### P27
Lines 117

```text
offside goals
```

#### P28
Lines 119

```text
own goals
```

#### P29
Lines 121

```text
action replays
```

#### P56
Lines 311–312 · also informs: A11

```text
There is a considerable advantage when playing at home. The host nation for a
competition enjoys this advantage in the finals.
```

#### P104
Lines 587–588 · also informs: A16

```text
Hit INS to toggle the action replay facility on or off. This enables/disbables
both the replay of goals and the option to save them.
```

#### P105
Lines 590–592

```text
During the game hit the spacebar to get the match commentary (up to the last 200
comments), enabling you to analyse exactly how a goal came about, etc. , and how
well individual players are doing.
```

#### P106
Lines 594–600 · also informs: A10, A16

```text
If you can't wait for the result, press R. The computer then calculates the
result. Goals, bookings, sendings-off and injuries are listed in the commentary.
There is a break at halftime so you can make substitutions. Likewise with any
injuries. This option is quick, but does not provide the same amount of control
over your team as actually watching the entire game. NB: if you use this option,
all match-related statistics (which rely entirely on the full-length game) are
discarded.
```

#### P107
Lines 602

```text
The scoreboard always shows the home team (if there is one) first.
```

#### P108
Lines 604

```text
Injury time will be allowed at the end of the match, if appropriate.
```

#### P110
Lines 610–614

```text
During the game you get the option to nominate penalty, free kick, goal kick and
corner takers. To help the flow of the game, if you wait 10 seconds without
pressing a key, the computer will accept the currently nominated player.
Note that free kick selection is always within shooting range, although the
player taking the free kick will not always have a pot at goal.
```

**Also informs this area** (quoted under another area): [P54](#p54) (lines 302–306), [P60](#p60) (lines 334–340), [P63](#p63) (lines 360–361), [P64](#p64) (lines 363), [P65](#p65) (lines 365), [P66](#p66) (lines 367–372), [P67](#p67) (lines 374–376), [P68](#p68) (lines 378–380), [P69](#p69) (lines 382), [P70](#p70) (lines 384–385), [P71](#p71) (lines 387–389), [P72](#p72) (lines 391), [P73](#p73) (lines 393–394), [P74](#p74) (lines 396–398), [P75](#p75) (lines 400–401), [P94](#p94) (lines 497–502), [P95](#p95) (lines 504–513), [P98](#p98) (lines 532–536), [P99](#p99) (lines 538–540), [P100](#p100) (lines 542–549), [P111](#p111) (lines 616–620), [P112](#p112) (lines 622–623).

**Not stated by the help file**: any rule of the simulation in numbers (shot, pass and tackle probabilities, the size of home advantage), and how long injury time is.

**Candidate research questions**

- **Q09.1** The match statistics include possession, territory, shots on target and the man of the match. ([P25](#p25))
- **Q09.2** Zonal marking is part of the match engine: under the zonal system each player defends his own zone, which is based on his playing position. ([P26](#p26), [P95](#p95))
- **Q09.3** Goals can be disallowed for offside and own goals can be scored. ([P27](#p27), [P28](#p28))
- **Q09.4** The host nation of a competition wins more of its finals matches, and with a better goal difference, than the same teams do in their other matches. ([P56](#p56))
- **Q09.5** Goals can be replayed after they are scored; the INS key switches the replay facility on or off, and with it off no goal can be saved. ([P29](#p29), [P104](#p104))
- **Q09.6** The commentary key (spacebar) shows the commentary for the match, up to the last 200 comments. ([P105](#p105))
- **Q09.7** Pressing R computes the result: goals, bookings, sendings off and injuries are listed in the commentary, there is a break at half time for substitutions, and also after any injury. ([P106](#p106))
- **Q09.8** After a result computed with R, the match statistics are discarded. ([P106](#p106))
- **Q09.9** The scoreboard shows the home team first, if there is one. ([P107](#p107))
- **Q09.10** Injury time is played at the end of a match when appropriate. ([P108](#p108))
- **Q09.11** During a match the player can nominate penalty, free kick, goal kick and corner takers, and after 10 seconds without a key press the computer accepts the nominated player. ([P110](#p110))
- **Q09.12** Free kick takers are chosen only from within shooting range, and a free kick taker does not always shoot at goal. ([P110](#p110))
- **Q09.13** The man of the match is the player with the highest performance rating, which is updated for every tackle, shot and dribble. ([P111](#p111))

## A10 Discipline, injuries and substitutions

#### P12
Lines 69

```text
- bookings,sendings off,suspensions,substitutions,injuries
```

#### P48
Lines 254–259 · also informs: A02, A12

```text
During your own matches you can alter tactics at any time and make substitutions
from any of your squad, via the 'bench' option. You get 2 substitutions in
competition matches and 5 in friendlies. Substitutions can be made from any of
your squad of 20 (not the pool): you do not have to nominate your substitutes
before a match. You can rearrange your team any way you like before the
kick-off.
```

#### P103
Lines 583–585 · also informs: A08

```text
Hit Esc or enter and you are into the 'bench' screen: from this you can make
substitutions and alter tactics at any point in the game (though you may have to
wait for a suitable break in play to put on a substitute).
```

**Also informs this area** (quoted under another area): [P57](#p57) (lines 318–322), [P61](#p61) (lines 342–350), [P87](#p87) (lines 459–463), [P100](#p100) (lines 542–549), [P106](#p106) (lines 594–600).

**Not stated by the help file**: how many bookings lead to a suspension, the length of suspensions, how long an injury lasts, and what makes a player injured outside heavy tackles.

**Candidate research questions**

- **Q10.1** Matches have bookings, sendings off, suspensions, substitutions and injuries. ([P12](#p12))
- **Q10.2** A manager has 2 substitutions in competition matches and 5 in friendlies. ([P48](#p48))
- **Q10.3** Substitutes are taken from any of the 20 in the squad, and substitutes need not be named before the match. ([P48](#p48))
- **Q10.4** The team can be rearranged in any way before kick-off. ([P48](#p48))
- **Q10.5** During a match, Esc or Enter opens the bench screen, where substitutions and tactics can be changed; a substitute may only come on at a suitable break in play. ([P103](#p103))
- **Q10.6** Injuries, bookings and sendings off lower a player's confidence. ([P61](#p61))

## A11 Competitions and fixtures

#### P04
Lines 24–26

```text
- continental championship, for each continent

- World Cup competition
```

#### P06
Lines 30–32

```text
- fixture list and results history for every country

- results summary for each competition
```

#### P24
Lines 110

```text
tournament top scorers
```

#### P32
Lines 143–152 · also informs: A12

```text
Like international soccer, GOAL works in 4 year cycles: each
cycle comprises:

year 1 - continental friendlies and championship qualifying matches
     2 - continental friendlies and championship finals
     3 - continental friendlies and World Cup qualifying
     4 - inter-continental friendlies (including tours) and World Cup finals

(dependent on the year you start playing, years 3+4 above are swapped with
years 1+2).
```

#### P43
Lines 239–240

```text
FIXTURE LIST - lists all arranged fixtures, filling in results as games are
played. You can select games to watch from here, too.
```

#### P44
Lines 242–243

```text
TOURNAMENT - note that you can always see all results for the current or most
recent occurrence of each of the 5 competitions.
```

#### P47
Lines 249–252

```text
PLAY  - this moves the game on, generally bringing you to your next match.
First you are given the 'latest results' service, with the option to watch any
pre-selected match (see 'fixtures') and then it's the big day and time to have
your wits about you....
```

#### P49
Lines 265–273

```text
The four continental championships are organised as follows:

- Qualifying : 8 groups of 4 teams, teams playing each other over two legs :
 group winners qualify for the finals

- Finals group stage : 2 groups of 4 teams, playing each other once :
 winner and second placed play off in the semi-finals

- Knockout stage : semi-finals,third place play-off,and final
```

#### P50
Lines 275–280

```text
Allocation of 32 World Cup final places is:

Europe - 16
America - 8
Africa - 4
Asia - 4
```

#### P51
Lines 282–286

```text
World cup qualifying is as folows:

- 8 groups of 4 teams in each continent : top two from each European group and
winners of each American group qualify. Winners of African and Asian groups have
play-offs over two legs to decide on the 4 qualifiers from each continent.
```

#### P52
Lines 288–291

```text
The World Cup finals start off with (yes you've guessed it) 8 groups of 4 teams
(oh if real life was only so simple....). Each play the other teams in the group
once. Winners and second placed from each group go forward to the last 16
knockout stage.
```

#### P53
Lines 293–300

```text
Matches in the knockout stages of every competition go into extra time and on to
a penalty shoot-out, if necessary, to produce a result. Penalty shootouts are
best out of five, with sudden death thereafter. African and Asian World Cup
qualifying play-offs are decided by a coin toss, should the aggregate scores
over the two legs tie. Group winners and second placed are decided first on
points (obviously), then on goal difference, then on goals scored, and finally
again by a coin toss (well after all there has always been a lot of luck
involved in football).
```

#### P54
Lines 302–306 · also informs: A09

```text
There are no exemptions from qualifying for the competitions, so the current
title holders and the host nations all have to compete along with everybody else.
However, the selection of host country for each competition is only made after
the qualifying stages from those teams who have been successful to ensure that
the host takes part in the finals.
```

#### P55
Lines 308–309 · also informs: A06

```text
Groups are selected in such a way as to ensure that major teams are spread among
the groups: effectively teams are seeded according to rankings.
```

**Also informs this area** (quoted under another area): [P34](#p34) (lines 161–169), [P36](#p36) (lines 179–185), [P38](#p38) (lines 196–205), [P56](#p56) (lines 311–312).

**Not stated by the help file**: match dates and the number of friendlies in a year, and how groups are drawn beyond the seeding by rankings.

**Candidate research questions**

- **Q11.1** The game runs in 4-year cycles: year 1 continental friendlies and championship qualifying; year 2 continental friendlies and championship finals; year 3 continental friendlies and World Cup qualifying; year 4 inter-continental friendlies (including tours) and World Cup finals. ([P32](#p32))
- **Q11.2** Depending on the year the game is started in, years 3 and 4 come before years 1 and 2. ([P32](#p32))
- **Q11.3** There are 5 competitions: four continental championships and the World Cup. ([P04](#p04), [P44](#p44))
- **Q11.4** Continental qualifying: 8 groups of 4 teams, each team playing every other over two legs (6 matches); group winners qualify for the finals. ([P49](#p49))
- **Q11.5** Continental finals: 2 groups of 4 teams, each team playing the others once; the winner and runner-up of each group meet in the semi-finals; then a third place play-off and the final. ([P49](#p49))
- **Q11.6** The 32 World Cup final places are shared Europe 16, America 8, Africa 4, Asia 4. ([P50](#p50))
- **Q11.7** World Cup qualifying: the top two of each European group, and the winner of each American group, qualify; the winners of the African and Asian groups play off over two legs for the 4 places of each of those continents. ([P51](#p51))
- **Q11.8** World Cup finals: 8 groups of 4 teams playing each other once; the winner and runner-up of each group go to the last 16 knockout stage. ([P52](#p52))
- **Q11.9** A knockout match that is level goes to extra time and then a penalty shoot-out; shoot-outs are best of five, then sudden death. ([P53](#p53))
- **Q11.10** An African or Asian qualifying play-off that is level on aggregate after two legs is decided by a coin toss. ([P53](#p53))
- **Q11.11** Group places are decided by points, then goal difference, then goals scored, then a coin toss. ([P53](#p53))
- **Q11.12** The current title holders and the host nations play qualifying like every other team. ([P54](#p54))
- **Q11.13** The host of a competition is chosen after the qualifying stage, from the teams that qualified, so the host is always in the finals. ([P54](#p54))
- **Q11.14** Groups are drawn so that major teams are spread over the groups, in effect seeded by the rankings: the top-ranked teams never share a group. ([P55](#p55))
- **Q11.15** The fixture list lists every arranged fixture and fills in results as games are played; the tournament screen shows all results of the current or most recent occurrence of each of the 5 competitions. ([P43](#p43), [P44](#p44))
- **Q11.16** PLAY moves the game on to the next match, beginning with the latest-results service, from which a pre-selected match can be watched. ([P47](#p47))
- **Q11.17** Each continent has 32 nations in its championship and World Cup qualifying. ([P34](#p34))
- **Q11.18** Tournament top scorers are recorded. ([P24](#p24))

## A12 Friendlies and tours

#### P05
Lines 28

```text
- friendlies, continental tours
```

#### P23
Lines 108

```text
cancel/rearrange friendlies
```

#### P42
Lines 235–237

```text
Hit enter for details of fixtures - for every team: note that from this option
you can select which matches you wish to watch, or cancel or rearrange your own
friendlies.
```

**Also informs this area** (quoted under another area): [P32](#p32) (lines 143–152), [P48](#p48) (lines 254–259), [P57](#p57) (lines 318–322), [P61](#p61) (lines 342–350).

**Not stated by the help file**: how the game arranges friendlies for each country, how many there are in a year, where tours go, and whether cancelling has a cost.

**Candidate research questions**

- **Q12.1** The game has friendlies and continental tours, and the friendlies of year 4 are inter-continental, including tours. ([P05](#p05), [P32](#p32))
- **Q12.2** From the team-info fixtures option, the manager can cancel or rearrange his own friendlies, and can select which matches to watch. ([P42](#p42))
- **Q12.3** The option to cancel or rearrange is offered only for the manager's own friendlies, and not for competition matches or other teams' fixtures. ([P42](#p42))
- **Q12.4** Squad changes are refused while the team is on tour abroad. ([P57](#p57))
- **Q12.5** Results of friendlies change player confidence, and a friendly allows 5 substitutions. ([P48](#p48), [P61](#p61))

## A13 The other managers

#### P21
Lines 104

```text
team managers
```

**Also informs this area** (quoted under another area): [P22](#p22) (lines 106), [P90](#p90) (lines 477–481), [P96](#p96) (lines 515–522), [P118](#p118) (lines 668–670).

**Not stated by the help file**: how computer-run teams pick their squads or their tactics before a match. The lines the knowledge map cited (104 and 106) are two feature labels ("team managers", "assistant auto-squad selection") that predict nothing observable alone; the area is documented only through the statement that opponents change tactics during a match.

**Candidate research questions**

- **Q13.1** A computer-run opponent changes its team tactics and its positioning during a match: its settings differ between the first minute and later minutes in some matches. ([P90](#p90))
- **Q13.2** When the opponent changes its team, the man-to-man marking assignments are recomputed. ([P96](#p96))
- **Q13.3** Each team has a manager with a name, shown on a team screen, and the ALTER utility can rename managers. ([P21](#p21), [P118](#p118))

## A14 Sacking and the end of the game

#### P33
Lines 154–156

```text
The shareware version limits you to one 4 year cycle, but with the registered
version you can play on forever (if you have nothing else to do). You may be
sacked if your performance is very poor.
```

**Not stated by the help file**: the sacking threshold or the measure of performance it uses.

**Candidate research questions**

- **Q14.1** In a shareware release, play stops after one 4-year cycle; in a registered release play goes on past year 4. Which behaviour the files of this artifact show is observable by playing to the end of year 4. ([P33](#p33))
- **Q14.2** A very poor run of results can end the game with the manager sacked. ([P33](#p33))

## A15 Several human players

#### P02
Lines 20

```text
- play with up to 5 friends
```

#### P16
Lines 84

```text
6 player game
```

**Also informs this area** (quoted under another area): [P117](#p117) (lines 666).

**Not stated by the help file**: the turn order, how each player picks a country, and what the screen does between players.

**Candidate research questions**

- **Q15.1** The game can be started with up to 6 human players (the player and up to 5 friends). ([P02](#p02), [P16](#p16))
- **Q15.2** Each human player can change his own name with F2 on the main screen. ([P117](#p117))

## A16 Data files and saves

#### P14
Lines 75 · also informs: A17

```text
- save and reload game (full registered version only)
```

#### P30
Lines 123–125

```text
save and load goals

save and load match summaries
```

#### P40
Lines 222–227

```text
F1:  displays this help file.
F3:  replays a saved goal.
F4:  loads a saved match summary.
F5:  prints the current screen: use this to print out results, history etc.
F7:  saves the game, and allows you to continue playing.
F10: quits game (and saves it if requested).
```

**Also informs this area** (quoted under another area): [P15](#p15) (lines 77–78), [P104](#p104) (lines 587–588), [P106](#p106) (lines 594–600), [P119](#p119) (lines 672–674).

**Not stated by the help file**: any file name or format of a save, saved goal or match summary, and any structure of GOAL.DAT beyond its role as the file ALTER saves.

**Candidate research questions**

- **Q16.1** F7 saves the game and play continues; F10 quits and saves if the player asks to. ([P40](#p40))
- **Q16.2** Saving and reloading a game works only in a full registered version; in other versions the save option is refused or absent. ([P14](#p14))
- **Q16.3** F3 replays a saved goal and F4 loads a saved match summary; goals and match summaries can be saved and loaded. ([P30](#p30), [P40](#p40))
- **Q16.4** A goal can be saved only while the action replay facility is on (INS toggles it). ([P104](#p104))
- **Q16.5** ALTER writes its changes to the file GOAL.DAT when asked on exit, and a game saved before the change keeps the old names and values. ([P119](#p119))

## A17 Customisation (ALTER.EXE)

#### P15
Lines 77–78 · also informs: A16

```text
- customisation of all player and country names, and strip colours (full
  registered version only)
```

#### P116
Lines 661–664

```text
Hit F2 whenever player information is shown, and you can alter that player's
name. Note that this new name remains only for the duration of the game.
Permanent alterations require the use of the ALTER utility (provided only with
the registered version of GOAL).
```

#### P117
Lines 666 · also informs: A15

```text
Hit F2 on the main screen, and you can alter your own name!
```

#### P118
Lines 668–670 · also informs: A13

```text
ALTER is very simple to use if you are familiar with GOAL and lets you customise
all team,manager and player names,team strips and individual team continental
and world rankings permanantly.
```

#### P119
Lines 672–674 · also informs: A16

```text
Just type in ALTER from DOS, and make any changes you want,then hit F10 to exit
and you will be asked if you want to save the changes to the 'GOAL.DAT' file.
Note that any previously saved game will be unaffected.
```

**Also informs this area** (quoted under another area): [P14](#p14) (lines 75).

**Not stated by the help file**: which player fields ALTER can edit beyond names (skills are not mentioned), and the format ALTER writes.

**Candidate research questions**

- **Q17.1** F2 on a player-information screen changes that player's name for the current game only. ([P116](#p116))
- **Q17.2** Permanent changes to names and strips need the ALTER utility, which comes only with the registered version. ([P15](#p15), [P116](#p116))
- **Q17.3** F2 on the main screen changes the manager's own name. ([P117](#p117))
- **Q17.4** ALTER lets the user change all team names, manager names and player names, team strips, and the continental and world rankings of each team; skills are not among the fields. ([P118](#p118))
- **Q17.5** In ALTER, F10 exits and asks whether to save the changes to GOAL.DAT; a previously saved game is not affected. ([P119](#p119))

## Passages outside the 17 areas

These passages make claims about the game that no knowledge-map area covers: the match screen and keys, records and history screens, newspapers and advice, sound, printing, display compatibility. They are recorded so that G5 can decide whether they need an area of their own. They carry no candidate questions yet.

#### P11
Lines 61–67

```text
- visual presentation of each of your matches, linked with text commentary :
  watch every move in the game, with variable speed control, and display
  options

- optional viewing of any other match you desire

- variable match speed (for the impatient and those into slow motion!)
```

#### P13
Lines 71–73

```text
- match statistics, newspaper reviews and comments

- team history and statistics - how well have you done?
```

#### P17
Lines 90

```text
extended history and statistics
```

#### P31
Lines 139–141

```text
Newspapers will keep you in touch with what is happening and you have access to
a comprehensive database of results, fixture lists and detailed information on
each team and on each player.
```

#### P39
Lines 211–218

```text
GOAL is designed so that all the displays and features are explained where you
find them - so just roam around and you will discover all the things you can do.
You can do just about everything with the following keys:

          enter          accept/proceed/select
          Esc            reject/backtrack/escape
          cursor keys    move selection bar up,down,left or right
          spacebar       next category (eg continent)
```

#### P45
Lines 245

```text
HISTORY - lets you assess every teams' performances.
```

#### P62
Lines 352–354

```text
Pay attention to The SPORTING TIMES, particularly if they offer advice on
replacing players (though they are not always right). Ignore your assistant,
physio and coach, unless for idle amusement!
```

#### P102
Lines 560–581

```text
GOAL centres around the visual presentation of the match. You can alter the
speed at which things happen (left/right arrow keys), and the way the players
are displayed (up/down arrow keys):

  - smiley face characters: home and away teams are distinguished by their team
    strips. The player with the ball, or last in possession, will be highlighted.

  - H/A: indicating home and away team, intended mainly for monochrome displays
    where the strip colours are not apparent.

  - block arrows: indicating direction of play, again intended for monochrome
    displays.

  - B-W: player position (see player positioning to learn the meaning of each
    symbol). Allows you to keep a track of individual players, especially when
    used in conjunction with the commentary.

  - 0-9: player number, 10 in all (the goalkeeper is always shown as a smiley
    face). Allows you to determine precisely which player is which.

The ball is shown as a dot when on or near to the ground, and as a larger dot
when high.
```

#### P113
Lines 635–637

```text
Anyway you can turn the noise off, and you can load the game in 'quiet' mode (if
you have the full registered version) by the command, from DOS:
               goal q
```

#### P114
Lines 643–645

```text
Press F5 at any point to provide a print-out of the screen. To avoid any printer
codes being erroneously transmitted, all possible printer control characters are
ignored.
```

#### P115
Lines 651–655

```text
Goal should work on any truly IBM compatible PC, including those with monochrome
or Hercules display adaptors.

As already mentioned, display options are available during the match so that you
can identify teams other than by strip colour.
```

## Lines read and not recorded

The file's remaining text makes no claim about the game that predicts anything observable, so it is not quoted.

| Lines | Why |
| --- | --- |
| 1–3, 701–702 | title banner |
| 5–14 | introductory marketing; its one countable claim (128 countries) is recorded at line 10 |
| 86, 88 | comparative marketing against version 1 ("much harder", "more realistic scores") with no stated observable |
| 133–137 | the introduction's summary of what the game covers; each item is recorded where it is specified |
| 158–159 | the authors' reason for simplifying the football structure |
| 192–194 | advice on choosing a weak team; its observable content is in lines 196–205 |
| 407–410 | advice on balancing a team |
| 629–633 | jokes about sound effects and the tune |
| 680–698 | contact addresses |
