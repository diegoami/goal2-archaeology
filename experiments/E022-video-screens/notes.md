# E022 Screens read back from a sitting's video (T39c, #139)

**Verdict: no-go for this sitting's video.** The video holds no game pixels, so no screen can be read
from it. The decoder itself works (below), so the question stays open for a recording that does film the
game.

## Numbers (`python3 experiments/E022-video-screens/check.py <session>`, sitting 20261011-161003)

```
frames 6389; distinct frames used 224; frames with any bright pixel 181; most bright pixels in one frame 61
screens exact: 0/224
cells exact: 114553/448000
cells with ink in the snapshot, exact: 0/331656
presses 397: gaps under 0.1 s 87, under 0.2 s 199, no frame between a press and the next 65
```

- `cells exact: 114553/448000` is not decoding: those are the cells that are blank on a black screen in
  the snapshot too, which a black frame "reads" as blank. Of the 331,656 cells where the snapshot has ink
  (text, box drawing, a coloured background), **0** match.
- The frames: ffmpeg 8.0.1-3ubuntu2 decodes `video.mkv` (h264 High, yuv420p, 1280x800, 10 fps,
  6389 frames, 639.1 s, sha256 ce0ce9ee...). The mean luma of every frame is at most 16.0131, which is black in
  limited range, and the brightest frame has 61 pixels above 64 in any channel: the X cursor (frames at
  130 s and 300 s, looked at as PNG). The first 125 s (frames 0-1250) are pure black. The same holds for the
  three other videos in the owner's `sessions/` folder (20261011-211051, 20261011-211125: mean luma at most 16.0132;
  20261011-160938 is 581 bytes and was not decoded).
- Grid: nothing to find. The window's 1280x800 is exactly the 640x400 screen at 2x, and `video.find_grid`
  returns `None` for a frame without ink (pinned by a test). On the synthetic crops the grid is found within
  one pixel and decodes exactly.
- Worst cases (all 224 are equally absent; the three with the fewest cells exact, by snapshot): seq 12, 14,
  15 in `out/worst-seq*-frame*.png` (the frame: black with the cursor) beside `out/worst-seq*-snapshot.png`
  (T39a's render of the snapshot). Per snapshot rows: `out/results.json`.

## Why the video is black (not investigated further)

`runtime/human/recorder.py` `video_cmd` grabs the *outer* display (`outer_display` in `meta.json`: `:0`, WSLg)
at the window's position, size 1280x800, while the game runs in Xephyr on `:600`. The grab returns the
root window (black, with the cursor) and not the Xephyr window's contents. The cause was not tested here (the
task owns no recorder change); two untested readings are that x11grab on WSLg's XWayland does not see
Xephyr's surface, or that the window's contents are drawn outside the grabbed region. Test: grab `:600`
itself (`-i :600+0,0`) in a short sitting and rerun `check.py`.

## Frame rate against the keys

The video is 10 fps (one frame per 0.1 s). Of 397 presses (396 gaps), 87 follow the previous press by less than 0.1 s and 199 by less
than 0.2 s (median gap 0.199 s; the smallest 0.0 s: two presses at one instant), and for 65 presses no frame
boundary falls between the press and the next press, so a 10 fps video cannot show the screen after those
presses even when it films the game; the other 331 of the 396 gaps have at least one. With the frame's own delay added
(DOSBox-X draws after the key) fewer would. A savestate-free per-key screen needs more than 10 fps in
fast scrolling; this is separate from the black frames.

## Method and limits

- Frame choice: the frame on screen at the snapshot's `request_s` (frame n covers n/10..(n+1)/10 s),
  taking the video's clock as the session's `elapsed_s` (not measured: every frame is black, so no frame
  choice could change a result). No frame was searched for by its match.
- Decoder (`tools/screens/video.py`): samples the centre of each font pixel, maps it to the nearest of the 16 VGA
  colours, finds the glyph with an exact bitmap or the nearest by differing pixels (`dist`), compares cells
  by *appearance* (blank chars 0x00, 0x20, 0xFF are one appearance; a blank cell's foreground is invisible).
- `tests/test_screens_video.py` pins the decoder on three committed crops, `crops/crop-{a,b,c}.png`
  (25x3 cells at 2x). **They are synthetic stand-ins, not video frames**: no frame holds text. Each is a
  piece of a snapshot's screen (snapshots 101 and 150) rendered by T39a's renderer with the savestate's font and
  up to +-12 noise per channel (`make_crops.py`). They prove the decoder reads text, box drawing and foreground
  colour back through pixel noise (exact, dist 0), not that h264 frames decode: that line of the Done-when
  (crops of video frames) is unmet.
- Outputs are under `out/` (`env.txt` has the ffmpeg version and the video's hash). The video is not
  committed (rule 18).
