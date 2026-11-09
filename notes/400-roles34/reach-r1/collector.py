#!/usr/bin/env python3
"""T131 collector: the penalty (role 3) and free-kick (role 4) taker decisions of CC7B, by the original's own keys.

Sub-commands (each writes a new folder notes/400-roles34/<name>/, never overwritten, and its raw states under
.cache/400-roles34/<name>/):

  reach NAME      T170e's path: boot at the DOS date call, new game, rounds from the manager menu, the player's repair
                  of an eleven the original refuses (the squad screen's own keys), until the unchanged Core stops.
  search NAME MENU ROUND SHA BOUND_S MAXROUND
                  From a kept manager menu play the rounds as the season oracle does (taker prompts answered by the
                  original's timer) and, at the first role 3 and the first role 4 taker decision, keep it and branch.
  preceding NAME MENU ROUND RUN
                  Replay one round from its kept menu and keep the wait just before the RUN-th key wait.

Only unchanged Core.boot/load/press and read-only observations: no guest write, no register edit, no CPU moved. The one
host adapter (`adapt`) widens the Core's *screen label* for CC7B roles 3 and 4 to the label it gives roles 2 and 5, so the
Core serves the original's own poll with the original's own keys (as notes/400-last's uc-r1 labelled roles 2/5). It
changes no guest byte; frames.py reads the actual role bytes, a label alone is never the evidence.
"""
import contextlib,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

CORE=ROOT/'.cache/400-roles34/core-source'
CACHE=ROOT/'.cache/400-roles34'
DATE_CALL=CACHE/'e039-r0005-date-call.sav';GOAL_DAT=CACHE/'GOAL.DAT'
DATE_CALL_SHA='0d9c683023c7327f17bfc29900f2eff4e703641d21d3f353693f09654688494b'
GOAL_DAT_SHA='bc5e5c04434d31f350eb7803afc3810333393e049d50dde559797a5b068c60ca'
BOOT_DATE,BOOT_TIME=(1990,10,4),(10,0,20,95)
DENMARK,MANAGER='7','bob'
SPACE,RETURN=0x20,13
def sha(b):return hashlib.sha256(b).hexdigest()

PIN='42c25412a81a397cb40ed28ba54bca7c688d8b07'   # goal2 main at T170e's merge (#694), copied by `git archive` into .cache/400-roles34/core-source
def pin():return PIN

def tree_hashes():
    files={}
    for p in sorted(CORE.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:files[str(p.relative_to(CORE))]=sha(p.read_bytes())
    return files

class Run:
    def __init__(self,name,bound_s,kind,**extra):
        self.name=name;self.pub=HERE/name;self.private=CACHE/name
        self.pub.mkdir(exist_ok=False);self.private.mkdir(exist_ok=False)
        self.n=0;self.start=time.monotonic()
        import sys as _s
        self.rec=dict(attempt=name,kind=kind,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                      collector_sha256=sha(Path(__file__).read_bytes()),frames_sha256=sha((HERE/'frames.py').read_bytes()),
                      core_source_commit=pin(),core_tree_sha256=sha(json.dumps(tree_hashes(),sort_keys=True).encode()),
                      date_call_sha256=sha(DATE_CALL.read_bytes()),goal_dat_sha256=sha(GOAL_DAT.read_bytes()),
                      python=_s.version,bound_s=bound_s,status='aborted',method='Unchanged Core.boot/load/press and the season oracle; read-only observations; no guest write, register edit or CPU move',**extra)
        for f in ('collector.py','frames.py'):
            (self.pub/f).write_bytes((HERE/('collect.py' if f=='collector.py' else f)).read_bytes())
        assert self.rec['date_call_sha256']==DATE_CALL_SHA and self.rec['goal_dat_sha256']==GOAL_DAT_SHA
        try:
            import unicorn;self.rec['unicorn']=unicorn.__version__
        except Exception:pass
        (self.pub/'source.json').write_text(json.dumps(self.rec,indent=2)+'\n')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError(f'{bound_s}-second bound')));signal.alarm(bound_s)
    def keep(self,label,data):
        p=self.private/label;p.write_bytes(data);return dict(file=str(p.relative_to(ROOT)),sha256=sha(data),bytes=len(data))
    def row(self,**kw):
        self.n+=1;kw=dict(n=self.n,t=round(time.monotonic()-self.start,3),**kw)
        with (self.pub/'steps.jsonl').open('a') as o:o.write(json.dumps(kw)+'\n')
        print(json.dumps({k:v for k,v in kw.items() if k in('n','t','label','round','site','kind','role','error','elapsed')}),flush=True)
        return kw
    def finish(self):
        signal.alarm(0);self.rec.update(elapsed_s=time.monotonic()-self.start,observations=self.n)
        (self.pub/'record.json').write_text(json.dumps(self.rec,indent=2)+'\n')

