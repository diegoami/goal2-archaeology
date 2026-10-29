#!/usr/bin/env python3
"""Pinned-source architecture inventory and compatibility proposal; no engine construction/calls."""
import argparse,json,subprocess,sys,tempfile
from pathlib import Path
from check import ROOT,BASE,git,sha,original,reference,pin,validate,write_new
def inventory():
 paths=git('ls-tree','-r','--name-only',BASE,'--','runtime/original_match').decode().splitlines()
 paths=[p for p in paths if p.endswith('.py')]
 hashes={p:sha(original(p)) for p in paths}
 # This source export is not a worktree or image. Only registry definitions are loaded.
 with tempfile.TemporaryDirectory(prefix='T110-frozen-registry-') as tmp:
  for p in paths:
   target=Path(tmp)/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original(p))
  code="""import json,sys
sys.path.insert(0,sys.argv[1])
from original_match.port import load
modules=[];addresses=[]
for reg,variant in load(['all']):
 modules.append(dict(name=reg.name,entries=len(reg.entries),declared_stubs=sum(e.stub is not None for e in reg.entries.values()),variants=len(reg.variants)))
 addresses.extend(reg.entries)
assert len(addresses)==len(set(addresses))
print(json.dumps(dict(modules=modules,entries=len(addresses),addresses=sorted(addresses))))
"""
  out=subprocess.check_output([sys.executable,'-B','-c',code,str(Path(tmp)/'runtime')],cwd=tmp,text=True)
 result=json.loads(out);result['source_files']=hashes
 result['method']='Import frozen registry definitions only; no Match, original image or registered routine invoked.'
 return result
def row(i,claim,validation,limits,*refs):
 return dict(id=i,claim=claim,validation=validation,limits=limits,obligations=[i],sources=[reference(p,n) for p,n in refs])
