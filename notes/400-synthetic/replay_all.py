#!/usr/bin/env python3
"""Replay the four saved synthetic inputs; compare every stopped machine byte-for-byte."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 suffix=sys.argv[1] if len(sys.argv)>1 else 'clean-r1'
 result=[]
 for case,original in [('role3','role3-r2'),('role4','role4-r2'),('E062','E062-r2'),('EC60','EC60-r1')]:
  attempt=case+'-'+suffix;private=ROOT/'.cache/400-synthetic'/original
  subprocess.run([sys.executable,'notes/400-synthetic/produce.py',case,attempt,'--base',str(private/'base.g2core'),'--replay',str(private/'input.ucstate')],cwd=ROOT,check=True)
  old=ROOT/'notes/400-synthetic'/original;new=ROOT/'notes/400-synthetic'/attempt
  a=json.loads((old/'record.json').read_text());b=json.loads((new/'record.json').read_text())
  assert b['status']=='passed' and b['keys']==a['keys'] and b['events']==a['events']
  assert b['constructed_sha256']==a['constructed_sha256']
  # Includes actual live memory/CPU zip hashes, displayed text, live frames and all labels.
  assert (new/'steps.jsonl').read_bytes()==(old/'steps.jsonl').read_bytes()
  result.append(dict(case=case,original=original,replay=attempt,status='byte-identical',input_sha256=a['constructed_sha256'],stopped_machines=b['observations'],elapsed_s=b['elapsed_s']))
 print(json.dumps(dict(synthetic=True,replays=result),indent=2))
if __name__=='__main__':main()
