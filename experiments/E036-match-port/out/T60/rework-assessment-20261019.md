# R1 survivor assessment, 2026-10-19

Port runtime.py/geometry.py are unchanged from reviewed 321d846. Historical raw measurements remain immutable.

- Full runtime hand measurement at 95eb3f6: 980 mutants, 673 caught, 307 survived. No fuzz classification is claimed for this run.
- Full geometry corrected measurement at ba20973: 564 mutants, 378 caught by hand tests, 91 by actual differential fuzz, 95 survived both.
- The reviewer's exact 310 unreached-region mutants at dd15f59: 98 survived hand tests, 39 survived hand tests plus actual original-image fuzz (not skipped). Previously these counts were125 and53. The helper retains the reviewer's120-second test timeout: a nonpassing process is excluded from the survivor set, not an asserted differential detection. Its raw output does not distinguish causes for excluded mutants; behavioral controls below provide the explicit regression evidence.
- The full runtime --fuzz measurement aborted on a300-second subprocess timeout. It remains incomplete and unclassified; this is not a fuzz kill. No combined all-killed result is claimed.

Nine concrete behavioral controls pass the actual reviewed hand tests and fail the corrected hand tests. The old broken runner also fails the new classification regression. controls-final-r1-20261019.txt and rework-controls.py preserve the exact changes and results. The final100-test run includes actual differential fuzz and passes; full-suite-rework-ba20973.txt predates the last added test and is1579tests, not a claimed1580-test run.

## The39 surviving targeted changes

The raw targeted measurement predates the final negative-index test. One real missing case was found: runtime1372's first `0 -> 1` changes the negative Copy count result, introducing an extra character in Insert/Delete at index0 or-1. The final test and ninth control catch it. Do not retrospectively change the raw39 count or claim a fresh310-mutant rerun after this last test.

The other changes have these explanations to be checked independently:

| Raw source line(s) | Why the targeted mutation can preserve the checked result |
| --- | --- |
| runtime668 | Changes the write-at provenance label, not bytes/registers. |
| runtime670,1128 | Final internal SP adjustment is not stored by Regs.store(); PortFrame restores the return SP. No later push observes the adjustment. |
| runtime672,1188,1457 | Changes scratch BX/CX, not the strict AX/DX/flags/memory contract. |
| runtime932 | On the negative-delta branch t_hi is0 orFFFF; changing signed0 comparison to signed1 preserves the decision. |
| runtime1006,1010,1181,1183,1314,1372 comparison,1373,1381 | Equality returns the same value on both branches; negative-count threshold0->1 still yields0 at count0. |
| runtime1103 | The outgoing carry of the BX rotation is immediately overwritten by subtraction before being consumed. The shifted BX value itself is unchanged. |
| runtime1108 | Both1 and2 take the same restore branch, which recomputes carry. |
| runtime1382 minus-to-plus or final255->256 | Extra Python tail bytes are discarded at the unchanged Pascal length byte before guest writes. The *first*255->256 is a genuine invalid length byte caught by the saturation test/control. |
| runtime1412,1437 | Copy count255 and256 both exceed a Pascal string's maximum length; copy result identical. |
| runtime1418,1443 | Changes scratch BX via store_max_bytes sp_at_call. |
| geometry180,569 | R.dx is overwritten by mul() before use; multiplication uses the separate literal argument. |
| geometry192 | R.enter size changes internal SP, but only BP-relative local8 follows and leave restores SP; no intervening push or guest call. |
| geometry352,353 | Halving's scratch CX/DX are overwritten before output; actual skill division is unchanged. |
| geometry581,589 | Temporary near return words are overwritten by later pushes at the same addresses before the pending writes are flushed. The final far return words are asserted by the new side-one test. |
| geometry597 | R.ax is overwritten inside wrap_add_byte; the actual pushed increment and explicit helper argument stay1. |
| geometry959 | args(mem,1)[0] and args(mem,2)[0] read the same first argument. |

This table is a source-level assessment, not an all-survivors behavioral proof. Full-module survivor lists include additional cases not classified by the targeted table; no zero-survivor or complete mutation-coverage claim is made. Independent rework review must assess R1 rather than treating a successful script exit as proof of all mutants being killed.
