#!/usr/bin/env python3
"""E036 (T57): run a family of matches through the original-match kit and write one record per match.

    python3 -B experiments/E036-match-port/family.py --family ALL --out experiments/E036-match-port/out/T<nn>/<name>.jsonl
        [--max N] [--workers 1|2] [--time-limit S] [--stretch-limit S] [--count SSSS:OOOO,...] [--mask FILE] [--only ID,...] [--cache DIR]
        [--ports M,...|all] [--variant M.NAME] [--checkpoint DIR]
    python3 -B experiments/E036-match-port/family.py --family ALL --find-ranges experiments/E036-match-port/out/T57/ranges-<stamp>.json [--only ID,...]

--family is ALL (the union of the families under families/) or comma-separated family names. The matches are the
declared ones (families.py); each spec binds a registered image source, fetched or verified by hash in --cache
(default .cache/dl). Historical specs retain E006-r0001.

The unhooked kit is the reference: no port is installed. `--ports M,...|all` (T59) runs the kit's port mode
(runtime/original_match/port/, as check.py takes it): those modules' Python routines in place of the original's;
`--variant M.NAME` one of a module's variants (a falsifier), its module added if not named. The record then carries
`ports`, `variant` and `port_calls` (records.py), a resumed --out must hold the same, and each match's line says the
ported routines' calls; a decision answered while a port's frame waits on a call of the original's code is printed
with the frames (port/guest.py). `--engine` comes with T78. One record per match (records.py): completion, score, ticks,
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
--stretch-limit (default 60 s, never more than --time-limit) bounds one stretch of the kit's run between two events (the
emulator's own watchdog, Match(timeout_s)): with every port installed on a slow machine, a knockout's quick result ran
one stretch over 60 s (2026-10-22, a cloud session, T63; issue #357). It changes no record of a match that completes.
--checkpoint DIR (#359) saves each running match there every CHECKPOINT_EVERY minute events (the kit's Match.save() and
this runner's own state: the events, decisions, strays, pauses, --count counters, the memory before the match for the
undeclared-write check, and the time used), so a run killed mid-match (a cloud container restarts) resumes inside the
match on the next run with the same command: the record is the one a straight run writes (cpu_s and wall_s add up both
parts). A checkpoint of another spec, image, kit, mask, --count or ports is not used; it is deleted once its match's
record is in --out. Not with --find-ranges.

Exit status: 0 when every selected match in --out is a completed match, 1 when one is not (an error, a stray
decision, no board), 2 for a refused command.

--find-ranges runs the selected matches with a write watch over all guest memory (about five times slower) and
writes, to a new file, every range written outside DS and the screen, the DS blocks written, and the ranges to
declare in records.RANGES (the finder of T57: the ranges are found once, not guessed)."""
import argparse
import hashlib
import json
import os
import pickle
import re
import sys
import time
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE))
import families  # noqa: E402
import fileopts  # noqa: E402
import records  # noqa: E402
import image_sources  # noqa: E402

DEFAULT_CACHE = ".cache/dl"
DISPLAY_PROFILE = HERE / "families/display/profile.json"
DEFAULT_TIME_LIMIT = 300.0
DEFAULT_STRETCH_LIMIT = 60.0    # the kit's watchdog per stretch between events, as before #357
CHECKPOINT_EVERY = 10    # minute events between two checkpoints of a match (#359): about 5 % of a match each
SEED_WORD = 0x7B62                                     # DS:7B62 the main RNG word (match.py SEED)
SCREEN_POINTERS = (0xA96A, 0xA96E, 0xA972)             # DS: the text page (B800:0) and the two text buffers
SCREEN_BYTES = 4000
COUNTRIES_PTR, FIXTURES_PTR, GAME_PTR = 0xA917, 0xA92B, 0xA923   # image.py


class Refused(Exception):
    """A command the script will not run (exit 2)."""


REFUSALS = (Refused, families.FamilyError, fileopts.PathError, image_sources.SourceError)    # what main() prints as "refused: ..." and the slot step skips


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
    data = fileopts.read_input(path, "--mask")
    try:
        mask = records.loads(data.decode("utf-8"))
        records.validate_mask(mask)
    except (OSError, ValueError) as e:
        raise Refused(f"--mask {path}: {e}")
    return mask


