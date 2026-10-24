"""One real-GUI diagnostic retry, then a complete full-suite rerun on unchanged source."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;PY='/home/diego/.local/bin/python3.12'
command=['tools/heavy.sh','--slots','8','T75-gui-retry-1','--',PY,'-B','-m','unittest','-v','tests.test_human_keys.GuardTests.test_scripted_sitting_produces_one_burst_snapshot_per_key_group']
folder=OUT/'gui-retry-1';folder.mkdir(exist_ok=False)
(folder/'command.json').write_text(json.dumps(command,indent=2)+'\n')
with (folder/'test.log').open('x') as log:r=subprocess.run(command,cwd=ROOT,env={**os.environ,'HARNESS_HEAVY_SLOTS':'8'},stdout=log,stderr=subprocess.STDOUT)
(folder/'test.exit').write_text(str(r.returncode)+'\n')
if r.returncode:raise SystemExit(r.returncode)
raise SystemExit(subprocess.call(['tools/heavy.sh','--slots','8','T75-full-suite-4','--',PY,'-B',str(OUT/'run_full_suite_4.py')],cwd=ROOT,env={**os.environ,'HARNESS_HEAVY_SLOTS':'8'}))
