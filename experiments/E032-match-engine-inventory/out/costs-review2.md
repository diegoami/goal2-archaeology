# E032 cost recount (PR 243 review rounds 1 and 2)

## Assumptions (not measured by any committed log)

- PILOT_MINUTES = 40: my own time for the pilot (reading, writing, first run), self-reported in notes.md, not logged
- RATE_FACTORS = {"optimistic (the pilot's rate)": 1.0, "central (half the pilot's rate)": 0.5, 'pessimistic (a quarter of it)': 0.25}: the share of the pilot's rate the rest of the engine allows
- FIXED_HOURS = {'P0 tooling': 3, 'P6 adapter and the port on its own': 4, 'P7 start states (preparing them)': 1, 'the distribution sheet (work, not CPU)': 2}: estimates of work that is not porting
- FAMILY = 40: matches per step check: 20 seeds plain + the same 20 with declared edits (a plan choice)
- CHECKS_PER_STEP = 6: family checks a step runs while it ports and debugs
- COVERAGE_RUNS = 5: coverage runs per step (as E032's union)
- STEPS_WITH_CHECKS = 8: P0-P7 each run family checks
- PORT_SPEED = the hooked pilot's mean: a port's match on its own is unmeasured until P6; the hooked pilot's speed stands in
- FALSIFIER_SET = the mean measured set: a step's three falsifiers cost what the pilot's three cost, the hung one included
- SHEET_A = (500, 2, 100): oracle matches on E011-r0001's state; new start states at P7; matches on each
- SD_GOALS = 1.37: C-MATCH-27's watched goals sd (measured there, F005), taken as given

## Seconds, measured (CPU)

- oracle, plain: mean 32.8 s, range 19.5-50.8 s, n = 10
- oracle, delay count at kick-off: mean 11.1 s, range 8.3-16.8 s, n = 10
- hooked pilot port (exact): mean 18.0 s, range 16.3-20.1 s, n = 18
- falsifier set 20261015: coin-swapped 16.3 s (completed), bound-36 314.2 s (did not complete), no-picture 16.9 s (completed); total 347.4 s
- falsifier set review1: coin-swapped 18.2 s (completed), bound-36 315.4 s (did not complete), no-picture 17.0 s (completed); total 350.6 s
- falsifier set, mean of the 2 sets: 349.0 s (budgeting them at the hooked mean would give 54.1 s)
- coverage run: mean 37.7 s, n = 5
- T48 proved whole matches (route A): 14 reached minute 91 in 32-80 min (median 49); 8 more stopped at a time limit

## Instructions by step (static, counted)

- P1: 2,449
- P2: 2,941
- P3: 3,293
- P4: 2,878
- P5: 3,457
- P7: 1,437
- P5 includes the set-up 0791:A4A1, 0791:1073, 0791:A375, 0791:A3B6, 0791:A3DE, 0791:A841; P7 is the frontier 0791:6ECF, 0791:73BA, 0791:7B77, 0791:7FCF, 0791:B3B7, 0791:C01A, 0791:C0DF, 0791:C48D and the shoot-out 0791:A10A, 0791:0C0B, 0791:9B93, 0791:9ED3, 0791:A006
- total: 16,455

## Implementer hours

The pilot: 555 static instructions (0791:8889, 0791:86D0, 0791:2BE5, 0791:2974, 0791:045D, 0791:2CC5, 0791:2DCA, 23E4:08DF, 214B:0688, 214B:06B1, 214B:06FA) in 40 min (ASSUMED) = 832 an hour.

Fixed hours (ASSUMED): P0 tooling 3 h, P6 adapter and the port on its own 4 h, P7 start states (preparing them) 1 h, the distribution sheet (work, not CPU) 2 h = 10 h.

| rate | P1 | P2 | P3 | P4 | P5 | P7 | porting | with fixed hours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| optimistic (the pilot's rate) | 2.9 | 3.5 | 4.0 | 3.5 | 4.2 | 1.7 | 19.8 | 29.8 |
| central (half the pilot's rate) | 5.9 | 7.1 | 7.9 | 6.9 | 8.3 | 3.5 | 39.5 | 49.5 |
| pessimistic (a quarter of it) | 11.8 | 14.1 | 15.8 | 13.8 | 16.6 | 6.9 | 79.1 | 89.1 |

## CPU per step and per review

- one family check: 40 x 18.0 s = 12.0 CPU min, 6.0 min elapsed on 2 workers
- one step: 6 checks + one falsifier set (349.0 s, measured) + 5 coverage runs = 1.35 CPU h, 0.68 h elapsed
- one review: one check + one falsifier set = 17.8 CPU min, 8.9 min elapsed
- all 8 steps: 10.8 CPU h, 5.4 h elapsed

## Matches per arm (goals, two arms, alpha 0.05, power 0.8)

- 0.25 goals: 472; 0.5 goals: 118
- route B, one effect at 0.25 goals, the oracle's two arms: 944 matches = 2.9 CPU h (1.5 h elapsed)

## The distribution sheets

- Sheet A: 700 oracle matches (500 at P6, reused at P7, plus 2 x 100); 1200 port matches (500 at P6, 700 at P7); 8.2 CPU h, 4.1 h elapsed (the port at the hooked speed, ASSUMED)
- Sheet B at 0.25 goals: 11 effect arms + one shared baseline = 12 arms x 472 = 5,664 matches at the oracle's 11.1 s: 17.5 CPU h, 8.7 h elapsed
- Sheet B at 0.5 goals: 11 effect arms + one shared baseline = 12 arms x 118 = 1,416 matches at the oracle's 11.1 s: 4.4 CPU h, 2.2 h elapsed

## Option D's first stage

- P0 tooling + the image adapter: 7 h, then 8.3-16.8 CPU s a match