def load_core():
    sys.dont_write_bytecode=True;sys.path.insert(0,str(CORE))
    global Core,Driver,so,screens,views,UnknownScreen,CoreError,DriverError,BRANCH_CORE
    from goal2.core import Core,CoreError,screens,views
    from goal2.core.runner import UnknownScreen
    from goal2.core.driver import Driver,DriverError
    from goal2.tests import season_oracle as so
    BRANCH_CORE=so._core_driver      # the oracle's own constructor, for a branch that must not enter a round's cores

def adapt():
    """Label CC7B roles 3 and 4 as the Core labels roles 2 and 5 (the same frame checks), so the Core's own poll
    service answers the original's poll. A host label only; nothing in guest memory or registers changes."""
    original=screens._taker
    def taker(f,bp):
        if f.byte(bp,4) in (3,4):
            if f.near_caller(bp)!=0x6D74 or f.byte(bp,6) not in (0,1) or not 1<=f.word(bp,-5)<=11:return None
            return screens.TAKER_SELECT
        return original(f,bp)
    screens._taker=taker

def build_start():
    wait=Core.boot(DATE_CALL.read_bytes(),BOOT_DATE,dos_time=BOOT_TIME,goal_dat=GOAL_DAT,title_key='n')
    driver=Driver(wait.core);driver.new_game(int(DENMARK),MANAGER)
    assert driver.wait.kind=='manager-menu'
    return driver.core.save(),len(driver.core.keys)

@contextlib.contextmanager
def capturing(counter=None):
    """Collect each Core `core_rounds` builds, and count (counter) the runs of the main one."""
    original=so._core_driver;cores=[]
    def wrapped(blob,goal_dat):
        core,driver=original(blob,goal_dat);core.main=True;cores.append(core);return core,driver
    so._core_driver=wrapped
    try:yield cores
    finally:so._core_driver=original

def repair_eleven(blob):
    """The player's answer to an eleven the original refuses, by the squad screen's own keys (T111 fix_eleven policy as
    goal2's T170e makes it): swap the first eleven player not fit with a fit bench player of the same line."""
    from goal2.core.driver import RETURN as RT,SQUAD
    driver=Driver(Core.load(blob,goal_dat=GOAL_DAT));wait=driver.wait;memory=views.Memory(wait.state)
    rows=views.team(wait.state)['squad'];cards={r['player']:views.player_card(wait.state,r['player']) for r in rows}
    fit=memory.code_str(0x1771,0x4298)
    off=next(r for r in rows if r['eleven'] and cards[r['player']]['readiness']!=fit)
    on=next(r for r in reversed(rows) if not r['eleven'] and r['line']==off['line'] and cards[r['player']]['readiness']==fit)
    driver._open_squad();driver._to_player(off['player'])
    if driver.press(RT,expect=(SQUAD,)).view['marked'] is None:raise AssertionError(f"the original did not mark player {off['player']}")
    driver._to_player(on['player']);driver.press(RT,expect=(SQUAD,));driver.to_menu()
    eleven=[r['player'] for r in views.team(driver.wait.state)['squad'] if r['eleven']]
    assert off['player'] not in eleven and on['player'] in eleven
    return driver.core.save(),(off['player'],on['player'])

