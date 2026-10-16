"""Key drivers for the original's screens: goal2 gives a decision, these press the original's keys for it.

Each driver is closed-loop: at every key read it looks at the screen's own state in guest memory (the highlighted
item, row or squad slot) and returns the next key, so nothing depends on a recorded key sequence. The screens are
the original's (static/goal-exe/named/): the team menu 0791:ED8A, the tactics screen 1771:1981, the SELECT TEAM
screen 0791:E44F, the captain and taker prompt 0791:CC7B. goal2 never sees them.

Key codes are what 214B:08DD stores in DS:A976 (seg_214B_02.asm:16-54): the character, or for an extended key
its scan code adjusted (Left -1, Right -2, End..PgDn -3) plus 0x64."""
ENTER, ESC, SPACE = 0x0D, 0x1B, 0x20
UP, DOWN, LEFT, RIGHT = 0xAC, 0xB1, 0xAE, 0xAF
KEY_R = ord("R")

# The team menu ED8A (named seg_0791_12.c in_match_menu): ten items, 1-5 for team 1 (DS:9B36) and 6-10 for
# team 0 (DS:9B34): `local_4 = local_9 < 6; local_7 = DS:9B34[local_4]`. Per side: +0 team tactics (1771:1981),
# +1 select team (E949 -> E44F), +2 E929, +3 the match board, +4 leave ("play", checked by EA09).
MENU_TACTICS, MENU_SELECT, MENU_PLAY = 0, 1, 4
# ED8A's locals, from its BP (Ghidra's local_N is [bp - (N - 2)]; E949 reads local_7 as [param_1 - 5]):
MENU_ITEM_BP = -7       # local_9, the highlighted item (word)
# The tactics screen 1771:1981: the row DS:0D8E (1..8), Enter toggles element DS:6BBF[row] of +0x2D.
TACTICS_ROW, TACTICS_ELEMENT_OF_ROW = 0x0D8E, 0x6BBF
# SELECT TEAM E44F: the squad cursor DS:0C1B (1..20, 214B menu_move_word_wrap(0x14, 0xC1B)); in a match Enter
# marks then swaps (E022) when DS:9B41 is set and a substitution is left, else toggles the request DS:9B40.
SELECT_CURSOR, SUBS_REQUEST, SUBS_ALLOWED, SUBS_LEFT = 0x0C1B, 0x9B40, 0x9B41, 0x9B38
# CC7B: the highlighted slot local_7 = [bp - 5] (moved by 214B menu_move_word_wrap(0xb, &local_7)).
PROMPT_SLOT_BP = -5


def step_toward(current, target):
    return DOWN if target > current else UP


class MenuPlan:
    """What to do in one visit of the team menu, from goal2's answer: tactics, substitutions, then play.

    `tactics` maps element (1..8) to the wanted value; `subs` is a list of (off, on) player words. Steps are done in
    the order tactics, subs, play. `request_only`: the original allows only a request now (DS:9B41 clear), so the
    select-team visit sets the request flag DS:9B40 and the substitutions wait for the next stoppage."""

    def __init__(self, side, tactics=None, subs=None):
        self.side = side                  # the managed team's engine side, 0 or 1
        self.steps = []
        if tactics:
            self.steps.append("tactics")
        if subs:
            self.steps.append("subs")
        self.steps.append("play")
        self.tactics = {int(e): bool(v) for e, v in (tactics or {}).items()}   # keys may be JSON strings
        self.subs = list(subs or [])
        self.sub_index = 0
        self.sub_marked = False
        self.in_screen = None             # "tactics" or "subs" while that screen is open
        self.done_subs = []               # (off, on) made
        self.refused = []                 # (off, on, message) refused by the original
        self.requested = False            # the request flag was set (request_only)
        self.menu_reads_after_play = 0
        self.pending_check = None         # (off, on) whose swap Enter was just pressed
        self.last_message = None          # the original's message text, when it refused something

    def item(self, step):
        base = 6 if self.side == 0 else 1
        return base + {"tactics": MENU_TACTICS, "subs": MENU_SELECT, "play": MENU_PLAY}[step]

    # -- the team menu -------------------------------------------------------------------------------
    def menu_key(self, item):
        if self.in_screen is not None:     # back from a screen: that step is done
            self.steps.pop(0)
            self.in_screen = None
        step = self.steps[0]
        target = self.item(step)
        if item != target:
            return step_toward(item, target)
        if step == "play":
            self.menu_reads_after_play += 1
        else:
            self.in_screen = step
        return ENTER

    # -- the tactics screen ----------------------------------------------------------------------------
    def tactics_key(self, row, element_of_row, tactics_byte):
        for element, want in self.tactics.items():
            have = bool(tactics_byte >> (element - 1) & 1)
            if have != bool(want):
                rows = [r for r in range(1, 9) if element_of_row[r] == element]
                if not rows:
                    raise ValueError(f"tactic element {element} has no row on the tactics screen")
                if row != rows[0]:
                    return step_toward(row, rows[0])
                return ENTER
        return ESC

    # -- SELECT TEAM -----------------------------------------------------------------------------------
    def select_key(self, cursor, squad, allowed, request_flag, subs_left):
        """squad: the managed country's 20 squad words now."""
        if self.pending_check is not None:        # the swap Enter was pressed: did the original make it?
            off, on = self.pending_check
            self.pending_check = None
            if on in squad[:11] and off not in squad[:11]:
                self.done_subs.append((off, on))
            else:
                self.refused.append((off, on, self.last_message or "refused by the original"))
            self.last_message = None
        if not allowed or subs_left == 0:
            if request_flag == 0 and subs_left and self.sub_index < len(self.subs) and not self.requested:
                self.requested = True
                return ENTER                      # toggles DS:9B40 on: substitution at the next stoppage
            return ESC
        while self.sub_index < len(self.subs):
            off, on = self.subs[self.sub_index]
            want = off if not self.sub_marked else on
            if want not in squad:
                self.refused.append((off, on, f"player {want} is not in the squad"))
                self.sub_index += 1
                self.sub_marked = False
                continue
            slot = squad.index(want) + 1
            if cursor != slot:
                return step_toward(cursor, slot)
            self.sub_marked = not self.sub_marked
            if not self.sub_marked:               # the second Enter: the swap (or the original's refusal)
                self.sub_index += 1
                self.pending_check = (off, on)
            return ENTER
        return ESC
