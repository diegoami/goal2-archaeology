# E032 cost recount (PR 243 review, R3)

Assumptions: pilot time 40 min; workers 2; family 40 matches per check; 6 checks per step; 3 falsifier matches per step; 5 coverage runs per step; sd of goals 1.37; 11 effects: skill +4, energy, form, tactic element 1, tactic element 2, tactic element 3, tactic element 4, tactic element 5, tactic element 6, tactic element 7, tactic element 8.

## Seconds per whole match (CPU, measured)

- oracle, plain: mean 32.8 s, range 19.5-50.8 s, n = 10
- oracle, delay count at kick-off: mean 11.1 s, range 8.3-16.8 s, n = 10
- oracle with the pilot's port hooked: mean 17.8 s, range 16.3-20.1 s, n = 10
- coverage run (block hook): mean 37.7 s, n = 5

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

The pilot: 555 static instructions (0791:8889, 0791:86D0, 0791:2BE5, 0791:2974, 0791:045D, 0791:2CC5, 0791:2DCA, 23E4:08DF, 214B:0688, 214B:06B1, 214B:06FA) in 40 min = 832 an hour.

Fixed hours: P0 tooling 3 h, P6 adapter and the port on its own 4 h, P7 start states (preparing them) 1 h, the distribution sheet (work, not CPU) 2 h = 10 h.

| rate | P1 | P2 | P3 | P4 | P5 | P7 | porting | with fixed hours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| optimistic (the pilot's rate) | 2.9 | 3.5 | 4.0 | 3.5 | 4.2 | 1.7 | 19.8 | 29.8 |
| central (half the pilot's rate) | 5.9 | 7.1 | 7.9 | 6.9 | 8.3 | 3.5 | 39.5 | 49.5 |
| pessimistic (a quarter of it) | 11.8 | 14.1 | 15.8 | 13.8 | 16.6 | 6.9 | 79.1 | 89.1 |

## CPU per step

- one family check: 40 x 17.8 s = 11.8 CPU min, 5.9 min elapsed on 2 workers
- one step: 6 checks + 3 falsifiers + 5 coverage runs = 1.25 CPU h, 0.63 h elapsed
- one review: 1 check + 3 falsifiers = 12.7 CPU min, 6.4 min elapsed
- seven steps with checks (P0-P5, P7; P6's check is the same family): 8.8 CPU h

## Matches per arm (goals, two arms, alpha 0.05, power 0.8)

- 0.25 goals: 472; 0.5 goals: 118
- route B, one effect at 0.25 goals, the oracle's two arms: 944 matches = 2.91 CPU h (1.46 h elapsed); the model's two arms come on top, at the model's speed

## The distribution sheets

- Sheet A (fidelity; required): the oracle's 500 matches on E011-r0001's state are run once, at P6, and reused at P7, which adds 2 x 100 on its new start states: 700 oracle matches; the port runs 500 at P6 and 700 at P7 (the port changes between them). At 11.1 s an oracle match and 17.8 s a port match (ASSUMED: the port's speed on its own is unmeasured until P6; the hooked pilot's speed stands in): 8.1 CPU h, 4.0 h elapsed
- Sheet B (effects for the bot; optional, goal2's call) at 0.25 goals: 11 effect arms and ONE baseline arm shared by all effects = 12 arms x 472 = 5,664 matches; at the oracle's 11.1 s: 17.5 CPU h, 8.7 h elapsed. Run once, after P7, on whichever engine is faster (an exact port gives the oracle's results)
- Sheet B (effects for the bot; optional, goal2's call) at 0.5 goals: 11 effect arms and ONE baseline arm shared by all effects = 12 arms x 118 = 1,416 matches; at the oracle's 11.1 s: 4.4 CPU h, 2.2 h elapsed. Run once, after P7, on whichever engine is faster (an exact port gives the oracle's results)

## Option D's first stage

- P0 tooling + the image adapter: 7 h of implementer time, then 11.1 s a match (range 8.3-16.8 s)

## Totals

- implementer hours, optimistic (the pilot's rate): 29.8
- implementer hours, central (half the pilot's rate): 49.5
- implementer hours, pessimistic (a quarter of it): 89.1
