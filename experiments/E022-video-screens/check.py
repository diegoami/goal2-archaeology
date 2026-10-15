#!/usr/bin/env python3
"""T39c: decode the sitting video's frame at each snapshot's request window and compare with the snapshot.

    python3 experiments/E022-video-screens/check.py <session folder> [--out DIR]

For each snapshot in index.jsonl the frame is chosen by the request window alone: the frame that is on
screen at `request_s` (frame n covers [n/fps, (n+1)/fps) video seconds, the video's clock taken as the
session's `elapsed_s` clock: the recorder starts ffmpeg with the sitting; assumption, not measured). No
frame is ever searched for by how well it matches (that would hide timing errors). The frame is decoded
on the window's grid (1280x800 = the 640x400 screen at 2x, offset 0, as recorder.video_cmd films it), and
compared cell by cell, by appearance (tools/screens/video.py), with the snapshot's own screen.

Writes, under --out (default experiments/E022-video-screens/out/): results.json (one row per snapshot),
keys.json (press gaps against the frame period), worst-*.png (the frame and the snapshot's render of the
worst screens), env.txt (the ffmpeg version). Prints the counts and exits 0."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "screens"))
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import render  # noqa: E402
import savestate  # noqa: E402
import video  # noqa: E402

FPS = 10
W, H, SCALE = 1280, 800, 2


def ffmpeg_frames(path, wanted):
    """{frame index: RGB bytes} of the wanted frame numbers, decoded by ffmpeg in one pass."""
    expr = "+".join(f"eq(n\\,{n})" for n in sorted(wanted))
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-vf", f"select='{expr}'",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    out = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout
    size = W * H * 3
    if len(out) != size * len(wanted):
        raise SystemExit(f"ffmpeg gave {len(out) // size} frames for {len(wanted)} wanted (video ends early?)")
    return {n: out[i * size:(i + 1) * size] for i, n in enumerate(sorted(wanted))}


def frame_count(path):
    out = subprocess.run(["ffmpeg", "-nostdin", "-i", str(path), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    last = [ln for ln in out.splitlines() if "frame=" in ln][-1]
    return int(last.split("frame=")[1].split()[0])


def video_start_bound(session, index):
    """(lo, hi) seconds: the video's start minus the origin of the snapshots' `elapsed_s` clock, or None.
    The video start is the session.log line `[HH:MM:SS] video started` (whole seconds, so 1 s wide); the origin
    is the first snapshot's `utc` minus its `elapsed_s`. meta.json holds no video start time. Positive
    means the video starts later than the clock: a frame time n/fps then lies that much after elapsed_s."""
    import re
    from datetime import datetime
    first = index[0]
    origin = datetime.fromisoformat(first["utc"].replace("Z", "+00:00")).timestamp() - first["elapsed_s"]
    for line in (session / "session.log").read_text(errors="replace").splitlines():
        m = re.match(r"\[(\d\d):(\d\d):(\d\d)\] video started", line)
        if m:
            h, mi, sec = map(int, m.groups())
            day = datetime.fromtimestamp(origin, tz=__import__("datetime").timezone.utc)
            whole = day.replace(hour=h, minute=mi, second=sec, microsecond=0).timestamp()
            return round(whole - origin, 3), round(whole - origin + 1, 3)
    return None


def appearance_rows(chars, attrs, glyphs):
    return [video.cell_appearance(c, a, glyphs) for c, a in zip(chars, attrs)]


def bright_pixels(rgb):
    """How many pixels have a channel above 64: a cursor or text; black is 0."""
    return sum(1 for i in range(0, len(rgb), 3) if rgb[i] > 64 or rgb[i + 1] > 64 or rgb[i + 2] > 64)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("session", type=Path)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    a = ap.parse_args(argv)
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((a.session / "meta.json").read_text())
    index = [json.loads(ln) for ln in (a.session / "index.jsonl").read_text().splitlines() if ln.strip()]
    vid = a.session / "video.mkv"
    ver = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.splitlines()[0]
    (out / "env.txt").write_text(f"{ver}\nvideo.mkv sha256 {meta['video']['sha256']}\n"
                                 f"video {meta['video']['bytes']} bytes, {meta['video']['seconds']} s, "
                                 f"geometry {meta['video']['geometry']}\n")
    nframes = frame_count(vid)
    want = {min(int(r["request_s"] * FPS), nframes - 1) for r in index}
    frames = ffmpeg_frames(vid, want)
    bright = {n: bright_pixels(f) for n, f in frames.items()}
    rows, worst = [], []
    cells_exact = ink_exact = ink_total = screens_exact = 0
    for r in index:
        n = min(int(r["request_s"] * FPS), nframes - 1)
        ss = savestate.Savestate(a.session / r["file"])
        glyphs, _ = render.font_for(ss)
        scr = ss.screen()
        chars, attrs, dists = video.decode_frame(frames[n], W, glyphs, 80, 25, SCALE)
        truth = appearance_rows(scr.chars, scr.attrs, glyphs)
        got = appearance_rows(chars, attrs, glyphs)
        same = [t == g for t, g in zip(truth, got)]
        ink = [len(set(t)) > 1 for t in truth]
        ok = sum(same)
        cells_exact += ok
        ink_total += sum(ink)
        ink_exact += sum(1 for s, i in zip(same, ink) if s and i)
        screens_exact += ok == 2000
        row = {"seq": r["seq"], "request_s": r["request_s"], "sent_s": r["sent_s"], "frame": n,
               "frame_time_s": n / FPS, "bright_pixels_in_frame": bright[n], "cells_exact": ok,
               "ink_cells": sum(ink), "ink_cells_exact": sum(1 for s, i in zip(same, ink) if s and i),
               "max_dist": max(dists), "cells_dist_gt0": sum(1 for d in dists if d)}
        rows.append(row)
        worst.append((ok, r["seq"], n, ss))
    (out / "results.json").write_text(json.dumps(rows, indent=1) + "\n")
    # the worst cases: fewest cells exact; their frame and the snapshot's render, as PNGs
    worst.sort(key=lambda w: (w[0], w[1]))
    for ok, seq, n, ss in worst[:3]:
        (out / f"worst-seq{seq:04d}-frame{n}.png").write_bytes(
            render.png([frames[n][y * W * 3:(y + 1) * W * 3] for y in range(H)], W, H))
        (out / f"worst-seq{seq:04d}-snapshot.png").write_bytes(render.render_savestate(ss)[0])
    # frame rate against the presses
    t0 = meta["monotonic_start_s"]
    presses = [json.loads(ln) for ln in (a.session / "keys.jsonl").read_text().splitlines() if ln.strip()]
    ts = [p["monotonic_s"] - t0 for p in presses if p["event"] == "press"]
    gaps = [b - x for x, b in zip(ts, ts[1:])]
    no_frame = sum(1 for x, b in zip(ts, ts[1:]) if int(b * FPS) == int(x * FPS))
    keys = {"presses": len(ts), "frame_period_s": 1 / FPS, "gaps_lt_0.1s": sum(1 for g in gaps if g < 0.1),
            "gaps_lt_0.2s": sum(1 for g in gaps if g < 0.2), "gaps_lt_0.5s": sum(1 for g in gaps if g < 0.5),
            "min_gap_s": round(min(gaps), 3), "median_gap_s": round(sorted(gaps)[len(gaps) // 2], 3),
            "presses_with_no_frame_boundary_before_the_next_press": no_frame}
    (out / "keys.json").write_text(json.dumps(keys, indent=1) + "\n")
    inked = sum(1 for b in bright.values() if b)
    print(f"frames {nframes}; distinct frames used {len(want)}; frames with any bright pixel {inked}; "
          f"most bright pixels in one frame {max(bright.values())}")
    bound = video_start_bound(a.session, index)
    print("ASSUMPTION (unproven): video time = the snapshots' elapsed_s clock; the recorder records no video start "
          "time, so a real recording may be decoded from a frame offset in time.")
    print(f"video start minus the elapsed_s clock's origin, from session.log: {bound} s (whole-second log line)")
    print(f"screens exact: {screens_exact}/{len(index)}")
    print(f"cells exact: {cells_exact}/{len(index) * 2000}")
    print(f"cells with ink in the snapshot, exact: {ink_exact}/{ink_total}")
    print(f"presses {keys['presses']}: gaps under 0.1 s {keys['gaps_lt_0.1s']}, under 0.2 s {keys['gaps_lt_0.2s']}, "
          f"no frame between a press and the next {no_frame}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