def read_display_profile():
    """The reviewed DS-only display profile; no unobserved or inferred fallback mask.

    The reference may be generated after this manifest is written, so its existence
    is checked by compare.py when used, not before the original reference run.
    """
    try:
        value = records.loads(fileopts.read_input(DISPLAY_PROFILE, "display profile").decode("utf-8"))
        if not isinstance(value, dict) or set(value) != {"schema", "mask", "reference", "proof"}:
            raise ValueError("expected schema, mask, reference and proof")
        if type(value["schema"]) is not int or value["schema"] != 1:
            raise ValueError("unknown display profile schema")
        records.validate_mask(value["mask"])
        if any(row[0] != "DS" for row in value["mask"]):
            raise ValueError("display profile requires a DS-only mask")
        for key in ("reference", "proof"):
            if not isinstance(value[key], str) or not value[key]:
                raise ValueError(f"display profile {key} must be a path")
        return value
    except (OSError, ValueError, fileopts.PathError) as exc:
        raise Refused(f"display profile {DISPLAY_PROFILE}: {exc}") from exc


def uses_display_projection(mask, selected=False):
    """Selected mode is separate from byte-mask content; even an empty profile projects its screen field."""
    if not selected:
        return False
    if [list(row) for row in mask] != read_display_profile()["mask"]:
        raise Refused("mask differs from the selected display profile")
    return True


def display_profile_selected(args):
    """Display ports select their profile; original references explicitly use its declared mask file.

    --mask is an existing option. Its declared path distinguishes an empty display
    profile from an ordinary raw --mask [] run, without a new record field or flag.
    """
    if "display" in {spec.split(".")[0] for spec in ports_of(args)}:
        return True
    return args.mask is not None and Path(args.mask).resolve() == DISPLAY_PROFILE.with_name("mask.json").resolve()


# ---- one match -------------------------------------------------------------------------------------------------
class TimeLimit(Exception):
    pass


class UndeclaredWrite(Exception):
    pass


def allowed_spans(machine, image_sha256=None):
    """The linear spans a match may change: DS, records.RANGES, and the screen's page and two text buffers."""
    base = machine.load * 16
    spans = [(machine.DS * 16, machine.DS * 16 + records.DS_SIZE)]
    spans += [(base + start, base + start + length) for start, length in records.ranges_for_source(image_sha256).values()]
    spans += [(machine.far(p), machine.far(p) + SCREEN_BYTES) for p in SCREEN_POINTERS]
    return spans


def undeclared_changes(before, after, spans):
    """[start, end) linear spans where `after` differs from `before` outside `spans` (a byte written back as it was
    is no change)."""
    a, b = bytearray(before), bytearray(after)
    for lo, hi in spans:
        a[lo:hi] = bytes(hi - lo)
        b[lo:hi] = bytes(hi - lo)
    if a == b:
        return []
    changed = [j for i in range(0, len(a), 4096) if a[i:i + 4096] != b[i:i + 4096]
               for j in range(i, min(i + 4096, len(a))) if a[j] != b[j]]
    return merge([[j, j + 1] for j in changed], gap=15)


def digest_memory(m, mask, image_sha256=None):
    """{'seed', 'ds', 'ranges'}: the main seed word, one digest per 1 KiB of DS, and of each of records.RANGES,
    after the post-match update, over the mask."""
    machine = m.m
    ds = records.apply_mask(machine.read(machine.DS * 16, records.DS_SIZE), "DS", 0, mask)
    out = {"seed": machine.rd(SEED_WORD), "ds": records.block_digests(ds), "ranges": {}}
    for name, (start, length) in records.ranges_for_source(image_sha256).items():
        buf = machine.read(machine.load * 16 + start, length)
        out["ranges"][name] = records.block_digests(records.apply_mask(buf, "P", start, mask))
    return out


