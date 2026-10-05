# F006 Neither `cycles`, the host's speed nor the start-up delay calibration changes a match. F001's sub-second first half at `max` was a measurement artefact of its probe.

- **Status**: proposed
- **Question**: Do `cycles`, the host speed or wall-clock time change a match, and why are the halves so unequal at `max`? (G5 Q003, `docs/backlog.md`; T12)
- **Tests claims**: none (no spec row exists yet). It bears on G-M4 and G-M5: whether samples of the original may run at `max`. It also bears on E004 and F005, whose matches ran at `cycles=30000`.
- **Experiment and runs**: E005; E005-r0001 … E005-r0055 (run number 33 reserved and unused, E005 README amendment 2):
  - calibration: E005-r0001 … r0009;
  - matches: E005-r0010 … r0055.
  - F001's probe re-run: `experiments/E005-q003-cycles/measurements/match-speed.json` (once at `max`, its own keys) and `match-speed-2.json` (at `max`, 60000 and 30000, with one read before its first key; README amendment 5).
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Max intervention**: I3 in the fresh launches: the DOS date and time are set in the autoexec before GOAL runs and verified by DOS's read-back. The restores do not set the clock.
  - I2: a savestate is written at every read, and loaded once in each restore.
  - I1: memory is read from those savestates.
- **Tier reached**: V2
- **Confidence**: unreviewed (status `proposed`). Each claim of the Answer names its routes. A claim with both a behavioural and a static row counts as corroborated once reviewed; a claim with one route stays at that route.

## Answer

No. Under E005's key conditions (below), the same seeded start state gave the same match at `cycles` 5000, 30000 and `max`. Of 41 runs compared with their 30000 reference, 40 are identical and none differs; for one, E005-r0035, identity is undetermined, because its reader never read one commentary line. That held both for a restored state carrying a delay calibration made at 30000 and for a fresh launch that calibrated anew at each setting. `cycles` and the host change only how long a match takes.

F001's halves at `max` and 60000 (first half under 1 s, second 6.5 … 9.7 s) were not the game. Its probe started its clock after the first half had already been played.

