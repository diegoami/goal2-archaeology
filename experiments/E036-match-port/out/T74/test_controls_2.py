"""T74 fixed-pre-task baseline and one-instruction/ABI controls; no checkout mutation."""
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent/'controls-2'
BASE='53b011249446c4a562624b573b84640726134c6b'
P='runtime/original_match/port/menus.py'
# (name,path,function boundary,unique original text,replacement)
CONTROLS=[
 ('poll-bool-inverted',P,'key_pressed','has = mem.keypressed(_ret_site(mem))','has = not mem.keypressed(_ret_site(mem))'),
 ('pushed-back-flag-kept',P,'read_key',"mem.wds8(0x79AE, 0, '214B:08EA')","mem.wds8(0x79AE, 1, '214B:08EA')"),
 ('pushback-flag-clear',P,'push_back_key',"mem.wds8(0x79AE, 1, '214B:0996')","mem.wds8(0x79AE, 0, '214B:0996')"),
 ('wait-current-key-kept',P,'wait_key_clear',"mem.wds8(0xA976, 0, '214B:098A')","mem.wds8(0xA976, 1, '214B:098A')"),
 ('home-clamps-to-two',P,'_clamp',"put(mem,r,0,1,'214B:'","put(mem,r,0,2,'214B:'"),
 ('clamp-down-at-max',P,'_clamp','if r.ax<ss16(mem,r,r.bp+6):','if r.ax<=ss16(mem,r,r.bp+6):'),
 ('wrap-down-stores-two',P,'_wrap',"put(mem,r,0,1,'214B:'","put(mem,r,0,2,'214B:'"),
 ('position-cycle-thirteen',P,'next_position','farg(mem,r,4);r.ax=14','farg(mem,r,4);r.ax=13'),
 ('club-role-not-restored',P,'edit_position','farg(mem,r,-4);r.al=rb(mem,r,7)','farg(mem,r,-4);r.al=rb(mem,r,6)'),
 ('position-refresh-unconditional',P,'edit_position','if mem.ds8(0x0C1F):','if True:'),
 ('quick-guard-omitted',P,'switch_to_quick','if not mem.ds8(0x9A3E) and mem.ds16(0x831B)','if True and mem.ds16(0x831B)'),
 ('quick-defer-not-marked',P,'switch_to_quick',"mem.wds8(0x7C38,1,'0791:934F')","mem.wds8(0x7C38,0,'0791:934F')"),
 ('quick-active-flag-clear',P,'switch_to_quick',"mem.wds8(0x9A3E,1,'0791:9356')","mem.wds8(0x9A3E,0,'0791:9356')"),
 ('speed-left-cap-four',P,'match_key_poll','key==0xAE and speed<5','key==0xAE and speed<4'),
 ('speed-right-wrong-step',P,'match_key_poll',"else speed-1,'9413'","else speed+1,'9413'"),
 ('poll-key-return-site-wrong',P,'match_key_poll',"ret='93D3'","ret='93D4'"),
 ('notice-keeper-template-wrong',P,'timed_notice','0x5B66 if keeper else 0x5B30','0x5B30 if keeper else 0x5B66'),
 ('notice-timeout-key-zero',P,'timed_notice',"mem.wds8(0xA977,0x1B,'0791:8052')","mem.wds8(0xA977,0,'0791:8052')"),
 ('tactics-ignore-lock',P,'edit_team_tactics','bool(r.al) and not mem.ds8(0x0C20)','bool(r.al)'),
 ('tactics-no-save-flag',P,'edit_team_tactics',"mem.wds8(0xC1A,1,'1771:1A72')","mem.wds8(0xC1A,0,'1771:1A72')"),
 ('menu-no-tactics-refresh',P,'in_match_menu',"mem.wds8(0x9B55,1,'0791:F004')","mem.wds8(0x9B55,0,'0791:F004')"),
 ('menu-all-esc-exit',P,'in_match_menu','and bool(mem.ds8(0xC1F))','and True'),
 ('menu-ignores-invalid-eleven',P,'in_match_menu','if r.al:break','if True:break'),
 ('own-default-override-set',P,'edit_own_tactics',"_g(mem,r,'0CA1',element,r.es,r.di,ret='1771:4C6F')","_g(mem,r,'0C79',element,r.es,r.di,ret='1771:4C6F')"),
 ('own-override-not-cleared',P,'edit_own_tactics',"_g(mem,r,'0CA1',element,r.es,r.di,ret='1771:4CB1')","_g(mem,r,'0C79',element,r.es,r.di,ret='1771:4CB1')"),
 ('marking-other-side-wrong',P,'cycle_marking','r.al=int(not second)','r.al=int(second)'),
 ('marking-no-wrap',P,'cycle_marking','if index>11:','if index>12:'),
 ('marking-unavailable-not-skipped',P,'cycle_marking','if not r.al:break','if True:break'),
 ('message-return-low-flag-wrong',P,'message_if_flag','r.al=ss8(mem,r,r.bp-1)','r.al=0'),
 ('message-attribute-not-restored',P,'message_wait_key',"mem.wds8(0x7922,r.al,'214B:0555')","mem.wds8(0x7922,0,'214B:0555')"),
 ('yes-no-tests-n',P,'ask_yes_no',"r.al==ord('Y')","r.al==ord('N')"),
 ('key-set-accepts-nonmember',P,'wait_key_in_set','if member(mem):break','if not member(mem):break'),
 ('list-pair-cursor-wrong-arg',P,'set_list_pair','r.ax=ss16(mem,r,r.bp+8)','r.ax=ss16(mem,r,r.bp+6)'),
 ('name-save-flag-clear',P,'edit_player_name',"mem.wds8(0xC1A,1,'1771:491A')","mem.wds8(0xC1A,0,'1771:491A')"),
 ('name-delete-count-one',P,'edit_player_name','r.ax=r.ax+1','r.ax=1'),
 ('list-home-cursor-two',P,'list_scroll','r.ax=1;pair=1,1','r.ax=2;pair=2,1'),
 ('list-end-top-off-by-one',P,'list_scroll','value=(count-page+1)','value=(count-page)'),
 ('interrupt-flags-df-lost',P,'_dos_interrupt',"saved_flags=mem.reg('eflags')&M16","saved_flags=mem.reg('eflags')&M16&~0x400"),
 ('msdos-return-displacement-zero',P,None,'return_stack_delta=-2','return_stack_delta=0'),
 ('cached-key-consumed-twice','runtime/original_match/match.py',None,'del k._ported_key','pass  # mutation: cache retained'),
 ('return-displacement-ignored','runtime/original_match/port/guest.py',None,'self.sp + entry.return_stack_delta','self.sp'),
]

