"""Original-backed headline/sack probes; all authored inputs are isolated function-domain states.

[confirmed: F025/F039; raw000E01FA/319B/4DB7/4E0E; F023 kind-stage mapping;
post-confidence original news loop000E6F91-6FE1.] No original memory bytes exported.
"""
import argparse,collections,datetime,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'experiments/E040-route-fixture-writes'))
from original_match import port,route as R
from original_match.image import Image
from original_match.port.prove import Prover,ProofError
import runner


def step(s):return (s*0x7ABD+0x1B0F)&65535

def seeds():return sorted({next(s for s in range(65536) if (step(s)*n>>16)+1==choice) for n in (2,3,4) for choice in range(1,n+1)})


def cases():
 out=[]
 def add(name,entry='319B',**e):out.append((name,entry,e))
 for side in (0,1):
  for score in (-128,-11,-10,-8,-7,-6,-5):
   add(f'band-{side}-{score}',side=side,score=score)
   add(f'outer-band-{side}-{score}','4E0E',side=side,score=score)
  for name,fields in (('year',{'year':1}),('friendly',{'kind':1}),('continent-group',{'kind':3,'stage':3,'group':1}),('world-group',{'kind':7,'stage':7,'group':1}),('country-exempt',{'exempt':1})):
   add(f'exempt-{side}-{name}',side=side,score=-11,**fields)
   add(f'outer-exempt-{side}-{name}','4E0E',side=side,score=-11,**fields)
  add(f'shootout-{side}',side=side,score=-11,kind=0x66,goals=(1,1),winner=1-side,slots=(1,))
  add(f'outer-shootout-{side}','4E0E',side=side,score=-11,kind=0x66,goals=(1,1),winner=1-side,slots=(1,))
  add(f'draw-{side}',side=side,score=-11,goals=(1,1),winner=2,slots=(1,))
  for slots in ((1,),(2,2),(4,4,4),(3,3,3,3),(2,4,2,4)):
   for performance in ('ahead','behind'):
    for seed in seeds():add(f'win-{side}-{len(slots)}-{slots[0]}-{performance}-{seed}',side=side,result='win',slots=slots,performance=performance,seed=seed)
  for performance in ('ahead','behind'):
   for rating in ('balanced','own-strong','other-strong'):
    for seed in seeds():add(f'loss-text-{side}-{performance}-{rating}-{seed}',side=side,score=-5,performance=performance,rating=rating,seed=seed)
  for kind in (0x67,0x65,0xCB,0xC9,0xC8):add(f'special-win-{side}-{kind}',side=side,result='win',kind=kind,slots=(1,))
  for slots in ((),(1,),(2,4,2,4),(0,0)):
   add(f'outer-hist-{side}-{len(slots)}-{slots[0] if slots else 0}','4E0E',side=side,result='win' if slots else 'loss',slots=slots,score=-5)
  for kind in (0x67,0xCB):add(f'outer-winner-flag-{side}-{kind}','4E0E',side=side,result='win',kind=kind,slots=(1,))
  for threshold,member in (('below',True),('below',False),('equal',True)):
   add(f'outer-threshold-{side}-{threshold}-{int(member)}','4E0E',side=side,result='win',slots=(1,),threshold=threshold,member=member)
  for score in (-11,-10,-6,-5):
   for seed in seeds():add(f'pages-{side}-{score}-{seed}','4DB7',side=side,score=score,seed=seed)
 for side in (0,1):
  for performance in ('ahead','behind'):
   for choice in (1,2):
    seed=next(s for s in range(65536) if (step(s)*2>>16)+1==choice)
    add(f'draw-branch-{side}-{performance}-{choice}',side=side,goals=(1,1),winner=2,slots=(1,),performance=performance,seed=seed)
 for manager in (1,2):
  for prefix in (0,2,16):
   for reverse in (False,True):
    add(f'unmanage-{manager}-{prefix}-{int(reverse)}','01FA',two=True,side=manager-1,prefix=prefix,reverse=reverse)
  add(f'unmanage-wrap-{manager}','01FA',two=True,side=manager-1,wrap=True)
 for swapped in (False,True):add(f'route-fragment-{int(swapped)}','route-fragment',two=True,swap=swapped)
 return out