def observe_state(run,label,core,**kw):
    """One observation of a Core at a wait or stopped: states kept, frame derived from the kept bytes themselves."""
    import frames
    snap=core.m.snapshot();keep=None;problems=[]
    d=None
    try:d=frames.derive(snap['memory'],snap['load'],snap['regs'])
    except AssertionError as e:problems.append(str(e))
    if core.wait is not None:
        blob=core.save();keep=run.keep(f'{run.n+1:03}-{label}.g2core',blob)
    else:
        import io,zipfile
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('memory.bin',snap['memory']);z.writestr('registers.json',json.dumps(dict(load=snap['load'],regs=snap['regs'])))
        keep=run.keep(f'{run.n+1:03}-{label}.ucstate',buf.getvalue())
    w=core.wait
    return run.row(label=label,site=(w.site if w else d and d['site']),kind=(w.kind if w else None),poll=(w.poll if w else None),
                   text=core._text(),keys=len(core.keys),keys_sha256=sha(bytes(core.keys)),regs=snap['regs'],load=snap['load'],
                   frame=d,frame_problems=problems,state=keep,**kw)

# --------------------------------------------------------------------------------------------------------------------

def reach(name):
    load_core()
    run=Run(name,5400,'reach',path='T170e: Core.boot at the date call, Driver.new_game, rounds with the squad-screen repair')
    run.rec['boot']=dict(date=BOOT_DATE,dos_time=BOOT_TIME,country=int(DENMARK),manager=MANAGER,title_key='n')
    (run.pub/'source.json').write_text(json.dumps(run.rec,indent=2)+'\n')
    try:
        blob,nkeys=build_start()
        run.row(label='start',kind='manager-menu',keys=nkeys,state=run.keep('start.g2core',blob),elapsed=round(time.monotonic()-run.start,2))
        current=blob
        for number in range(1,13):
            run.row(label=f'menu-r{number:02}',round=number,state=run.keep(f'menu-r{number:02}.g2core',current),elapsed=round(time.monotonic()-run.start,1))
            attempts=0
            while True:
                with capturing() as cores:
                    try:got=so.core_rounds(current,GOAL_DAT,1)
                    except DriverError as e:
                        if 'refuses the eleven' not in str(e) or attempts>=8:raise
                        refusal=str(e)
                    except UnknownScreen as e:
                        core=cores[-1]
                        observe_state(run,f'unknown-screen-r{number:02}',core,round=number,site=e.site,poll=e.poll,error=str(e).splitlines()[0])
                        run.rec['status']='unknown screen captured';run.rec['stop']=dict(round=number,site=e.site,poll=e.poll)
                        raise SystemExit
                    else:break
                attempts+=1
                current,swap=repair_eleven(current)
                run.row(label=f'repair-r{number:02}',round=number,refusal=refusal,swap=list(swap),
                        state=run.keep(f'menu-r{number:02}-repair{attempts}.g2core',current),elapsed=round(time.monotonic()-run.start,1))
            run.row(label=f'round-r{number:02}',round=number,round_kind=got[0].kind,before=got[0].before,after=got[0].after,elapsed=round(time.monotonic()-run.start,1))
            if got[0].kind=='deferred-rollover':run.rec['status']='season ended';break
            current=cores[-1].save()
    except SystemExit:pass
    except BaseException as e:
        run.rec['error']=repr(e);print(repr(e),flush=True)
    finally:run.finish()

