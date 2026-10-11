"""Shared helpers of E020: the hash-checked half-time savestate, memory edits by player word, and
the equal-skill scenario as a list of edits (so the original binary and the model start from the same
bytes).

The input is E010-r0010's half-time savestate (release E010, quick mode, countries 7 and 19); its
sha256 is fixed here and checked on every load."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT))
import players  # noqa: E402
import savestate  # noqa: E402

STATE_SHA256 = "3c7983fa4869d3278fe9f1f6140e5ca1b84f602e97b5862f547c6332d086e1e6"
STATE_ASSET = "3c7983fa4869d327-E010-r0010-halftime.sav"
DL = ROOT / ".cache/dl"

TEAM0_COUNTRY, TEAM1_COUNTRY = 7, 19     # this state's two sides (QuickMatch.teams, D77E-D798)


def load_state():
    """The half-time savestate bytes; downloaded from release E010 when missing, sha256-checked."""
    path = DL / STATE_ASSET
    if not path.is_file():
        DL.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gh", "release", "download", "E010", "--repo", "diegoami/goal2-archaeology",
                        "--pattern", STATE_ASSET, "--dir", str(DL)], check=True)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != STATE_SHA256:
        raise SystemExit(f"{path}: sha256 does not match {STATE_SHA256}")
    return data


def player_base(state):
    """Guest physical address of the player array (far pointer DS:A91B)."""
    return players.far_pointer(state, players.PLAYERS_PTR)[2]


def country_base(state):
    return players.far_pointer(state, players.COUNTRIES_PTR)[2]


def apply_edits(data, edits):
    """The savestate `data` with the edits applied (savestate.with_memory, I3). An edit is one of
    {"player_word": w, "offset": o, "hex": "..."}  - bytes at player w's record + o,
    {"country": c, "offset": o, "hex": "..."}      - bytes at country c's record + o,
    {"ds_offset": o, "hex": "..."}                 - bytes at DS:o."""
    state = savestate.Savestate(data)
    pb, cb = player_base(state), country_base(state)
    ds = state.program().ds_base
    for e in edits:
        new = bytes.fromhex(e["hex"])
        if "player_word" in e:
            addr = pb + players.PLAYER_SIZE * e["player_word"] + e["offset"]
        elif "country" in e:
            addr = cb + players.COUNTRY_SIZE * e["country"] + e["offset"]
        else:
            addr = ds + e["ds_offset"]
        data = savestate.with_memory(data, addr, new)
    return data


def squad_words(data, country):
    state = savestate.Savestate(data)
    return players.squad(players.countries(state), country)


def player_record(data, word):
    state = savestate.Savestate(data)
    return bytes(players.record(players.players(state), players.PLAYER_SIZE, word))


def equal_skill_edits(data, a_energy, a_form, b_energy, b_form, fit_side_is_team0=True,
                      home_flag_off=True):
    """Edits making the two sides identical in every skill byte and differing only in condition.

    Team 1's twenty squad records are overwritten with team 0's, slot for slot, except byte 0 (the
    country, which `players.check` and `1771:96D3` tie to the squad); country 19's tactic byte
    (+0x2D) and manager index (+0x2E) are overwritten with country 7's, and the home flag DS:80FC
    (which adds a share to team 1's line sums only, F012: 0BC4 flag) is cleared. Then the energy
    (+0xE) and form (+0xC) of team 0's twenty players are set to (a_energy, a_form), team 1's to
    (b_energy, b_form). Fitness (+0xD) is left as it is: no match code reads it (F021)."""
    s0, s1 = squad_words(data, TEAM0_COUNTRY), squad_words(data, TEAM1_COUNTRY)
    state = savestate.Savestate(data)
    carr = players.countries(state)
    c0 = players.record(carr, players.COUNTRY_SIZE, TEAM0_COUNTRY)
    edits = []
    for w0, w1 in zip(s0, s1):
        rec = bytearray(player_record(data, w0))
        rec[0] = TEAM1_COUNTRY
        rec[0xC], rec[0xE] = b_form, b_energy
        edits.append({"player_word": w1, "offset": 0, "hex": bytes(rec).hex()})
        edits.append({"player_word": w0, "offset": 0xC, "hex": bytes([a_form]).hex()})
        edits.append({"player_word": w0, "offset": 0xE, "hex": bytes([a_energy]).hex()})
    edits.append({"country": TEAM1_COUNTRY, "offset": 0x2D, "hex": bytes(c0[0x2D:0x2F]).hex()})
    if home_flag_off:
        edits.append({"ds_offset": 0x80FC, "hex": "00"})
    return edits


def seed_edit(seed):
    return {"ds_offset": 0x7B62, "hex": seed.to_bytes(2, "little").hex()}