def display_events_digest(events):
    """Display-profile event digest: only full_time.data.screen_sha256 is excluded.

    The ordinary producer continues using records.events_digest unchanged. This
    projection is for both new display-profile original references and candidates;
    every event, its metadata and every other data field remain in the digest.
    Input event objects are never mutated.
    """
    projected = []
    for kind, minute, score, data in events:
        if kind == "full_time" and "screen_sha256" in data:
            data = {key: value for key, value in data.items() if key != "screen_sha256"}
        projected.append((kind, minute, score, data))
    return records.events_digest(projected)


def play(m, spec, deadline, say=None, state=None, checkpoint=None):
    """Drive a Match with the spec's answer policy; (events, decisions, strays, stopped_at_board). say(line): told of
    each decision answered while a port's frame waits on a call of the original's code (T59). state: this loop's own
    state of a resumed match (a checkpoint's); checkpoint(state): called after each `minute` event is handled (#359)."""
    state = state or {"events": [], "decisions": [], "strays": [], "paused": [], "board": False}
    events, decisions, strays = state["events"], state["decisions"], state["strays"]
    paused, board = set(state["paused"]), state["board"]
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
            frames = m.port_frames() if getattr(m, "ports", None) else []
            if frames and say is not None:
                say(f"{spec.id}: decision {context} at minute {ev.minute} answered with port frames live: "
                    + "; ".join(frames))
            if context in policy.contexts:
                policy.answer(m, ev.data)
            else:
                strays.append(context)
                m.answer()
        if checkpoint is not None and ev.kind == "minute":
            checkpoint({"events": events, "decisions": decisions, "strays": strays, "paused": sorted(paused),
                        "board": board})
    return events, decisions, strays, board


class Checkpoints:
    """--checkpoint DIR (#359): one file per running match, <id>.ckpt, written whole (a temporary file renamed over it),
    read by the next run of the same match. Pickle holds the runner's own state (event data keeps its int keys, which
    JSON would turn into strings); the files are this runner's own, under a folder the command names."""
    MAGIC = b"E36C1"

    def __init__(self, folder, every=CHECKPOINT_EVERY):
        self.given, self.folder, self.every = str(folder), Path(folder), every       # the option as given ("" is not ".")

    def path(self, match_id):
        return self.folder / (re.sub(r"[^A-Za-z0-9._-]", "_", match_id) + ".ckpt")

    def save(self, match_id, key, match_blob, runner, before_z):
        fileopts.check_folder_output(self.given, "--checkpoint")      # the check prepare() applied before the slot
        self.folder.mkdir(parents=True, exist_ok=True)
        body = pickle.dumps({"key": key, "runner": runner, "match": match_blob, "before": before_z}, protocol=4)
        path = self.path(match_id)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            f.write(self.MAGIC + body)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def load(self, match_id, key):
        """The saved state of this match under this key, or None (no file, another key, or a file that does not read)."""
        path = self.path(match_id)
        try:
            data = path.read_bytes()
            if not data.startswith(self.MAGIC):
                return None
            saved = pickle.loads(data[len(self.MAGIC):])
        except (OSError, pickle.UnpicklingError, EOFError, ValueError):
            return None
        return saved if saved.get("key") == key else None

    def drop(self, match_id):
        for p in (self.path(match_id), self.path(match_id).with_suffix(".tmp")):
            try:
                p.unlink()
            except FileNotFoundError:
                pass


def port_specs(ports, variant):
    """The kit's port specs for --ports M,...|all and --variant M.NAME (T59, as check.py takes them), checked by the
    kit (an unknown module or variant is refused before any match), and (modules, variant) as a record names them."""
    names = [s for s in (ports or "").split(",") if s]
    if variant is not None:
        if not records.PORT_VARIANT.fullmatch(variant):
            raise Refused(f"--variant {variant!r}: MODULE.NAME")
        names = [s for s in names if s != variant.split(".")[0]] + [variant]
    if not names:
        return [], [], None
    from original_match import port
    try:
        specs = port.spec_names(port.load(names))
    except ValueError as e:
        raise Refused(f"--ports/--variant: {e}")
    modules = sorted(s.split(".")[0] for s in specs)
    return specs, modules, variant


