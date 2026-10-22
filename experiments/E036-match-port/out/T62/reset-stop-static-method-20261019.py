"""Static candidate inventory for #336; no original execution or classifier."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
root=Path('/home/diego/projects/goal2-archaeology')
work=root/'.claude/worktrees/agent-a55a365b32cd67a36'
out=work/'experiments/E036-match-port/out/T62/reset-stop-static-20261019.json'
assert not out.exists(),'Retain immutable prior output'
pin='424d5998076da1e4efc399c2715689ddb44d3e1a'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
sha=lambda b:hashlib.sha256(b).hexdigest()
files={};writes=[]
for listing in sorted((root/'static/goal-exe/code').glob('seg_0791_*.asm')):
 data=listing.read_bytes();name=str(listing.relative_to(root))
 old=subprocess.check_output(['git','show',pin+':'+name],cwd=root)
 assert old==data,(name,'listing differs from downstream pin')
 files[name]={'sha256':sha(data),'same_at_requested_pin':True}
 routine=None
 for number,line in enumerate(data.decode().splitlines(),1):
  header=re.match(r'; ---- routine (\S+)',line)
  if header:routine=header[1]
  found=re.search(r'mov (byte|word) ptr \[0x(9b55|8325|8302|9b41|7c39)\], (.+)$',line)
  if found:writes.append({'routine':routine,'offset':'0791:'+line[:4],'path':name,'line':number,'width':found[1],'ds_offset':found[2].upper(),'value_expression':found[3],'listing_line':line})
kit=subprocess.check_output(['git','show',pin+':runtime/original_match/match.py'],cwd=root)
text=kit.decode();start=text.index('    def _on_tick(');end=text.index('\n    def ',start+1)
result={'kind':'static-only candidate inventory; proposed, not independent review or runtime corroboration','created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'issue':336,'requested_kit_pin':pin,'read_checkout_head':head,'listing_files':files,'kit_path':'runtime/original_match/match.py','kit_sha256':sha(kit),'tick_handler_at_requested_pin':text[start:end],'direct_literal_mov_writes':writes,'limits':['Only direct literal mov writes to five selected candidate globals; indirect stores, other instructions and other globals are not exhaustively inventoried.','An instruction write is not proof of observability at a completed-tick stop.','No game runs, seed coverage, state predicate or interpolation design is claimed.','No T62/T64/T69 runtime, test, annotation or queued input changes.']}
out.write_text(json.dumps(result,indent=2)+'\n')
print(len(writes),'direct selected candidate writes; requested pin matches',len(files),'raw listing files; no classifier claimed')
