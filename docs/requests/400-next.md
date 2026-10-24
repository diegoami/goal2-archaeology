# Original-key goal-kick input and closer-source search (#400, T89)

T89 continues [T88's delivery](400-remaining-inputs.md). It supplies a genuine original
**CC7B role 5 GOAL KICK** input, the original **Space → pitch → CF3A** blocking read,
and return to the same selector. Roles 2 and E19F were already supplied by T88; this work
does not recollect them as new coverage. Findings F029/F030 retain their existing status.

## Get and verify the private inputs

The owner's [private T89 folder](https://drive.google.com/drive/folders/1TDVXoWa1EV1HRl6EeUkY6d3EHYFmmJP2)
is `goal2drive:goal2-archaeology/400-next-inputs-20261024/`.
[delivery.json](../../notes/400-next/delivery.json) gives every exact filename, full hash,
preceding input/hash, private location, live-frame fields and readback path.

```sh
rclone copy goal2drive:goal2-archaeology/400-next-inputs-20261024 .cache/400-next/readback
unzip -n .cache/400-next/readback/t89-all-attempts-private.zip -d .
unzip -n .cache/400-next/readback/t89-core-vacancy-inventory-private.zip -d .
python3 notes/400-next/verify.py
```

These are the complete clean-cache setup commands. Verification reads the downloaded archives
directly from `readback/`; it needs no separate copy of either archive at a collector-only path.
The first archive retains every native observation, original G3B source and all17 original
E031 saves needed for the inventory. The second retains the12 distinct G13 inputs inspected
read-only. No game is executed by this verification, and no original byte payload enters Git
or a public release. The inputs and both archives pass actual upload/download SHA-256 checks.

| Input | Full SHA-256 | Meaning |
| --- | --- | --- |
| `t89-cd047f4a697e5244-goal-kick-before-space.sav` | `cd047f4a697e5244ea11e1609138ca45d8d070754ce857ea89f6459f78eef482` | Genuine role5 timed selector before Space, r1 step20. |
| `t89-21e794f7867309dc-goal-kick-CF3A.sav` | `21e794f7867309dcacb2d6d034878a76fedef972619cf490e947b55dded96710` | Space reached the actual extra blocking read returning CF3A, step21. |
| `t89-58c1d8107a1269ec-goal-kick-after-pitch.sav` | `58c1d8107a1269ec90988104fa82473748b5eda4d25c5ba9a08b26bb498039bf` | Return restored the same selector, step22. |

Step20's preceding genuine native input is step19, SHA-256
`40587fe09717d687fe4ed1c9979dc9dc17aabce93bd1a89f227d8d0b7fc9e771`.
The next two inputs each name the preceding delivered state. Separate preceding files are
provided, and the complete100-state native sequence is also retained in the private archive.

## Original source and bounded method

Static-first reading used the named CC7B, E022, EA09, DEA6 and original loader027B views,
then their listings. F030/T84 already supply the prompt contract; a listing cannot supply a
genuine stopped input. E031's C43b / g1 step2630 records a goal-kick selector shortly after
the retained G3B.GL save, giving a cheaper starting point than another campaign.

The original DOS loader read unchanged **G3B.GL**, SHA-256
`e7bedd5507e4b16f38973b8fc9b113da01435f74935f5c8eb5e61ce843faeb8c`, from the merged
[T84 inventory](../../notes/390/inventory.json). It is immediately before Iceland–Holland
in World Cup qualifying. r1's collector source was committed at
`bf55828c9899fd5988e610b246846c1430bc9ffc`, SHA-256
`9b7302d9472bfb564abfe751f5b37d63daa7f6db22be2b7a4a85fa6199368e83`, **before launch**.
The append-only source, key, screen, CPU and caller records are under `notes/400-next/G3B-r1/`;
their raw commit `7e283c90` precedes interpretation. The source `.GL` is not converted or
reconstructed into a machine state.

Runtime: DOSBox-X **2024.03.01**, private Xvfb, nohost mapper, raw XTEST original keys,
`machine=svga_s3`, `memsize=16`, `cycles=fixed 8000`, `core=auto`, `cputype=auto`.
Explicit DOS date/time: 10/24/2026 12:00:00; actual readback 10/24/2026 11:59:59.
Original Insert disables replay when needed; original Right keys select the fastest speed.
Every key and driver timing is retained. No guest-memory, fixture, RNG or CPU-entry edit was made.
The loaded game's trajectory is not claimed identical to E031's earlier campaign seed.

r1 was bounded to **240 seconds and the first managed fixture**, and captured role5 at
minute6 in **23.830 seconds**. The separately assessed r2 resumed r1's genuine last input
on **both verified identical native C/D mounts**, using only normal original keys. It stopped
at full time after **52.231 seconds**, with no retained role3/4 choice. Both raw attempts,
all100 observations and exact collector source pins are retained. No further fixture was played.

The r2 raw method label inherited the first-run phrase `no restore`; its explicit `resume`
object, original source hash and pinned implementation record the actual same-mount normal
replay. That label is not used to claim no restoration occurred. The raw record remains
unchanged. A pool-inventory comment also named the wrong hex-file part; values/indexing were
correct and the table is in `ds_2581_03.hex`. Both corrections are explicit in
[provenance-clarifications.json](../../notes/400-next/provenance-clarifications.json).

## Exact original decision and keys

At minute **6**, Iceland0–Holland0, qualifying:

1. Step20: CPU **214B:1E4A**, SS **3875**, SP **3E38**, BP **3E40**. The live BP chain
   is **3E40 →3E4C →3E60 →3E6A**, with returns **CC65 →CED9 →6D74**. This is the
   original CC2E delay inside the selector, **not** a captured poll instruction.
   The original polls/optional read are CC4F/CC54, CED9/CEDE and CEE8/CEED (F030).
2. **Space** produces step21: CPU **F000:CFAB**, SS **3875**, SP **3E24**. The live08DD
   frame at BP **3E4C** far-returns to **0791:CF3A**; saved parent BP **3E60** is the
   same live CC7B frame. BIOS EBP is zero and is not substituted for the game BP.
3. **Return** produces step22: CPU **214B:1E40**, back in the same timed selector.
   r2's original Enter then accepts the selection and resumes the same fixture.

Across these inputs: **role5**, **side0**, country **20 (Holland)**, highlighted squad slot
**4**, selected/stored player **383 (B Van Aerle)**, status **0**, position **2**;
main RNG **31813**, auxiliary RNG **0**. The eleven is
`381,393,384,383,382,395,2575,387,388,2748,400`. Side and country identifiers come from this
actual loaded state; do not infer them from scoreboard order. CC7B's role/side arguments
are bytes, so scratch high bytes are ignored. [frames.py](../../notes/400-next/frames.py)
derives these fields from the live caller chain and validates the build guard.

For a native reproduction at another path, load G3B.GL through the original loader on local
drives and follow the recorded original keys. Do not blindly restore a native save whose
embedded mounts point elsewhere. For a Unicorn consumer the delivered files are genuine
machine inputs at their saved CPU; the timed selector and the actual CF3A blocking read
are distinct inputs. Do not jump the CPU to CC7B/CEE8/CF35. Import/recovery implementation
belongs to goal2; this work supplies no `.GL` converter or desktop code.

## Remaining four cases and the vacancy search

Read-only inspection follows the original22-block `.GL` loader sequence in1771:027B.
All **17** hash-verified E031 saves contain **no zero player word** in the managed squad20
or its reserve pool80. The pool starts1,81,161,241,321,401 for managers1..6, from the original
DS:6D1A table. The raw inventories are [inventory-r1.json](../../notes/400-next/inventory-r1.json)
and [pool-inventory-r1.json](../../notes/400-next/pool-inventory-r1.json).

A separate read-only search of existing `g13-*.g2core` files in the goal2 cache/keep stores
inspected **12 distinct hashes**, retained each unchanged privately, and found no empty managed
squad or pool slot either. It executed no guest instructions. Source paths, duplicate locations,
hashes and observations are in [core-inventory-r1.json](../../notes/400-next/core-inventory-r1.json).

| Still missing | Exact limit and cheaper existing assumption |
| --- | --- |
| Role3 penalty | No retained CC7B role3 choice in the one bounded qualifier. A shootout-order input is not this case. F030's role3 contract remains static-only. |
| Role4 free kick | No retained CC7B role4 choice through full time. Ordinary free kicks do not prove the dangerous free-kick selector. Keep F030's conditional contract static-only. |
| E022 / E062 no player | Requires selecting an actual zero squad word; none exists in the inspected17 saves or12 retained G13 inputs. No direct guest edit or external save alteration is used to manufacture one. Keep the conditional original caller contract. |
| EA09 / EC60 vacancy | Requires a genuine first-eleven vacancy while earlier checks pass; no such input was found. The known retirement path replaces the retiring member at once (F017), so a new multi-year run has no justified cheap yield. Keep the conditional contract. |

This bounds the search, not global reachability. The inspected original DEA6 controls can
swap into an already empty pool slot, but no such slot was present in these retained sources.
No source is advertised as proving an unvisited role or warning. Wider runs need a new cost
assessment or a genuinely closer input. **#400 remains open** for these four cases.

The §14 handover/consumer issue is [goal2 #372](https://github.com/diegoami/goal2/issues/372),
linked on PR407 and #400 before merge. Its docs-only
register branch follows upstream merge so the rows cite merged evidence. Goal2 owns recovery
and reviews/merges that branch; archaeology changes no goal2 implementation.