def checkpoint_key(spec, mask, counts, ports, display_profile=False):
    """What a checkpoint must have been taken under to be resumed: the same match, image, kit, mask, --count and ports."""
    from original_match.match import VERSION
    key = {"spec_sha256": spec.sha256, "image_sha256": spec.image_sha256, "kit": VERSION,
           "mask": [list(s) for s in mask], "counts": list(counts), "ports": sorted(ports)}
    if display_profile:
        key["display_profile"] = 1
    return key


def run_match(image, spec, mask=(), counts=(), time_limit=DEFAULT_TIME_LIMIT, watch=None, check_writes=True,
              stretch_limit=DEFAULT_STRETCH_LIMIT,
              ports=(), say=None, checkpoints=None, display_profile=False):
    """The record of one match. Never raises for the match's own failure: that is the record's `error`.
    check_writes=False leaves the undeclared-write check out (the write watch that finds the ranges needs it so).
    ports: the kit's port specs (port_specs); the record then carries ports, variant and port_calls.
    checkpoints: a Checkpoints (#359): the match resumes from its checkpoint when there is one, and saves one every
    `every` minute events (not with a watch)."""
    from original_match import Match, Fixture
    from original_match.match import VERSION, MatchError
    try:
        image_sources.validate_image(image, spec.image)
    except image_sources.SourceError as e:
        raise Refused(str(e)) from e
    cpu0, wall0 = time.process_time(), time.time()
    cpu_before = wall_before = 0.0          # the time a resumed match had used before its checkpoint
    rec = {"id": spec.id, "family": spec.family, "spec_sha256": spec.sha256, "image_sha256": spec.image_sha256,
           "kit": VERSION, "mask": [list(s) for s in mask], "error": None, "stopped_at_board": False, "strays": [],
           "cpu_s": 0.0, "wall_s": 0.0, "score": None, "ticks": None, "draws": None, "board": None,
           "templates": None, "result_sha256": None, "events": None, "decisions": None, "after": None,
           "counts": {}}
    if ports:
        variants = [s for s in ports if "." in s]
        rec.update(ports=sorted(s.split(".")[0] for s in ports), variant=variants[0] if variants else None,
                   port_calls={})
    seen = {a: 0 for a in counts}
    m = None
    if watch is not None:
        checkpoints = None
    key = checkpoint_key(spec, mask, counts, ports, display_profile) if checkpoints is not None else None
    saved = checkpoints.load(spec.id, key) if checkpoints is not None else None
    try:
        if saved is not None:
            m = Match.load(saved["match"])
            if sorted(m.ports.names if m.ports else []) != sorted(ports):
                raise MatchError(f"the checkpoint's ports {m.ports.names if m.ports else []} are not {sorted(ports)}")
            m.timeout_s = min(stretch_limit, time_limit)
            runner = saved["runner"]
            seen.update(runner["seen"])
            cpu_before, wall_before = runner["cpu_s"], runner["wall_s"]
            if say is not None:
                say(f"{spec.id}: resumed from its checkpoint after {runner['minutes']} minute events "
                    f"({wall_before:.0f} s of the match)")
        else:
            players = countries = None
            if spec.edits:
                players, countries = families.apply_edits(image.players(), image.countries(), spec.edits)
            first, second, index, kind = spec.fixture
            m = Match(image, Fixture(first, second, index=index, kind=kind), managed=spec.managed, seed=spec.seed,
                      record_draws=True, delay_byte=spec.delay_byte, substitutions=spec.substitutions, players=players,
                      countries=countries, timeout_s=min(stretch_limit, time_limit), ports=list(ports) or None,
                      **({"set_piece": True} if "set_piece" in spec.policy.contexts else {}))
        if counts:
            from unicorn import UC_HOOK_CODE
        for address in counts:
            # A raw code hook registered after the kit's own: when a kit hook at the address stops the run, Unicorn
            # leaves the later hooks to the resumed pass, so each execution is counted once (the kit's `at` handlers
            # run in order and the stopping one ends the pass, which undercounted the tick routine: 3265 of 4146).
            def count(uc, addr, size, data, address=address):
                seen[address] += 1
            m.m.uc.hook_add(UC_HOOK_CODE, count, begin=m.m.lin(address), end=m.m.lin(address))
        if watch is not None:
            watch(m)
        if saved is not None:
            before_z = saved["before"]
            before = zlib.decompress(before_z)
            minutes, state = saved["runner"]["minutes"], saved["runner"]["play"]
        else:
            before = m.m.read(0, 0x110000)
            before_z = zlib.compress(before, 6) if checkpoints is not None else None
            minutes, state = 0, None
        hook = None
        if checkpoints is not None:
            def hook(play_state):
                nonlocal minutes
                minutes += 1
                if minutes % checkpoints.every:
                    return
                try:
                    blob = m.save()
                except MatchError:          # a port's frame is live, or the kit drives a screen: the next minute
                    return
                checkpoints.save(spec.id, key, blob, {
                    "minutes": minutes, "play": play_state, "seen": dict(seen),
                    "cpu_s": cpu_before + time.process_time() - cpu0, "wall_s": wall_before + time.time() - wall0},
                    before_z)
        events, decisions, strays, board = play(m, spec, time.time() + time_limit - wall_before, say, state, hook)
        result = m.result()
        outside = undeclared_changes(before, m.m.read(0, 0x110000), allowed_spans(m.m,spec.image_sha256)) if check_writes else []
        if outside:
            raise UndeclaredWrite(f"{sum(b - a for a, b in outside)} bytes changed outside the declared ranges, first at "
                                  f"P+0x{outside[0][0] - m.m.load * 16:X}: rerun --find-ranges")
        draws = m.st["draws"]
        rec["strays"], rec["stopped_at_board"] = strays, board
        n_events, events_sha = display_events_digest(events) if uses_display_projection(mask, display_profile) else records.events_digest(events)
        b = result["board"]
        rec.update(
            score=list(result["score"]), ticks=result["ticks"],
            draws={"count": len(draws), "digest": records.draws_digest(draws), "per_minute": records.draws_per_minute(draws)},
            board={"statistics": {k: list(v) for k, v in b["statistics"].items()}, "bars": [list(r) for r in b["bars"]],
                   "man_of_the_match": b["man_of_the_match"], "final_score": list(b["final_score"]), "seed": b["seed"],
                   "screen_sha256": b["screen_sha256"]},
            templates=records.template_counts(result["commentary"]), result_sha256=records.result_digest(result),
            events={"count": n_events, "sha256": events_sha}, decisions=decisions, after=digest_memory(m, mask,spec.image_sha256))
    except Exception as e:      # the record says what failed; a missing record would be a silent gap
        rec.update(error=clean_error(e), score=None, ticks=None, draws=None, board=None, templates=None,
                   result_sha256=None, events=None, decisions=None, after=None)
    rec["counts"] = dict(seen)
    if ports:                   # the calls made, also by a match that stopped (an error record)
        rec["port_calls"] = dict(m.ports.calls) if m is not None and m.ports else {}
        if not rec["port_calls"]:
            from original_match import port
            rec["port_calls"] = {a: 0 for reg, _ in port.load(ports) for a in reg.entries}
    rec["cpu_s"] = round(cpu_before + time.process_time() - cpu0, 3)
    rec["wall_s"] = round(wall_before + time.time() - wall0, 3)
    records.validate(rec)       # a record the grammar refuses is a bug here, not evidence
    return rec