def mutate(source,function,old,new):
    if function is None:
        assert source.count(old)==1,(function,old,source.count(old))
        return source.replace(old,new)
    start=source.index('def '+function+'(')
    end=source.find('\n\ndef ',start+1)
    decorator=source.find('\n\n@',start+1)
    if decorator!=-1:end=min(end,decorator) if end!=-1 else decorator
    if end==-1:end=len(source)
    body=source[start:end]
    assert body.count(old)==1,(function,old,body.count(old))
    return source[:start]+body.replace(old,new)+source[end:]

OUT.mkdir(exist_ok=False)
results=[]
for name,path,function,old,new in [('fixed-pre-task-baseline',None,None,None,None)]+CONTROLS:
    with tempfile.TemporaryDirectory(prefix='T74-controls-') as raw:
        tree=Path(raw)
        if path is None:
            archive=subprocess.check_output(['git','archive',BASE,'runtime'],cwd=ROOT)
            with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(tree,filter='data')
        else:
            shutil.copytree(ROOT/'runtime',tree/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            source=(tree/path).read_text();(tree/path).write_text(mutate(source,function,old,new))
        (tree/'tests').mkdir()
        (tree/'tests/__init__.py').write_text('')
        for test in ('test_port_menus.py','test_port_update.py'):
            shutil.copy(ROOT/'tests'/test,tree/'tests'/test)
        r=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_port_menus'],cwd=tree,
                         capture_output=True,text=True,timeout=90)
        (OUT/(name+'.log')).write_text(r.stdout+r.stderr)
        caught=r.returncode!=0 and ('AssertionError' in r.stderr or 'GuestError' in r.stderr or
                                    (path is None and 'cannot import name' in r.stderr))
        results.append({'name':name,'caught':caught,'returncode':r.returncode,'path':path,'function':function,
                        'original':old,'replacement':new})
        print(f'{name}: exit{r.returncode}, '+('caught' if caught else 'NOT CAUGHT'),flush=True)
(OUT/'summary.json').write_text(json.dumps({'baseline':BASE,'menus_sha256':hashlib.sha256((ROOT/P).read_bytes()).hexdigest(),
    'tests_sha256':hashlib.sha256((ROOT/'tests/test_port_menus.py').read_bytes()).hexdigest(),'results':results},indent=2)+'\n')
print(f'{sum(r["caught"] for r in results)}/{len(results)} controls caught',flush=True)
raise SystemExit(0 if all(r['caught'] for r in results) else 1)
