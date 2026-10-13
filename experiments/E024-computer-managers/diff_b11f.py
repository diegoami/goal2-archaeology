"""E024: differential test of the lineup routine 0791:B11F: the ORIGINAL code, run unhooked in Unicorn, against
a Python reading of it, on the squads of the ten E010 half-time savestates and on random perturbations of them.

    python3 -B experiments/E024-computer-managers/diff_b11f.py [scenarios per team]

For each E010 record's half-time savestate and for each of the two teams in it (DS:9B34, DS:9B36), and for
scenario 0 (the state as saved) and S random scenarios (a seeded `random.Random`): the guest memory is
patched (player bytes +4, +6, +7, +0xC, +0xE, +0x10 of the country's twenty players), then

  original:  the unpacked GOAL.EXE's own 0791:B11F(country) runs in Unicorn from CS:IP = B11F with a
             far-call frame; nothing is hooked or stubbed (code hooks are used only to read the branch
             counters below, never to write); the interrupt hook only swallows interrupts. It reads and
             writes the guest memory exactly as in the game.
  reference: `reference()` below, a reading of seg_0791_17.asm:1091-1139 (AC67), seg_0791_18.asm:6-354
             (AD8F, AFA3) and 355-385 (B11F) written from the listing, on the same bytes, using the
             model's player predicates (runtime/model/quick_engine.py: 3216, 3041, 3088, 3179, 377E,
             AAE8's table walk, A9B8's value table).

They are compared on: the set of the twenty squad words in slots 1..11 and in 12..20 (1771:52CC sorts each
half by +6 with a quicksort whose order among equal keys the reference does not model, so the ORDER inside a
half is not compared; it is checked to be non-decreasing in +6), every squad player's +6 byte, and the
14 bytes DS:99A2. Any difference stops being silent: it is printed and the script exits non-zero.
Branch counters (in the reference, and equal to the original wherever the comparison holds) say which
branches of B11F the scenarios reach. A new log out/diff-b11f-<UTC time>.log (never overwritten).

A second argument names a falsifier, a deliberately wrong reference that the comparison must catch: `tie` (AC67
replaces on equal strength), `first` (AAE8 keeps the first passing candidate, not the last), `noweaker` (no swap of
an out-of-position starter for a weaker bench player of his role), `nofoot` (3179 never penalises).
"""
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "runtime/model"))
sys.path.insert(0, str(ROOT / "experiments/E010-q010-quick-engine"))
import json  # noqa: E402

import check_model  # noqa: E402
import players  # noqa: E402
import quick_engine  # noqa: E402
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import (UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_DS, UC_X86_REG_ES,  # noqa: E402
                               UC_X86_REG_CS, UC_X86_REG_BP)

S = int(sys.argv[1]) if len(sys.argv) > 1 else 60
FALS = sys.argv[2] if len(sys.argv) > 2 else ""      # a falsifier: a deliberately wrong reference (see the docstring)
MEM = savestate.MEM_BASE
T_ADDR = 0x99A2
PAIRS = ({5, 6}, {7, 10}, {8, 11}, {12, 13})       # CS:AD0F, AD2F, AD4F, AD6F (bytes in the listing)
cnt = Counter()