# ---- the family run --------------------------------------------------------------------------------------------
_worker = {}


def _init_worker(cache, mask, counts, time_limit, ports=(), stretch_limit=DEFAULT_STRETCH_LIMIT, checkpoint=None, display_profile=False):
    """A worker finds the declared matches itself (families.discover), so no policy object crosses a process."""
    from original_match import Image
    from original_match.assets import reference_image
    _worker.update(image=image_sources.load(image_sources.DEFAULT,cache), images={}, cache=cache, mask=mask, counts=counts, time_limit=time_limit,
                   ports=list(ports), stretch_limit=stretch_limit, display_profile=display_profile,
                   checkpoints=Checkpoints(checkpoint) if checkpoint else None, specs={m.id: m for fam in families.discover().values() for m in fam.matches})


def _run_in_worker(match_id):
    lines = []
    spec = _worker["specs"][match_id]
    if spec.image == image_sources.DEFAULT:
        image = _worker["image"]
    else:
        if spec.image not in _worker["images"]:
            _worker["images"][spec.image] = image_sources.load(spec.image,_worker["cache"])
        image = _worker["images"][spec.image]
    rec = run_match(image, spec, _worker["mask"], _worker["counts"],
                    _worker["time_limit"], ports=_worker["ports"], say=lines.append,
                    stretch_limit=_worker["stretch_limit"], checkpoints=_worker.get("checkpoints"),
                    display_profile=_worker.get("display_profile",False))
    return rec, lines