DECISIONS={13037: '1771:5C60', 13147: '000E:1F4D', 13163: '214B:06B1', 13321: '214B:06B1', 13486: '214B:06B1', 13880: '000E:1F4D', 13893: '214B:06B1', 13976: '214B:06B1', 14098: '000E:0B77', 14270: '000E:1F4D', 14286: '214B:06B1', 14445: '000E:09DB', 14458: '214B:06B1', 14580: '000E:0A53', 14593: '214B:06B1', 14714: '214B:06B1', 11003: '000E:0B77', 19906: '000E:3CC8', 19914: '000E:4A87', 19940: '000E:4A87', 20133: '1771:3A82'}
DECISIONS[0x6FAE]='1771:0B77'



class Input:
 def __init__(self,data):
  self.image=Image.from_savestate(data);self.route=R.Route(self.image,record_writes=False);self.m=self.route.m;self.edits=[]
 def write(self,a,data,why):
  old=self.m.read(a,len(data));self.m.write(a,data);self.edits.append({'linear':a,'size':len(data),'old_sha256':hashlib.sha256(old).hexdigest(),'new_sha256':hashlib.sha256(data).hexdigest(),'why':why})
 def byte(self,a,v,why):self.write(a,bytes([v&255]),why)
 def word(self,a,v,why):self.write(a,(v&65535).to_bytes(2,'little'),why)
 def ptr(self,ds,seg,off,why):self.write(self.m.DS*16+ds,(off&65535).to_bytes(2,'little')+(seg&65535).to_bytes(2,'little'),why)


