import sys,json
from pathlib import Path
sys.path[:0]=['runtime','experiments/E040-route-fixture-writes/out/T125']
import prove
from original_match import port
from original_match.assistant import _ports
from original_match.port.prove import Prover
source,sha=prove.image()
for case in ('improve','finals','tour'):
 m=prove.prepare(source,0,case)
 def read_key(replay):m.wr(0xA976,0x0D0D);m.return_from(True)
 def keypressed(replay):m.set_reg('ax',(m.reg('ax')&0xFF00)|1);m.return_from(True)
 class Keys:
  def key(self,site):m.wr(0xA976,0x0D0D);m.set_reg('ax',(m.reg('ax')&0xFF00)|13);return 13
  def keypressed(self,site):return True
 # The menus port supplies these same boundary operations.
 inst=port.install(m,list(_ports()),keys=Keys());p=Prover(m,inst)
 try:prove.call(m,'0791:DC7E');print(case,'passed')
 except Exception as e:print(case,type(e).__name__,str(e))
 print(json.dumps({k:v for k,v in p.summary().items() if v['proved'] or v['nested']},sort_keys=True))
