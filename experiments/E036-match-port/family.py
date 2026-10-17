#!/usr/bin/env python3
"""E036 (T57): run a family of matches through the original-match kit and write one record per match.

    python3 -B experiments/E036-match-port/family.py --family ALL --out experiments/E036-match-port/out/T<nn>/<name>.jsonl
        [--max N] [--workers 1|2] [--time-limit S] [--count SSSS:OOOO,...] [--mask FILE] [--only ID,...] [--cache DIR]
    python3 -B experiments/E036-match-port/family.py --family ALL --find-ranges experiments/E036-match-port/out/T57/ranges-<stamp>.json [--only ID,...]

--family is ALL (the union of the families under families/) or comma-separated family names. The matches are the
declared ones (families.py); the image is E006-r0001, fetched by hash into --cache (default .cache/dl).

The unhooked kit is the reference: no port is installed (`--ports`, `--variant` come with T59, `--engine` with T78,
and the record grammar, records.py, grows with them). One record per match (records.py): completion, score, ticks,
the draws (count, digest, one digest per minute), the board's raw statistics and bars, the commentary's template
counts, the result's digest without the screen and the board screen's digest apart, the events' digest, and, after
the post-match update, the seed word and one digest per 1 KiB of DS and of each range a match writes outside the
screen (records.RANGES), taken over the declared mask (--mask: a JSON list of [space, start, length]; by default
nothing is masked). `--count` counts the executions of each instruction address (a routine's entry or a branch's
target), skipping the replays the kit's own stops cause.

--out is resumable: the matches already in it (each a valid record of a selected match, with the declared spec, mask
and image) are not run again and no line is ever rewritten; a record that is not valid, or not of this run, makes
the command refuse (exit 2). A record is appended and synced as soon as its match ends. --max stops after N new
matches. --workers 2 runs two matches at a time in two processes (the most the shared machine allows); the default
is one. --time-limit (default 300 s) bounds one match's wall time: a match over it is recorded as an error.

Exit status: 0 when every selected match in --out is a completed match, 1 when one is not (an error, a stray
decision, no board), 2 for a refused command.

--find-ranges runs the selected matches with a write watch over all guest memory (about five times slower) and
writes, to a new file, every range written outside DS and the screen, the DS blocks written, and the ranges to
declare in records.RANGES (the finder of T57: the ranges are found once, not guessed)."""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE))
import families  # noqa: E402
import records  # noqa: E402

DEFAULT_CACHE = ".cache/dl"
DEFAULT_TIME_LIMIT = 300.0
SEED_WORD = 0x7B62                                     # DS:7B62 the main RNG word (match.py SEED)
SCREEN_POINTERS = (0xA96A, 0xA96E, 0xA972)             # DS: the text page (B800:0) and the two text buffers
SCREEN_BYTES = 4000
COUNTRIES_PTR, FIXTURES_PTR, GAME_PTR = 0xA917, 0xA92B, 0xA923   # image.py


class Refused(Exception):
    """A command the script will not run (exit 2)."""


def clean_error(e):
    """One line of printable ASCII: the exception's class and the first line of its message (the kit puts the screen's
    text on the following lines, which is commentary and names: never kept)."""
    first = (str(e).splitlines() or [""])[0]
    text = f"{type(e).__name__}: {first}"
    text = "".join(c if 0x20 <= ord(c) < 0x7F else "?" for c in text).strip()
    return text[:200].rstrip() or "Error"


def parse_count(arg):
    if arg is None:
        return []
    out = arg.split(",")
    if not all(records.ADDRESS.fullmatch(a) for a in out) or len(set(out)) != len(out):
        raise Refused(f"--count {arg!r}: distinct SSSS:OOOO addresses (upper-case hex), comma-separated")
    return out


def parse_mask(path):
    if path is None:
        return []
    try:
        mask = records.loads(Path(path).read_bytes().decode("utf-8"))
        records.validate_mask(mask)
    except (OSError, ValueError) as e:
        raise Refused(f"--mask {path}: {e}")
    return mask


# ---- one match -------------------------------------------------------------------------------------------------
class TimeLimit(Exception):
    pass


