"""Original-backed isolated function inputs for T122c, never natural-calendar claims.

[confirmed: F039; code/seg_000E_03.asm2071-2389/26F2-2E1E;
F023 builders: continental knockout101..103 at stage4/class0, world8/200..203 at8/class1;
1771:3216/377E/3179/3041 in port/attributes.py; original LCG port/pilot.py.]
Every changed private-memory field is recorded by before/after hash only.
"""
import argparse,collections,datetime,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'experiments/E040-route-fixture-writes'))
from original_match import port,route as R
from original_match.image import Image
from original_match.port.prove import Prover,ProofError
import runner


def step(seed):return (seed*0x7ABD+0x1B0F)&65535

def seed_for(role=None,choice=None,bound=10):
 return next(s for s in range(65536) if (role is None or (step(s)*14>>16)==role) and (choice is None or (step(step(s))*bound>>16)+1==choice))


def cases():
 out=[]
 def add(name,routine='2071',**e):out.append((name,'000E:'+routine,e))
 modes=('gate','no-role','unavailable-squad','equal','improve','ties','pool-unavailable','pool-mismatch','pool-first-unavailable','wrap')
 for routine in ('2071','26F2'):
  for side in (0,1):
   for mode in modes:add(f'pool-{routine}-{side}-{mode}',routine,side=side,mode=mode,seed=seed_for(role=0),result='win',margin=1,kind=2,streak=1)
 for role in range(14):
  for side in (0,1):add(f'role-{side}-{role}',side=side,mode='improve',seed=seed_for(role=role),result='win',margin=1,kind=2,role=role)
 for choice in range(1,11):
  for routine in ('2071','26F2'):
   for side in (0,1):add(f'recommend-text-{routine}-{side}-{choice}',routine,side=side,mode='ties',seed=seed_for(role=0,choice=choice),result='win',margin=1,kind=2,expected_choice=choice)
 for side in (0,1):
  for kind in (0xCB,0x67,0xC9,0x65,0xC8,8):
   for result in ('win','loss'):add(f'column-special-{side}-{kind}-{result}','26F2',side=side,mode='gate',seed=0,result=result,margin=1,kind=kind)
  for streak,bound in ((0,16),(1,4),(2,2)):
   for choice in range(1,bound+1):add(f'column-streak-{side}-{streak}-{choice}','26F2',side=side,mode='gate',seed=seed_for(choice=choice,bound=bound),result='win',margin=1,kind=2,streak=streak)
  for streak in range(3,8):add(f'column-streak-{side}-{streak}','26F2',side=side,mode='gate',seed=0,result='win',margin=1,kind=2,streak=streak)
  for profile,margin,stat3,stat5,bound in (('attack',1,0,0,3),('keeper',1,8,0,3),('general',1,8,1,6),('defence',3,0,0,6),('draw',0,0,0,3)):
   for choice in range(1,bound+1):add(f'column-loss-{side}-{profile}-{choice}','26F2',side=side,mode='gate',seed=seed_for(choice=choice,bound=bound),result='draw' if profile=='draw' else 'loss',margin=margin,kind=2,stat3=stat3,stat5=stat5)
  for confidence in (-11,-10,0):add(f'column-sack-{side}-{confidence}','26F2',side=side,mode='gate',seed=0,result='loss',margin=1,kind=2,year=2,confidence=confidence)
 return out


# Filled from the original call instructions when the driver is authored.
DECISIONS = {8349: '214B:06B1', 8463: '1771:3216', 8486: '1771:377E', 8510: '1771:377E', 8670: '1771:377E', 8694: '1771:377E', 8750: '1771:377E', 8767: '214B:06B1', 10189: '000E:2071', 10220: '214B:06B1', 10378: '214B:06FA', 10599: '214B:06B1', 11003: '000E:0B77', 11050: '000E:2071', 11071: '1771:5C60', 11088: '214B:06B1', 11342: '214B:06B1', 11496: '214B:06B1', 11602: '214B:06B1'}
DIRECT = {'1771:3216':1,'1771:377E':1,'1771:2E93':1,'214B:06B1':1,'214B:06FA':0}


