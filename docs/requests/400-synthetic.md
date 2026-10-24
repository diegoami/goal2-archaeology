# Controlled SYNTHETIC original-code fixtures (#400, T92)

Four synthetic fixtures execute and replay original GOAL instructions. They do not establish natural reachability, naturally awarded penalties/free kicks or full match continuation. All four unchanged-original gaps remain on #400; F029/F030 are not promoted. [T92](../tasks/T92.md) landed through PR424 before implementation; [owner authorization and acceptance](https://github.com/diegoami/goal2-archaeology/issues/400#issuecomment-6389898635) are recorded on #400. Research PR425 holds the executions. Persistent worktree: `/home/diego/projects/goal2-archaeology-400`; primary checkouts, other worktrees and active reviews preserved.

| Case | Classification | Actual original execution and limit |
|---|---|---|
| CC7B role3 regular penalty | delivered isolated-synthetic | Artificial call frame enters6ECF; original whistle/substitution check and2996→6D4E(10,3,1)→CC7B. Stop before82E0. No awarded foul, shootout or further match-flow claim. |
| CC7B role4 free kick | delivered isolated-synthetic | Artificial call enters6F3E(1); edited ball(x=0,y=-18), original direction-1 and product18 pass6F70/6F7F range gate→6D4E(11,4,1)→CC7B. Stop before6FEA. No foul-award claim. |
| E022/E062 no player | delivered integrated-synthetic | Edited retained E44F input; actual Enter→E690→E022 first-selection zero-word branch→1765→message read098A; Return→E44F readE61F. Stop there. |
| EA09/EC60 vacancy | delivered isolated-synthetic | Artificial EA09 call and zero outfield slot10; original eligibility and keeper checks all return0; vacancy helper returns1; Return completes EA09 with AL0. Stop beforeF067. No branch-boundary/local-counter edit. |

## Private inputs, exact recipe and provenance