def existing_records(out, selected, mask, ports=()):
    """The valid records already in --out, {id: record}. Refuses a file that is not this run's: an invalid line, an
    id twice or not selected, a spec, mask, image or ports (with their variant) that is not the declared one."""
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
        if r["spec_sha256"] != expected[r["id"]].sha256 or r["image_sha256"] != expected[r["id"]].image_sha256:
            raise Refused(f"{out}: {r['id']} was run from another declaration or image than the one declared now")
        if r["mask"] != [list(s) for s in mask]:
            raise Refused(f"{out}: {r['id']} was taken over another mask than --mask")
        variants = [s for s in ports if "." in s]
        want = (sorted(s.split(".")[0] for s in ports), variants[0] if variants else None) if ports else (None, None)
        if (r.get("ports"), r.get("variant")) != want:
            raise Refused(f"{out}: {r['id']} was run with other ports ({r.get('ports')}, variant {r.get('variant')}) "
                          "than --ports and --variant")
        done[r["id"]] = r
    return done


def append(out, record):
    """One line, appended and synced: a record is never rewritten."""
    fileopts.check_log_output(out, "--out")
    fd = os.open(out, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, (records.dumps(record) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def run_family(selected, out, workers=1, max_new=None, cache=DEFAULT_CACHE, mask=(), counts=(),
               time_limit=DEFAULT_TIME_LIMIT, say=print, run_one=None, ports=(), stretch_limit=DEFAULT_STRETCH_LIMIT,
               checkpoint=None, display_profile=False):
    """Run the selected matches not yet in `out`; returns the records of every selected match now in `out`.
    run_one(spec) -> record replaces the kit for a test (one process only). ports: the kit's port specs (port_specs).
    checkpoint: the --checkpoint folder (#359); a match's checkpoint is dropped once its record is in `out`."""
    checkpoints = Checkpoints(checkpoint) if checkpoint else None
    fileopts.check_log_output(out, "--out")     # the check prepare() applied before the slot
    done = existing_records(out, selected, mask, ports)
    todo = [s for s in selected if s.id not in done]
    if max_new is not None:
        todo = todo[:max_new]
    say(f"{len(selected)} matches selected, {len(done)} already in {out}, {len(todo)} to run")
    if checkpoints is not None:
        for match_id in done:                 # killed after the record was appended, before its checkpoint went
            checkpoints.drop(match_id)
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    def took(rec):
        append(out, rec)
        done[rec["id"]] = rec
        if checkpoints is not None:
            checkpoints.drop(rec["id"])
        state = "completed" if records.is_completed(rec) else f"NOT COMPLETED ({rec['error'] or rec['strays'] or 'no board'})"
        extra = "".join(f"; {a} executed {n}" for a, n in rec.get("counts", {}).items())
        extra += "".join(f"; port {a} called {n}" for a, n in sorted(rec.get("port_calls", {}).items()))
        say(f"{rec['id']}: {state}; score {rec['score']} ticks {rec['ticks']} cpu {rec['cpu_s']} s{extra}")

    if run_one is not None:
        for spec in todo:
            took(run_one(spec))
    elif workers == 1:
        from original_match import Image
        from original_match.assets import reference_image
        images = {}
        for spec in todo:
            if spec.image not in images:
                images[spec.image] = image_sources.load(spec.image,cache)
            image = images[spec.image]
            took(run_match(image, spec, mask, counts, time_limit, ports=ports, say=say, stretch_limit=stretch_limit,
                           checkpoints=checkpoints, display_profile=display_profile))
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                                 initargs=(cache, mask, counts, time_limit, list(ports), stretch_limit, checkpoint, display_profile)) as pool:
            for rec, lines in pool.map(_run_in_worker, [s.id for s in todo]):
                for line in lines:
                    say(line)
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


def write_ranges(path, report):
    """The --find-ranges output, created exclusively (the same check prepare() applies before the slot)."""
    with fileopts.create_new_output(path, "--find-ranges") as f:
        json.dump(report, f, indent=1)


def find_ranges(image, selected, path, time_limit=3600.0, say=print):
    """Play the selected matches under a write watch on all guest memory and write the report to the new file `path`."""
    from unicorn import UC_HOOK_MEM_WRITE
    if not selected or len({s.image for s in selected}) != 1:
        raise Refused("--find-ranges requires matches from exactly one registered image")
    image_sources.validate_image(image,selected[0].image)
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
        rec = run_match(image, spec, time_limit=time_limit, watch=watch, check_writes=False)
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
    report = {"image_sha256": selected[0].image_sha256, "matches": ids, "load_segment": info["load"],
              "ds_program_relative": info["ds"], "screen_program_relative": info["screen"],
              "records_program_relative": info["records"],
              "written_outside_ds_and_screen": outside, "written_inside_records": inside_records,
              "ds_blocks_written": ds_blocks, "ds_blocks_of_the_screen": screen_blocks,
              "ranges": {"records": [rec_lo, rec_hi - rec_lo], **{f"w{a:05x}": [a, -(-(b - a) // 16) * 16]
                                                                 for a, b in other}}}
    write_ranges(path, report)
    say(f"ranges found: {report['ranges']}")
    return report


def parser():
    """The command line's one definition: main() parses with it, and so does the slot weight (heavy_slot.parsed)."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--family", required=True)
    ap.add_argument("--out")
    ap.add_argument("--find-ranges")
    ap.add_argument("--max", type=int)
    ap.add_argument("--workers", type=int, choices=(1, 2), default=1)
    ap.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT)
    ap.add_argument("--stretch-limit", type=float, default=DEFAULT_STRETCH_LIMIT)
    ap.add_argument("--checkpoint", help="a folder for each running match's checkpoint, to resume inside it (#359)")
    ap.add_argument("--count")
    ap.add_argument("--mask")
    ap.add_argument("--only")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--ports", help="port modules (runtime/original_match/port/) in place of the original's routines: "
                                    "M,... or all (T59)")
    ap.add_argument("--variant", help="MODULE.NAME: one of a port module's variants (a falsifier; T59)")
    return ap


def ports_of(a):
    """The kit's port specs of a parsed command line (T59: --ports, --variant); Refused when main() will refuse them."""
    ports = port_specs(a.ports, a.variant)[0]
    if a.find_ranges and ports:
        raise Refused("--find-ranges runs the unhooked kit: no --ports or --variant")
    return ports


def prepare(a):
    """(selected, mask, counts) for a parsed command line; Refused or families.FamilyError when main() will refuse it.
    The one place a parsed command line is refused: main() calls it, and so does the slot step (_slot_weight), so a refused
    line is answered at once and never queues for a slot (#328); ports_of(a) is the other half, called beside it by both. Run-time refusals (a match under the watch that does not
    complete) are not here: they need the run."""
    if (a.out is None) == (a.find_ranges is None):
        raise Refused("give --out (a family run) or --find-ranges (the write watch), not both and not neither")
    if a.max is not None and a.max < 1:
        raise Refused("--max is a number of matches, 1 or more")
    if not 0 < a.time_limit <= 36000:
        raise Refused("--time-limit is a number of seconds, up to 36000")
    if not 0 < a.stretch_limit <= 36000:
        raise Refused("--stretch-limit is a number of seconds, up to 36000")
    if a.checkpoint is not None:
        if a.find_ranges is not None:
            raise Refused("--checkpoint is for a family run (--out), not --find-ranges")
        fileopts.check_folder_output(a.checkpoint, "--checkpoint")
    # each path option is checked by the operation the run applies to it (runtime/fileopts.py), here and not in main(): the slot
    # step runs prepare() too (#328)
    if a.find_ranges is not None:
        fileopts.check_new_output(a.find_ranges, "--find-ranges")
    if a.out is not None:
        fileopts.check_log_output(a.out, "--out")
    from original_match.assets import check_cache
    check_cache(a.cache)
    selected = [m for fam in families.select(a.family, families.discover()) for m in fam.matches]
    if a.only is not None:
        ids = a.only.split(",")
        unknown = [i for i in ids if i not in {m.id for m in selected}]
        if unknown or len(set(ids)) != len(ids):
            raise Refused(f"--only {a.only!r}: distinct ids among the selected matches (unknown: {unknown})")
        selected = [m for m in selected if m.id in ids]
    mask = parse_mask(a.mask)
    if display_profile_selected(a):
        profile = read_display_profile()
        if a.mask is not None and mask != profile["mask"]:
            raise Refused("--mask differs from the declared display profile")
        mask = profile["mask"]
    return selected, mask, parse_count(a.count)


def processes(a, selected, mask, ports=()):
    """How many match processes this command runs at once, which is what the slot weight is. The write watch runs its
    matches one after another in this process, whatever --workers says. A family run with --workers 2 runs the matches
    not yet in --out (up to --max) in a pool of 2 worker processes, so at most min(workers, matches to run) matches run at
    once: Python 3.14 (forkserver) starts a worker only for a match to run, and 3.12 (fork) starts both, one idle, which
    costs no CPU (both checked on this machine). At least 1: the kit is loaded. Other modes: none (checked: the options
    --count, --mask, --only, --cache, --time-limit, --stretch-limit, --checkpoint, --ports, --variant change what a match records or which ones, never how
    many run at once; a ported match is one process like any other: T59)."""
    if a.find_ranges:
        return 1
    todo = len([s for s in selected if s.id not in existing_records(a.out, selected, mask, ports)])
    if a.max is not None:
        todo = min(todo, a.max)
    return max(1, min(a.workers, todo))


def main(argv=None):
    a = parser().parse_args(argv)
    try:
        selected, mask, counts = prepare(a)
        ports = ports_of(a)
        if ports:
            print(f"ports: {', '.join(ports)}", flush=True)
        if a.find_ranges:
            from original_match import Image
            from original_match.assets import reference_image
            find_selected=selected[:a.max]
            if not find_selected or len({s.image for s in find_selected}) != 1:
                raise Refused("--find-ranges requires matches from exactly one registered image")
            find_ranges(image_sources.load(find_selected[0].image,a.cache), find_selected, a.find_ranges)
            return 0
        recs = run_family(selected, a.out, a.workers, a.max, a.cache, mask, counts, a.time_limit, ports=ports,
                          stretch_limit=a.stretch_limit, checkpoint=a.checkpoint, display_profile=display_profile_selected(a))
    except REFUSALS as e:
        print(f"refused: {e}")
        return 2
    bad = [r["id"] for r in recs if not records.is_completed(r)]
    print(f"{len(recs)} of {len(selected)} matches in {a.out}, {len(bad)} not completed" + (f": {bad}" if bad else ""))
    return 1 if bad else 0


def _slot_weight(argv):
    """The slots this command line needs: the match processes it will start (processes()), derived from main()'s own
    parser and preparation, or None when main() would refuse the line (no slot; main() then says why)."""
    import heavy_slot
    ns = heavy_slot.parsed(parser(), argv)
    if ns is None:
        return None
    try:
        selected, mask, _ = prepare(ns)
        return processes(ns, selected, mask, ports_of(ns))
    except REFUSALS:
        return None


if __name__ == "__main__":
    import heavy_slot
    # a heavy job (#318): one slot per match process, so --workers 2 holds two of the machine's slots; a command line
    # main() refuses holds none (it prints argparse's message at once)
    _w = _slot_weight(sys.argv[1:])
    if _w is not None:
        heavy_slot.take("family", weight=_w)
    sys.exit(main())
