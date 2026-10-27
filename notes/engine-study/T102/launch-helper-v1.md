# Bounded launch-arithmetic assistance

- Agent: `/root/launch_arithmetic`.
- Requested model/effort: `gpt-6.1-sol` / `xhigh`, fresh context. Effective settings were not exposed by the agent runtime; these are requested settings, not independent attestation.
- Reason: main-session reading found the decompiler obscured 34C1's long-division operands, signed byte differences and degenerate displacement branches.
- Scope: read-only original/named/listing-to-port arithmetic check of 0791:34C1, with source-derived examples. No file/Git/GitHub writes, engine calls, Match creation, matches, probes or subagents were authorised.
- Role: implementation assistance; **not independent milestone review**. Main session owns integration and verification.
- Primary-source snapshot: `a42c2cbe91300c8ee261b82fa993e665ed3f3325`.
- Main session independently re-read 37CE–37F5 and 23E4:0294 after receiving the response: divisor is the velocity absolute-value sum, not a universal two.

## Agent response

Static derivation by `/root/launch_arithmetic`; effective model/effort was not exposed to this agent. Original listings were read before the port. No engine routines or matches were executed.

The final timer is **divided by `abs(vx)+abs(vy)`**, then floored at 2. It is not universally halved.

```text
U8(x) = x modulo 256; U16(x) = x modulo 65536
S8(x) = signed interpretation of U8(x)
step(d) = +1 if d > 0, otherwise -1   # zero selects -1

dx = S8(target_x - ball_x)
dy = S8(target_y - ball_y)
A = abs(dx); B = abs(dy)
vx = vy = 0

if A > B:
    vx = step(dx)
    T = A
    if B >= A // 2:
        vy = step(dy)
        T = U16(T + B)
else:                                 # includes A == B == 0
    vy = step(dy)
    T = B
    if A > 0 and A >= B // 2:
        vx = step(dx)
        T = U16(T + A)
        if B >= A // 2:
            vy = U16(vy << 1)         # interpreted as signed word thereafter

if event == 6:
    if T > 20: event = 7
    elif keeper_slot(kicker) and own_goal_strip(kicker, BALL_POSITION):
        event = 8

DS8327 = U8(event)
element = DS8[U16(0779h + event)]

if U8(event) in {1,2}:
    V = effective_skill(kicker, element)       # unsigned word
    T = max(U16(T + 5), U16(V + pitch_extra_byte) // 3)
elif U8(event) in {3,4}:
    V = effective_skill(kicker, element)
    T = max(U16(T + 5), V // 3)
else:
    apply conditional miscue logic below

DS8323 = 0
D = signed_word(U16(abs(signed_word(vx)) + abs(signed_word(vy))))
T = U16(max_signed_long(2, zero_extended(T) / sign_extended(D)))
projected_x = U8(ball_x + signed_word(vx) * T)
projected_y = U8(ball_y + signed_word(vy) * T)
```

The last division truncates toward zero; with the shipped sign table, `D` is positive, so this is floor division. In the y-dominant diagonal branch the final doubling condition is redundant mathematically: entering it already establishes `B >= A > 0`. Thus that branch produces `(±1,±2)`, giving divisor 3.

Key instruction evidence:

- **Byte differences/sign extension:** `34E4–34ED` subtract bytes; `34FA–3512` sign-extend before taking absolute values and selecting dominance. Listing bytes `98/99` mean 16-bit CBW/CWD here.
- **X-dominant threshold:** `3542–3556` computes `A div 2` before comparing `B`; `3558–356C` selects `DS7920[dy>0]`. Consequently `(dx,dy)=(1,0)` becomes `(vx,vy)=(1,-1)`.
- **Y-dominant/tie branch:** `3580–35A1` initializes `vy=DS7920[dy>0]`, `T=B`; `35AE–35D0` requires `A>0` and `A>=B div 2`; `3601–361C` tests `B>=A div 2` and doubles `vy`. Zero displacement therefore initializes `(0,-1), T=0`.
- **Event rewrite:** `361F–3655`: unsigned `T>20` changes 6 to 7; otherwise keeper and own-strip predicates can change it to 8. `3644` passes the **ball’s current point**, not the target.
- **Event sets:** CS:`3481` contains `06`, selecting low-byte events 1/2; CS:`34A1` contains `18`, selecting 3/4. `23E4:08DF–08FA` implements byte-indexed set membership. Event comparisons/rewrite otherwise use the word argument.
- **Skill terms:** `3670–36AA` includes the explicit extra pitch byte at `3692`, wrapping word addition at `3698`, unsigned `/3` at `369F`. `36C0–36ED` divides `V` directly. DS:`0779[1..4]` is `11,4,12,12`; `[6,7,8]` is `6,6,1`.
- **Final divisor:** `37CE–37E7` builds the absolute-velocity sum in BX:CX; `37E9–37EE` supplies zero-extended timer in DX:AX to signed-long division `23E4:0294`. `37F5` applies long maximum with 2.
- **Projection:** `37FD–382B` copies the ball point, multiplies signed velocity by zero-extended final timer, and adds only each product’s low byte.

Miscue order is exact:

1. Only outside the two event sets, with full-word `event != 8`, unsigned `T>1`, and `DS830B != DS830C`, call `287C` (`36F3–3727`).
2. Its one draw uses `n=V//32+1`; drawing 1 returns failure (`288E–28A4`).
3. Failure clears `DS830C` **before** checking keeper status (`372C–3742`). Keepers then stop this branch.
4. A nonkeeper always draws coin `06FA` at `3745`, even when `DS8323 != 0`. Coin true **or** nonzero flag selects `T -= rand(T//2)` (`3755–3765`).
5. Otherwise, when `vx==0`, another coin selects `vx=±1`, then `vy += step(vy)` (`376B–3797`). When `vx!=0`, `abs(vy)==1` sets `vy=0` without another draw; otherwise another coin replaces `vy` with ±1 (`379D–37BF`).

Hand-calculated examples, all starting at `(0,0)`, kicker slot 2, `DS830C=2`, `DS8323=0`. Supplied `V` is the effective return value, not an inferred player record.

| Target; event | Supplied skill | Base `(vx,vy); T` | Adjusted T | Final T; projection |
|---|---|---|---|---|
| `(8,3)`; 1 | V=90, extra=12 | `(1,0); 8` | max(13,102//3)=34 | 34; `(34,0)` |
| `(4,8)`; 3 | V=90, extra=12 | `(1,2); 12` | max(17,90//3)=30 | 10; `(10,20)` |
| `(7,14)`; 6→7 | Skill unread | `(1,2); 21` | 21 | 7; `(7,14)` |
| `(1,0)`; 6 | Skill unread | `(1,-1); 1` | 1 | 2; `(2,-2)` |
| `(0,0)`; 6 | Skill unread | `(0,-1); 0` | 0 | 2; `(0,-2)` |

No favorable miscue draws are assumed: events 1/3 bypass it; row 3 bypasses through equal slot selectors; rows 4/5 bypass through `T<=1`.

**Falsifying control:** universally halving row 3 gives `T=10`, projection `(10,20)`, contradicting the original divisor 3 and result `(7,14)`.

The inspected port reproduces these branches and widths. These are static arithmetic cases; natural reachability, frequency, complete post-launch behavior, and original behavioral corroboration remain unproven.
