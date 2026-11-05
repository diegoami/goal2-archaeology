"""Supplement T125's synthetic function-domain matrix with native published records.
Only declared SELECT TEAM context flags are prepared. Original record arrays,
player affiliation/availability/current positions, pools and manager map are retained.
No calendar or full E44F/52CC/menu-path claim; the isolated ABI frame is prove.call's.
"""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'runtime'),str(HERE),str(HERE.parent.parent)]
import prove,sealed as S
from runner import expected
from original_match import port
from original_match.image import Image
from original_match.machine import Machine,REGS,MEM_SIZE
from original_match.port.prove import Prover
from original_match.port.tables import load

ASSETS=['c6b4796bbd02b1ab-e006-0000-r0007.sav',
        '53b69d3dfb964e77-snap-0213-20261011T142027Z.sav',
        'b9f1fe3925f4b8b3-e006-1200-r0009.sav']

def sha(data):return hashlib.sha256(data).hexdigest()
def view(source,m,tables):
    i=Image.__new__(Image);i.memory=bytearray(source.memory);i.memory[:MEM_SIZE]=m.read(0,MEM_SIZE)
    i.header=source.header;i.load=source.load;i.DS=source.DS;i.tables=tables
    return i

def keys(m):
    def read(replay):m.wr(0xA976,0x0D0D);m.return_from(True)
    def poll(replay):m.set_reg('ax',(m.reg('ax')&0xFF00)|1);m.return_from(True)
    m.at('214B:08DD',read);m.at('214B:0723',poll)

def run(out):
    tables=load(ROOT/'static/goal-exe/tables')
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in
      [Path(__file__),HERE/'prove.py',HERE/'sealed.py',ROOT/'runtime/original_match/port/assistant.py',ROOT/'runtime/original_match/assistant.py']}
    for asset in ASSETS:
      data=(ROOT/'.cache/dl'/asset).read_bytes();assert sha(data)==expected(asset)
      source=Image.from_savestate(data);original_fields=S.fields(source)
      prepared=Image.__new__(Image);prepared.memory=bytearray(source.memory);prepared.header=source.header
      prepared.load=source.load;prepared.DS=source.DS;prepared.tables=tables
      edits=[]
      for off in (0xC1E,0xC1F):
        address=source.DS*16+off;before=bytes(prepared.memory[address:address+1]);prepared.memory[address]=0
        edits.append({'field':f'DS:{off:04X}','linear':address,'size':1,'before_sha256':sha(before),
                      'after_sha256':sha(bytes([0])),'changed':before!=bytes([0]),'why':'prepared outside-match SELECT TEAM context'})
      before=S.fields(prepared)
      assert before['records']==original_fields['records']
      assert before['manager']==original_fields['manager'] and before['country']==original_fields['country']
      # Capture actual affiliation/current-position/availability context as counts only.
      def word(address):return int.from_bytes(prepared.memory[address:address+2],'little')
      def far(off):return word(source.DS*16+off)+16*word(source.DS*16+off+2)
      players=far(0xA91B);population=before['squad']+before['pool'];positions={};affiliation={};energy={}
      for player in population:
        rec=players+20*player
        for counter,value in ((positions,prepared.memory[rec+6]),(affiliation,prepared.memory[rec]),(energy,'positive' if 0<prepared.memory[rec+14]<128 else 'unavailable-energy')):
          counter[str(value)]=counter.get(str(value),0)+1
      native=Machine(prepared.memory,prepared.load);translated=Machine(prepared.memory,prepared.load)
      keys(native);keys(translated)
      strength=[];swaps=[]
      native.at('1771:377E',lambda replay:strength.append(['call',native.stack_word(4)]))
      for site in ('0791:DD6B','0791:DD7F'):
        def returned(replay,site=site):strength.append([site,native.reg('ax')])
        native.at(site,returned)
      native.at('214B:007B',lambda replay:swaps.append([native.stack_word(i) for i in (4,6,8,10,12)]))
      inst=port.install(translated,['assistant']);p=Prover(translated,inst)
      started=time.monotonic();prove.call(native,'0791:DC7E');prove.call(translated,'0791:DC7E')
      assert native.read(0,MEM_SIZE)==translated.read(0,MEM_SIZE),'full native/port memory mismatch'
      assert all(native.reg(r)==translated.reg(r) for r in REGS),'native/port ALLREGS mismatch'
      summary=p.summary();assert summary['0791:DC7E']['proved']==1
      assert not any(v['scratch'] for v in summary.values())
      expected_image=view(source,native,tables);expected_fields=S.fields(expected_image)
      state=prepared.state(tables)
      child=subprocess.run([sys.executable,'-B',str(HERE/'sealed.py'),'--child'],input=json.dumps(state),text=True,capture_output=True)
      if child.returncode:raise RuntimeError(child.stderr)
      result=json.loads(child.stdout)
      assert result['fields']==expected_fields,'native/sealed allocated record/selection/RNG mismatch'
      assert result['normalized_state_sha256']==S.normalized(expected_image.state(tables)),'whole normalized native/sealed state mismatch'
      assert result['tables_unchanged'] and result['copy_isolated'] and result['unicorn_denied'] and result['exe_denied']
      assert expected_fields['records']['players']==before['records']['players'],'assistant changed native player records'
      # At least the published fresh-career context must exercise real strength,
      # not merely pass through a tour/finals refusal.
      if asset==ASSETS[0]:assert strength and result['result']['allowed']
      record={'schema':'t125-published/1','input_type':'native-published-record-population','asset':asset,'asset_sha256':sha(data),
        'source_image_sha256':sha(bytes(source.memory)),'prepared_image_sha256':sha(bytes(prepared.memory)),
        'source_hashes':source_hashes,'field_edits':edits,'record_arrays_retained':True,
        'active_manager_edited':False,'source_fields':original_fields,'prepared_fields':before,
        'native_context_counts':{'affiliation':affiliation,'current_position':positions,'energy':energy},
        'after_fields':expected_fields,'status':'passed','summary':summary,'port_calls':inst.calls,
        'returned_registers':{r:native.reg(r) for r in REGS},'full_memory_sha256':sha(native.read(0,MEM_SIZE)),
        'full_memory_and_ALLREGS_match':True,'strength_trace':strength,'swap_args':swaps,'sealed':result,
        'elapsed_s':round(time.monotonic()-started,3),
        'scope':'Isolated DC7E on untouched native published player/country/pool/manager records, context flags only. No natural calendar/full E44F journey claim.'}
      with out.open('a') as f:f.write(json.dumps(record,sort_keys=True)+'\n')
      print(asset,'passed','strength_calls',len(strength)//2,'swaps',len(swaps),'refusal',result['result']['refusal'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise SystemExit('immutable output exists')
    run(a.out)
