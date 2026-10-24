"""T76's opt-in original-screen taker scenario; old policy source stays immutable."""
from families import Policy


class SetPieceTaker(Policy):
    """Choose the last available eleven player different from the original pick."""

    def answer(self, m, d):
        if d["context"] == "set_piece":
            m.answer(taker=next(w for w in reversed(d["available"]) if w != d["current"]))
        else:
            m.answer()


POLICIES = {"SetPieceTaker": SetPieceTaker}