| Claim | Behavioural (`runs/E005/`, `summarise.py`) | Static (`static/goal-exe/code/`) |
| --- | --- | --- |
| The same start state gives the same match at 5000, 30000 and `max`, restored or launched afresh | 45 match records. The first restore at 30000 of each state and arm is the reference (E005-r0010, r0012, r0022, r0023). Of the 41 others, 40 are identical to their reference (score, events, every commentary line, `DS:7B62` at full time), none differs, and one, E005-r0035, is undetermined (next row) (`summarise.py`: `identical: 40; identity undetermined: 1; differ: 0; references: 4`). The runs: 30000 restores E005-r0010, r0012, r0014, r0015, r0018, r0020, r0022, r0023, r0026 … r0029; 30000 fresh E005-r0011, r0013, r0016, r0017; 5000 fresh E005-r0019, r0021, r0024, r0025; 5000 restores E005-r0030 … r0032, r0034 … r0039; `max` restores E005-r0040 … r0051; `max` fresh E005-r0052 … r0055. Matches: e004-1001 quick 0-0 `0xe081`, watched 0-2 `0x1d0e`; e004-1337 quick 1-0 `0x5109`, watched 2-3 `0xa621` (E004's matches, F005) | No time source reachable from a match writes game state (rows below). The game's RNG `DS:7B62` takes no input but the DOS hour:minute at `Randomize` (`seg_23E4_02.asm:805`–`808`: `11D7 mov ah, 0x2c` … `11DB mov word ptr [0x7b62], cx`), which no match routine reaches |
| E005-r0035's identity is undetermined | Score, events, `DS:7B62` and `DS:80EE` at full time (0x005e) equal E005-r0023's, and so does every commentary line its reader read. One line was never read: occurrence 412 of the match, record 12, flagged `match read 425: record 12 is the end marker 0xFF`. The reference has `Vilfort is OFFSIDE` there. What E005-r0035 had there is unknown. The flag shows only that the reader did not see the record, and no read's screen shows it: read 425 shows up to `deflected by Eriksson` (occurrence 411), read 426 starts at `*** FREE KICK ***` (occurrence 413). The other two watched restores at 5000 of that state, E005-r0037 and r0039, are identical line for line | — (the reader's defect: `runtime/driver/commentary.py` `Tracker.add` skips a record still 0xFF and moves past it; issue #38; README amendments 3 and 6) |
| The delay count `DS:A9FF` is measured once, at start-up, and follows the speed the emulator runs at then | Fresh launches at the title screen: 5000 → 0x2c5 (709) ×3, 30000 → 0x10b3 (4275) ×3 (E005-r0001 … r0006, ratio 6.03); `max` → 0x2d9 … 0x32c (E005-r0007 … r0009). Fresh launches of matches at `max`: 0x1022 … 0x1ef0 (E005-r0052 … r0055). Every restore keeps the state's 0x10b3, at every setting (E005-r0010 … r0051), and so does every read during a match | `1DA7` has one caller, `214B:206A` (`seg_214B_04.asm:416` `20CA call 0x1da7`), called only from the entry (`seg_0000_01.asm:11` `000A call far 214B:206A`). `1DA7` counts loop passes over one BIOS tick (`seg_214B_04.asm:44`–`62`), divides by 55 (`:66` `1DF4 mov cx, 0x37`, `:68` `1DF9 call far 23E4:0294`) and stores the dword (`:69` `1DFE mov word ptr [0xa9ff], ax`, `:70` `1E01 mov word ptr [0xaa01], dx`). `calls.tsv` has no path to `1DA7` or `206A` from `0791:97D0`, `9564`, `D733`, `A4A1`, `F098` or `F1F6` |
| After a restore, the `cycles` in effect are the session's, not the state's | The state's count is fixed, so a busy-wait's guest time scales as 1/cycles. First halves against the 30000 restores imply 5016 … 5360 cycles at 5000 (E005-r0030 … r0039), 29608 … 30200 at 30000, and 61198 … 89679 at `max` (E005-r0040 … r0051) (`summarise.py` "Cycles in effect"). A watched restore at 5000 took 449.7 guest s for a first half that took 75.1 at 30000 (E005-r0031, r0012) | — (emulator behaviour; the savestate's `CPU` component holds no 5000 or 30000 value: a scratch probe, not a record) |
| Every delay in a match counts passes against `DS:A9FF`, so it sets only host time | Matches identical while `DS:A9FF` differs 6-fold between restores and fresh launches at 5000 (E005-r0019, r0021, r0024, r0025 against E005-r0030 … r0039) and 8-fold between fresh launches at `max` (E005-r0052 … r0055) | `214B:1E09(n)` counts to the dword n times (`seg_214B_04.asm:100` `1E40 cmp dx, word ptr [0xaa01]`, `:102` `1E46 cmp ax, word ptr [0xa9ff]`); the whistle `214B:1F87` reads it too (`:272` `1F91 les ax, ptr [0xa9ff]`); both only loop and write ports and locals (Observations, Static) |
| F001's first half under 1 s at `max` and 60000 was its probe's clock starting after half time | F001's probe re-run at `max` with its own keys reproduces it: HALF TIME 1.0 s, second half started 3.28 s, FULL TIME 13.53 s, ratio 0.098 (`match-speed.json`). With one read before its first match key `c`: at `max` and at fixed 60000 that read already shows `---- HALF TIME ----` with `DS:80EE` = 154, so the first half had been played before the probe's clock started. At 30000 it shows `DS:80EE` = 0 and no HALF TIME (`match-speed-2.json`, `summarise.py` "F001's probe re-run"). E005's driver, whose clock starts with the match's first key, gives first/second ratios of 0.91 … 1.67 in 8 of 8 watched runs at `max` (E005-r0041 … r0055): not reproduced | No delay in a match follows guest time. The only tick read reachable from a match, `214B:0D90`, waits for a key (`seg_214B_02.asm:613`; F005). Nothing runs only in the second half on a timer: the end-of-half whistles `0441(3)`, `0425(4)`, `0441(6)` run at the end of each half (`seg_0791_16.asm:78`–`86`), and the one second-half-only call, `ED8A(0)` before the second half, opens the team screen and waits for a key (`seg_0791_16.asm:405`–`417`) |
| `max` may be used for sampling, under E005's key conditions | 16 of 16 match records at `max` are identical to their 30000 references, restores and fresh launches alike. The host load was 1.7 to 4.5 (`/proc/loadavg`, 1-minute), with no other DOSBox-X and 7 other Xvfb servers from other sessions running (each record) | the two rows above: no state written from a time source reachable from a match |

**Key conditions** (E005's, `runtime/driver/match.py`, listed in every match record, E005-r0010 … r0055): the match's starting keys go in one burst. After that, a key goes only to a stable `hit any key` screen before full time or to the team screen, one Enter each, at half time. No key reaches the match while its clock runs.

Under other conditions the host's speed does matter. F004 showed that the moment a key reaches a live match changes the match, and `DS:A9FF` and `cycles` set how much game time passes per host second. A sample that sends keys by wall-clock time during play is not reproducible at `max`, and not across settings either.

## Method

- **Machine and tools**: as F005, except where named. DOSBox-X 2024.03.01, `svga_s3`, memsize 16; `cycles` 5000, 30000 or `max` per record, named in the arm, `actions.args`, an observation, `runtime.fingerprint.cycles` and the config, all checked to agree by `summarise.py` "Checks".
- **Start states**: E004's `e004-1001` (Denmark v England, DOS 10:01) and `e004-1337` (Sweden v Denmark, DOS 13:37), both remade at 30000 with E004's `make-state`. Their `DS:7B62` (0xf3ab, 0xfabd) equals E004's and their `DS:A9FF` is 0x10b3. A recreation from the recipe is not byte-identical. These states (sha256 `ffcdac52…`, `d168d36f…`, named in every record) differ from E004's (`26a9a4d9…`, `120ccba1…`), and the reviewer's recreation of e004-1337 gave a third (`9e3164b3…`). The claims here rest on each record's own state, and on the states' seeds and matches agreeing with E004's.
- **Routes** (`experiments/E005-q003-cycles/run.py`):
  - restore: a fresh process at the setting, then Host+L of the state;
  - fresh: a launch at the setting with the state's DOS date and time set (I3), then E004's keys to the captain screen.
- **Arms**: E004's (`match.py`, unchanged), with a match bound of 2700 s.
- **Runs**: per state, setting and arm, 3 restores and 1 fresh launch. One exception (T12 Done-when 2, amended at `e70b1a6`): e004-1001 restored at 5000 is E005-r0030 … r0032, 2 quick and 1 watched.
- **Reads**: every read during a match keeps the host UTC time and the host seconds since the starting burst, on the same monotonic clock `match.play` uses. It also keeps the BIOS ticks, `DS:A9FF`, the screen digest, `DS:80EE`, `DS:7B62`, the score bytes and the commentary rows. From E005-r0034 on, all reads are one observation (README amendments 1, 2).
- **Order**: the 5000 and 30000 runs came first; fresh launches in a second game folder sometimes ran alongside restores. The `max` runs (E005-r0040 … r0055) ran with no other run of E005, then F001's probe.
- **Host conditions**: each record lists the other DOSBox-X and Xvfb processes and `/proc/loadavg`, at launch and at the end.
- **Identity** (`summarise.py` `compare`, review rounds 1–3). A run is called identical to its reference only when both are complete and every line, the score, `DS:7B62` and `DS:80EE` are equal.
  - A run is complete when it carries no reader flag and read as many lines as its counter advanced over its reads.
  - What both sides read and differs makes `DIFFERS`. Anything else is `IDENTITY UNDETERMINED`.
  - The reader's stride flag (`counter a -> b (n lines)`, a read that took 100 to 199 lines) names no unread line, since every record of that read is read. It warns that 200 or more lines may have passed unseen. It is settled when the flagged run counted as many lines as its complete reference, because a hidden stride would leave it 200 short. The 8 watched runs at `max` carry such flags (1 to 6 each) and are identical on that ground: 1307 lines counted on both sides for e004-1001, 1094 for e004-1337 (E005-r0041 … r0055).
  - A flag-free run is taken as complete on the reader's own assumption that no 200-line stride passes between two reads without a flag. The 30000 references read at most 79 lines between reads.
- **Halves** (`summarise.py` "Halves"):
  - host: from the starting burst to the first read holding HALF TIME, and from the team-screen Enter to the first read holding FULL TIME;
  - guest: from the BIOS ticks (18.2065 per s), the first half from the read before the burst, the second from the first read after the team-screen Enter.
- **Static**: the listing, `calls.tsv` and `datarefs.tsv` searched for every BIOS-tick read (`0:046C`, `0040:006C`), `int 0x1a`, INT 21h AH=2Ah/2Ch, `in`/`out` on ports 0x40–0x43 and 0x61, hooks of INT 8 and 1Ch, and every reader of `DS:A9FF`; reachability by breadth-first search over `calls.tsv` from `0791:97D0`, `9564`, `D733`, `A4A1`, `F098`, `F1F6`.

## Observations

### Halves of the watched runs (`summarise.py`; guest s from the BIOS ticks, host ratio first / second)

| State | 30000 restores | 30000 fresh | 5000 restores | 5000 fresh | `max` restores | `max` fresh |
| --- | --- | --- | --- | --- | --- | --- |
| e004-1001 | 75.1 / 73.8, 75.2 / 73.9, 75.3 / 73.7 (ratios 1.01 … 1.04) | 75.0 / 73.7 (1.05) | 449.7 / 444.4 (1.15) | 96.9 / 96.2 (0.97) | 35.5 / 29.8, 29.7 / 28.6, 28.5 / 30.2 (0.91 … 1.20) | 49.9 / 48.8 (1.01) |
| e004-1337 | 49.6 / 29.4, 49.4 / 29.5, 49.2 / 29.2 (1.60 … 1.66) | 49.5 / 29.5 (1.65) | 294.9 / 176.8, 294.8 / 177.0, 294.6 / 176.7 (1.57 … 1.69) | 73.4 / 53.7 (1.39) | 16.5 / 11.2, 16.9 / 11.5, 18.4 / 10.8 (1.40 … 1.67) | 15.5 / 10.3 (1.46) |

- Within a state, the halves are the match's own.
  - e004-1001's halves are equal at every setting, though all its goals and cards fall in the first half.
  - e004-1337's first half is longer than its second at every setting and on both routes, but not by a fixed ratio: host 1.39 … 1.69, guest 1.37 … 1.71 (the fresh launch at 5000, E005-r0025, lowest in both).
  - So a match's halves can differ by its content, in the same direction at every setting, with a ratio that varies with the setting and the route. Which part of the content does this is not settled. The listing's candidates are the event-driven waits: the substitution notice `7FCF` (`CC2E` of 400 or 1000 calibrated × 10 ms, `seg_0791_13.asm:890`–`898`), the action-replay prompt `0B7C` (`CC2E(600)`, `seg_0791_02.asm:284`–`286`) and the ball-flight loop `7881` (`seg_0791_13.asm:55`–`68`).
- At `max`, guest seconds vary by run (e004-1001 first half 28.5 … 35.5), as `max` runs at another speed each time. The matches do not vary.
- Host time per watched match, from the starting burst to full time (`summarise.py`, "match s"):
  - e004-1001: 77.2 … 128.1 s at `max`, 201.6 … 210.6 s at 30000, 265.5 s for the fresh launch at 5000 and 1254.9 s for the restore at 5000 (E005-r0031);
  - e004-1337: 35.3 … 40.1 s at `max`, 108.7 … 112.4 s at 30000, 180.2 s for the fresh launch at 5000 and 619.3 … 631.5 s for the restores at 5000.
  - The reads add host time; the guest seconds exclude it.

### F001's probe re-run (`measurements/`)

| File | Setting | HALF TIME, 2nd half started, FULL TIME (s) | Read before `c` | `DS:A9FF`, delay byte |
| --- | --- | --- | --- | --- |
| `match-speed.json` | `max` | 1.0, 3.28, 13.53 (ratio 0.098) | not taken | 0x1a7 (423; `main.sav` made at `auto`), 1 |
| `match-speed-2.json` | `max` | 0.99, 3.07, 11.92 (0.112) | HALF TIME on screen, `DS:80EE` 154 | 0x1a7, 1 |
| `match-speed-2.json` | 60000 | 0.99, 3.08, 15.46 (0.080) | HALF TIME on screen, `DS:80EE` 154 | 0x1a7, 1 |
| `match-speed-2.json` | 30000 | 6.22, 6.91, 22.73 (0.393) | `DS:80EE` 0, no HALF TIME | 0x1a7, 0 from the first poll |

- The probe reaches the match with `Esc Up Enter` and then `Enter Enter`, each followed by a settle poll (`runtime/spike/probe.py`: `SEQ_A` plus two Enters; then `c` and Right ×5). E004 reaches the captain screen with `Esc Up Enter Enter`.
  - At `max` and 60000, the probe's last Enter reached the captain screen and started the match. Its settle poll waited for a stable screen, which first came at the half-time pause.
  - Only then did the probe press `c` and start its clock.
  - Its "second half" (6.5 … 9.7 s in F001) is a whole half; its "first half" is the time from `c` to its first poll.
- At 30000 the match had not started before `c`. That run's halves are 5.3 and 13.1 guest s (ratio 0.39) because of its own content: `main.sav` is made anew by the probe at the current host time, so this is another match than F001's. With the delay byte at 0 it is not comparable with E005's matches.

### Static (`static/goal-exe/code/`; reachability over `calls.tsv`)

- **The calibration runs once, at start-up**: see the Answer.
- **The match's delays**:
  - `0791:0425(n)` calls `1E09(n)` only when the speed byte `[DS:A923]+0x3F` is above 0 (`seg_0791_01.asm:487`–`491`: `042C cmp byte ptr es:[di + 0x3f], 0` / `0431 jbe 0x43b` / `0436 call far 214B:1E09`). The whistle `0441(n)` works likewise (`:502`–`505`).
  - `0791:94E8`, called for each of the 22 players every tick of the watched engine (`seg_0791_15.asm:1128` `96DB call 0x94e8`; loop bound `:1139` `96F3 cmp word ptr [bp - 2], 0x16`), ends with `0425(speed)` (`:934`–`938`).
  - The clock `0791:970C` calls `0441(3)`, `0425(4)`, `0441(6)` at the end of a half only (`seg_0791_16.asm:78`–`86`).
  - The ball-flight loop `0791:7881` calls `1E09(2)` per pass at speed 0 and `1E09(1)` at speed 1 (`seg_0791_13.asm:55`–`68`).
  - `0791:CC2E(n)` is n × (keypressed `214B:0723`, else `1E09(10)`) (`seg_0791_20.asm:1063`–`1072`).
  - None reads a clock.
- **The time sources in the listing**, in three classes. First, decoded routines with callers. Second, the one decoded routine with none, `235C:00A2`. Third, bytes the disassembler did not decode, `2382:02C6`. The decoded instructions contain no `int 0x1a`, no `in` from ports 0x40–0x43 and no hook of INT 8 or 1Ch:

  | Source | Where | Reached from a match | Where the value goes |
  | --- | --- | --- | --- |
  | BIOS tick `0:046C` | `214B:1DA7` (`seg_214B_04.asm:44`–`62`) | no (start-up) | `DS:A9FF`: a loop bound only |
  | BIOS tick `0:046C` | `0791:F3F2` (`seg_0791_24.asm:38`–`39`: `F443 mov ax, word ptr es:[0x46c]`, `F447 mov word ptr [0x8336], ax`), called by the entry (`seg_0000_01.asm:14`) | no (start-up) | `DS:8336`, read only by `0791:94C9` (`seg_0791_15.asm:889` `94CF mov di, 0x8336`), whose draw decides only whether and at what pitch the speaker sounds in `94E8` (`:904`–`932`) |
  | BIOS tick `0040:006C` | Borland CRT start-up `2382:0030` (`seg_2382_01.asm:59`–`74`: `0066 mov ax, 0x40` … `0089 mov word ptr [0xaab8], ax`), from the entry (`seg_0000_01.asm:10`) | no (start-up) | `DS:AAB8`, which no instruction in the listing reads (`datarefs.tsv`) |
  | BIOS tick `0:046C` | `214B:0D90` (`seg_214B_02.asm:613`), inside the line editor `214B:1086` | yes, on routes that need a key (F005) | which of two attributes one screen cell shows; the loop leaves only on a key |
  | INT 21h AH=2Ch (time) | `Randomize` `23E4:11D7` (`seg_23E4_02.asm:805`–`808`) | no (start-up and new game, F004) | the seed `DS:7B62` (hour:minute) and `DS:7B64` |
  | INT 21h AH=2Ah (date) | `235C:006C` (`seg_235C_01.asm:98`) via `214B:1C63`, start-up | no | the year `DS:A9FD` (F004) |
  | PIT ports 0x42, 0x43 and speaker gate 0x61 | `214B:1E75`, `1EBC`, `1EF1` (`seg_214B_04.asm:136`–`140`, `:193`–`195`, `:252`–`254`) | yes | written only (0x61 read and written back to set its low bits, `:138`–`140`); nothing reads the timer |
  | INT 21h AH=2Ch (time), decoded but uncalled | `235C:00A2` (`seg_235C_01.asm:127`–`147`, `00A5 mov ah, 0x2c` / `00A7 int 0x21`; found by its prologue only), a Turbo Pascal `GetTime`-shaped routine storing the hour, minute, second and hundredths through four far pointers | no: no caller in `calls.tsv`, so no path from the six roots | nowhere the listing shows |
  | Port 0x61, 0x43, 0x42 (speaker), undecoded bytes | `2382:02C6` … `02FB` (`seg_2382_01.asm:237`–`240`, `; data (not reached as code), 70 bytes`): read as code, CRT `Sound`/`NoSound`-shaped (`E4 61` `in al, 0x61`, `E6 43`, `E6 42`, `E6 61`) and a keyboard check (`B4 01 CD 16`) | no: not reached as code by the disassembler, no recorded call | the speaker, if ever run |
- **The match clock counts loop passes, not time**: `970C` decrements `DS:831D` once per call (`seg_0791_16.asm:16`–`18`) and resets it to 0x24 per game minute (`9771 mov word ptr [0x831d], 0x24`).
- **No loop of a match polls the keyboard a number of times that depends on `DS:A9FF` or the tick and then branches without a key**: `CC2E` polls n times whatever the count, and `9372` polls once per player per tick (F005). With no key, the timed prompts end the same way at every speed: `7FCF` writes Esc to `DS:A977` (`seg_0791_13.asm:898` `8052 mov byte ptr [0xa977], 0x1b`) and `0B7C` returns 0 (F005).

## Inferences

- `cycles`, the host's speed and `max`'s varying speed do not change a match whose keys arrive only at stopped-clock screens. Behaviourally, 40 of the 41 runs compared are the same match as their 30000 reference and none differs; E005-r0035 is undetermined, since one of its lines was never read (E005-r0010 … r0055). Statically, no time source reachable from a match writes game state. Both routes agree, so this is corroborated once reviewed.
- Under those key conditions, the matches E004 and F005 recorded at 30000 are the same matches at 5000 and `max`. E005 replays two of E004's states at all three settings with E004's results (E005-r0010 … r0055 against F005's Pairs).
- F001's "first half under 1 s at `max` and 60000; not explained" is now explained, on the behavioural route: its probe's clock began after half time (`match-speed-2.json`), while E005's driver, whose clock starts with the match's first key, finds no such half in 8 of 8 watched runs at `max` (E005-r0041 … r0055). On the static route, nothing in the listing makes a first half shorter on a timer. The second half F001 measured is a whole half at a delay count calibrated at `auto` (0x1a7).
- How long a half takes depends on the match's content: e004-1337's first half is the longer at 5000, 30000 and `max`, by a ratio that varies, host 1.39 … 1.69 (E005-r0023, r0025, r0035, r0047). Which events cost that time is not settled.

## Alternatives considered

- **"The savestate carries the `cycles` it was made with"**: refuted for these settings by the implied cycles after a restore (5016 … 5360 at 5000, 61198 … 89679 at `max`, against a state made at 30000).
- **"The match draws on a timer or the tick, so the host's speed changes it"**: refuted on both routes under E005's key conditions (Answer).
- **"`max` adapts its speed to the savestate reads and so slows one half"**: not needed. F001's asymmetry comes from where its clock starts (`match-speed-2.json`), and E005's `max` runs, read throughout, show no such half. Whether `max` changes its speed around each read was not measured.
- **"The anomaly is the delay calibration of an `auto`-made state"**: the probe's `main.sav` has `DS:A9FF` 0x1a7, which makes its matches short at every fast setting. That explains its short second half, not the missing first half (Observations).

## What this does not establish

- Keys sent during play: F004 showed that their moment changes a match, and that moment depends on `cycles` and the host. Not tested here.
- Other start states, cup matches, extra time and penalties, other machines, other DOSBox-X versions, and settings other than 5000, 30000, 60000 (probe only) and `max`.
- Why e004-1337's first half is the longer, and why the ratio varies between settings and routes (candidates in Observations).
- What E005-r0035's unread line held.
- Whether `max`'s speed changes during a match, beyond the guest seconds per half that each record carries.

## Defect found

`runtime/driver/commentary.py` `Tracker.add`: when a read falls between the game raising `DS:80EE` and writing the record, the record is still the end marker 0xFF. The tracker flags it, skips it and moves past it, so that line is never read (E005-r0035, read 425). It is filed as issue #38, for a fix outside T12, since `runtime/driver/` is additions-only here. E005's `summarise.py` reports a run whose only difference is lines its reader never read as identity undetermined, never as identical. Each flag counts for the one occurrence it names (README amendment 6).

## Where the evidence is

- `runs/E005/E005-r0001.json` … `E005-r0055.json` (number 33 unused).
- `experiments/E005-q003-cycles/measurements/match-speed.json` and `match-speed-2.json`.
- No evidence bundle: the start states and savestates stay in `.cache/` and `scratch/` (git-ignored), since they hold the game.

## Reproduction

1. `bash setup/goal2-runtime.sh` (prints `ready`).
2. The commands of `experiments/E005-q003-cycles/README.md`: E004's `make-state` for 10:01 and 13:37; `run.py calibrate`, `restores` and `fresh` per setting; `probe_f001.py`, then `probe_f001.py --cycles max 60000 30000 --pre-read`.
3. `python3 experiments/E005-q003-cycles/summarise.py`.
4. `python3 tools/validate_runs.py runs/E005`.