def prepare(data,entry,e):
 b=Input(data);m=b.m;game=m.far(0xA923);fxbase=m.far(0xA92B);managed=set(b.image.managed_countries())
 index=next(i for i in range(b.image.fixture_index(),b.image.rd_far(0xA923,0x28)) if any(m.word_at(fxbase+8*(i-1)+4+2*s) in managed for s in (0,1)))
 fx=fxbase+8*(index-1);countries=[m.word_at(fx+4),m.word_at(fx+6)];original_country=next(c for c in countries if c in managed)
 if e.get('two'):
  assert countries[0]==original_country
  # Private synthetic buffers; no bytes are written to a repository artifact.
  old_map=m.read(m.far(0xA91F),130*3);new_map=bytearray(old_map+b'\0'*3)
  new_map[130*3:131*3]=bytes([countries[1],0,0]);b.write(0x90200,new_map,'private two-manager country map, preserving original0..129')
  b.ptr(0xA91F,0x9000,0x200,'two-manager map pointer')
  old_poolbase=m.rd(0x6D18+2);old_pool=[m.word_at(m.far(0xA927)+2*i) for i in range(old_poolbase,old_poolbase+80)]
  second_pool=list(range(2000,2080));assert not set(old_pool)&set(second_pool)
  assert not set(second_pool)&{m.word_at(m.far(0xA917)+191*c+2*i) for c in countries for i in range(20)}
  values=[0]+old_pool+second_pool;b.write(0x90000,b''.join(x.to_bytes(2,'little') for x in values),'private two-manager pool-index table, allocated original player IDs')
  b.ptr(0xA927,0x9000,0,'two-manager pool pointer');b.word(m.DS*16+0x6D18+2,1,'actual manager-slot1 pool base');b.word(m.DS*16+0x6D18+4,81,'actual manager-slot2 pool base')
  initials=m.read(m.far(0x9B78),130)+b'B';names=m.read(m.far(0x9B74),130*13)+b'\x06SECOND'+bytes(6)
  b.write(0x90700,initials,'private manager initials with authored second initial');b.ptr(0x9B78,0x9000,0x700,'manager initials pointer')
  b.write(0x91000,names,'private manager names with authored SECOND name');b.ptr(0x9B74,0x9000,0x1000,'manager names pointer')
  b.byte(game,2,'two active manager count')
  for c,manager in zip(countries,(0x81,0x82)):
   b.byte(m.far(0xA917)+191*c+0x2E,manager,'actual manager slot1/2 ownership')
   b.write(m.far(0xA91F)+3*manager,bytes([c,0,0]),'coherent active manager record')
  if e.get('swap'):countries.reverse();b.write(fx+4,b''.join(c.to_bytes(2,'little') for c in countries),'swap original route news order')
 side=e.get('side',0)
 if not e.get('two') and countries[side]!=original_country:countries.reverse();b.write(fx+4,b''.join(c.to_bytes(2,'little') for c in countries),'coherent managed side swap')
 country=countries[side];cbase=m.far(0xA917)+191*country;manager=m.read(cbase+0x2E,1)[0];assert manager in (0x81,0x82)
 kind=e.get('kind',2);stage=e.get('stage',4 if kind in (0x65,0x66,0x67) else 8 if kind in (8,0xC8,0xC9,0xCA,0xCB) else 2);world=int(stage in (5,6,7,8))
 b.byte(game+0x3C,stage,'actual stage byte');b.byte(game+0x40,world,'matching competition class');b.word(game+0x38,e.get('year',2),'isolated year predicate input')
 raw_scores={}
 for s,c in enumerate(countries):
  base=m.far(0xA917)+191*c;mgr=m.read(base+0x2E,1)[0]
  if mgr>=128:
   b.byte(game+(mgr-128)+0x13,1,'explicit recommendation suppression for isolated news probe')
   b.byte(game+mgr-0x7F,e.get('group',0),'actual manager finals group')
   b.byte(base+0xBE,e.get('exempt',0),'country sack exemption')
   b.byte(m.far(0xA91F)+3*mgr+1,0,'active manager status')
   score=-11 if entry=='route-fragment' and s==0 else 0 if entry=='route-fragment' else e.get('score',0)
   raw_scores[c]=score
   b.byte(m.far(0xA91F)+3*mgr+2,score,'real signed manager confidence')
   b.byte(game+0x47+(mgr-128),0,'initial manager-release flag')
   threshold=kind-1 if e.get('threshold')=='below' else kind
   b.byte(game+6*world+(mgr-128)+0x19,threshold,'manager news-kind threshold')
 if 'member' in e:
  at=m.DS*16+0xA943+(kind>>3);old=m.read(at,1)[0];v=(old|(1<<(kind&7))) if e['member'] else old&~(1<<(kind&7));b.byte(at,v,'explicit DS:A943 membership control')
 members={}
 for c in countries:
  base=m.far(0xA917)+191*c;mgr=m.read(base+0x2E,1)[0]
  if mgr<128:continue
  if e.get('reverse'):
   roster=[m.word_at(base+2*i) for i in range(20)];b.write(base,b''.join(w.to_bytes(2,'little') for w in reversed(roster)),'explicit roster-order stress before actual tactic reset')
  roster=[m.word_at(base+2*i) for i in range(20)];start=m.rd(0x6D18+2*(mgr-128));pool=[m.word_at(m.far(0xA927)+2*i) for i in range(start,start+80)]
  for w in pool:b.byte(m.far(0xA91B)+20*w,c,'nonzero pool affiliation to verify all80 clears')
  if e.get('wrap') and c==country:b.word(m.DS*16+0x6D18+2*(mgr-128),0xFFF0,'explicit unsigned pool-end wrap stress')
  prefix=e.get('prefix',2);future=[];listing=m.far(0xA92F)+72*c
  for slot in range(21,37):
   value=0 if slot<21+prefix else 20+slot-(21+prefix)
   b.word(listing+2*(slot-1),value,'actual future fixture-list word')
   if value:
    mark=0xFE if slot%2 else 0xFF;b.write(fxbase+8*(value-1),bytes([mark,0,2,2])+b''.join(x.to_bytes(2,'little') for x in countries),'authored future fixture record')
    if mark==0xFE:future.append(value)
  if prefix>=16:b.word(listing+2*36,20,'actual nonzero sentinel at raw scan slot37')
  members[c]={'manager':mgr,'roster_before':roster,'pool':pool,'future_fe':future,'post_reset_bench':None,'wrap':bool(e.get('wrap') and c==country)}
 result=e.get('result','loss');slots=list(e.get('slots',() if result=='loss' else (1,)))
 if entry=='route-fragment':goals=[0,1];winner=1
 elif 'goals' in e:goals=list(e['goals']);winner=e.get('winner',1-side)
 else:goals=[0,0];goals[side]=len(slots);goals[1-side]=0 if result=='win' else max(1,len(slots)+1);winner=side if result=='win' else 1-side
 assert goals[0]!=goals[1] or winner==2 or kind in (0x66,0xCA)
 b.write(fx,bytes(goals+[kind,winner])+b''.join(c.to_bytes(2,'little') for c in countries),'completed isolated fixture result')
 b.write(m.DS*16+0x9B3C,bytes(goals),'matching score-word bytes');b.write(m.DS*16+0x80F0,bytes(goals),'matching scorer counters')
 packets=[];histograms={};top={}
 for s,c in enumerate(countries):
  roster=[m.word_at(m.far(0xA917)+191*c+2*i) for i in range(20)]
  chosen=slots if s==side and len(slots)==goals[s] else [1]*goals[s]
  if entry=='route-fragment':chosen=[1]*goals[s]
  assert len(chosen)==goals[s] and goals[s]<=11
  packet=bytearray(33);hist=[0]*21
  for j,slot in enumerate(chosen,1):
   player=roster[slot-1] if slot else m.word_at(m.far(0xA917)+191*countries[1-s])
   packet[3*(j-1):3*(j-1)+2]=player.to_bytes(2,'little');packet[3*(j-1)+2]=10+j+(128 if slot==0 else 0);hist[slot]+=1
  b.write(m.DS*16+0x7BD4+33*s,packet,'completed scorer rows: actual roster IDs and authored minutes')
  histograms[c]=hist;top[c]=0 if goals[s]==0 else next(i for i in range(1,21) if hist[i]==max(hist[1:]))
  b.byte(m.far(0xA917)+191*c+0xAC,1 if winner==s else 0,'isolated current win streak')
 own_goal_credits=[histograms[c][0] for c in countries]
 on_target=[goals[s]-own_goal_credits[s]+1 for s in (0,1)]
 if e.get('performance')=='ahead':on_target[side]+=4
 if e.get('performance')=='behind':on_target[1-side]+=4
 for s in (0,1):
  stats=[0,0,0,on_target[s]+2,on_target[s],on_target[1-s]-(goals[1-s]-own_goal_credits[1-s]),0,0,0,0]
  b.write(m.DS*16+0x7B7E+10*s,bytes(stats),'bounded shots/on-target/saves statistics consistent with completed goals')
 ratings={'balanced':((16,64,1),(16,64,1)),'own-strong':((1,1,1),(32,128,1)),'other-strong':((32,128,1),(1,1,1))}[e.get('rating','balanced')]
 for s,c in enumerate((country,countries[1-side])):b.write(m.far(0xA917)+191*c+0x2A,bytes(ratings[s]),'isolated valid-byte regional/world ranking and continent inputs')
 b.word(m.far(0xA978),e.get('seed',0),'original LCG seed');b.write(m.DS*16+R.DELAY_COUNT,R.DELAY_COUNT_VALUE.to_bytes(4,'little'),'same declared delay calibration as Route.call')
 ss=m.seg(0x3052);parent=0x4200;wrapper=0x4300
 for off,value in ((4,(m.rd(0xA92B)+8*(index-1))&65535),(6,m.rd(0xA92D)),(8,country)):b.word(ss*16+parent+off,value,'actual country/fixture parent frame')
 b.byte(ss*16+parent-1,side,'actual parent side');b.byte(ss*16+parent-2,0,'initial parent sack flag');b.write(ss*16+parent-0x1B,bytes(histograms[country]),'authored parent scorer histogram');b.word(ss*16+parent-6,top[country],'authored parent first strict maximum')
 b.word(ss*16+wrapper+4,parent,'headline parent-link frame')
 expected_scores={c:0 if e.get('year',2)<2 or kind==1 or e.get('exempt',0) or (stage in (3,4,7,8) and e.get('group',0)) else (score+128)%256-128 for c,score in raw_scores.items()}
 expected_sack={c:int(winner not in (countries.index(c),2) and goals[0]!=goals[1] and -255<=score<=-11) for c,score in expected_scores.items()}
 return b,{'expected_scores':expected_scores,'expected_sack':expected_sack,'game':game,'fx':fx,'fxbase':fxbase,'index':index,'countries':countries,'country':country,'manager':manager,'side':side,'kind':kind,'stage':stage,'world':world,'goals':goals,'winner':winner,'members':members,'histograms':histograms,'top':top,'ss':ss,'parent':parent,'wrapper':wrapper}


