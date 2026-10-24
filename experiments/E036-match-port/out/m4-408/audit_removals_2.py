"""Bounded static audit of all 31 original B removals, not a reachability proof.

Named bodies were read before the raw listing. This combines the hand-read
effects below with exact listing writes/calls and the immutable native census.
Absence of a direct store is never treated as absence of indirect state writes.
"""
import ast,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
base='6342c48dda5c513dca8df39101475695134683fb'
source=subprocess.check_output(['git','show',base+':runtime/original_match/port/display.py'],cwd=ROOT,text=True)
tree=ast.parse(source)
returns=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='RETURNS' for a in n.targets))
loop=next(n for n in tree.body if isinstance(n,ast.For));removed=sorted(set(returns)-ast.literal_eval(loop.body[0].test.comparators[0]));assert len(removed)==31
inventory={r['address']:r for r in json.loads((ROOT/'experiments/E036-match-port/out/T73/static-inventory.json').read_text())}
named={r['address']:r for r in csv.DictReader((ROOT/'static/goal-exe/named/index.tsv').open(),delimiter='\t')}
census=ROOT/'experiments/E036-match-port/out/T73/coverage-unported-desktop-20261023/coverage-unported.jsonl'
native=[json.loads(line) for line in census.read_text().splitlines()];assert len(native)==62
# Every row describes original writes, including callees; these are not claims
# that the present void stub implements the original outside declared states.
effects={
'0791:006C':('observed-output-elision','Local ratio/frame; two 00DB calls write attributes through DS:A96E. No direct global scalar store.','Sole caller 0106 replaces scratch result; output/stack equivalence is bounded by the B ablation and joint ALL62, not arbitrary destinations.'),
'0791:0425':('observed-output-elision','Saved BP and optional 1E09 busy-wait/frame; no direct persistent scalar store.','Calls from 72F2,798D,7E60,94E8,970C; omission is the declared elapsed-delay boundary, not a no-stack-write claim.'),
'1771:0AF8':('observed-output-elision','Local manager pointer; 026D writes a status string through DS:A96E.','157D reloads the next country expression; zero-manager and visited status bands bound the existing ALL proof.'),
'1771:1527':('observed-output-elision','Local country pointer; 10E7 is read-only except its frame; 026D writes the rating label through DS:A96E.','157D reloads a manager byte after this call. Buffer/stack omission remains observational, not state-free.'),
'1771:3947':('observed-overwritten-global','Direct DS:AAB2=70h at 3961; locals and twelve 00DB attribute writes through DS:A96E.','Sole caller 42BC:4651. Later status paths set an explicit attribute or AAB2=15 at 47CD before further current-attribute reads; see frozen ablation-static-1.md. Not a no-global-write routine.'),
'1771:50F1':('unreached-stateful','Via 1560, writes DS:0C1B cursor and key state. Conditional 4859 edits player-name data; 4E22 writes display buffers. Own locals also change.','Callers E949 and 26B9. E949 unmanaged branch enters it; no ordinary-input witness is supplied by ALL62. Not proved generally removable.'),
'1771:5C94':('unreached-return-value','Frame/locals and AX fixture-winner result; no direct heap/global store.','Return is meaningful to campaign and bracket callers. Incoming-AX stub is not a general implementation; census supplies no execution proof.'),
'1771:5CCB':('unreached-return-value','Frame/locals and AX fixture-loser result; no direct heap/global store.','Return is meaningful to campaign and bracket callers. Incoming-AX stub is not a general implementation; census supplies no execution proof.'),
'1771:883F':('unreached-stateful','Direct DS:AAB2=7 at 8881. 0329/026D/01A3 write template/text; number/character helpers write local strings.','Callers 9028 and 9509 are also unvisited. This is stateful, not proved pure by a zero count.'),
'1771:89C1':('unreached-stateful','0329 writes the DS:A96E target; 13C5 writes selector attributes.','Reached only through unvisited competition selector/bracket paths in this census. No general no-write claim.'),
'1771:89FE':('unreached-stateful','13C5 writes selector attributes via the current buffer pointer; own frame/local pointer writes.','89FE is called by 8A5D. Zero execution is not a proof that buffer effects are disposable.'),
'1771:8A5D':('unreached-stateful','0329 template writes plus the 89C1/89FE attribute writes.','Callers include retained 8E9A and unvisited 9028/91CE. No static unreachability claim is made.'),
'1771:8CCF':('unreached-stateful','Fixture/name/score drawing writes buffers; conditional 02C8 also sets DS:AAB2. Own fixture pointer locals change.','Bracket callers 8D84/91CE/937C; no execution witness in ALL62.'),
'1771:8D84':('unreached-stateful','Locals; transitive name/fixture/8CCF rendering, including the latter conditional AAB2 store.','Called by retained 8E9A. This audit does not infer unreachability from the sample.'),
'1771:9028':('unreached-stateful','Writes parent SS country/group locals (including 9050,90A5,91C4); 1560 changes parent selection/key state; 883F writes AAB2; renderers write buffers.','Called by retained 958D. Parent-frame and key effects make it stateful even without a direct default-DS scalar store.'),
'1771:91CE':('unreached-stateful','Own locals and transitive template/selectors/bracket buffer writes; child 8CCF may set AAB2. Winner/loser results are consumed.','Called by 9509; no execution witness. Not classified pure merely because the outputs are text.'),
'1771:937C':('unreached-stateful','Own locals and transitive selector/bracket/template writes, including conditional AAB2; meaningful fixture winner/loser reads.','Called by 9509; no execution witness. Not a general void-equivalent body.'),
'1771:9509':('unreached-stateful','883F and brackets change attribute/buffer state; 025D copies 4000 bytes A96E to A96A; 08DD changes key state.','Called by retained 958D. A copy/read boundary cannot be declared pure from its zero count.'),
'214B:0661':('unreached-device-boundary','Register packet in its SS frame; 235C:000B INT10 cursor operation may write packet results.','Startup/DOS-shell callers 0813/206A; no observed in-match execution. Hardware output and stack effects are separate categories.'),
'214B:0755':('unreached-stateful','Direct DS:A964 and DS:A96A/A96C screen pointer stores; conditional 2382:016D also changes CRT globals.','Callers 0813/206A are startup/DOS-shell paths; no normal-match witness. Not a state-free routine.'),
'214B:1E5A':('corrected-by-408','Direct DS:A9FC toggle at 1E6E; frame and 1E8D call/return effects.','Ordinary 9372 A7 input reproduced despite zero census calls. Retained now; native differential and actual key-poll proof cover it.'),
'214B:1E75':('observed-device-elision','Saved BP, conditional IN/OUT and AL/flags. No direct non-stack memory store.','Used by jingle/frequency paths. Hardware omission is deliberate; preserved incoming registers are a scoped reduction, not standalone CPU equivalence.'),
'214B:1E8D':('corrected-by-408','Saved frame and conditional AL input result/flags; no direct persistent DS scalar store.','Now retained so its caller-frame/return effects match the original, including the new A7 path. Only hardware output remains omitted.'),
'214B:1EA1':('observed-device-elision','Frame; frequency child overwrites its copied argument; delay/off children have stack/register effects. No direct persistent scalar store.','34C1/539F do not retain a tone result; original B ablation/joint match bounds the omission.'),
'214B:1EBC':('observed-device-elision','Frame and copied stack argument overwritten by divisor at 1EDE; speaker-on/division effects; hardware port writes.','94E8 reloads speed/clears AH; 1EA1 proceeds to delay/off. Neither reuses the popped argument. Not a general no-memory-write body.'),
'2382:0099':('unreached-stateful','Explicit ES=0040 BIOS byte 0087 AND/OR stores, plus INT10 device effects. Stack pushes preserve AX.','CRT initialization/text-mode callers; this is a non-DS memory writer, not pure output by default.'),
'2382:00E7':('unreached-stateful','Direct DS:AAB0,AABA,AAAF,AAAE,AAB4,AAB6 stores and INT10 calls.','CRT initialization/016D callers; no execution witness. Globals cannot be ignored as if the body were empty.'),
'2382:016D':('unreached-stateful','Direct DS:AAB2 from AABC; transitive BIOS byte and CRT global stores via 0099/00E7.','0755 text-mode initialization caller; no normal-match witness. Explicit stateful boundary.'),
'2382:0215':('unreached-device-boundary','Window bounds are read; 04FC/0608 performs cursor INT10 and register saves. No direct scalar store.','0813/136B callers; no observed match execution. Device/stack effects remain documented.'),
'2382:04FC':('unreached-device-boundary','Sets AH/BH and tail-jumps to 0608; transitive saved registers/INT10.','Tail control transfer is not a ret body; retained return metadata records it. No general CPU-equivalence claim.'),
'2382:0608':('unreached-device-boundary','Push/pop SI,DI,BP,ES around INT10; potential device state, no explicit persistent scalar store.','CRT unit callers; no execution witness. Device and stack effects are not inferred absent.'),
}
assert set(effects)==set(removed)
rows=[]
for address in removed:
 r=inventory[address];path=ROOT/r['listing'];lines=path.read_text().splitlines();start=r['line']-1
 end=next((n for n in range(start+1,len(lines)) if lines[n].startswith('; ---- routine')),len(lines))
 writes=[];calls=[]
 for line_no,line in enumerate(lines[start:end],start+1):
  m=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s+)+([a-z].*)$',line)
  if not m:continue
  pc,ins=m.groups();op=ins.split()[0];operand=ins.partition(' ')[2].split(',')[0]
  if op in ('mov','and','or','add','sub','inc','dec','xchg','xor','neg','not') and '[' in operand:writes.append({'pc':pc,'line':line_no,'instruction':ins})
  if op in ('call','int') or (op=='jmp' and pc=='0500'):calls.append({'pc':pc,'line':line_no,'instruction':ins})
 nr=named[address];classification,description,scope=effects[address]
 rows.append({'address':address,'classification':classification,'original_nonstack_and_callee_effects':description,'scope_and_limit':scope,'native_ALL62_calls':sum(n['counts'][address] for n in native),'raw':{'file':r['listing'],'line':r['line'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()},'named':{'file':'static/goal-exe/named/'+nr['file'],'line':int(nr['line'])},'explicit_memory_destination_instructions':writes,'calls_or_interrupts':calls,'direct_callers':r['callers'],'direct_callees':r['callees']})
receipt={'owner_decision':'2026-10-24: statically check all 31 original B removals for state writes, including unvisited routines','candidate_reviewed':base,'method':'Named bodies then raw listings and direct callers; transitive writes are explicitly listed, not excluded by a direct-store scan','original_census':str(census.relative_to(ROOT)),'census_sha256':hashlib.sha256(census.read_bytes()).hexdigest(),'census_matches':62,'audited':31,'mask_changed':False,'scope_warning':'This is a static inventory. Zero calls do not prove unreachability or removability. Unreached stateful stubs remain an explicit coverage limit; no arbitrary-input or standalone equivalence is claimed.','rows':rows}
with (OUT/'removal-state-audit-2.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
text=['# Static state-write audit of the 31 original T73 removals','',receipt['owner_decision'],'',receipt['method']+'.','',receipt['scope_warning'],'','Direct DS scalar writers are 1771:3947,1771:883F,214B:0755,214B:1E5A,2382:00E7 and2382:016D. The CRT 0099 additionally writes BIOS memory 0040:0087. Indirect buffer, attribute, key and parent-frame writes are included below. Saved frames/arguments are memory effects too.','', '| Routine | Native ALL62 calls | Classification | Original effects | Scope / evidence limit |','| --- | ---: | --- | --- | --- |']
for r in rows:text.append(f"| {r['address']} | {r['native_ALL62_calls']} | {r['classification']} | {r['original_nonstack_and_callee_effects']} | {r['scope_and_limit']} Raw `{r['raw']['file']}:{r['raw']['line']}`. |")
text += ['','The 3947 overwrite argument is already documented in immutable `out/T73/ablation-static-1.md`; its 638 native entries are not hidden. The corrected 1E5A/1E8D differ from that observational reduction: a persistent mute flag and the newly admitted call chain require their original effects.','', 'All original records, profile and reference bytes are retained. The stricter audit changes no comparison field and authorizes no DS mask.']
with (OUT/'removal-state-audit-2.md').open('x') as f:f.write('\n'.join(text)+'\n')
print('PASS: all 31 original removals inspected; direct, indirect, parent-frame, BIOS and return effects recorded; no zero-count safety inference')
