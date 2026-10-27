"""Detached, one-shot T78b unittest control with an explicit exit/source receipt."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
root=Path(__file__).resolve().parents[4]
name,target,receipt=sys.argv[1:]
paths=sorted((root/'runtime/original_match').rglob('*.py'))
paths += [root/'tests/test_port_engine.py',root/'experiments/E036-match-port/family.py',root/'experiments/E036-match-port/records.py']
def fingerprints():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=fingerprints()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
start=time.monotonic()
command=['tools/heavy.sh','T78b-'+name,'--',sys.executable,'-B','-m','unittest',target,'-v']
run=subprocess.run(command,cwd=root,stdin=subprocess.DEVNULL)
after=fingerprints()
report={'name':name,'command':command,'source_head_at_start':head,'source_sha256':before,
        'source_unchanged':before==after,'exit_code':run.returncode,'wall_s_including_queue':time.monotonic()-start,
        'finished_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version}
with open(receipt,'x') as output:json.dump(report,output,indent=2);output.write('\n')
raise SystemExit(run.returncode if before==after else 2)