[Owner-only private folder](https://drive.google.com/drive/folders/1b5VlP-nFHkWilG576gQj1P4iwERF9S7a), [full delivery manifest](../../notes/400-synthetic/delivery.json). Final `t92-fixtures-v2-private.zip`:13,842,233 bytes, SHA256 `ab1864e3449a643bdc6119650e09b9d29e90ab01476aa9eace468d6834f9eeae`. Actual upload/download hashes match. Folder and final file readbacks show only user/owner permission. Initial uploads under the existing shared archaeology parent inherited anyoneWithLink writer; those two uploads and newly created shared subfolders were deleted. This corrected privacy incident is explicitly retained; the initial uploads are not claimed private.

Untouched base for every case: T90 `uc-r1/0046.g2core`, SHA256 `068a47729a3b1822ae6d3df7777eb99880bbcf74315e22098869ccaeac29ad28`; native ancestor G1A-r1/0034.sav `6731809257089157904884a54148f6f71b87a3073aaa9d433479744ba8844915`. Each private attempt retains its untouched base, constructed input and complete stopped machines. The verifier requires executable memory byte-identical to the base in every input/stop. No instruction, text or observation is patched.

Backend goal2 is pinned to commit `5061474420b842ee98a4a1e4c9c2673c0764b1f2`; every source/runtime file hash and Unicorn version is in each immutable record. Runtime hashes match T90's committed manifest; no mutable goal2 checkout is imported. Final producer SHA256 `05728dd5b8a361c71755fece7e7e094d2b3be8c69286096fa92bd28cd24a720a`; E062-r2 used `1c0efbaa449b6b35d6a1aefb52e8b7655e99ea027b1bfc3e0088888d5888d931`, EC60-r1 `cbfe7236a7b413d6796a8e1fca2f0374697dc68ccb578f0d2a433f122175b733`. Each version/recipe was committed and pushed before execution.

[Producer](../../notes/400-synthetic/produce.py), [pre-execution recipe and revisions](../../notes/400-synthetic/recipe.md), and each `construction.json`/`record.json` record every edit's actual address/register, old/new value, source and purpose. Country20/Holland is the existing managed side1 (manager129 unchanged). Isolated frames use existing SS3875, SP3800 and synthetic BP0 root, stopping before the original caller continuation. EA09 additionally receives parent static link3C00/country20 at-5. These roots are artificial. E062 preserves original CPU and caller stack; squad slot10/player390→0 and DS9B41 0→1 enable the original zero first-selection branch; parent first-selection flag was already0. Keeper381 remains intact.

| Input | Full raw snapshot SHA256 |
|---|---|
| role3-r2/input.ucstate | `0c096ee73d3be86dba4bb2f145762299a0086bdc8bc55298425e2b23033f31ae` |
| role4-r2/input.ucstate | `d776b78f0b8e559cfe42664dca4b4da3e430a211b825a4cbe73502c31a6fe48e` |
| E062-r2/input.ucstate | `a648f87fa04ae70224e5e6a052daa4998a14ee91d1b8c5f1fd5bd85f4ee08ed4` |
| EC60-r1/input.ucstate | `769934144d99e1dceb2a9015122401245bd2b2884320e9a960adef486b04188b` |

## Original controls, stopped machines and expected/observed results

Both takers independently restore the same constructed input for each sequence: **UpAC, DownB1, Enter0D**; **C63**; **Esc1B**; **no key through original1000-poll timeout**; **Space20→CF3A blocking read→Return0D→same selector→Enter0D**. Complete concatenated keys: `[172,177,13,99,27,32,13,13]`; default supplies no key. Live highlight4→3→4 verifies Up/Down. Expected/observed: all five sequences return available player384 in AX to6D74 and store384 at the role's DS9976+10*side+2*role. C executes original1FDD and happens to choose the same player. Esc/timeout retain the stored pick. Space actually blocks at214B:08DD with return0791:CF3A; Return reaches CC54 before final Enter.

CC54 is inside CC2E BP37D6, linking to CC7B BP37EA, return6D74. CC7B's low-byte arguments are role3/4 and side1 (actual scratch high bytes0E retained). Parent6D4E BP37F4 has `[bp+4,+6,+8]` `[10,3,1]` or `[11,4,1]`, return6EEF/6F92; wrapper BP37FE has synthetic root0. At CF3A current BP is CC7B37EA. Raw frame words cover offsets-16..+16 by2: parent[bp], near return[bp+2], far segment[bp+4]. `site` is meaningful as a far keyboard return only in read/poll rows; pre-entry/near-boundary stack words are not live far callers. Actual PC is recorded separately in every row.

Both refusals wait at214B:08DD, return214B:098A, nested under original0983,04F8 and1765. The live1765 far return is0791:E062/EC60. E062 displays “There is no player here”; keys `[13,13]` trigger/dismiss and return to E61F, still unmarked. EC60 displays “Holland has a vacancy in the first team”; key `[13]` dismisses, helper returns1 and EA09 returns AL0. Actual EB82/EBD7/EC22 returns are each0; actual vacancy counter1 and keeper count1 are captured at the wait. No earlier warning was substituted/dismissed.

EA8F's fill covers the counter **before** scanning/counting, so it does not erase this vacancy afterward. Existing in-match DS0C1F=1 follows original EA09's in-match validation rules; it is unchanged. This fixture needs no counter-local edit. This corrects any inference that the fill alone prevents entry-to-exit vacancy construction, without claiming natural generation of a zero word.

Every raw `.ucstate` ZIP holds full1.1MiB memory, all16 CPU registers and load. Research RawIO changes only host keyboard stop/classification policy: poll AL0/1; read storage/AL/retf use the pinned unchanged Core._answer. Original game behavior runs under Unicorn. Unsupported waits remain at their actual PCs and resume directly, without rewinding into supported Core saves.

## Exact reproduction and limits

From a source clone of the research head, with Python/Unicorn and authenticated rclone `goal2drive`, starting with an empty cache:

```sh
set -e
mkdir -p .cache/400-synthetic/readback
rclone copyto --drive-root-folder-id 1b5VlP-nFHkWilG576gQj1P4iwERF9S7a goal2drive:t92-fixtures-v2-private.zip .cache/400-synthetic/readback/t92-fixtures-v2-private.zip
cp .cache/400-synthetic/readback/t92-fixtures-v2-private.zip .cache/400-synthetic/t92-fixtures-v2-private.zip
unzip -n .cache/400-synthetic/readback/t92-fixtures-v2-private.zip -d .
python3 notes/400-synthetic/verify.py
tools/heavy.sh --slots 4 T92-replay -- python3 notes/400-synthetic/replay_all.py replay-r1
```

One exact replay: substitute CASE=role3/role4/E062/EC60 and ORIGINAL=role3-r2/role4-r2/E062-r2/EC60-r1, respectively; use a fresh attempt name:

```sh
tools/heavy.sh --slots 4 T92-one -- python3 notes/400-synthetic/produce.py CASE fresh-name --base .cache/400-synthetic/ORIGINAL/base.g2core --replay .cache/400-synthetic/ORIGINAL/input.ucstate
```

Omit `--replay` to reconstruct from the untouched base. The offline verifier independently applies every recorded edit and requires exact equality with the constructed input, then verifies every stop. Every attempt is limited to60 seconds including independent controls; standard four slots, no waiver. Actual role3-r1/r2:1.353/1.281s; role4-r1/r2:1.100/1.078s; E062-r1/r2:0.060/0.048s; EC60-r1:0.044s. All failures/superseded receipts remain immutable: E062-r1 reached/dismissed but failed a wrong observer return-site assertion; taker-r1 used B0 instead of UpAC and do not supply Up coverage. One source-justified revision per affected case; no campaigns, random sweep or further construction revision.

Actual empty-cache reproduction downloaded into fresh source `git archive2a740adb` at `/tmp/T92-clean-reproduction`. All36 final replay stops, full memory/register ZIP hashes, frames, text, keys and observer events were byte-identical; times1.183/0.988/0.042/0.043s. [Immutable reproduction receipt and raw metadata](../../notes/400-synthetic/clean-reproduction-r1/receipt.json) disclose the initial missing readback directory (fixed before verification passed), and raw `record.head` being the external GIT_DIR's primary HEAD rather than extraction2a740adb; producer hash independently pins actual executed source. No raw record rewritten. Replay snapshot bytes are already present identically in the private bundle.

Independent review and required CI precede research merge. §14 delivery must cite merged evidence and preserve consumer Live cells and F029/F030 proposed status. No goal2 runtime/vendor edits or goal2 merges. Stop after this delivery; no automatic inventory or collection.