def prove(data,case,variant=None):
 name,entry,e=case;b,c=prepare(data,entry,e);route=b.route;m=b.m;ss=c['ss'];sp=0x3900;timeline=[];decisions=[];reset_stack=[]
 def country_base(country):return m.far(0xA917)+191*country
 def manager_at(country):return m.read(country_base(country)+0x2E,1)[0]
 def key_reads():return sum(1 for v in route.record if v[0]=='key' and v[1]=='000E:0629' and v[2]=='read')
 def event(kind,**fields):timeline.append({'event':kind,**fields})
 def news_entry(replay):
  if replay:return
  country=m.stack_word(6);event('news-entry',country=country,manager=manager_at(country),fxoff=m.stack_word(2),fxseg=m.stack_word(4),return_ip=m.stack_word(0),ss=m.reg('ss'),sp=m.reg('sp'),caller_bp=m.reg('bp'))
 def wait_entry(replay):
  if replay or m.stack_word(0)!=0x4F72:return
  bp=m.reg('bp');country=m.frame_word(bp,8);hist=m.read(ss*16+bp-0x1B,21)
  expect=bytes(c['histograms'][country]);words=[m.stack_word(2+2*i) for i in range(3)]
  game=c['game'];mgr=manager_at(country);kind=c['kind'];threshold=m.read(game+6*c['world']+(mgr-128)+0x19,1)[0]
  member=bool(m.rd(0xA943+(kind>>3),1)&(1<<(kind&7)))
  expected_flags=[int(c['winner']==c['countries'].index(country) and kind in (0x67,0xCB)),int(threshold<kind and member),0]
  event('wait-entry',country=country,manager=mgr,sack_flag=m.read(ss*16+bp-2,1)[0],expected_sack_flag=c['expected_sack'][country],words_f1_f2_f3=words,expected_low_bytes=expected_flags,histogram_sha256=hashlib.sha256(hist).hexdigest(),expected_histogram_sha256=hashlib.sha256(expect).hexdigest(),top_slot=m.frame_word(bp,-6),expected_top=c['top'][country],key_reads=key_reads())
 def wait_return(replay):
  if not replay:
   country=m.frame_word(m.reg('bp'),8);event('wait-return',country=country,manager=manager_at(country),key_reads=key_reads())
 def unmanage_entry(replay):
  if replay:return
  index=m.stack_word(2);country=m.read(m.far(0xA91F)+3*(index+128),1)[0]
  event('unmanage-entry',manager_index=index,country=country,manager=manager_at(country),key_reads=key_reads(),return_ip=m.stack_word(0))
 def reset_entry(replay):
  if replay or m.stack_word(0)!=0x0244 or m.stack_word(2)!=m.seg(0xE):return
  country=m.stack_word(4);mgr=manager_at(country);base=country_base(country)
  before=[m.word_at(base+2*i) for i in range(20)];reset_stack.append(country)
  event('reset-entry',country=country,manager=mgr,release_flag=m.read(c['game']+0x47+(mgr-128),1)[0],record_flag=m.read(m.far(0xA91F)+3*mgr+1,1)[0],roster=before)
 def reset_return(replay):
  if replay:return
  country=reset_stack.pop();base=country_base(country);roster=[m.word_at(base+2*i) for i in range(20)];c['members'][country]['post_reset_bench']=roster[11:]
  event('reset-return',country=country,manager=manager_at(country),roster=roster)
 for country,member in c['members'].items():
  address=country_base(country)+0x2E
  def release(a,size,value,country=country,member=member):
   if value>=128:return
   pool_zero=sum(m.read(m.far(0xA91B)+20*w,1)[0]==0 for w in member['pool'])
   bench=member['post_reset_bench'] or []
   restored=sum(m.read(m.far(0xA91B)+20*w+6,1)==m.read(m.far(0xA91B)+20*w+7,1) for w in bench)
   left=sum(m.read(c['fxbase']+8*(i-1),1)[0]==0xFE for i in member['future_fe'])
   event('release-write',country=country,new_manager=value,pool_zero=pool_zero,expected_pool_zero=0 if member['wrap'] else 80,post_reset_bench_restored=restored,future_fe_still_before_changes=left,expected_future_fe=len(member['future_fe']))
  m.on_write(address,address,release)
 loaded=port.load(['news'])
 if entry!='route-fragment':
  reg=loaded[0][0];copy=port.Registry('news',reg.doc);copy.entries={'000E:'+entry:reg.entries['000E:'+entry]};copy.variants=reg.variants;loaded=[(copy,variant)]
 else:loaded=[(loaded[0][0],variant)]
 installed=port.install(m,loaded)
 m.at('000E:4E0E',news_entry);m.at('000E:05F6',wait_entry);m.at('000E:4F72',wait_return);m.at('000E:01FA',unmanage_entry);m.at('0791:BC5D',reset_entry);m.at('000E:0244',reset_return)
 def decision(ret):
  def visit(replay):
   if not replay:
    ax=m.reg('ax');decisions.append({'return':f'000E:{ret:04X}','target':DECISIONS[ret],'ax':ax,'al':ax&255,'signed_ax':(ax+32768)%65536-32768})
  return visit
 for ret in DECISIONS:m.at(f'000E:{ret:04X}',decision(ret))
 prover=Prover(m,installed)
 if entry=='route-fragment':
  bp=0x3EDE;sp=bp-0x16
  b.word(ss*16+bp,0x3EEA,'actual route caller saved BP');b.word(ss*16+bp+2,0x70D4,'actual route caller return IP')
  for off,value in ((-0x10,m.rd(0xA923)),(-0xE,m.rd(0xA925)),(-0x14,(m.rd(0xA92B)+8*(c['index']-1))&65535),(-0x12,m.rd(0xA92D))):b.word(ss*16+bp+off,value,'actual route-frame far pointer')
  b.byte(ss*16+bp-4,1,'managed-match flag in actual route frame')
  b.word(c['game']+0x26,c['index'],'post-match route cursor')
  start=0x6F91;end='000E:6FE1';m.at(end,lambda replay:m.stop('news-loop-return'))
 else:
  bp=0x3F00;start=int(entry,16);end='000E:7080';m.at(end,lambda replay:m.stop('function-return'))
  args=[c['manager']-128] if entry=='01FA' else [c['wrapper']] if entry=='319B' else [c['parent']] if entry=='4DB7' else [(m.rd(0xA92B)+8*(c['index']-1))&65535,m.rd(0xA92D),c['country']]
  for i,value in enumerate([0x7080]+args):b.word(ss*16+sp+2*i,value,'actual near-call stack')
 for k,v in (('ss',ss),('sp',sp),('bp',bp),('ds',m.DS),('es',m.DS),('cs',m.seg(0xE)),('eip',start)):m.set_reg(k,v)
 status,error='completed',None
 try:
  reason=m.run(m.lin(end)+1,fresh=True)
  if reason not in ('function-return','news-loop-return'):raise RuntimeError('unexpected '+str(reason))
 except ProofError as exc:status,error='differs',str(exc)
 except Exception as exc:status,error='aborted',type(exc).__name__+': '+str(exc)
 checks={}
 if status=='completed' and not variant:
  if entry in ('319B','4DB7'):
   flag=m.read(ss*16+c['parent']-2,1)[0];checks['outer_sack_flag']=flag
   score=e.get('score',0)
   if e.get('year',2)<2 or c['kind']==1 or e.get('exempt',0) or (c['stage'] in (3,4,7,8) and e.get('group',0)):score=0
   expected=int(c['winner'] not in (c['side'],2) and c['goals'][0]!=c['goals'][1] and -255<=score<=-11)
   checks['expected_sack_flag']=expected
   if flag!=expected:status,error='invalid-sack-coverage',str(checks)
  for ev in timeline:
   if ev['event']=='wait-entry':
    if ev['sack_flag']!=ev['expected_sack_flag'] or ev['histogram_sha256']!=ev['expected_histogram_sha256'] or ev['top_slot']!=ev['expected_top'] or [w&255 for w in ev['words_f1_f2_f3']]!=ev['expected_low_bytes']:
     status,error='invalid-wait-frame',str(ev)
   if ev['event']=='reset-entry' and (ev['manager']<128 or ev['release_flag']!=1 or ev['record_flag']!=1):status,error='invalid-reset-order',str(ev)
   if ev['event']=='release-write' and (ev['pool_zero']!=ev['expected_pool_zero'] or ev['post_reset_bench_restored']!=9 or ev['future_fe_still_before_changes']!=ev['expected_future_fe']):status,error='invalid-unmanage-fields',str(ev)
  released=[ev['country'] for ev in timeline if ev['event']=='release-write']
  for country in released:
   member=c['members'][country]
   if manager_at(country)!=country or any(m.read(c['fxbase']+8*(i-1),1)[0]!=0xFF for i in member['future_fe']):status,error='invalid-unmanage-postcondition',str(country)
  if entry=='4E0E' and released!=([c['country']] if c['expected_sack'][c['country']] else []):status,error='missing-or-extra-integrated-unmanage',str(timeline)
  if entry=='01FA' and released!=[c['country']]:status,error='invalid-unmanage-path',str(timeline)
  if entry=='4E0E' and released:
   events=[ev['event'] for ev in timeline]
   if not events.index('wait-return')<events.index('unmanage-entry')<events.index('reset-entry')<events.index('release-write'):status,error='invalid-sack-order',str(timeline)
   if next(ev['key_reads'] for ev in timeline if ev['event']=='unmanage-entry')<1:status,error='missing-actual-key-read',str(timeline)
  if entry in ('319B','4DB7','4E0E'):
   scores=[d['signed_ax'] for d in decisions if d['return']=='000E:3712']
   should_read=c['winner'] not in (c['side'],2) and c['goals'][0]!=c['goals'][1]
   checks['headline_real_scores']=scores;checks['expected_headline_real_scores']=[c['expected_scores'][c['country']]] if should_read else []
   if scores!=checks['expected_headline_real_scores']:status,error='invalid-real-score-coverage',str(checks)
  if e.get('reverse'):
   before=[v['roster'] for v in timeline if v['event']=='reset-entry'];after=[v['roster'] for v in timeline if v['event']=='reset-return']
   checks['actual_reset_changed_roster_order']=[a!=b for a,b in zip(before,after)]
   if not checks['actual_reset_changed_roster_order'] or not all(checks['actual_reset_changed_roster_order']):status,error='unreached-roster-order-stress',str(checks)
  if entry=='route-fragment':
   news=[ev['country'] for ev in timeline if ev['event']=='news-entry'];waits=[ev['country'] for ev in timeline if ev['event']=='wait-return']
   ownership=[d['al'] for d in decisions if d['return']=='000E:6FAE'];checks['actual_original_ownership_results']=ownership
   if ownership!=[1,1]:status,error='invalid-original-ownership-recheck',str(ownership)
   checks.update({'news_order':news,'wait_order':waits,'released':released,'expected_order':c['countries'],'second_manager_after':manager_at(c['countries'][1])})
   if news!=c['countries'] or waits!=c['countries'] or released!=[c['countries'][0]] or manager_at(c['countries'][1])<128:status,error='invalid-two-manager-route',str(checks)
   elif next(i for i,ev in enumerate(timeline) if ev['event']=='release-write')>=next(i for i,ev in enumerate(timeline) if ev['event']=='news-entry' and ev['country']==c['countries'][1]):status,error='invalid-second-news-order',str(timeline)
 return {'case':name,'entry':entry,'category':'declared-original-route-fragment' if entry=='route-fragment' else 'isolated-unmanage-stress' if entry=='01FA' else 'isolated-headline-news-frame','authored_inputs':e,'country':c['country'],'manager':c['manager'],'side':c['side'],'fixture_index':c['index'],'goals':c['goals'],'winner':c['winner'],'kind':c['kind'],'stage':c['stage'],'world_class':c['world'],'inputs':b.edits,'status':status,'error':error,'calls':installed.calls,'proof':prover.summary(),'timeline':timeline,'decision_calls':decisions,'checks':checks}


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE);ap.add_argument('--cases');ap.add_argument('--group');ap.add_argument('--variant');ap.add_argument('--no-record',action='store_true');a=ap.parse_args()
 if not a.no_record:
  dirty=subprocess.check_output(['git','status','--porcelain','--','runtime/original_match',str(Path(__file__).relative_to(ROOT))],cwd=ROOT,text=True)
  if dirty:raise SystemExit('refused dirty proof source:'+dirty)
 chosen=cases()
 if a.group:chosen=[c for c in chosen if c[0].startswith(a.group)]
 if a.cases:chosen=[c for c in chosen if c[0] in a.cases.split(',')]
 assert chosen
 source=next(c for c in runner.CASES if c[0]=='E040-r0004');path=ROOT/'.cache/dl'/source[3];data=path.read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==runner.expected(source[3])
 results=[]
 for case in chosen:
  r=prove(data,case,a.variant);results.append(r);print(case[0],r['status'],r['error'],flush=True)
  if r['status']!='completed':break
 caught=bool(a.variant and results[-1]['status']=='differs')
 good=caught if a.variant else len(results)==len(chosen) and all(p['status']=='completed' and all(v['proved']+v['nested']==p['calls'].get(k,0) and not v['before'] for k,v in p['proof'].items()) for p in results)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 record={'schema':'e040-t122d-function/1','task':'T122d','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+' '.join(sys.argv[1:]),'source_state':{'asset':source[3],'sha256':digest},'variant':a.variant,'caught':caught,'passes':results,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),ROOT/'runtime/original_match/port/news.py')}}
 if not a.no_record:
  a.out.mkdir(parents=True,exist_ok=True);dest=a.out/('function-'+(a.variant or 'normal')+'-'+stamp+'.json');assert not dest.exists();dest.write_text(json.dumps(record,indent=1)+'\n');print('record:',dest,flush=True)
 return 0 if good else 1
if __name__=='__main__':sys.exit(main())
