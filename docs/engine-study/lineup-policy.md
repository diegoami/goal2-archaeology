# How the computer chooses its eleven

The computer performs an ordered repair of its current XI using its bench. It does not search
all possible formations or maximise a whole-team score. This explains why a locally stronger
player can remain on the bench while a weaker natural-role replacement enters.

The [nine-routine ledger](../../notes/engine-study/T103/T103b-v1.json) and
[calculator](../../notes/engine-study/T103/lineups.py) retain four source-conditioned cases and
six altered-rule controls. These are proposed source interpretations, not newly executed
lineup routines or matches. F024/F028 and T70/T75 retain their actual historical coverage.

## The greedy selection sequence

`A3DE` installs fixture countries/host/decider state and reseeds. For each unmanaged side it
calls **B11F→34E7→BD83**: choose lineup, freshly derive personal tactics, then choose current
team tactics. Managed sides are skipped. This runs at setup, not after an arbitrary first minute.
B11F clears the14-byte natural-role bench map99A2, callsAC67 on slots12..20, scans starters
throughAFA3, and sorts by played role afterward.

AC67 ignores unavailable players and retains the **strictly strongest** available bench player
per natural role+7, using377E. Equal strength keeps the earlier slot. For available natural2
players at12/15/18 with supplied strengths90/90/100, the map evolves12→12→18. With only the
first two, it keeps12. The [in-match replacement map](substitutions.md), C7EB, simply keeps
the last available slot per role; reusing that implementation here would choose15 on a tie.

377E combines ability, signed energy and form, clamps0..256, applies availability and placement
penalties. It is not the watched skill278A. See [strength formulas](strength-formulas.md) for
its form32 discontinuity and [player-derived](player-derived.md) for foot/keeper placement.
The examples here supply strength values explicitly rather than executing either helper.

AFA3 visits starters1..11. It asksAAE8 for a candidate using the outgoing **played** role's
ordered natural-role preferences and the flank/foot filter. The **last passing preference**
wins. For played5, preferences are `[1,3,4,7,8,6,5]`: an eligible natural5 map entry wins over
an eligible natural1 entry, regardless of which has the greater strength across those roles.
The map comparison maximises only *within* a natural role; it does not compare every bench
player against every starter.

With a candidate, the starter gives way if:

1. The candidate's strength is strictly greater; or
2. The starter is away from its natural role and the candidate's natural role equals the
   starter's played role, even if the candidate is weaker.

Otherwise an unavailable or placement-penalised starter, or a natural nonkeeper in slot1,
needs replacement. The existing candidate is used; without one,A9B8 selects the available
bench player with the strongest **compatibility-table grade**, subject to its own foot rule.
That grade is not ability, keeping skill or a whole-XI optimum. With no available candidate,
the routine cannot manufacture a replacement. A valid, available, correctly placed starter
can stay despite a stronger bench player outside its candidate-role path.

## Role transfer and candidate depletion

AD8F clears the chosen bench player's natural-role map entry and swaps squad identities.
The incoming player inherits the outgoing played role **except** when both roles lie in one
of `{5,6}`, `{7,10}`, `{8,11}`, `{12,13}`; then the incoming player uses its own natural role.
Thus outgoing played7 with incoming natural10 becomes10, while outgoing2/incoming5 becomes2.
The outgoing player, now on the bench, returns to its own natural role. These are prematch
selection rules; [managed swaps](substitutions.md) have a different role protocol.

Only **AC67 on the outgoing player's new bench slot** follows this swap. It does not rescan
all remaining bench players. Suppose map2 names slot18/strength100 and another natural2 at
slot12/90 remains. If18 enters and outgoing natural5/70 moves to18, map2 is cleared and
map5 can receive18. Slot12 does not automatically reappear as the second-best natural2.
Later AAE8 requests can therefore see an empty role2 entry despite a remaining available
natural2 player. A fallback may still choose that player under its own conditions.

This is a source-derived limit of the greedy map, not an established new port bug or proof
of a worse match result. A rewrite that globally rebuilds the map after every swap would
change original decisions. Natural frequency and practical impact need their own bounded
question before a correction is considered.

## Sorting and visible formation

517A sorts squad words with a middle pivot, ascending played role. It swaps each identity's
parallel saved role byte along with the identity. Equal keys can exchange: two equal records
A,B become B,A in the small partition example. A stable sort is not an exact substitute.
This matters because subsequent algorithms choose first or last eligible players.

52CC sorts the XI1..11 and bench12..20 **separately**. For a managed country only, unavailable
players temporarily receive role14 to sort last; their saved roles are restored to the correct
identities afterward. Sorting alone does not promote bench players, select a formation or
permanently change natural/played roles. The saved-byte transaction is part of its meaning.

5532 instead sorts the current manager's80 pool words using53E8. Pool indices are raw indices,
not the squad's one-based1..20 convention. It temporarily gives an empty identity role14,
carries saved bytes through the partition and restores them. It does not use exactly the
squad's managed-availability sentinel rule. Dummy-record/duplicate-identity edited states
need separate qualification; ordinary-roster reasoning is not a proof for arbitrary aliases.

The visible defence-midfield-attack label is a count of available played roles, described in
[tactics](tactics.md). It does not capture the role sequence, asymmetrical feet, duplicate-post
separation, energy, marking assignments or these selection priorities. Two teams with the same
label can consequently behave differently.

## Worked checks and limits

The retained cases cover strict per-role ties, a weaker natural-role correction, map depletion
and saved-role sorting. Six alternatives change tie handling, global-best selection, weaker
replacement refusal, universal role inheritance, full map rebuilding and stable sorting.
All are source arithmetic/ordering projections; source hashes and coverage checks establish
which code was interpreted, not that every context is naturally reached.

No new lineup or match execution was needed to read these branches. Existing F024's reached
cases and T70's full machine-state comparison retain their original sample limits. T105 can
select a cheap original-backed probe for a materially uncertain boundary after ES-R2, while
broader claims about winning formations require a different design and budget.
