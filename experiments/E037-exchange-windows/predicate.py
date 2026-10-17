"""When the squad and the reserve pool may exchange records (F031, T81): the listing's rule as a function.

Every name below is a field of the original, read in GOAL.EXE's listing (static/goal-exe/code/):

- in_match_menu_used : DS:0C1F. 0 outside a match and in a match's first (pre-match) team screen; set to 1 when
                       the in-match menu 0791:ED8A returns (F08A), cleared by match_setup (A5BA) and at the end of
                       run_match (F398). The SELECT TEAM screen 0791:E44F shows the pool, and sends Enter to the
                       exchange 0791:DEA6 and Ins to the assistant 0791:DC7E, only while it is 0.
- sacked             : [A923]+0x47+m. The main menu opens the SELECT TEAM screen only while it is 0 (000E:7439);
                       1771:55FC also returns 0 for a sacked manager.
- finals_flag        : [A923]+0x13+m. Set to 1 by route_fixture (000E:6E75) for each managed side of a fixture
                       whose kind is in CS:6C87 = {3, 7} (the continental and the World Cup finals groups), before
                       that fixture is played; cleared (6 bytes at +0x14) only by the stage 2 / stage 5 builder
                       1771:6730 (6743-6750). 0791:DBFA refuses "cannot alter squad during finals" when it is set.
- own_continent      : the managed country's continent, country +0x2C (1 Europe, 2 America, 3 Africa, 4 Asia).
- next_fixture       : DS:9B43 as 1771:55FC leaves it: the first of the trailing run of the country's list entries
                       (DS:A92F + 0x48*country, 36 words) that are unplayed (record +0 >= 0xFE) and not below the
                       next number to play ([A923]+0x26); None when there is none (9B43 = 0).
- last_played        : the newest entry of the same list whose record +0 is < 0xFE (0791:DB38's backward walk);
                       None when the walk reaches the list's start.

A fixture is given as (kind, side_b_continent): the record's byte +2 and the continent of the country in its word
+6. 1771:5A38(record, country) is true iff kind == 1 and continent(side B) != continent(country); when the country
is itself side B it compares the country with itself and is false, so it is true exactly for a friendly the
country plays as side A against a side B of another continent.
"""

ALLOWED = 'allowed'
REFUSED_FINALS = 'refused: cannot alter squad during finals'
REFUSED_TOUR = 'refused: cannot alter squad whilst on tour'
REFUSED_IN_MATCH = 'refused: no pool view in a match after the pre-match screen'
REFUSED_SACKED = 'refused: no SELECT TEAM screen for a sacked manager'

FINALS_KINDS = frozenset({3, 7})          # CS:6C87, bytes 88 00 .. (000E:6E22 tests the kind against it)
CLEAR_STAGES = frozenset({2, 5})          # stages built by 1771:6730, which clears [A923]+0x14..+0x19


def away_cross_friendly(fixture, own_continent):
    """1771:5A38 for the managed country: kind 1 and side B of another continent."""
    if fixture is None:
        return False
    kind, side_b_continent = fixture
    return kind == 1 and side_b_continent != own_continent


def on_tour(own_continent, next_fixture, last_played):
    """0791:DB38: 0791:DAF8 (55FC finds a next fixture and 5A38 holds for it), then 5A38 for the last played one."""
    if next_fixture is None or not away_cross_friendly(next_fixture, own_continent):
        return False
    if last_played is None:
        return False
    return away_cross_friendly(last_played, own_continent)


def exchange(in_match_menu_used, sacked, finals_flag, own_continent, next_fixture, last_played, involves_pool=True):
    """The verdict on an Enter swap in the SELECT TEAM screen (0791:E44F -> DEA6) or the assistant (DC7E).

    involves_pool: the swap is made with the pool list up (E44F's side 2), so it moves a record between the squad
    and the pool (or within the pool). DEA6 calls DBFA only then (DEB9: `cmp [di-5], 2`); a swap of two squad
    players with the squad list up is not gated by DBFA. The assistant DC7E always calls DBFA (DCB0).
    """
    if sacked:
        return REFUSED_SACKED
    if in_match_menu_used:
        return REFUSED_IN_MATCH
    if not involves_pool:
        return ALLOWED
    if finals_flag:
        return REFUSED_FINALS
    if on_tour(own_continent, next_fixture, last_played):
        return REFUSED_TOUR
    return ALLOWED


def finals_flag_after_route(flag, kind):
    """000E:6E15-6E75: routing a managed fixture of kind 3 or 7 sets the flag; nothing else in route_fixture clears it."""
    return 1 if kind in FINALS_KINDS else flag


def finals_flag_after_build(flag, stage):
    """1771:76B1 -> 6730 for stages 2 and 5 clears the flag; the other builders leave it."""
    return 0 if stage in CLEAR_STAGES else flag


UNKNOWN = 'unknown'


def _fixtures(kind, side_b_continent):
    """'-' is no fixture; '?' is a record the listing does not settle: none, or an away cross-continent friendly
    (continent 0 differs from every real continent)."""
    if kind == '-':
        return (None,)
    if kind == '?':
        return (None, (1, 0))
    return ((int(kind), int(side_b_continent)),)


def _values(field):
    """'?' stands for a value the listing does not settle: both 0 and 1 are tried."""
    return (0, 1) if field == '?' else (int(field),)


def evaluate_row(row):
    """The verdict for one row of cases.tsv; UNKNOWN when an unsettled input ('?') changes the verdict."""
    verdicts = set()
    for in_match in _values(row['in_match_menu_used']):
        for sacked in _values(row['sacked']):
            for flag in _values(row['finals_flag']):
                for nxt in _fixtures(row['next_kind'], row['next_b_continent']):
                    for last in _fixtures(row['last_kind'], row['last_b_continent']):
                        verdicts.add(exchange(in_match, sacked, flag, int(row['own_continent']), nxt, last,
                                              involves_pool=row['involves_pool'] == '1'))
    return verdicts.pop() if len(verdicts) == 1 else UNKNOWN
