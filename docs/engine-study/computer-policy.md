# The computer's tactical policy and emergency reshaping

Computer tactics combine default restoration, a coarse strength comparison, repeated random
bit changes and score-gap latches. They are not a search over expected wins. Emergency
reshaping uses ordered role rules, often selecting the first eligible player.

The [13-routine ledger](../../notes/engine-study/T103/T103c-v2.json) and
[calculator](../../notes/engine-study/T103/computer.py) contain four worked source projections
and seven altered-rule controls. No original/port routines, match events or UI keys were
executed for this study. These interpretations remain proposed pending ES-R2; historical
F010/F024/F028 and T68/T77 coverage keeps its actual scope.

## When the computer changes tactics

At setup,A3DE runs lineup selection, personal-tactic reset/derivation, thenBD83 for each
unmanaged side. The [lineup chapter](lineup-policy.md) explains selection. Managed sides skip
that policy. After a goal in normal play (8326 clear),65FE callsC173; C173 again skips managed sides. The code does not
implement a universal “change after the first minute” rule.

For ordinary scores, the policy is:

| Absolute score gap | Team ahead | Team behind |
| --- | --- | --- |
| 0 or1 | BD83 baseline/strength policy | BD83 baseline/strength policy |
| Exactly2 | BF6B:BD83 then three exclusions | BF6B:BD83 then three inclusions |
| Greater than2 | C0DF, once per exclusion stretch | C01A, once per inclusion stretch |

C173 stores the subtraction in a **signed byte**, takes its absolute value, and separately
uses unsigned score-byte comparison to identify the leader. Arbitrary edited scores can
therefore differ from unbounded integer logic:255–0 stores gap−1 and takesBD83. This raw-width
case is not claimed naturally reached. At3–0 with side0 managed, side0 is skipped while
unmanaged side1 takesC01A; management is not inferred from who has the ball.

BD03 compares the **unsigned sums of377E over each XI**, strictly greater. A tie is not
stronger. This differs from country ranking, manager ability, full-match goal expectation
and watched per-element278A skill. The exact call-argument order matters; reading the wrong
sum as “own” reverses the policy.

## Repeated draws, latches and resets

BBFF writes the current country+2D byte and re-derives3431 for nonzero squad identities
without clearing old personal overrides. BD83 first uses it to restore R008 defaults. For
side1 only, if80FC says side1 is the host and its XI is stronger, element1 is included.
If the side's XI is stronger, two `rand(6)` values are included. Both latches8332/8334 for
that side are cleared regardless of strength. Tactics7/8 are not selected by those draws.

The draws are with replacement: two supplied2s include only mask2. They do not choose two
distinct settings. BF6B calls this baseline policy first, then makes three `rand(6)` changes,
excluding when ahead and including when behind. With baseline128 and stronger draws1,1,
BD83 gives129; ahead exclusions1,1,1 return128. Skipping the reset or selecting three distinct
bits changes both the byte and random consumption.

C01A runs only with inclusion latch8332 clear. It includes `rand(5)` five times, includes
fixed element6, writes throughBBFF and sets the latch. Five supplied1s produce **33**,
not63. A repeated call with that latch set changes nothing and consumes no new draws there.
BD83 later clears it, permitting another stretch. C0DF similarly excludes five `rand(5)`
values and fixed6 under exclusion latch8334, without C01A's forward-conversion tail.

C01A checks the **ninth squad player's played role** against{12,13}. If it is outside that
set, it callsBEC7 and230C. A striker elsewhere does not satisfy that particular slot test.
BEC7 changes only the first available played9,10,11: height below72 inches gives13, at least72
gives12, then returns. Height is generated from identity/natural-role tables; it is not a
freely stored height byte. This is a role-policy use of height; direct aerial contests use
heading skill rather than a separate height term.

BC5D is a broader reset: clear all20 personal-tactic bytes, restore R008 throughBBFF, sort the
squad, then install XI played roles from R011. The order is significant: derivation precedes
that final role installation. F1F6 applies it to unmanaged sides; other callers can apply it
to both. Managed-choice persistence is therefore route dependent, as [lifecycle](lifecycle.md)
explains. A fresh derive, nonclearing derive and full reset are distinct transactions.

## Emergency role repair

C48D handles loss/removal without a normal available bench substitution. It dispatches on
the removed player's **played role**, then calls230C to rebind/resort/rebuild posts and caches:

| Removed role | Routine | Change among available XI |
| --- | --- | --- |
| 0 keeper | C24D | First available slot2..11 becomes played0; no comparison of keeping skill |
| 1 sweeper or2 centre back | C2A8 | Count roles; choose first surplus donor by table priority, then first eligible identity of that role |
| 3 or4 fullback | C406 | Every available played3/4 becomes centre back2 |
| 12 or13 forward | BEC7 | First available9..11 becomes13 below72 inches, otherwise12 |
| Other role | No role-specific helper | Still refresh230C |

C2A8's priority roles are `[2,5,6,7,8]` with thresholds `[1,0,0,0,0]`, using strict count>
threshold. Requested1 starts at index1; requested2 starts at index2 and therefore skips
role2 as donor. On available roles `[0,2,2,3,4,5,6,7,8,9,13]`, request1 takes the first
centre back (slot2) because count2>1. Request2 instead takes role5 at slot6 because count1>0.
No surplus leaves roles unchanged; no available outfielder gives C24D no replacement.
These are conditional inner-helper projections, not a claim that every such roster is
naturally reached after removal.

For a fullback loss,C406 converts **all** matching available fullbacks, rather than repairing
one wing or selecting the strongest donor. Normal substitution uses C88D/C5DC and the budget/
bench-selection protocol in [substitutions](substitutions.md); those are not interchangeable
with the emergency role policy.

## Worked checks and remaining limits

Four examples cover managed skips/score gaps, duplicate draws and latch suppression, centre-back
donor priority and the inclusive72-inch threshold. Seven alternatives challenge managed updates,
distinct-bit sampling, omitted reset/latch, strongest emergency keeper, strict>72 height and
single-fullback conversion. Source checks cover all15 entries deferred from T104: two pool
sort entries are in T103b and the other13 policy entries here.

The original instructions answer these local branch questions without a new match campaign.
They do not establish normal reach, frequency or whether the policy helps. F024's ten historical
second halves reached three C173 calls in its small-gap branch and did not exercise its three
other policy branches; later T68/T77 receipts must be consulted for their own exact reach.
Neither source projections nor a passed hash/coverage check upgrades that historical sample.

T105 can choose cheap falsifiable probes for relevant unresolved boundaries. Net tactical
benefit, natural emergency incidence and a readable policy rewrite remain separate questions.
A faithful rewrite must first preserve branch ordering, duplicate draws, latches, strict tests,
identity sorting and explicit refresh; a more capable computer manager would be a design change.

With8326 set,65FE jumps past both the normal goal update and C173 at6649→66DF.
Consequently that mode does not consume the computer-policy draws described above.