def build():
 rows=[
 row('arithmetic','Retain byte/word wrapping, signed reads, truncation, staged clamping and 40-bit Real rules; names do not imply host integers/floats.',
 'Reused T98 numerical records and existing original-differential tests; full wrapper state still needs its own boundary comparison.',
 ['376 retained strength returns and other sampled tests are not all-input equivalence; Real multiply/divide/ln/exp not fully hand-traced.'],
 ('runtime/original_match/port/attributes.py','def idiv('),('static/goal-exe/code/seg_1771_05.asm','37D6'),('docs/engine-study/strength-formulas.md','trunc_div')),
 row('random-order','Preserve both PRNG streams, their cursors and conditional consumption; failed moves and branches consume actual draws in sequence.',
 'Compare ordered draw/write/site traces plus final seeds/cursors, not just initial seed or score.',
 ['Equal initial seeds do not preserve later alignment after changed branches.'],
 ('runtime/original_match/port/geometry.py','def draw_table_byte('),('static/goal-exe/code/seg_0791_14.asm','8AD1'),('docs/engine-study/movement.md','Every failure')),
 row('occupancy','Keep the simulation-visible picture character and attribute words, background restoration, update order and special-player exemptions.',
 'Retained T101 blocked-step/control examples; later candidate needs complete picture/write and RNG trace comparisons.',
 ['A boolean occupancy grid or a render-only replacement changes a branch; natural incidence is not measured here.'],
 ('runtime/original_match/port/motion.py','PICTURE, BACKGROUND'),('static/goal-exe/code/seg_0791_14.asm','86D0'),('docs/engine-study/movement.md','attribute 0x0D')),
 row('event-order','Preserve event kind, full data, score/minute stamps and ordering at the original writes, including provisional goals and rollback.',
 'Existing stamp/order and original/port Engine controls; a later candidate must preserve the full externally observed stream.',
 ['Result equality alone hides intermediate events and effects.'],
 ('runtime/original_match/match.py','def _on_score('),('runtime/original_match/match.py','def _flush('),('runtime/original_match/README.md','**Order**:')),
 row('decisions','Preserve pending/queued events, answer contexts, refusal/re-entry, pause and optional taker interactions at existing public boundaries.',
 'Compare remaining event stream and state before/after answers, including refused answers and defaults.',
 ['No claim of fresh genuine original-key reachability; #400 remains separate.'],
 ('runtime/original_match/match.py','def answer('),('runtime/original_match/README.md','**Decisions**')),
 row('modes','Keep watched, quick and outer silent-result paths distinct; public Match does not reproduce the whole campaign router.',
 'Use actual admitted family modes and retained per-path comparisons; never substitute quick/silent outcomes for watched effect measurements.',
 ['T79 broad fidelity and natural reachability remain separate; current inventory is not path coverage.'],
 ('runtime/original_match/port/frame.py','0791:97D0'),('docs/engine-study/inventory.md','A quick or silent result')),
 row('phase-tail','Keep F1F6 match completion separate from B7FA player update; public completion includes post-fixture continuation.',
 'Compare pre-update versus finished records, result events and all post-update player bytes under the chosen boundary.',
 ['Outer campaign news/sacking/router effects are not automatically part of Match.'],
 ('runtime/original_match/match.py','def _advance('),('runtime/original_match/match.py','PLAYER_UPDATE'),('docs/engine-study/match-flow.md','B7FA')),
 row('public-api','Preserve original default, explicit engine identity, event/answer/result grammar, complete player/country records and adapter behavior.',
 'Existing Engine/records/admission tests plus downstream #427 obligations; version any deliberately changed interface.',
 ['No sealed delivery or checkpoint/default acceptance is implied by m7 or this assessment.'],
 ('runtime/original_match/match.py','engine="original"'),('experiments/E036-match-port/records.py','def validate('),('runtime/original_match/README.md','## Competitive fixtures')),
 row('checkpoints','Preserve supported original-engine event-boundary continuation and pending answers; plain engine=port save/load is explicitly refused at m7.',
 'Existing original replay/boundary tests and explicit port refusal; future port support must prove its own event/state/RNG reconstruction.',
 ['T78c/T80 may advance independently later; do not project those capabilities backwards onto this source baseline.'],
 ('runtime/original_match/match.py','def save('),('runtime/original_match/match.py','port/unknown engine checkpoint'),('runtime/original_match/match.py','def _load_replay(')),
 row('identities','Keep far-pointer offset wrapping, aliasing, player/country/pitch identity and cached field lifetimes explicit; typed views share storage.',
 'Pointer-edge/sentinel tests and read/write traces around rebind/setup; preserve unnamed bytes and packed words.',
 ['Copying a record or refreshing a cache can change behavior even when visible fields have the same names.'],
 ('runtime/original_match/port/attributes.py','class Rec:'),('runtime/original_match/port/attributes.py','return (self.seg << 4)'),('docs/engine-study/transient-state.md','cached')),
 row('machine-state','For in-place readability changes preserve the existing boundary ABI, physical writes/sites and unmasked state; do not silently discard stack/register observations.',
 'Candidate-versus-accepted-port full boundary snapshots/traces plus independent original comparisons under the existing disclosed contract.',
 ['T106 has0/18 joint full-memory/all-captured-register equality; #591 alias/liveness gap is unresolved, not a new permitted mask.'],
 ('docs/engine-study/micro-probes.md','0/18'),('docs/engine-study/audit-boundaries.md','complete transitive liveness'),('runtime/original_match/port/guest.py','class PortFrame')),
 row('evidence-scope','Keep historical producers, fixtures, reachability, no-op/mutation coverage and proposed interpretations distinct from design choices.',
 'Preserve old records; reuse T95/T98/T101/T106/T109 evidence with exact scope and owner decisions. Any new prototype needs a new contract/oracles/budget.',
 ['No T107 effect interval, natural incidence, exhaustive fidelity or production rewrite approval exists here.'],
 ('docs/engine-study/t107-revision-proposal.md','#'),('docs/engine-study/micro-probes.md','Synthetic direct calls'),('docs/engine-study/inventory.md','423 unique registered')),
 ]
 inv=inventory()
 d=pin('T110a',__file__,rows,['The code being assessed','Compatibility levels','Twelve obligations','Validation and boundary decisions'],
  inventory=inv,compatibility_levels={
   'machine-boundary':'Existing routine ABI/effects plus explicit full-state diagnostics; preserve known differences and caller/liveness limits.',
   'public-api-records':'A different contract that may remove DOS internals only after explicit owner choice and end-to-end evidence; not adopted.',
   'redesigned-semantics':'Deliberately changed football rules; separate owner design and validation project; not fidelity-preserving.'
  },adopted_weaker_contract=False,research_engine_calls=0,prototype_implemented=False)
 d['sources'].update(inv['source_files'])
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args()
 d=build()
 if a.check:
  p=ROOT/'notes/engine-study/T110/T110a-v1.json';old=json.loads(p.read_text());assert sha(Path(__file__).read_bytes())==old['producer']['sha256']
  d['producer']=old['producer'];assert d==old,'inventory/contract ledger differs'
  validate('T110a',old,(ROOT/'docs/engine-study/rewrite-contract.md').read_text());print('PASS:12 obligations and frozen registry inventory reproduced; no engine call')
 else:
  assert a.out;write_new(a.out,d);print(json.dumps({'modules':len(d['inventory']['modules']),'entries':d['inventory']['entries'],'obligations':len(d['rows'])}))
if __name__=='__main__':main()
