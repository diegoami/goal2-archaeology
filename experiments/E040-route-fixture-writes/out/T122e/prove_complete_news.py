"""T122e isolated statistics/parent proof and actual-page comparisons.
All public page outputs are hashes/scalars. Raw4000cellcaptures remain privatecache.
"""
import argparse,collections,datetime,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'experiments/E040-route-fixture-writes'))
from original_match import port
from original_match.news import news_pages
from original_match.port.prove import Prover,ProofError
spec=importlib.util.spec_from_file_location('t122d_frozen_recipe',HERE.parent/'T122d/prove_headlines.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
prepare=d.prepare
spec=importlib.util.spec_from_file_location('e040_news_proof',HERE.parents[1]/'prove.py');ep=importlib.util.module_from_spec(spec);spec.loader.exec_module(ep)
page_receipts=ep.news_receipts

def step(seed):return (seed*0x7ABD+0x1B0F)&65535

def seed_choice(bound,choice):return next(s for s in range(65536) if (step(s)*bound>>16)+1==choice)

def cases():
 out=list(d.cases())
 def add(name,entry,**e):out.append((name,entry,e))
 for side in (0,1):
  for result in ('win','loss'):
   for choice in range(1,19):add(f'stat-4440-{side}-{result}-{choice}','4440',side=side,result=result,slots=(1,) if result=='win' else (),score=0,seed=seed_choice(18,choice),row=6 if side==0 else 10)
  for kind in (0xCB,0x67,0xC9,0x65):add(f'stat-3CC8-special-{side}-{kind}','3CC8',side=side,result='win',kind=kind,slots=(1,))
  for margin,member in ((1,True),(1,False),(3,True)):
   for choice in range(1,7):add(f'stat-3CC8-win-{side}-{margin}-{int(member)}-{choice}','3CC8',side=side,result='win',slots=(1,)*margin,member=member,seed=seed_choice(6,choice))
  for choice in range(1,4):add(f'stat-3CC8-zero-draw-{side}-{choice}','3CC8',side=side,goals=(0,0),winner=2,seed=seed_choice(3,choice))
  for score in (-128,-11,-10,-8,-7,-6):
   for entry in ('3CC8','4A87'):add(f'stat-band-{entry}-{side}-{score}',entry,side=side,score=score)
  for rating in ('balanced','own-strong','other-strong'):
   for choice in range(1,7):add(f'stat-3CC8-loss-{side}-{rating}-{choice}','3CC8',side=side,score=-5,rating=rating,seed=seed_choice(6,choice))
  for choice in range(1,17):add(f'stat-4A87-win-{side}-{choice}','4A87',side=side,result='win',slots=(1,),seed=seed_choice(16,choice))
  for kind,bound in ((1,2),(2,4)):
   for choice in range(1,bound+1):add(f'stat-4A87-fouls-{side}-{kind}-{choice}','4A87',side=side,kind=kind,fouls=11,seed=seed_choice(bound,choice))
  add(f'stat-4A87-high-kind-{side}','4A87',side=side,kind=0x67,threshold='below',seed=0)
  for member in (False,True):
   for rating in ('own-strong','other-strong'):
    for seed in (0,1):add(f'stat-4A87-set-{side}-{int(member)}-{rating}-{seed}','4A87',side=side,member=member,rating=rating,seed=seed)
 add('crowd-positive','4E0E',side=0,result='win',kind=0xCB,slots=(1,),queued_key=13)
 return out

DECISIONS={13037: '1771:5C60', 13147: '000E:1F4D', 13163: '214B:06B1', 13321: '214B:06B1', 13486: '214B:06B1', 13880: '000E:1F4D', 13893: '214B:06B1', 13976: '214B:06B1', 14098: '000E:0B77', 14270: '000E:1F4D', 14286: '214B:06B1', 14445: '000E:09DB', 14458: '214B:06B1', 14580: '000E:0A53', 14593: '214B:06B1', 14714: '214B:06B1', 14977: '214B:06B1', 15728: '1771:5C60', 15742: '214B:06B1', 15873: '214B:06B1', 15930: '214B:06B1', 16008: '214B:06B1', 16067: '000E:0B77', 16208: '000E:09DB', 16221: '214B:06B1', 16312: '000E:0A53', 16325: '214B:06B1', 16398: '214B:06B1', 17528: '214B:06B1', 17927: '214B:06B1', 18455: '214B:06FA', 19145: '000E:0B77', 19363: '000E:4865', 19385: '214B:06FA', 19434: '214B:06B1', 19530: '214B:06B1', 19859: '000E:09DB', 19868: '214B:06FA', 19906: '000E:3CC8', 19914: '000E:4A87', 19940: '000E:4A87', 20133: '1771:3A82', 1152: '214B:06B1', 1164: '214B:06B1', 1207: '214B:06B1', 28590: '1771:0B77'}

def run_one(data,case,variant=None,original=False,capture=True):
 name,entry,e=case;b,c=prepare(data,entry,e);
 if 'fouls' in e:b.byte(b.m.DS*16+0x7B84+10*c['side'],e['fouls'],'actual foul statistic for4865')
 route=b.route;route.capture_news=capture;
 if e.get('queued_key') is not None:route.keys.waiting=e['queued_key']
 m=b.m;ss=c['ss'];sp=0x3900;timeline=[];decisions=[];reset_stack=[]
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
 loaded=[] if original else [(port._module_registry('news'),variant)]
 installed=port.install(m,loaded)
 m.at('000E:4E0E',news_entry);m.at('000E:05F6',wait_entry);m.at('000E:4F72',wait_return);m.at('000E:01FA',unmanage_entry);m.at('0791:BC5D',reset_entry);m.at('000E:0244',reset_return)
 def decision(ret):
  def visit(replay):
   if not replay:
    ax=m.reg('ax');decisions.append({'return':f'000E:{ret:04X}','target':DECISIONS[ret],'ax':ax,'al':ax&255,'signed_ax':(ax+32768)%65536-32768})
  return visit
 for ret in DECISIONS:m.at(f'000E:{ret:04X}',decision(ret))
 note_count=[0]
 def note(replay):
  if not replay:note_count[0]+=1
 m.at('214B:1EF1',note)
 prover=None if original else Prover(m,installed)
 if entry=='route-fragment':
  bp=0x3EDE;sp=bp-0x16
  b.word(ss*16+bp,0x3EEA,'actual route caller saved BP');b.word(ss*16+bp+2,0x70D4,'actual route caller return IP')
  for off,value in ((-0x10,m.rd(0xA923)),(-0xE,m.rd(0xA925)),(-0x14,(m.rd(0xA92B)+8*(c['index']-1))&65535),(-0x12,m.rd(0xA92D))):b.word(ss*16+bp+off,value,'actual route-frame far pointer')
  b.byte(ss*16+bp-4,1,'managed-match flag in actual route frame')
  b.word(c['game']+0x26,c['index'],'post-match route cursor')
  start=0x6F91;end='000E:6FE1';m.at(end,lambda replay:m.stop('news-loop-return'))
 else:
  bp=0x3F00;start=int(entry,16);end='000E:7080';m.at(end,lambda replay:m.stop('function-return'))
  args=[c['manager']-128] if entry=='01FA' else [c['wrapper'],e.get('row',6)] if entry=='4440' else [c['wrapper']] if entry in ('319B','3CC8','4A87') else [c['parent']] if entry=='4DB7' else [(m.rd(0xA92B)+8*(c['index']-1))&65535,m.rd(0xA92D),c['country']]
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
 result={'case':name,'entry':entry,'category':'declared-original-route-fragment' if entry=='route-fragment' else 'isolated-unmanage-stress' if entry=='01FA' else 'isolated-headline-news-frame','authored_inputs':e,'country':c['country'],'manager':c['manager'],'side':c['side'],'fixture_index':c['index'],'goals':c['goals'],'winner':c['winner'],'kind':c['kind'],'stage':c['stage'],'world_class':c['world'],'inputs':b.edits,'status':status,'error':error,'calls':installed.calls,'proof':prover.summary() if prover else {},'timeline':timeline,'decision_calls':decisions,'checks':checks}
 result['note_calls']=note_count[0]
 result['actual_crowd_conditional_third_draws']=sum(d['return']=='000E:04B7' for d in decisions)
 if name=='crowd-positive' and status=='completed' and not variant:
  armed=installed.calls.get('000E:045D',0)>=1 and result['actual_crowd_conditional_third_draws']>0 and note_count[0]==0 and len(route.news_history)==1 and route.news_history[0].waiting_key==13
  result['positive_crowd_arming_check']=armed
  if not armed:result['status'],result['error']='unreached-crowd-or-note-policy',str({'calls':installed.calls,'third_draws':result['actual_crowd_conditional_third_draws'],'notes':note_count[0]})
 result['news_history']=page_receipts(route)
 result['formal_prover']=not original
 return result,route


def prove(data,case,variant=None):
    result,route=run_one(data,case,variant)
    if case[1]=='route-fragment' and variant is None and result['status']=='completed':
        reference,original=run_one(data,case,original=True)
        control,plain=run_one(data,case,original=True,capture=False)
        equal=[a.cells==b.cells for a,b in zip(route.news_history,original.news_history)]
        attrs=('country','side','manager','flags_words','return_address','waiting_key','pushed_back','key_code','seed_words')
        metadata=[all(getattr(a,k)==getattr(b,k) for k in attrs) for a,b in zip(route.news_history,original.news_history)]
        regs=('eax','ebx','ecx','edx','esi','edi','ebp','esp','eflags','cs','ds','es','ss','fs','gs','eip')
        compare={'reference_status':reference['status'],'control_status':control['status'],'ported_pages':len(route.news_history),'original_pages':len(original.news_history),'cells_equal_each':equal,'metadata_equal_each':metadata,
                 'reference_page_receipts':reference['news_history'],'original_capture_control_memory_equal':original.m.read(0,0x110000)==plain.m.read(0,0x110000),'original_capture_control_registers_equal':all(original.m.reg(k)==plain.m.reg(k) for k in regs),'original_capture_control_key_rng_record_equal':original.record==plain.record,
                 'first_page_retained_after_second':len(route.news_history)==2 and route.news_history[0].cells!=route.news_history[1].cells,
                 'first_manager_frozen_before_release':route.news_history[0].manager>=128 and route.m.read(route.m.far(0xA917)+191*route.news_history[0].country+0x2E,1)[0]==route.news_history[0].country}
        result['page_comparison']=compare
        if reference['status']!='completed' or control['status']!='completed' or len(equal)!=2 or not all(equal+metadata) or not all(compare[k] for k in ('original_capture_control_memory_equal','original_capture_control_registers_equal','original_capture_control_key_rng_record_equal','first_page_retained_after_second','first_manager_frozen_before_release')):
            result['status'],result['error']='page-comparison-failed',str(compare)
    return result


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE);ap.add_argument('--group');ap.add_argument('--cases');ap.add_argument('--variant');ap.add_argument('--no-record',action='store_true');a=ap.parse_args()
 paths=['runtime/original_match',str(Path(__file__).relative_to(ROOT)),str(HERE.parent.relative_to(ROOT)/'T122d/prove_headlines.py'),'experiments/E040-route-fixture-writes/prove.py']
 if not a.no_record:
  dirty=subprocess.check_output(['git','status','--porcelain','--',*paths],cwd=ROOT,text=True)
  if dirty:raise SystemExit('refused dirty source:'+dirty)
 selected=cases()
 if a.group:selected=[c for c in selected if c[0].startswith(a.group)]
 if a.cases:selected=[c for c in selected if c[0] in a.cases.split(',')]
 assert selected
 source=next(c for c in d.runner.CASES if c[0]=='E040-r0004');data=(ROOT/'.cache/dl'/source[3]).read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==d.runner.expected(source[3])
 results=[]
 for case in selected:
  p=prove(data,case,a.variant);results.append(p);print(case[0],p['status'],p['error'],flush=True)
  if p['status']!='completed':break
 caught=bool(a.variant and results[-1]['status']=='differs')
 good=caught if a.variant else len(results)==len(selected) and all(p['status']=='completed' and all(v['proved']+v['nested']==p['calls'].get(k,0) and not v['before'] for k,v in p['proof'].items()) for p in results)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 record={'schema':'e040-t122e-parent/1','task':'T122e','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+' '.join(sys.argv[1:]),'source_state':{'asset':source[3],'sha256':digest},'variant':a.variant,'caught':caught,'passes':results,
         'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths if (ROOT/p).is_file()}|{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('runtime/original_match/news.py','runtime/original_match/port/news.py','runtime/original_match/route.py')}}
 if not a.no_record:
  a.out.mkdir(parents=True,exist_ok=True);p=a.out/('parent-'+(a.variant or 'normal')+'-'+stamp+'.json');assert not p.exists();p.write_text(json.dumps(record,indent=1)+'\n');print('record:',p,flush=True)
 return 0 if good else 1
if __name__=='__main__':sys.exit(main())
