"""Named 3216/3179/377E arithmetic checked against retained original returns."""
import json
from pathlib import Path
import sys
from tables import ROOT,load_ds,s8,s16
from skill import record

sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha


def trunc_div(a,b):return -(abs(a)//b) if a<0 else a//b


def placement(p,n):
    read,_,_=load_ds()
    foot=read(0xE60+14*read(0xE7C+n%3)+p[7]);two=p[2]+p[5]==30
    flag=(not two and foot!=0 and p[6] in {3,7,10}) or (foot==0 and p[6] in {4,8,11}) or ((p[6]==0)!=(p[7]==0))
    return int(flag),foot,two


def trace(p,n=1,mutation=None):
    reason='energy' if s8(p[14])<1 else next((f'status-element-{e}' for e in [8,6,3] if p[16]&(1<<(e-1))),None)
    result={'unavailable':reason,'base_word':None,'form_high':None,'after_form_word':None,'clamped':None,'placement':None,'foot_index':None,'two_footed':None,'value':0}
    if reason and mutation!='ignore-unavailable':return result
    v=(p[4]+s8(p[14])-62)&65535;result['base_word']=v
    high=s8(p[12]) >= (33 if mutation=='form-cutoff33' else 32)
    result['form_high']=high
    v=(v-trunc_div(s16(v),16) if high else v+s8(p[12]))&65535
    result['after_form_word']=v
    v=max(0,min(255 if mutation=='clamp255' else 256,s16(v)));result['clamped']=v
    flag,foot,two=placement(p,n);result.update(placement=flag,foot_index=foot,two_footed=two)
    result['value']=v//2 if flag else v
    return result


def example(name,n=1,ability=225,energy=32,form=31,played=2,club=2,status=0,profile=8,peak=27,fitness=32):
    p=bytearray(record(ability=ability,profile=profile,club=club,form=form,energy=energy))
    p[6]=played;p[16]=status;p[2]=peak;p[13]=fitness
    return {'name':name,'inputs':{'player_index':n,'ability':ability,'energy':energy,'form':form,'played':played,'club':club,'status':status,'profile':profile,'peak':peak,'fitness':fitness},'trace':trace(p,n)}


def build():
    _,ds,ds_sources=load_ds();sources=list(ds_sources);files=[];errors=[]
    controls={m:0 for m in ['form-cutoff33','clamp255','ignore-unavailable']}
    for name in ['strength-001.json','strength-002-fitness.json','strength-003-structure.json']:
        path=f'experiments/E020-q018-condition-performance/records/{name}';sources.append(path);d=json.loads((ROOT/path).read_text())
        for key,base in [('foot_table_DS_0E60',0xE60),('foot_index_DS_0E7C',0xE7C)]:
            raw=bytes.fromhex(d[key]);assert raw==ds[base:base+len(raw)],f'foot window/static mismatch: {path}'
        for i,c in enumerate(d['comparisons']):
            p=bytes.fromhex(c['record']);n=c['player_word'];wanted=c['strength'];got=trace(p,n)['value']
            if got!=wanted:errors.append([path,i,got,wanted])
            for m in controls:controls[m]+=trace(p,n,m)['value']!=wanted
        files.append({'path':path,'cases':len(d['comparisons'])})
    assert not errors,errors[:5]
    assert all(controls.values()),controls
    examples=[example('healthy'),example('form32',form=32),example('energy1',energy=1),example('fitness0-same-strength',fitness=0),
      example('different-centre-role',played=5),example('left-index-right-flank',played=4),example('left-two-footed-right-flank',played=4,profile=5,peak=25),
      example('right-index-left-flank',n=2,played=3),example('right-two-footed-left-flank',n=2,played=3,profile=5,peak=25),
      example('keeper-outfield',club=0,played=2),example('outfielder-in-goal',played=0),example('injured-zero-energy',energy=0),
      example('substituted-off',status=4),example('booked-only',status=16),example('sent-off',status=32),example('mark-override-only',status=64),example('suspended',status=128),
      example('upper-clamp',ability=255,energy=127),example('clamp-before-placement',ability=255,energy=127,played=4),
      example('available-zero-strength',ability=0,energy=1,form=1),example('synthetic-negative-form',ability=180,energy=1,form=128)]
    return pin({'task':'T98b','sections':['Strength is a different reader','Availability and placement','Worked strength traces','Validation and interpretation limits'],
                'checks':{'retained_original_literal_cases':sum(f['cases'] for f in files),'mismatches':0,'caught_original_return_controls':controls},
                'retained_files':files,'examples':examples,
                'analysis_sha256':{p:sha((ROOT/p).read_bytes()) for p in ['notes/engine-study/T98/strength.py','notes/engine-study/T98/skill.py','notes/engine-study/T98/tables.py']}},
               ['1771:3216','1771:3179','1771:377E','1771:3041','1771:3088','1771:0BC4','1771:0AA7','1771:97CC','0791:BD03'],
               sources+['runtime/original_match/port/attributes.py','runtime/original_match/port/quick.py','static/goal-exe/code/seg_1771_05.asm',
                        'findings/F007-player-values-are-made-at-a-new-game-from-a-seed-per-country-not-from-the-dos-time.md'])
