"""Development-only static completeness audit; never loaded by the engine."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[4]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);a=ap.parse_args()
    text=(ROOT/'static/goal-exe/code/seg_000E_02.asm').read_text()
    text=text[text.index('; ---- routine 000E:11D9'):]
    # Independent lexer: remove each complete byte token, then read mnemonic.
    rows={}
    for line in text.splitlines():
        parts=line.split()
        if not parts or not re.fullmatch('[0-9A-F]{4}',parts[0]):continue
        pc=int(parts[0],16);k=1
        while k<len(parts) and re.fullmatch('[0-9A-F]{2}',parts[k]):k+=1
        if k>1 and k<len(parts):rows[pc]=' '.join(parts[k:])
    assert min(rows)==0x11D9 and max(rows)==0x1F4A
    frame={0x11D9,0x11DA,0x11DC,0x1F47,0x1F49,0x1F4A}
    jumps={pc for pc,ins in rows.items() if ins.startswith('jmp ')}
    source=(ROOT/'runtime/original_match/port/news.py').read_text();source=source[source.index('\n\ndef _result_call'):]
    represented=Counter(int(x,16) for x in re.findall(r'# ([0-9A-F]{4})\b',source))
    missing=set(rows)-set(represented)-frame-jumps;extra=set(represented)-set(rows)
    assert not missing and not extra,(sorted(missing),sorted(extra))
    assert 0x1B9B in represented
    gen=ROOT/'experiments/E040-route-fixture-writes/out/T122b/generate_result_column.py'
    subprocess.run(['python3','-B',str(gen),'--check'],cwd=ROOT,check=True)
    record={'schema':'e040-t122b-transcription/1','task':'T122b',
      'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'listing_rows':len(rows),'represented_unique_pcs':len(represented),'represented_statements':sum(represented.values()),
      'missing_semantic_instructions':sorted(missing),'extra_pcs':sorted(extra),
      'folded_frame_pcs':[f'{pc:04X}' for pc in sorted(frame)],
      'folded_frame_reason':'push BP / mov BP,SP / sub SP,308 are Regs.enter(308); mov SP,BP / pop BP / ret2 are _end and registry ret2',
      'folded_unconditional_jumps':[f'{pc:04X}' for pc in sorted(jumps)],
      'folded_jump_reason':'acyclic edges become structured Python flow or direct shared-suffix generator calls; no decoder/dispatch loop',
      'duplicate_statement_pcs':{f'{pc:04X}':n for pc,n in represented.items() if n>1},
      'six_byte_cmp_1B9B_present':True,
      'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'runtime/original_match/port/news.py',gen,Path(__file__),ROOT/'static/goal-exe/code/seg_000E_02.asm']}}
    if a.out:
        assert not a.out.exists();a.out.write_text(json.dumps(record,indent=1)+'\n')
    print(json.dumps({k:record[k] for k in ('listing_rows','represented_unique_pcs','represented_statements','missing_semantic_instructions','extra_pcs','six_byte_cmp_1B9B_present')}))

if __name__=='__main__':main()