def digest_memory(m, mask):
    """{'seed', 'ds', 'ranges'}: the main seed word, one digest per 1 KiB of DS, and of each of records.RANGES,
    after the post-match update, over the mask."""
    machine = m.m
    ds = records.apply_mask(machine.read(machine.DS * 16, records.DS_SIZE), "DS", 0, mask)
    out = {"seed": machine.rd(SEED_WORD), "ds": records.block_digests(ds), "ranges": {}}
    for name, (start, length) in records.RANGES.items():
        buf = machine.read(machine.load * 16 + start, length)
        out["ranges"][name] = records.block_digests(records.apply_mask(buf, "P", start, mask))
    return out


def play(m, spec, deadline):
    """Drive a Match with the spec's answer policy; (events, decisions, strays, stopped_at_board)."""
    events, decisions, strays, paused, board = [], [], [], set(), False
    policy = spec.policy
    for ev in m.events():
        events.append((ev.kind, ev.minute, ev.score, ev.data))
        if time.time() > deadline:
            raise TimeLimit("the match is over its time limit")
        if ev.kind == "full_time":
            board = True
        if ev.kind == "minute" and ev.minute in policy.pause_at and ev.minute not in paused:
            paused.add(ev.minute)
            m.pause()
        if ev.kind == "decision":
            context = ev.data["context"]
            decisions.append([ev.minute, context])
            if context in policy.contexts:
                policy.answer(m, ev.data)
            else:
                strays.append(context)
                m.answer()
    return events, decisions, strays, board


def run_match(image, spec, mask=(), counts=(), time_limit=DEFAULT_TIME_LIMIT, watch=None):
    """The record of one match. Never raises for the match's own failure: that is the record's `error`."""
    from original_match import Match, Fixture
    from original_match.match import VERSION
    cpu0, wall0 = time.process_time(), time.time()
    rec = {"id": spec.id, "family": spec.family, "spec_sha256": spec.sha256, "image_sha256": families.image_sha256(),
           "kit": VERSION, "mask": [list(s) for s in mask], "error": None, "stopped_at_board": False, "strays": [],
           "cpu_s": 0.0, "wall_s": 0.0, "score": None, "ticks": None, "draws": None, "board": None,
           "templates": None, "result_sha256": None, "events": None, "decisions": None, "after": None,
           "counts": {}}
    seen = {a: 0 for a in counts}
    try:
        players = countries = None
        if spec.edits:
            players, countries = families.apply_edits(image.players(), image.countries(), spec.edits)
        first, second, index, kind = spec.fixture
        m = Match(image, Fixture(first, second, index=index, kind=kind), managed=spec.managed, seed=spec.seed,
                  record_draws=True, delay_byte=spec.delay_byte, substitutions=spec.substitutions, players=players,
                  countries=countries, timeout_s=min(60, time_limit))
        for address in counts:
            def count(replay, address=address):
                if not replay:
                    seen[address] += 1
            m.m.at(address, count)
        if watch is not None:
            watch(m)
        events, decisions, strays, board = play(m, spec, time.time() + time_limit)
        result = m.result()
        draws = m.st["draws"]
        rec["strays"], rec["stopped_at_board"] = strays, board
        n_events, events_sha = records.events_digest(events)
        b = result["board"]
        rec.update(
            score=list(result["score"]), ticks=result["ticks"],
            draws={"count": len(draws), "digest": records.draws_digest(draws), "per_minute": records.draws_per_minute(draws)},
            board={"statistics": {k: list(v) for k, v in b["statistics"].items()}, "bars": [list(r) for r in b["bars"]],
                   "man_of_the_match": b["man_of_the_match"], "final_score": list(b["final_score"]), "seed": b["seed"],
                   "screen_sha256": b["screen_sha256"]},
            templates=records.template_counts(result["commentary"]), result_sha256=records.result_digest(result),
            events={"count": n_events, "sha256": events_sha}, decisions=decisions, after=digest_memory(m, mask))
    except Exception as e:      # the record says what failed; a missing record would be a silent gap
        rec.update(error=clean_error(e), score=None, ticks=None, draws=None, board=None, templates=None,
                   result_sha256=None, events=None, decisions=None, after=None)
    rec["counts"] = dict(seen)
    rec["cpu_s"], rec["wall_s"] = round(time.process_time() - cpu0, 3), round(time.time() - wall0, 3)
    records.validate(rec)       # a record the grammar refuses is a bug here, not evidence
    return rec


