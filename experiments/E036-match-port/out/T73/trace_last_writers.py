"""Original-only final-writer diagnostic for missing memory effects, NEVER mask evidence.

Focus locations come from a candidate diagnostic only to prioritize porting. This
observer records no values or original bytes and cannot establish read liveness.
Stack writes are observable without the perturbing raw stack READ hook.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
E036 = ROOT/'experiments/E036-match-port'
sys.path.insert(0, str(ROOT/'runtime'))
sys.path.insert(0, str(E036))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare
import families
import family
import records
from watch_accesses import owner
from original_match import Image
from original_match.assets import reference_image
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE

HELPERS = ('23E4:0644', '214B:0147', '23E4:025D', '214B:003C')

class LastWrites:
    def __init__(self, focus):
        self.focus = focus
        self.last = [None]*65536
        self.pc = None
        self.placements = {}
        self.callers = {}

    def install(self, match):
        m = match.m
        assert not m._ports
        ds, load = m.DS*16, m.load*16

        def placement(pc):
            if pc not in self.placements:
                routine = owner(pc-load)
                if routine == 'UNKNOWN':
                    at = f'P+{pc-load:X}'
                else:
                    seg = int(routine[:4],16)
                    at = f'{seg:04X}:{pc-load-seg*16:04X}'
                self.placements[pc] = routine, at
            return self.placements[pc]

        for helper in HELPERS:
            def entered(replay, helper=helper):
                if replay:
                    return
                # All four helpers have far returns in the listing. No register
                # or stack read occurs in a native memory callback.
                ip, cs = m.stack_word(0), m.stack_word(2)
                routine, _ = placement(cs*16+ip)
                self.callers[helper] = m.where(cs,ip), routine
            m.at(helper, entered)

        def code(uc, address, size, data):
            self.pc = address
        m.uc.hook_add(UC_HOOK_CODE, code)

        def changed(start,end,stamp):
            for offset in range(max(start-ds,0),min(end-ds,65536)):
                if self.focus[offset]:
                    self.last[offset] = stamp

        def written(uc, access, address, size, value, data):
            lo,hi=max(address-ds,0),min(address+size-ds,65536)
            if lo>=hi or not any(self.focus[lo:hi]):
                return
            routine,at=placement(self.pc) if self.pc is not None else ('UNKNOWN','UNKNOWN')
            caller,caller_routine=self.callers.get(routine,('-','-'))
            changed(address,address+size,('guest',routine,at,caller,caller_routine))
        m.uc.hook_add(UC_HOOK_MEM_WRITE,written,begin=ds,end=ds+65535)
        assert m.write_tap is None
        def host_write(address,data):
            lo,hi=max(address-ds,0),min(address+len(data)-ds,65536)
            if lo<hi and any(self.focus[lo:hi]):
                frame=sys._getframe(1)
                origin=frame.f_code.co_name
                changed(address,address+len(data),('host',origin,'-','-','-'))
        m.write_tap=host_write

    def report(self):
        spans=[]
        for offset,wanted in enumerate(self.focus):
            if not wanted:
                continue
            stamp=self.last[offset] or ('initial/unwritten','-','-','-','-')
            if spans and spans[-1]['start']+spans[-1]['length']==offset and spans[-1]['writer']==list(stamp):
                spans[-1]['length']+=1
            else:
                spans.append({'start':offset,'length':1,'writer':list(stamp)})
        return spans

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--diff',required=True)
    ap.add_argument('--out-dir',required=True)
    ap.add_argument('--only',default='O8/c1-c2-friendly')
    args=ap.parse_args()
    source=Path(args.diff).read_bytes()
    diff=json.loads(source)
    focus=bytearray(65536)
    for span in diff['regions']['DS']:
        start,end=span['start'],span['start']+span['length']
        assert 0<=start<end<=65536
        focus[start:end]=b'\1'*(end-start)
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=False)
    watcher=LastWrites(focus)
    spec=next(m for f in families.discover().values() for m in f.matches if m.id==args.only)
    t0=time.monotonic()
    rec=family.run_match(Image.from_bytes(reference_image(family.DEFAULT_CACHE)),spec,
                         time_limit=1800,stretch_limit=300,watch=watcher.install)
    (out/'original-record.jsonl').open('x').write(records.dumps(rec)+'\n')
    ref=compare.load(E036/'out/T57/reference.jsonl')
    lines,ok=compare.check(ref,{spec.id:rec},{spec.id:spec.sha256},image_sha256=families.image_sha256())
    (out/'compare.txt').open('x').write('\n'.join(lines)+'\n')
    report={'warning':'Final-write diagnostic only; NEVER mask/read-liveness evidence',
            'match':spec.id,'original_exact':ok,'focus_diff_sha256':hashlib.sha256(source).hexdigest(),
            'elapsed_s':time.monotonic()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'writer_fields':['kind','actual_routine','instruction','shared_helper_return','caller_routine'],
            'spans':watcher.report()}
    (out/'last-writers.json').open('x').write(json.dumps(report,indent=2)+'\n')
    print(lines[-1],flush=True)
    return 0 if ok else 1

if __name__=='__main__':
    sys.exit(main())
