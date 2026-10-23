# Static scope of the six additional whole-body ablations

This is a listing/caller inspection, not a claim that a short witness proves
removability. The full ALL ablations and a combined final ALL run decide that.
No mask is inferred here. Back-buffer and picture-copy bytes remain protected.

| Routine | Original writes and calls | Caller/return obligation |
| --- | --- | --- |
| `0791:006C` | `code/seg_0791_01.asm:62`: a local ratio and two `214B:00DB` calls write attributes through `DS:A96E`; no character, record or RNG write. | Sole caller `0106` calls it at `024F`/`025C`. The first return is followed by fresh pointer/row setup; the second by a local counter reset and explicit AL loads. The caller does not test or save a result. Return cleanup is `ret 8`. |
| `1771:0AF8` | `code/seg_1771_02.asm:39`: reads the manager index/status, writes its local pointer and calls `214B:026D` for one status label. The nonzero status branch was not entered by original ALL. | `157D:15FB` continues by constructing a new numeric expression from a country byte. The other direct caller, `000E:72E3`, next calls `7072` before pushing a result; it does not test/save the status renderer's result. Return cleanup is `retf 6`. The ALL entry-reached states, not arbitrary manager states, bound a removal claim. |
| `1771:1527` | `code/seg_1771_03.asm:6`: local pointer, country-rating call `10E7`, signed band lookup and `214B:026D` label. `10E7` (`code/seg_1771_02.asm`, heading `10E7`) only reads the country ranks/continent and writes its own locals. | Sole caller `157D:15C1` proceeds to an explicit manager-byte load and `xor ah,ah` for the next expression. No result test/save. Return cleanup is `ret 6`. |
| `1771:3947` | `code/seg_1771_05.asm:955`: writes **`DS:AAB2 := 70h` at `3961`**, its local loop/pointer/scales, and twelve attribute bars through `214B:00DB`. It is not correct to describe it as having no global write. | Sole caller `42BC:4651` immediately loads AX=4 and begins the status-bit/icon chain. Every later status-label path either calls a set-attribute writer or writes `AAB2 := 15` at `47CD`; performance rendering may replace it again. The intermediate back-buffer attributes and stack still require the actual ALL ablation. Return cleanup is `ret 6`. |
| `214B:1E8D` | `code/seg_214B_04.asm:146`: saved BP, optional port61 input/AND/output and the returned AL; no DS field or record write beyond the frame. Original kit return-register controls are in `speaker-returns-1.txt`. | Reached match callers include `94E8`, `9372`, `C5DC`, `CC2E` and the shot/ball tails. `94E8` explicitly reloads AL from game+3F and clears AH at `9536`/`953A`; `CC2E` reloads AX from its own argument. The early `9372` off call is followed by read-key and a fresh AL key load. Several other callers return immediately, so this inspection does **not** assert general AX-equivalence for every possible caller. `retf` cleanup and actual ALL caller behavior remain the test. |
| `214B:1EBC` | `code/seg_214B_04.asm:176`: saved BP, speaker-on call, long division and overwrite of its **copied stack argument** with the PIT divisor, then two port writes. No record, primary RNG or global DS field is written. | Direct callers are `94E8` and `1EA1`; neither reuses the callee's popped argument copy. `94E8` reloads the speed byte and clears AH before continuing. `1EA1` proceeds to its duration delay and speaker-off call. There is no direct result test/save at either call site. `retf 2`; all stack residue and any indirectly propagated scratch values stay subject to ALL comparison. |

The additional speaker-off direct callers from the static inventory are
`000E:04F5`, `000E:0572`, `0791:112C`, `8062`, `9372`, `94E8`, `983F`,
`98C4`, `9955`, `C5DC`, `CC2E`, `1771:07B4`, `214B:1E5A`, `1EA1`, `1F87`.
Immediate-return paths are not silently converted into a claim that AL is
unconditionally dead outside the declared ALL states. A scalar register return
or dead-frame difference in a synthetic standalone call is separate evidence
from whether an accepted match reads it.