def prove(data,case,variant=None):
 name,address,e=case;image=Image.from_savestate(data);route=R.Route(image,record_writes=False);m=route.m
 ss=m.seg(0x3052);sp=0x3900;parent=0x4200;wrapper=0x4300;edits=[]
 def write(a,b,why):
  old=m.read(a,len(b));m.write(a,b);edits.append({'linear':a,'size':len(b),'old_sha256':hashlib.sha256(old).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),'why':why})
 def word(a,v,why):write(a,(v&65535).to_bytes(2,'little'),why)
 def byte(a,v,why):write(a,bytes([v&255]),why)
 managed=set(image.managed_countries());fxbase=m.far(0xA92B)
 index=next(i for i in range(image.fixture_index(),image.rd_far(0xA923,0x28)) if any(m.word_at(fxbase+8*(i-1)+4+2*s) in managed for s in (0,1)))
 fx=fxbase+8*(index-1);countries=[m.word_at(fx+4),m.word_at(fx+6)];country=next(c for c in countries if c in managed);side=e.get('side',0)
 if countries[side]!=country:countries.reverse();write(fx+4,b''.join(c.to_bytes(2,'little') for c in countries),'coherent managed-side country swap')
 cbase=m.far(0xA917)+191*country;manager=m.read(cbase+0x2E,1)[0];assert manager>=128
 word(ss*16+wrapper+4,parent,'recommendation caller frame points at country/fixture parent')
 for off,value in ((4,(m.rd(0xA92B)+8*(index-1))&65535),(6,m.rd(0xA92D)),(8,country)):word(ss*16+parent+off,value,'original parent fixture/country field')
 byte(ss*16+parent-1,side,'managed fixture side')
 write(m.DS*16+R.DELAY_COUNT,R.DELAY_COUNT_VALUE.to_bytes(4,'little'),'same delay calibration as Route.call')
 kind=e.get('kind',2);stage=4 if kind in (0x65,0x66,0x67) else 8 if kind in (8,0xC8,0xC9,0xCA,0xCB) else 2
 world=int(stage==8);year=e.get('year',4 if world else 2 if stage==4 else 1)
 game=m.far(0xA923);byte(game+0x3C,stage,'actual stage byte');byte(game+0x40,world,'matching competition class');word(game+0x38,year,'year predicate input')
 mode=e.get('mode','gate');byte(game+(manager-128)+0x13,int(mode=='gate'),'actual recommendation suppression flag')
 byte(game+manager-0x7F,0,'active manager group zero for sack predicate');byte(cbase+0xBE,0,'no country sack exemption')
 byte(m.far(0xA91F)+3*manager+2,e.get('confidence',0),'signed manager confidence byte')
 byte(cbase+0xAC,e.get('streak',0),'country streak counter')
 result=e.get('result','win');margin=e.get('margin',1);goals=[0,0]
 if result=='win':goals[side]=margin;winner=side
 elif result=='loss':goals[1-side]=margin;winner=1-side
 else:winner=2
 assert margin or winner==2 or kind in (0x66,0xCA)
 write(fx,bytes(goals+[kind,winner]),'authored fixture goals/kind/result')
 for s in (0,1):
  stats=[goals[s],0,0,e.get('stat3',0) if s==side else 0,0,e.get('stat5',0) if s==side else 0,0,0,0,0]
  write(m.DS*16+0x7B7E+10*s,bytes(stats),'isolated statistic row')
 seed=e.get('seed',0);word(m.far(0xA978),seed,'original LCG seed');role=step(seed)*14>>16
 squad=[m.word_at(cbase+2*i) for i in range(20)];poolbase=m.rd(0x6D18+2*(manager-128));pool=[m.word_at(m.far(0xA927)+2*i) for i in range(poolbase,poolbase+80)]
 assert len(set(squad))==20 and len(set(pool))==80 and not set(squad)&set(pool)
 if mode!='gate':
  players=m.far(0xA91B)
  for n,group in ((squad,'squad'),(pool,'pool')):
   for j,w in enumerate(n):
    p=players+20*w
    # Two-foot marker (+2 + +5 ==30), neutral form, available energy10.
    for off,v in ((2,15),(5,15),(4,62),(6,role),(7,role),(0xC,0),(0xE,10),(0x10,0)):byte(p+off,v,'authored role-population '+group+' field')
    if mode=='no-role' and group=='squad':byte(p+6,(role+1)%14,'no current-position match')
    if mode=='unavailable-squad' and group=='squad':byte(p+0x10,128,'unavailable squad status')
    if mode=='pool-mismatch' and group=='pool':byte(p+7,(role+1)%14,'no club-position match')
    if mode=='pool-unavailable' and group=='pool':byte(p+0x10,128,'unavailable pool status, still considered by caller')
    if mode in ('improve','ties','pool-first-unavailable'):
     strength=10 if group=='squad' else 30
     if mode in ('ties','pool-first-unavailable') and j>=2:strength=20
     byte(p+4,62+strength-10,'nominal strength with energy10/form0')
    if mode=='pool-first-unavailable' and group=='pool' and j==0:byte(p+0x10,128,'first pool candidate unavailable')
  if mode=='wrap':word(m.DS*16+0x6D18+2*(manager-128),0xFFF0,'explicit wrapped-end pool-base stress')
 reg=port._module_registry('news');copy=port.Registry('news',reg.doc);copy.entries={address:reg.entries[address]};copy.variants=reg.variants
 installed=port.install(m,[(copy,variant)]);decisions=[];calls=[]
 decisions_at=dict(DECISIONS)
 if address=='000E:2071':decisions_at[0x7080]='000E:2071'
 def returned(ret):
  def visit(replay):
   if not replay:
    ax=m.reg('ax');decisions.append({'return':f'000E:{ret:04X}','target':decisions_at[ret],'ax':ax,'al':ax&255,'signed_ax':(ax+32768)%65536-32768})
  return visit
 for ret in decisions_at:m.at(f'000E:{ret:04X}',returned(ret))
 def entering(target,n):
  def visit(replay):
   if not replay and m.stack_word(2)==m.seg(0xE):
    ret=m.stack_word(0)
    if 0x2071<=ret<0x2E1F:calls.append({'target':target,'return':f'000E:{ret:04X}','args':[m.stack_word(4+2*i) for i in range(n)]})
  return visit
 for target,n in DIRECT.items():m.at(target,entering(target,n))
 prover=Prover(m,installed)
 arg=wrapper if address=='000E:2071' else parent
 for i,value in enumerate((0x7080,arg)):word(ss*16+sp+2*i,value,'near-call frame')
 for k,v in (('ss',ss),('sp',sp),('bp',0x3F00),('ds',m.DS),('es',m.DS),('cs',m.seg(0xE)),('eip',int(address.split(':')[1],16))):m.set_reg(k,v)
 m.at('000E:7080',lambda replay:m.stop('synthetic-return'))
 status,error='completed',None
 try:
  reason=m.run(m.lin('000E:7080')+1,fresh=True)
  if reason!='synthetic-return':raise RuntimeError('unexpected '+str(reason))
 except ProofError as exc:status,error='differs',str(exc)
 except Exception as exc:status,error='aborted',type(exc).__name__+': '+str(exc)
 recommendation=[d['al'] for d in decisions if d['target']=='000E:2071']
 count=collections.Counter(c['return'] for c in calls)
 checks={'recommendation_result':recommendation,'direct_calls_by_return':dict(count),'role_after':m.rd(0x22,1),'role_expected':role}
 if status=='completed' and not variant:
  recommend_draws=[d['ax'] for d in decisions if d['return']=='000E:223F']
  checks['recommendation_draws']=recommend_draws
  if 'expected_choice' in e and recommend_draws!=[e['expected_choice']]:status,error='invalid-draw-coverage',str(checks)
  if name.startswith('column-sack-'):
   scores=[d['signed_ax'] for d in decisions if d['target']=='000E:0B77']
   checks['actual_sack_scores']=scores
   if scores!=[e['confidence']] or recommendation!=([] if e['confidence'] < -10 else [0]):status,error='invalid-sack-coverage',str(checks)
  if recommendation and checks['role_after']!=role:status,error='invalid-input-check','wrong role write'
  if address=='000E:2071':
   want=int(mode in ('improve','ties','pool-first-unavailable'))
   if recommendation!=[want]:status,error='invalid-input-check',str(checks)
   if mode in ('equal','ties','pool-unavailable','pool-first-unavailable') and role==0:
    expected={'000E:210F':20,'000E:2126':20,'000E:213E':1,'000E:21DE':80,'000E:222E':1}
    expected['000E:21F6']=int(mode in ('ties','pool-first-unavailable'))
    if any(count[k]!=v for k,v in expected.items()):status,error='invalid-loop-count',str(checks)
   if want and role==0:
    weak=m.word_at(ss*16+sp-2-7);best=m.word_at(ss*16+sp-2-9)
    checks.update({'weak_player':weak,'expected_weak':squad[0],'pool_player':best,'expected_pool':pool[1] if mode=='pool-first-unavailable' else pool[0]})
    if weak!=squad[0] or best!=checks['expected_pool']:status,error='invalid-strict-tie',str(checks)
 return {'case':name,'routine':address,'authored_inputs':e,'category':'wrapped-index-stress' if mode=='wrap' else 'role-population-stress' if mode!='gate' else 'isolated-column-branch','fixture_index':index,'country':country,'manager':manager,'side':side,'stage':stage,'world_class':world,'year_word':year,'inputs':edits,'status':status,'error':error,'calls':installed.calls,'proof':prover.summary(),'decision_calls':decisions,'direct_calls':calls,'checks':checks}


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE);ap.add_argument('--group');ap.add_argument('--cases');ap.add_argument('--variant');ap.add_argument('--no-record',action='store_true');a=ap.parse_args()
 if not a.no_record:
  dirty=subprocess.check_output(['git','status','--porcelain','--','runtime/original_match',str(Path(__file__).relative_to(ROOT))],cwd=ROOT,text=True)
  if dirty:raise SystemExit('refused dirty proof source: '+dirty)
 chosen=cases()
 if a.group:chosen=[c for c in chosen if c[0].startswith(a.group)]
 if a.cases:chosen=[c for c in chosen if c[0] in a.cases.split(',')]
 assert chosen
 case=next(c for c in runner.CASES if c[0]=='E040-r0004');path=ROOT/'.cache/dl'/case[3];data=path.read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==runner.expected(case[3])
 results=[]
 for c in chosen:
  p=prove(data,c,a.variant);results.append(p);print(c[0],p['status'],p['error'],flush=True)
  if p['status']!='completed':break
 caught=bool(a.variant and results[-1]['status']=='differs')
 good=caught if a.variant else all(p['status']=='completed' and p['proof'][p['routine']]['proved']==1 and p['proof'][p['routine']]['before']==0 for p in results) and len(results)==len(chosen)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 record={'schema':'e040-t122c-synthetic/1','task':'T122c','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+' '.join(sys.argv[1:]),'source_state':{'asset':case[3],'sha256':digest},'variant':a.variant,'caught':caught,'passes':results,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),ROOT/'runtime/original_match/port/news.py')}}
 if not a.no_record:
  a.out.mkdir(parents=True,exist_ok=True);dest=a.out/('synthetic-'+(a.variant or 'normal')+'-'+stamp+'.json');assert not dest.exists();dest.write_text(json.dumps(record,indent=1)+'\n');print('record:',dest,flush=True)
 return 0 if good else 1
if __name__=='__main__':sys.exit(main())
