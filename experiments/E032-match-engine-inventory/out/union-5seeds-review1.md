# E032 coverage of a seed family: 0x1234, 0x2345, 0x4c1d, 0xc3c3, 0xe719

Code bytes reached between kick-off and full time, per part, by each seed and by their union, against the size of the part's reached routines.

| part | size (bytes) | each seed | union |
| --- | --- | --- | --- |
| ball and player motion, offside line | 2,449 | 97% / 97% / 98% / 96% / 97% | 98% |
| ball, passing, shooting | 4,491 | 96% / 93% / 95% / 93% / 93% | 98% |
| commentary and ratings | 1,151 | 99% / 99% / 99% / 99% / 99% | 99% |
| decisions and contests | 3,405 | 89% / 88% / 87% / 85% / 89% | 91% |
| duels and play at the ball | 2,015 | 85% / 70% / 83% / 77% / 81% | 88% |
| form, fouls, cards, substitutions | 1,543 | 61% / 63% / 80% / 64% / 61% | 84% |
| geometry and queries | 2,325 | 97% / 97% / 97% / 97% / 93% | 97% |
| goals, restarts, set pieces | 5,515 | 69% / 66% / 77% / 66% / 68% | 82% |
| marking and leaders | 976 | 72% / 72% / 97% / 72% / 72% | 97% |
| match frame | 2,166 | 70% / 76% / 77% / 77% / 76% | 77% |
| player attributes (1771) | 3,044 | 94% / 94% / 94% / 94% / 94% | 95% |
| positioning and marking movement | 3,051 | 94% / 90% / 93% / 90% / 94% | 94% |
| set-up and computer manager | 3,651 | 72% / 73% / 81% / 76% / 67% | 86% |
| LIB: runtime (RNG, sets, longs, screen, delay) | 3,385 | 84% / 84% / 84% / 84% / 84% | 84% |
| UI: boards, scores | 720 | 82% / 82% / 82% / 82% / 82% | 82% |
| UI: delay, whistle | 56 | 71% / 71% / 71% / 71% / 71% | 71% |
| UI: draws or waits (skip.py checks) | 8,635 | 69% / 69% / 69% / 70% / 69% | 70% |
| UI: menus, captain screen | 2,529 | 57% / 57% / 57% / 57% / 57% | 58% |
| sound | 123 | 83% / 83% / 83% / 83% / 83% | 83% |

Frontier: 9 routines called from reached engine routines that no seed reached (1,120 static instructions, their own code only).

| routine | name | instructions | called from |
| --- | --- | --- | --- |
| 0791:6ECF | dead_ball_penalty | 23 | 0791:8206 |
| 0791:73BA |  | 112 | 0791:8AE9 |
| 0791:7B77 | send_off | 142 | 0791:7EEF |
| 0791:7FCF | timed_notice | 57 | 0791:8062 |
| 0791:B3B7 | update_top_scorers | 221 | 0791:6443 |
| 0791:C01A | computer_include_tactics | 76 | 0791:C173 |
| 0791:C0DF | computer_exclude_tactics | 57 | 0791:C173 |
| 0791:C48D | remove_from_pitch | 55 | 0791:C88D |
| 0791:D733 | quick_match_engine | 377 | 0791:97D0 |
