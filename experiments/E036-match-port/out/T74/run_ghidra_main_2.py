import json,subprocess,time
from pathlib import Path
o=Path(__file__).resolve().parent
cmd=['env','-u','JAVA_TOOL_OPTIONS','bash','tools/static/decompile.sh','--annotations','static/goal-exe/annotations','.cache/artifacts/goal2-a949da2f/GOAL.EXE','static/goal-exe/named']
start=time.time()
with (o/'ghidra-regeneration-2.log').open('x') as f:
 r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
(o/'ghidra-regeneration-2.exit').write_text(str(r.returncode)+'\n')
(o/'ghidra-regeneration-2-time.json').write_text(json.dumps({'seconds':time.time()-start,'command':cmd})+'\n')
sys_exit=r.returncode
raise SystemExit(sys_exit)