# ---------------------------------------------------------------- the reference (the listing's reading)
def reference(m, c):
    """Returns (squad words list of 20, {player: +6}, T bytes[14]) after B11F(c), with the order of each half
    left as the swaps made it."""
    sq = m._country(c)["squad"][:]
    P = m._player
    strength = m.player_strength
    T = [0] * 14

    def ac67(k):                                                    # seg_0791_17.asm:1091-1139
        w = sq[k - 1]
        if m.unavailable(w):
            cnt["AC67 slot unavailable: skipped"] += 1
            return
        pos = P(w)[7]
        if T[pos] == 0:
            T[pos] = k
            cnt["AC67 position entry empty: stored"] += 1
        elif (strength(w) >= strength(sq[T[pos] - 1])) if FALS == "tie" else (strength(w) > strength(sq[T[pos] - 1])):
            T[pos] = k
            cnt["AC67 strictly stronger than the stored: replaced"] += 1
        else:
            cnt["AC67 not stronger than the stored: kept (tie keeps the earlier slot)"] += 1

    def aae8(w):                                                    # seg_0791_17.asm:932-1090
        pos = P(w)[6]
        table = m.t_formation[8 * pos:8 * pos + 8]
        count = m._pos_string_index(pos)
        expect = 1 if count > 3 else 0
        best = 0
        for i in range(1, table[0] + 1):
            k = T[table[i]] if table[i] < 14 else 0
            if not k:
                continue
            cw = sq[k - 1]
            if count > 0 and not m.two_footed(cw) and m.foot_index(cw) != expect:
                continue
            if FALS == "first" and best:
                continue
            best = k                                                # the LAST passing entry
        return best

    def a9b8(pos):                                                  # seg_0791_17.asm:808-931 (bound 20)
        count = m._pos_string_index(pos)
        expect = 1 if count > 3 else 0
        best, best_v = 0, 0
        for k in range(12, 21):
            cw = sq[k - 1]
            if m.unavailable(cw):
                continue
            v = m.t_benchvalue[14 * pos + P(cw)[7]]
            if count > 0 and not m.two_footed(cw) and m.foot_index(cw) != expect:
                v //= 2
            if v > best_v:
                best, best_v = k, v
        return best

    def swap(s, b):                                                 # seg_0791_18.asm:6-210
        T[P(sq[b - 1])[7]] = 0
        sq[s - 1], sq[b - 1] = sq[b - 1], sq[s - 1]
        inc, out = sq[s - 1], sq[b - 1]
        role_out = P(out)[6]
        if any(role_out in g and P(inc)[7] in g for g in PAIRS):
            P(inc)[6] = P(inc)[7]
            cnt["AD8F incoming takes his own +7 (same pair as the slot's role)"] += 1
        else:
            P(inc)[6] = role_out
            cnt["AD8F incoming takes the slot's role"] += 1
        P(out)[6] = P(out)[7]
        ac67(b)

    for k in range(12, 21):
        ac67(k)
    for s in range(1, 12):                                          # seg_0791_18.asm:211-354
        w = sq[s - 1]
        b = aae8(w)
        cnt["AFA3 AAE8 found a bench slot" if b else "AFA3 AAE8 found none"] += 1
        replace = False
        if b:
            wb = sq[b - 1]
            if strength(wb) > strength(w):
                cnt["AFA3 bench strictly stronger: swap"] += 1
                swap(s, b)
                continue
            if FALS != "noweaker" and P(w)[7] != P(w)[6] and P(wb)[7] == P(w)[6]:
                cnt["AFA3 starter away from +7 and bench +7 = his role: swap although weaker"] += 1
                swap(s, b)
                continue
        if m.unavailable(w):
            cnt["AFA3 starter unavailable"] += 1
            replace = True
        elif FALS != "nofoot" and m.wrong_foot(w):
            cnt["AFA3 starter 3179-penalised"] += 1
            replace = True
        elif s == 1 and P(w)[7] != 0:
            cnt["AFA3 slot 1 holds a non-goalkeeper"] += 1
            replace = True
        if replace:
            if b:
                swap(s, b)
            else:
                b2 = a9b8(P(w)[6])
                cnt["AFA3 no AAE8 candidate: A9B8 " + ("found one" if b2 else "found none")] += 1
                if b2:
                    swap(s, b2)
        else:
            cnt["AFA3 starter kept"] += 1
    return sq, {w: P(w)[6] for w in sq}, T


# ---------------------------------------------------------------- the original (Unicorn, unhooked)
def run_original(mem, st, c):
    prog = st.program()
    load = prog.ds_base // 16 - 0x2581
    CODE, DS = load + 0x791, prog.ds_base // 16
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(0, bytes(mem[MEM:MEM + 0x110000]))
    sp = 0x6FF0
    mu.reg_write(UC_X86_REG_SS, 0x7000)
    mu.reg_write(UC_X86_REG_SP, sp)
    mu.reg_write(UC_X86_REG_DS, DS)
    mu.reg_write(UC_X86_REG_ES, DS)
    mu.reg_write(UC_X86_REG_CS, CODE)
    mu.reg_write(UC_X86_REG_BP, 0)
    ret_off = 0x0010
    mu.mem_write(0x70000 + sp, ret_off.to_bytes(2, "little") + CODE.to_bytes(2, "little") + c.to_bytes(2, "little"))
    mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
    mu.emu_start(CODE * 16 + 0xB11F, CODE * 16 + ret_off, timeout=20 * 1000000, count=2000000)
    return mu, DS


def read_back(mu, DS, c, ca, pa):
    """(squad words, {player: +6}, T) from the emulated memory."""
    sqb = bytes(mu.mem_read(ca + 0xBF * c, 40))
    sq = [int.from_bytes(sqb[2 * i:2 * i + 2], "little") for i in range(20)]
    pos = {w: bytes(mu.mem_read(pa + 20 * w + 6, 1))[0] for w in sq}
    T = list(bytes(mu.mem_read(DS * 16 + T_ADDR, 14)))
    return sq, pos, T