# ---- the family run --------------------------------------------------------------------------------------------
_worker = {}


def _init_worker(cache, mask, counts, time_limit, specs):
    from original_match import Image
    from original_match.assets import reference_image
    _worker.update(image=Image.from_bytes(reference_image(cache)), mask=mask, counts=counts, time_limit=time_limit,
                   specs={s.id: s for s in specs})


def _run_in_worker(match_id):
    return run_match(_worker["image"], _worker["specs"][match_id], _worker["mask"], _worker["counts"],
                     _worker["time_limit"])


def existing_records(out, selected, mask):
    """The valid records already in --out, {id: record}. Refuses a file that is not this run's: an invalid line, an
    id twice or not selected, a spec, mask or image that is not the declared one."""
    if not Path(out).exists():
        return {}
    try:
        recs = records.read_log(out)
    except records.SchemaError as e:
        raise Refused(f"{out} is not a valid log: {e}")
    expected = {s.id: s for s in selected}
    done = {}
    for r in recs:
        if r["id"] not in expected:
            raise Refused(f"{out} holds {r['id']}, which is not a selected match")
        if r["id"] in done:
            raise Refused(f"{out} holds {r['id']} twice")
        if r["spec_sha256"] != expected[r["id"]].sha256 or r["image_sha256"] != families.image_sha256():
            raise Refused(f"{out}: {r['id']} was run from another declaration or image than the one declared now")
        if r["mask"] != [list(s) for s in mask]:
            raise Refused(f"{out}: {r['id']} was taken over another mask than --mask")
        done[r["id"]] = r
    return done


