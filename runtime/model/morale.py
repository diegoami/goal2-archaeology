"""Q017 events-morale result delta, transcribed from GOAL.EXE.

Listing: 0791:7CC5 (the live-form helper), 0791:798D (booking), 0791:7B77
(send_off), 0791:7D56 (injure), 0791:6443 (record_goal scorer), 0791:65FE
(after_goal team reaction), 1771:13D0 (team aggregate, six-word bar
DS:9B5A..9B64). This module is the F019 model extended with the event
writers and the team aggregate. Callers must preserve the in-match event
sequence (goal scorer's flag-1, team reaction's flag-0, send-off head's
flag-1 + tail's flag-0, injury's flag-1, panel-render recomputation).
"""

BYTE_BITS = 8
WORD_BITS = 16

# 7CC5 adjust_player_form clamps
LIVE_LOWER = 1
LIVE_UPPER = 255
SAVED_UPPER = 32

# 1771:13D0 team-aggregate clamps
PANEL_MIN = 0
PANEL_MAX = 32
PANEL_SEED = 6
PANEL_DIVISOR = 11
PANEL_FLOOR = 1


def _signed(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def event_clamp(before, delta, persist):
    """0791:7CC5: signed byte plus signed word, clamp to 1..255; persist writes
    min(32, signed(new)) to DS:9B07. The delta is the HIGH word of the routine's
    int parameter; the persist flag is the low byte of its low word (the low
    word's high byte is unused and may be zero or sign-extension).
    """
    value = _signed(_signed(before, BYTE_BITS) + _signed(delta, WORD_BITS), WORD_BITS)
    live = min(LIVE_UPPER, max(LIVE_LOWER, value))
    saved = min(SAVED_UPPER, _signed(live, BYTE_BITS)) & 0xFF if persist else None
    return live, saved


def injure(before):
    """0791:7D56: clamp(+0xC + (-2), 1, 255); persist True (DS:9B07 written).
    The routine also sets +0xE = 0 (F018), which this helper does not model.
    """
    return event_clamp(before, -2, True)


def send_off(before):
    """0791:7B77 head call: clamp(+0xC + (-2), 1, 255); persist True (DS:9B07
    written). The routine's tail call on the OTHER team's available players
    applies +2 with persist False and is not this helper.
    """
    return event_clamp(before, -2, True)


def scorer(before, morale_delta):
    """0791:6443: clamp(+0xC + morale_delta, 1, 255); persist True (DS:9B07
    written). morale_delta is s8(DS:0x7920[DS:7C39==0 ? 1 : 0]) — usually +1.
    """
    if not -128 <= morale_delta <= 127:
        raise ValueError('event delta must fit a signed byte')
    return event_clamp(before, morale_delta, True)


def team_reaction(before, morale_delta):
    """0791:65FE: clamp(+0xC + morale_delta, 1, 255); persist False (DS:9B07
    NOT written). morale_delta is s8(DS:0x7920[side_of_ball]) — +1 or -1.
    """
    if not -128 <= morale_delta <= 127:
        raise ValueError('event delta must fit a signed byte')
    return event_clamp(before, morale_delta, False)


def team_panel_morale(morales):
    """1771:13D0: team morale aggregate DS:9B5A over the 11 available starters.
    morals is the iterable of +0xC bytes (signed) of the 11 starters, in
    starting-XI order; unavailable starters (energy 0, booked, sent off,
    suspended) are filtered by the caller. Each remaining byte contributes
    max(0, min(32, signed_byte(+0xC))) to the sum. The seed is 6 and the
    divisor is 11; the result is at least 1 (the panel index must be in range).
    """
    if not isinstance(morales, (list, tuple)):
        raise ValueError('starters must be a list or tuple of +0xC bytes')
    total = PANEL_SEED
    for value in morales:
        signed = _signed(value, BYTE_BITS)
        total += max(PANEL_MIN, min(PANEL_MAX, signed))
    quotient = total // PANEL_DIVISOR
    return max(PANEL_FLOOR, quotient)