# ---------------------------------------------------------------- scenarios
def perturb(mem, st, c, rng):
    pa = players.far_pointer(st, players.PLAYERS_PTR)[2]
    ca = players.far_pointer(st, players.COUNTRIES_PTR)[2]
    sqb = mem[MEM + ca + 0xBF * c:MEM + ca + 0xBF * c + 40]
    sq = [int.from_bytes(sqb[2 * i:2 * i + 2], "little") for i in range(20)]
    kinds = Counter()
    for k, w in enumerate(sq, 1):
        base = MEM + pa + 20 * w
        if rng.random() < 0.12:
            mem[base + 0xE] = 0
            kinds["injured (+0xE = 0)"] += 1
        elif rng.random() < 0.25:
            mem[base + 0xE] = rng.randint(1, 32)
        if rng.random() < 0.06:
            mem[base + 0x10] |= 1 << rng.choice((7, 5, 2))        # elements 8, 6, 3 of +0x10
            kinds["status element set"] += 1
        if rng.random() < 0.3:
            mem[base + 0xC] = rng.randint(1, 40)
        if rng.random() < 0.3:
            mem[base + 4] = max(1, min(255, mem[base + 4] + rng.randint(-40, 40)))
        if k <= 11 and rng.random() < 0.15:
            mem[base + 6] = rng.randint(0, 13)
            kinds["starter role changed"] += 1
        if rng.random() < 0.08:
            mem[base + 7] = rng.randint(0, 13)
            kinds["+7 changed"] += 1
    return kinds


records = sorted((ROOT / "runs/E010").glob("E010-r*.json"))
lines = []


def out(s):
    lines.append(s)
    print(s, flush=True)


n = bad = 0
for p in records:
    record = json.loads(p.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    st0 = savestate.Savestate(check_model.halftime_sav(entry))
    for team in (0, 1):
        c = st0.ds_word(0x9B34 + 2 * team)
        for scen in range(S + 1):
            mem = bytearray(st0.mem)
            if scen:
                perturb(mem, st0, c, random.Random(f"{record['run_id']}/{team}/{scen}"))
            st0_mem_backup = st0.mem
            st0.mem = mem                                           # the model reads the patched bytes
            m = quick_engine.QuickMatch(st0)
            cnt_before = Counter(cnt)
            ref_sq, ref_pos, ref_T = reference(m, c)
            st0.mem = st0_mem_backup
            pa = players.far_pointer(st0, players.PLAYERS_PTR)[2]
            ca = players.far_pointer(st0, players.COUNTRIES_PTR)[2]
            mu, DS = run_original(mem, st0, c)
            o_sq, o_pos, o_T = read_back(mu, DS, c, ca, pa)
            problems = []
            if set(o_sq[:11]) != set(ref_sq[:11]) or set(o_sq[11:]) != set(ref_sq[11:]):
                problems.append(f"halves differ: original {o_sq} reference {ref_sq}")
            if o_pos != {w: ref_pos[w] for w in o_pos}:
                problems.append("a +6 byte differs: " + str({w: (o_pos[w], ref_pos.get(w)) for w in o_pos if o_pos[w] != ref_pos.get(w)}))
            if o_T != ref_T:
                problems.append(f"DS:99A2 differs: original {o_T} reference {ref_T}")
            managed = m._country(c)["managed"] > 0x80               # 1771:0B77; 52CC marks the unavailable
            for half in (o_sq[:11], o_sq[11:]):                    # of a managed country 0xE (sorts last)
                keys = [0xE if managed and m.unavailable(w) else o_pos[w] for w in half]
                if keys != sorted(keys):
                    problems.append(f"original half not sorted by +6: {keys}")
            n += 1
            if problems:
                bad += 1
                out(f"{record['run_id']} team {team} country {c} scenario {scen}: DIFFERENCE " + " | ".join(problems)[:600])
            changed = (set(o_sq[:11]) != set(m._country(c)["squad"][:11]))
            cnt["scenarios in which the original changed the eleven" if changed else "scenarios in which the eleven was unchanged"] += 1
out(f"cases compared: {n}, differing: {bad}")
out("branches of the reference over all cases:")
for k in sorted(cnt):
    out(f"  {cnt[k]:6d}  {k}")
d = HERE / "out"
d.mkdir(exist_ok=True)
fn = d / f"diff-b11f-{FALS or 'main'}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines) + "\n")
print("log:", fn)
sys.exit(1 if bad else 0)