def search(name,menu,number,menu_sha,bound,maxround):
    load_core();adapt()
    number=int(number);raw=Path(menu).read_bytes();assert sha(raw)==menu_sha
    run=Run(name,int(bound),'search',menu=dict(file=str(Path(menu)),sha256=menu_sha),first_round=number,max_round=int(maxround),
            adapter='screens._taker also labels CC7B roles 3 and 4 TAKER_SELECT (host label only)')
    captured={};seen=set();state=dict(round=number,runs=0)
    original_run=Core._run
    def counting(self):
        if getattr(self,'main',False):state['runs']+=1
        return original_run(self)
    Core._run=counting
    original_key=Driver.taker_key
    def hooked(self,key):
        w=self.core.wait
        if w.kind==screens.TAKER_SELECT and self.core.m is not None and getattr(self.core,'main',False):
            try:
                import frames
                s=self.core.m.snapshot();d=frames.derive(s['memory'],s['load'],s['regs'])
            except AssertionError as e:
                d=None;run.row(label='taker-frame-problem',round=state['round'],error=str(e),site=w.site)
            if d is not None:
                ident=(state['round'],d['role'],d['side'],d['minute'])
                if ident not in seen:
                    seen.add(ident)
                    run.row(label=f"taker-r{state['round']:02}-role{d['role']}",round=state['round'],role=d['role'],side=d['side'],minute=d['minute'],run_index=state['runs'],poll=w.poll,text_head=w.text.splitlines()[:6])
                    if d['role'] in (3,4) and d['role'] not in captured:
                        captured[d['role']]=capture(run,self.core,d['role'],state)
        return original_key(self,key)
    Driver.taker_key=hooked
    try:
        current=raw
        while state['round']<=int(maxround):
            number=state['round']
            run.row(label=f'menu-r{number:02}',round=number,state=run.keep(f'menu-r{number:02}.g2core',current),elapsed=round(time.monotonic()-run.start,1))
            attempts=0
            while True:
                state['runs']=0
                with capturing() as cores:
                    try:got=so.core_rounds(current,GOAL_DAT,1)
                    except DriverError as e:
                        if 'refuses the eleven' not in str(e) or attempts>=8:raise
                        refusal=str(e)
                    else:break
                attempts+=1;current,swap=repair_eleven(current)
                run.row(label=f'repair-r{number:02}',round=number,refusal=refusal,swap=list(swap),state=run.keep(f'menu-r{number:02}-repair{attempts}.g2core',current),elapsed=round(time.monotonic()-run.start,1))
            run.row(label=f'round-r{number:02}',round=number,round_kind=got[0].kind,before=got[0].before,after=got[0].after,elapsed=round(time.monotonic()-run.start,1))
            if got[0].kind=='deferred-rollover':run.rec['status']='season ended';break
            current=cores[-1].save();state['round']+=1;state['runs']=0
            if {3,4}<=set(captured):run.rec['status']='roles 3 and 4 captured';break
        else:run.rec.setdefault('status','bound of rounds reached')
        if run.rec['status']=='aborted':run.rec['status']='finished'
        run.rec['captured']={str(r):c for r,c in captured.items()}
    except BaseException as e:
        run.rec['error']=repr(e);run.rec['captured']={str(r):c for r,c in captured.items()};print(repr(e),flush=True)
    finally:run.finish()

def capture(run,core,role,state):
    """At a CC7B taker poll wait of role 3 or 4: keep it (the decision pending), then branch on a copy, never the main
    run: Space (the board, the blocking read at CF3A), Return (back to the same selector), Return (accept)."""
    out={}
    out['decision']=observe_state(run,f'role{role}-decision-before-space',core,round=state['round'],role_label=role,run_index=state['runs'])
    blob=(ROOT/out['decision']['state']['file']).read_bytes()
    branch,driver=BRANCH_CORE(blob,GOAL_DAT);branch.main=False
    assert branch.wait.kind==screens.TAKER_SELECT and branch.wait.poll
    for label,key in (('space-pitch-read',SPACE),('return-back-at-selector',RETURN),('return-accept',RETURN)):
        try:
            driver.taker_key(key)
        except BaseException as e:
            run.row(label=f'role{role}-{label}',round=state['round'],error=repr(e),key=key);break
        out[label]=observe_state(run,f'role{role}-{label}',branch,round=state['round'],key=key)
    return {k:dict(n=v['n'],state=v['state']) for k,v in out.items()}

def preceding(name,menu,number,menu_sha,run_index):
    load_core();adapt()
    raw=Path(menu).read_bytes();assert sha(raw)==menu_sha;run_index=int(run_index)
    run=Run(name,3600,'preceding',menu=dict(file=str(menu),sha256=menu_sha),round=int(number),run_index=run_index)
    count=dict(n=0);original_run=Core._run;kept={}
    def counting(self):
        out=original_run(self)
        if getattr(self,'main',False):
            count['n']+=1
            if count['n']==run_index-1:kept['obs']=observe_state(run,'preceding-wait',self,round=int(number),run_index=count['n'])
            if count['n']==run_index:kept['next']=self.wait.kind if self.wait else None
        return out
    Core._run=counting
    try:
        with capturing() as cores:
            try:so.core_rounds(raw,GOAL_DAT,1)
            except UnknownScreen:pass
            except DriverError:pass
        run.rec['preceding']=kept
        run.rec['status']='kept' if 'obs' in kept else 'not reached'
    except BaseException as e:
        run.rec['error']=repr(e);print(repr(e),flush=True)
    finally:run.finish()

if __name__=='__main__':
    cmd,*args=sys.argv[1:]
    {'reach':reach,'search':search,'preceding':preceding}[cmd](*args)