def append(out, record):
    """One line, appended and synced: a record is never rewritten."""
    fd = os.open(out, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, (records.dumps(record) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def run_family(selected, out, workers=1, max_new=None, cache=DEFAULT_CACHE, mask=(), counts=(),
               time_limit=DEFAULT_TIME_LIMIT, say=print):
    """Run the selected matches not yet in `out`; returns the records of every selected match now in `out`."""
    done = existing_records(out, selected, mask)
    todo = [s for s in selected if s.id not in done]
    if max_new is not None:
        todo = todo[:max_new]
    say(f"{len(selected)} matches selected, {len(done)} already in {out}, {len(todo)} to run")
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    def took(rec):
        append(out, rec)
        done[rec["id"]] = rec
        state = "completed" if records.is_completed(rec) else f"NOT COMPLETED ({rec['error'] or rec['strays'] or 'no board'})"
        say(f"{rec['id']}: {state}; score {rec['score']} ticks {rec['ticks']} cpu {rec['cpu_s']} s")

    if workers == 1:
        from original_match import Image
        from original_match.assets import reference_image
        image = Image.from_bytes(reference_image(cache))
        for spec in todo:
            took(run_match(image, spec, mask, counts, time_limit))
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                                 initargs=(cache, mask, counts, time_limit, todo)) as pool:
            for rec in pool.map(_run_in_worker, [s.id for s in todo]):
                took(rec)
    return [done[s.id] for s in selected if s.id in done]


# ---- the write watch -------------------------------------------------------------------------------------------
def merge(spans, gap=0):
    spans = sorted(spans)
    out = []
    for a, b in spans:
        if out and a <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def subtract(spans, cut):
    """spans minus the span `cut` = [a, b)."""
    out = []
    for a, b in spans:
        if b <= cut[0] or a >= cut[1]:
            out.append([a, b])
            continue
        if a < cut[0]:
            out.append([a, cut[0]])
        if b > cut[1]:
            out.append([cut[1], b])
    return out


def find_ranges(image, selected, path, time_limit=3600.0, say=print):
    """Play the selected matches under a write watch on all guest memory and write the report to the new file `path`."""
    from unicorn import UC_HOOK_MEM_WRITE
    blocks, info, ids = set(), {}, []

    def watch(m):
        def hook(uc, access, address, size, value, data):
            blocks.add(address >> 4)
            blocks.add((address + size - 1) >> 4)
        m.m.uc.hook_add(UC_HOOK_MEM_WRITE, hook, begin=0, end=0x10FFFF)
        machine = m.m
        base = machine.load * 16
        info["load"] = machine.load
        info["ds"] = [machine.DS * 16 - base, machine.DS * 16 - base + records.DS_SIZE]
        info["screen"] = [[machine.far(p) - base, machine.far(p) - base + SCREEN_BYTES] for p in SCREEN_POINTERS]
        count = machine.rd_far(GAME_PTR, 0x28)
        info["records"] = [machine.far(COUNTRIES_PTR) - base, machine.far(FIXTURES_PTR) - base + 8 * count]
    for spec in selected:
        rec = run_match(image, spec, time_limit=time_limit, watch=watch)
        if not records.is_completed(rec):
            raise Refused(f"{spec.id} did not complete under the watch ({rec['error'] or rec['strays']})")
        ids.append(spec.id)
        say(f"{spec.id}: watched; {len(blocks)} 16-byte blocks written so far")
    base = info["load"] * 16
    written = merge([[(b << 4) - base, ((b + 1) << 4) - base] for b in blocks])
    outside = written
    for cut in [info["ds"]] + info["screen"]:
        outside = subtract(outside, cut)
    outside = merge(outside)
    rec_lo, rec_hi = info["records"]
    inside_records = [s for s in outside if rec_lo <= s[0] and s[1] <= rec_hi]
    other = merge([s for s in outside if not (rec_lo <= s[0] and s[1] <= rec_hi)], gap=0x400)
    ds_lo, ds_hi = info["ds"]
    ds_blocks = sorted({(x - ds_lo) // records.BLOCK for a, b in written for x in range(max(a, ds_lo), min(b, ds_hi), 16)})
    screen_blocks = sorted({(x - ds_lo) // records.BLOCK for lo, hi in info["screen"] for x in range(max(lo, ds_lo), min(hi, ds_hi))})
    report = {"image_sha256": families.image_sha256(), "matches": ids, "load_segment": info["load"],
              "ds_program_relative": info["ds"], "screen_program_relative": info["screen"],
              "records_program_relative": info["records"],
              "written_outside_ds_and_screen": outside, "written_inside_records": inside_records,
              "ds_blocks_written": ds_blocks, "ds_blocks_of_the_screen": screen_blocks,
              "ranges": {"records": [rec_lo, rec_hi - rec_lo], **{f"w{a:05x}": [a, -(-(b - a) // 16) * 16]
                                                                 for a, b in other}}}
    with open(path, "x") as f:
        json.dump(report, f, indent=1)
    say(f"ranges found: {report['ranges']}")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--family", required=True)
    ap.add_argument("--out")
    ap.add_argument("--find-ranges")
    ap.add_argument("--max", type=int)
    ap.add_argument("--workers", type=int, choices=(1, 2), default=1)
    ap.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT)
    ap.add_argument("--count")
    ap.add_argument("--mask")
    ap.add_argument("--only")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    a = ap.parse_args(argv)
    try:
        if (a.out is None) == (a.find_ranges is None):
            raise Refused("give --out (a family run) or --find-ranges (the write watch), not both and not neither")
        if a.max is not None and a.max < 1:
            raise Refused("--max is a number of matches, 1 or more")
        if not 0 < a.time_limit <= 36000:
            raise Refused("--time-limit is a number of seconds, up to 36000")
        selected = [m for fam in families.select(a.family, families.discover()) for m in fam.matches]
        if a.only is not None:
            ids = a.only.split(",")
            unknown = [i for i in ids if i not in {m.id for m in selected}]
            if unknown or len(set(ids)) != len(ids):
                raise Refused(f"--only {a.only!r}: distinct ids among the selected matches (unknown: {unknown})")
            selected = [m for m in selected if m.id in ids]
        mask, counts = parse_mask(a.mask), parse_count(a.count)
        if a.find_ranges:
            if a.find_ranges and Path(a.find_ranges).exists():
                raise Refused(f"refused: {a.find_ranges} exists (an output is never overwritten)")
            from original_match import Image
            from original_match.assets import reference_image
            find_ranges(Image.from_bytes(reference_image(a.cache)), selected[:a.max], a.find_ranges)
            return 0
        recs = run_family(selected, a.out, a.workers, a.max, a.cache, mask, counts, a.time_limit)
    except (Refused, families.FamilyError) as e:
        print(f"refused: {e}")
        return 2
    bad = [r["id"] for r in recs if not records.is_completed(r)]
    print(f"{len(recs)} of {len(selected)} matches in {a.out}, {len(bad)} not completed" + (f": {bad}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
