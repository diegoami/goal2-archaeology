# Original-key corner input and remaining limits (#400)

T88 / [PR #405](https://github.com/diegoami/goal2-archaeology/pull/405) supplies a genuine
**CC7B role 2 corner** input, its **Space → pitch → CF3A** blocking read, and the return
to that same corner selection. This is original DOSBox execution, not a constructed fixture.
The [supplemental original-key E19F input](400-nice-try.md) also captures “Nice try” from the
closer T114 stoppage checkpoint identified in a newer #400 comment. The raw records were committed before this interpretation. Findings F029/F030 retain their
existing status; this collection establishes no new general game rule.

## Private inputs

Use the owner's [private delivery folder](https://drive.google.com/drive/folders/1a9afcTH1f_tFDgJ1OOgbH7Bzfy_gea0h),
`goal2drive:goal2-archaeology/400-remaining-inputs-20261024/`.
[delivery.json](../../notes/400-remaining/delivery.json) gives every full hash, preceding
input/hash, exact filename, source, extracted frame and private readback path. Original files
and machine states remain private; no original bytes were added to Git or a public release.

| Input | Full SHA-256 | Meaning |
| --- | --- | --- |
| `t88-bda98a358d98a82f-corner-before-space.sav` | `bda98a358d98a82f9243ec7025bb8f7f02e0f80a69b37c5bc763faf2aa6e741d` | Original timed corner selection immediately before Space, step 87. |
| `t88-72d72b0dc1b809fe-corner-pitch-read.sav` | `72d72b0dc1b809fe10c9c29814ebf33610ae8e900aa2eadd50661849eec0dafe` | Space has opened the pitch; actual blocking read returns CF3A, step 88. |
| `t88-dc81d0bc8f325051-corner-after-pitch.sav` | `dc81d0bc8f325051be943d11b90e94a4b1415d0ca76e466c04d2d3a4f114f91f` | Return dismissed the pitch and returned to the corner selector, step 89. |

Step 87's preceding genuine input is step 86, SHA-256
`442fd4065ffdfcd905c37e86a21e2d89863874cbeb851e1c8b0554a2780a7ef7`.
Steps 88 and 89 each name the immediately preceding delivered state. Separate preceding-input
files are supplied too. `t88-all-attempts-private.zip` retains **all 404 observations from all
four attempts**, both original .GL sources, collector sources, raw key/runtime records and
native configurations. Its full hash is in the delivery manifest. Uploads are verified by
downloading the actual bytes and hashing them, including the complete attempt package.

## Source, keys and exact frames

The successful collector is pinned at archaeology
`b5f769a6` (the full source commit is in `native-r4/source.json`), collector SHA-256
`97c8c81135bef3dfda7a7b6dc4456867f6101cf48db39feac4ba27ec4799de7a`.
The original loader read E031 `G1A.GL`, SHA-256
`b6e3c4c14d25543d28e4d5a38a43882c562b3acfe4f8834a7b64183024c6b152`;
its immutable source identity/location is in the merged [T84 inventory](../../notes/390/inventory.json).
This existing save is immediately before Holland's first friendly, not a newly played campaign.
No seed, guest memory, fixture kind or CPU continuation was edited.

Runtime: pinned DOSBox-X 2024.03.01, private Xvfb, raw XTEST keys, nohost mapper,
`cycles=fixed 8000`, `machine=svga_s3`, `memsize=16`, `core=auto`, `cputype=auto`.
Explicit DOS date/time: 10/24/2026 12:00:00; the actual readback and every key/host timing are
in `native-r4/record.json`. Original Right keys increased match speed; original Insert disabled
action replays. The complete loader/navigation trace is in `native-r4/steps.jsonl`.

At minute 87 of Holland–Eire, score 1–2, the exact final key sequence is:

1. Step 87 observes the corner choice. CPU **214B:1E46**, SS **3875**, SP **3E36**,
   BP **3E3E**: the original delay inside CC2E, **not a snapshot at the poll instruction**.
   Live saved-BP chain: `3E3E → 3E4A → 3E5E → 3E68`; return offsets
   `CC65 → CED9 → 6D74`. This identifies the live CC7B frame at BP **3E5E**.
   Its original poll is `CC4F → 0723` (return CC54), then `CED9 → 0723` (CEDE),
   and a pending key is consumed at `CEE8 → 08DD` (CEED), as in F030/T84.
2. **Space** produces step 88. CPU **F000:CFAA**, SS **3875**, SP **3E22**.
   The validated 08DD frame at BP **3E4A** far-returns to **0791:CF3A** and its saved
   parent BP is **3E5E**, the same live CC7B frame. BIOS EBP is zero and is not treated
   as a game frame. This proves the additional blocking read, independently of the screen.
3. **Return** produces step 89: CPU **214B:1E40**, the same delay chain and corner pick.
   Another **Return** accepts it and resumes ordinary play (step 90, also retained privately).

Across all three inputs: role **2**, side **1**, country **20 (Holland)**, manager byte **129**,
highlighted squad slot **6**, selected/stored player **386 (R Witschge)**, selected status **0**,
position **7**, main RNG **14477**, auxiliary RNG **0**. The eleven is
`381,382,384,383,385,386,387,388,389,390,391`. These country/player identifiers belong to
this loaded game; do not substitute identifiers from G4C. The live byte arguments sit in
words **0E02/0E01**: the high bytes are scratch register contents. The collector's original
diagnostic `takers: []` used a whole-word comparison and missed them. Raw records stay unchanged;
[frames.py](../../notes/400-remaining/frames.py) derives the actual low bytes and live caller chain.

## Reproduce and verify

```sh
rclone copy goal2drive:goal2-archaeology/400-remaining-inputs-20261024 .cache/400-remaining/readback
mkdir -p .cache/400-nice-try .cache/400-remaining/native-r3/preceding-driver-files
cp .cache/400-remaining/readback/t88-all-attempts-private.zip .cache/400-remaining/t88-all-attempts-private.zip
cp .cache/400-remaining/readback/t88-ee0c00a59111bc8d-E19F-private-attempt.zip .cache/400-nice-try/t88-E19F-attempt-private.zip
unzip -n .cache/400-remaining/readback/t88-all-attempts-private.zip -d .
unzip -n .cache/400-remaining/readback/t88-ee0c00a59111bc8d-E19F-private-attempt.zip -d .
cp notes/400-remaining/native-r3/preceding-dosbox.conf .cache/400-remaining/native-r3/preceding-driver-files/dosbox.conf
python3 notes/400-remaining/verify.py
```

Expected: 404 native observations / 4 native attempts plus 17 core observations / 1 bounded
attempt verified; corner, CF3A and E19F, with five cases still unavailable. The verifier checks
the collector against its recorded Git source, every raw observation hash and preceding link,
original loads, verified same-mount replay, live frames, selected eleven, upload readbacks and
the complete private package. It executes no guest instructions and changes no guest memory.

Both downloaded archives must be copied to their recorded local paths as well as extracted.
The preceding native configuration is collector-generated text retained in Git, not original
game bytes; copying it supplies r3's preserved configuration receipt for offline verification.
The commands do not launch DOSBox or restore any embedded drive paths. Existing private
archives and raw attempts are unchanged.

For the desktop core, import the supplied .sav as a genuine Unicorn machine input at its saved
CPU. From the corner input, send Space through the original keyboard path; the additional wait
is CF3A. Return resumes the corner selector; Return accepts the original highlighted pick.
Normal replay is allowed; do not move the CPU to CC7B, CEE8 or CF35.

For a native run on a different machine/path, **load the supplied G1A.GL through the original
loader on worktree-local drives** and follow the recorded original keys. DOSBox states embed
both C and D mounts. These states are portable Unicorn inputs, not permission to restore them
blindly under a different native mount layout. Native timing/RNG equivalence on another host
is not claimed; the hash-verified kept inputs are the exact reproducible machine states.

## Bounded attempts and unavailable cases

| Attempt | Bound and actual time | Result |
| --- | --- | --- |
| native-r1 | 900 s; 900.02 s including final observation overhead | Original G4C load; interactive transport stalled at the first other-team result; bound expired. Retained as unsuccessful. |
| native-r2 | 900 s; 276.97 s | G4C loaded on local drives; stopped at minute-41 substitution opportunity. No delivered taker/warning state. |
| native-r3 | 900 s; 129.11 s | Normal replay of r2's genuine last input on **verified identical C and D paths**, with prior driver files retained privately. Original keys to full time: Belgium 1–Holland 0. |
| native-r4 | 900 s; 154.86 s | One friendly from existing G1A, Holland 1–Eire 2. Retained role 2 and CF3A; stopped at full time. |

Static-first work used merged T84/#392, notes/390 and the named views of CC7B, E022, E44F,
EA09, then their original listings. Static contracts cannot supply genuine machine inputs,
which is why these bounded runs were needed. Cost was assessed before each continuation;
only two existing fixtures were played, with no campaign advancement beyond them.

T89 subsequently delivered the role 5 goal-kick input; see [its delivery and reproduction](400-next.md). The table below records T88's collection limits, not the combined coverage of later deliveries.

| Still unavailable | Exact limit and cheaper §15 assumption |
| --- | --- |
| Role 3 penalty | No retained original penalty-taker input in either fixture. A penalty cannot be promised within another short run. Keep F030's role-3 contract as static-only evidence. |
| Role 4 free kick | Ordinary free kicks occurred, but no retained CC7B role-4 choice. A free-kick statistic does not prove that routine/role was reached. Keep its existing static contract. |
| Role 5 goal kick | No retained CC7B role-5 input. Do not extend this corner's proof to goal kicks; F030/T84 remain static-only for this role. |
| E022 / E062 “no player” | Inspected managed squads had nonzero player words; no original empty-slot selection was retained. E44F's inspected controls provide no direct remove-player key. Keep the conditional caller contract until a genuine empty-slot input is available. |
| EA09 / EC60 vacancy | No actual vacancy warning/caller frame was retained. Normal menu exits and eleven checks do not establish it. Keep the conditional vacancy contract; do not invent an empty squad slot. |

E19F was unavailable from the two native fixtures, but was subsequently captured by a 1.139-second
original-key replay of the newly identified T114 sent-off-player input; see the linked supplement.
These are collection limits, not proofs that the paths cannot occur. No absence is inferred
from intermittent observations alone. Wider collection would need a separate cost assessment
or a genuinely closer existing input. **#400 remains open** for all five missing cases. Desktop
owns extra-time 9B42/9B70 and injury walk-off; no desktop code was changed by this work.

The §14 handover is [goal2 #368](https://github.com/diegoami/goal2/issues/368), with the private
delivery/reproduction links published before merge. The docs-only register/handover branch
is produced after upstream merge, as §14 requires register rows to cite merged research;
its final head is linked there, on PR #405 and on #400. That post-merge step is not claimed
complete before the branch exists.
