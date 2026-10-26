"""Named 3A06/278A arithmetic, independently checked against retained literal returns."""
import json
from pathlib import Path
import sys
from tables import ROOT,load_ds,s8

sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha

RECORD_DIR='experiments/E020-q018-condition-performance/records'


def trace(record,element,slot=13,extra=56,halved=0,venue=0,event=0,mutation=None):
    read,_,_=load_ds()
    klass=read(0x6D25+12*record[7]+element)
    weight=read(0x6DCD+12*record[5]+klass)
    product=(weight*(record[4]+1))&65535
    derived=product//(31 if mutation=='divisor31' else 32)
    skill=derived//2 if halved and mutation!='omit-placement' else derived
    form=s8(record[12]);energy=s8(record[14])
    cutoff=33 if mutation=='form-cutoff33' else 32
    base=((form+1 if form<cutoff else 0)+(32 if element>=12 else energy))&65535
    low=(base*skill)&65535
    condition=low//256;quarter=skill//4
    before=condition+quarter
    gate=read(0x769+element)!=0 or (element==1 and event in {3,4})
    if mutation=='drop-element11' and element==11:gate=False
    after=(before+(extra if gate else 0))&65535
    share=after//16 if slot<12 and venue else 0
    return dict(klass=klass,weight=weight,scale=record[4]+1,display_bar=product//256,
                derived_skill=derived,skill_after_placement=skill,form_signed=form,energy_signed=energy,
                base_word=base,product_low=low,condition_term=condition,quarter_term=quarter,
                extra_applies=gate,extra_added=extra if gate else 0,before_venue=after,
                venue_share=share,value=(after+share)&65535)


def record(ability=180,profile=8,club=2,form=31,energy=32):
    p=bytearray(20);p[0]=7;p[1]=25;p[2]=27;p[3]=200;p[4]=ability;p[5]=profile;p[6]=club;p[7]=club;p[12]=form;p[13]=32;p[14]=energy
    return bytes(p)


def build():
    read,ds,ds_sources=load_ds()
    compared=[];mismatches=[];controls={m:0 for m in ['divisor31','form-cutoff33','omit-placement']};sources=list(ds_sources)
    for name in ['contest-001.json','contest-002-events.json','contest-003-fitness.json']:
        source=f'{RECORD_DIR}/{name}';sources.append(source);d=json.loads((ROOT/source).read_text())
        for key,base in [('class_table_DS_6D25',0x6D25),('profile_table_DS_6DCD',0x6DCD),('keeper_gate_DS_0769',0x769)]:
            raw=bytes.fromhex(d[key]);assert raw==ds[base:base+len(raw)],f'retained/static table mismatch: {source}/{key}'
        for i,c in enumerate(d['comparisons']):
            args=(bytes.fromhex(c['record']),c['element'],c['pitch_6'],c['pitch_11'],c['pitch_13'],c['flag_80fc'],c['event_code_8327'])
            got=trace(*args)['value'];expected=c['contest']
            if got!=expected:mismatches.append([source,i,got,expected])
            for m in controls:controls[m]+=trace(*args,mutation=m)['value']!=expected
        compared.append({'path':source,'cases':len(d['comparisons'])})
    assert not mismatches,mismatches[:5]
    assert all(controls.values()),controls
    examples=[]
    specs=[('healthy-tackling',{},3,{}),('form32-tackling',{'form':32},3,{}),('energy1-tackling',{'energy':1},3,{}),
      ('placement-tackling',{},3,{'halved':1}),('shooting-extra',{},11,{}),('placement-shooting',{},11,{'halved':1}),
      ('penalty-energy1',{'energy':1},12,{}),('penalty-energy32',{},12,{}),
      ('keeper-side1-host',{'club':0},1,{'slot':1,'venue':1}),('keeper-side0-context',{'club':0},1,{'slot':12,'venue':1}),
      ('keeper-event3',{'club':0},1,{'slot':1,'event':3}),('synthetic-negative-form',{'form':128,'energy':1},3,{}),
      ('profile16-last-role',{'profile':16,'club':13},12,{}),('ability255-display-edge',{'ability':255,'profile':1,'club':0},1,{})]
    for name,changes,e,flags in specs:
        p=record(**changes);settings=dict(slot=13,extra=56,halved=0,venue=0,event=0);settings.update(flags)
        examples.append({'name':name,'inputs':{'ability':p[4],'profile':p[5],'club_position':p[7],'form':p[12],'energy':p[14],'element':e,**settings},'trace':trace(p,e,**settings)})
    e11=next(c for c in examples if c['name']=='shooting-extra')
    assert trace(record(),11,mutation='drop-element11')['value']!=e11['trace']['value']
    # Full one-based indices, not the shorter windows saved for E020's profile8/club2 tests.
    class_max=max(12*c+e for c in range(14) for e in range(1,13))
    profile_max=max(12*p+read(0x6D25+12*c+e) for p in range(1,17) for c in range(14) for e in range(1,13))
    return pin({'task':'T98a','sections':['Inputs and finite-width operations','Effective skill pipeline','Worked traces','Validation scope and limitations'],
                'checks':{'retained_original_literal_cases':sum(c['cases'] for c in compared),'mismatches':0,'caught_original_return_controls':controls,'element11_source_control':'caught on worked trace'},
                'retained_files':compared,'examples':examples,'legacy_window_bounds':{'class_saved_bytes':168,'class_max_index':class_max,'profile_saved_bytes':192,'profile_max_index':profile_max},
                'analysis_sha256':{p:sha((ROOT/p).read_bytes()) for p in ['notes/engine-study/T98/skill.py','notes/engine-study/T98/tables.py']}},
               ['1771:3A06','1771:3947','0791:278A','0791:A260','1771:0AA7','0791:2974'],
               sources+['runtime/original_match/port/geometry.py','runtime/original_match/port/attributes.py','static/goal-exe/code/seg_0791_04.asm','static/goal-exe/code/seg_1771_05.asm'])
