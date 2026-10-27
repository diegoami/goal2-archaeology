#!/usr/bin/env python3
"""Metered direct original/production-port calls. Every reservation and result is exclusive."""
import time
STARTED=time.monotonic()
import argparse,fcntl,json,os,resource,subprocess,sys,tempfile,traceback
from pathlib import Path
from check import ROOT,sha,write_new
from construction import image,construct,ENTRY_SP,CALLER_BP

BASE=ROOT/'notes/engine-study/T106'
CAPS=dict(invocations=60,cpu_s=600,active_wall_s=900,invoke_cpu_s=5,invoke_wall_s=10)
STRICT=('ax','dx','bp','sp','ds','ss','cs','ip')
ALL_REGS=('eax','ebx','ecx','edx','esi','edi','ebp','esp','cs','ds','es','ss','fs','gs','eip','eflags')


def cpu():
    r=resource.getrusage(resource.RUSAGE_SELF);c=resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime+r.ru_stime+c.ru_utime+c.ru_stime


class Budget:
    def __init__(self,base=BASE/'budget'):
        self.base=Path(base)
        for name in ['reservations','outcomes','starts','batches']:(self.base/name).mkdir(parents=True,exist_ok=True)
    def read(self,folder):return [json.loads(p.read_text()) for p in sorted((self.base/folder).glob('*.json'))]
    def audit(self,ignore_batch=None):
        reserved=self.read('reservations');outcomes={r['seq']:r for r in self.read('outcomes')};starts=self.read('starts');ends={r['batch']:r for r in self.read('batches')}
        assert len({r['seq'] for r in reserved})==len(reserved)<=60
        assert {r['seq'] for r in reserved}>=set(outcomes)
        groups={g:sum(r['group']==g for r in reserved) for g in ['launch','wall']}
        assert groups['launch']<=16 and groups['wall']<=44
        opened=[r['batch'] for r in starts if r['batch'] not in ends and r['batch']!=ignore_batch]
        # An externally killed parent leaves unknown overhead: conservatively spend the whole remaining cap.
        unclosed=[r for r in reserved if r['seq'] not in outcomes]
        charged_cpu=sum(r['cpu_s'] for r in ends.values())+5*len(unclosed)+(600 if opened else 0)
        charged_wall=sum(r['active_wall_s'] for r in ends.values())+10*len(unclosed)+(900 if opened else 0)
        return dict(invocations=len(reserved),cpu_s=charged_cpu,active_wall_s=charged_wall,groups=groups,unclosed_invocations=[r['seq'] for r in reserved if r['seq'] not in outcomes],unclosed_batches=opened,failed_invocations=[r['seq'] for r in outcomes.values() if not r['completed']])
    def start(self,batch,manifest):
        prior=self.audit();assert not prior['unclosed_batches'] and not prior['unclosed_invocations'],'unfinished batch/invocation: no implicit retry/budget reset'
        assert prior['cpu_s']<600 and prior['active_wall_s']<900
        write_new(self.base/'starts'/f'{batch}.json',dict(batch=batch,manifest=manifest,started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
        return prior
    def reserve(self,batch,group,logical,manifest,prior):
        rows=self.read('reservations');assert len(rows)<60,'global invocation cap'
        assert sum(r['group']==group for r in rows)<{'launch':16,'wall':44}[group],'slice invocation cap'
        assert not any(r['batch']==batch and r['logical']==logical for r in rows),'logical invocation already reserved'
        assert prior['cpu_s']+cpu()+5<=600,'CPU reserve cap'
        assert prior['active_wall_s']+time.monotonic()-STARTED+10<=900,'wall reserve cap'
        seq=max([r['seq'] for r in rows]+[0])+1
        reservation=dict(seq=seq,batch=batch,group=group,logical=logical,manifest_sha256=manifest,cpu_reserve_s=5,wall_reserve_s=10)
        write_new(self.base/'reservations'/f'{seq:04}.json',reservation)
        return reservation
    def finish(self,batch,error):
        data=dict(batch=batch,cpu_s=cpu(),active_wall_s=time.monotonic()-STARTED,error=error)
        write_new(self.base/'batches'/f'{batch}.json',data)
        after=self.audit();assert after['cpu_s']<=600 and after['active_wall_s']<=900,'global actual cap exceeded'
        return after


def validate_sources(manifest):
    for name,digest in manifest['source_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,('source drift',name)


def field_values(machine,spec):
    def signed(v):return v-256 if v>=128 else v
    if spec['kind']=='launch':
        def word_signed(v):return v-65536 if v>=32768 else v
        return dict(velocity=[word_signed(machine.rd(0x82fc)),word_signed(machine.rd(0x82fe))],timer=machine.rd(0x8300),event=machine.rd(0x8327,1),projected=[signed(machine.rd(0x8313,1)),signed(machine.rd(0x8314,1))])
    point=0x80e8+22*spec['slot']
    return dict(target=[signed(machine.rd(point+7,1)),signed(machine.rd(point+8,1))],state=machine.rd(point+0x12,1))


def require_registered_target(machine,target):
    assert machine.lin(target) in machine._ports,('unregistered native fallback refused',target)


def worker(manifest_path,logical,memory_output):
    resource.setrlimit(resource.RLIMIT_CPU,(5,5))
    manifest=json.loads(Path(manifest_path).read_text());validate_sources(manifest)
    item=next(i for i in manifest['invocations'] if i['spec']['logical']==logical);spec=item['spec']
    img=image();memory,state=construct(img,spec);assert state==item['input'],'construction/input drift'
    from original_match import port
    from original_match.machine import Machine,MEM_SIZE
    from unicorn import UC_HOOK_CODE
    result=dict(logical=logical,spec=spec,input_memory_sha256=sha(memory),completed=False,port_entries=[],yielded_calls=[],production_stub_entries=[],known_entry_events=[],instruction_events=0,native_instruction_attempts=[],main_rng_writes=[])
    entries={a:e for reg,_ in port.load(['all']) for a,e in reg.entries.items()}
    class AuditedMachine(Machine):
        def port(self,address,run):
            def observed(m):
                result['port_entries'].append(address)
                if run.entry.stub is not None:
                    result['production_stub_entries'].append(dict(address=address,why=run.entry.stub))
                    assert address=='214B:1EA1',('undeclared production stub',address)
                return run(m)
            observed.entry=run.entry
            super().port(address,observed)
        def expect_return(self,frame):
            call=frame.waiting
            require_registered_target(self,call.target)
            result['yielded_calls'].append(dict(caller=frame.entry.address,target=call.target,return_to=call.ret_to,far=call.far,args=list(call.args)))
            super().expect_return(frame)
    original_code=bytes(memory[img.load*16:img.DS*16])
    m=AuditedMachine(memory,img.load) if spec['backend']=='port' else Machine(memory,img.load)
    try:
        if spec['backend']=='port':
            installed=port.install(m,['all']+(['ball.launch-reverse-x'] if spec.get('variant')=='launch-reverse-x' else []))
        for name,value in state['registers'].items():m.set_reg(name,value)
        known={m.lin(address):address for address in entries}
        seed=m.far(0xa978);result['seed_before']=m.word_at(seed)
        m.watch(seed,2,lambda old,new:result['main_rng_writes'].append(dict(old=int.from_bytes(old,'little'),new=int.from_bytes(new,'little'),writer=m.where(m.reg('cs'),m.reg('ip')))))
        def code_guard(uc,address,size,data):
            result['instruction_events']+=1
            if address in known:result['known_entry_events'].append(known[address])
            if spec['backend']=='original':return
            # Existing entry handlers redirect before this hook. Newly registered frame-return
            # handlers can follow it; only a matching actual SS:SP return may await that handler.
            redirected=m.pc()!=address
            pending=any(f.ret_lin==address and f.returned(m) for f in m.frames)
            if not redirected and not pending:
                result['native_instruction_attempts'].append(m.where(m.reg('cs'),m.reg('ip')))
                m.error=RuntimeError('native instruction execution refused in production-port arm');uc.emu_stop()
        m._uc.hook_add(UC_HOOK_CODE,code_guard)
        reason=m.run(state['return_linear'],timeout_s=10,fresh=True)
        assert reason is None and m.pc()==state['return_linear'],'normal sentinel return required'
        assert m.reg('sp')==state['expected_return_sp'] and m.reg('bp')==CALLER_BP,'return cleanup/BP mismatch'
        assert not m.frames,'unclosed port frames'
        assert m.read(img.load*16,len(original_code))==original_code,'original code changed during call'
        result.update(trace_limits='Entry/return hook events are not native executed instructions in the port arm;inlined production helpers are not separately counted.',completed=True,observed=field_values(m,spec),registers={n:m.reg(n) for n in ALL_REGS},abi_registers={n:m.reg(n)&65535 for n in STRICT},seed_after=m.word_at(seed),frames_remaining=len(m.frames),full_memory_sha256=sha(m.read(0,MEM_SIZE)))
        Path(memory_output).write_bytes(m.read(0,MEM_SIZE))
    except Exception:
        result['error']=traceback.format_exc()
        result['partial_registers']={n:m.reg(n) for n in ALL_REGS}
        result['partial_memory_sha256']=sha(m.read(0,MEM_SIZE))
    print(json.dumps(result,sort_keys=True))


def run_batch(path):
    manifest=json.loads(path.read_text());validate_sources(manifest)
    relative=str(path.relative_to(ROOT))
    assert path.read_bytes()==subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT),'input manifest must be committed before invocation'
    for name in manifest['source_sha256']:
        assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT),('producer/source must be committed',name)
    digest=sha(path.read_bytes());batch=path.stem+'-'+digest[:12]
    lock=ROOT/'.cache/T106.lock';lock.parent.mkdir(exist_ok=True)
    with lock.open('a') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        budget=Budget();prior=budget.start(batch,dict(path=str(path.relative_to(ROOT)),sha256=digest));error=None;results=[];memories={}
        out=path.parent/'out';out.mkdir(exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(prefix='T106-private-',dir=ROOT/'.cache') as tmp:
                for item in manifest['invocations']:
                    spec=item['spec'];res=budget.reserve(batch,manifest['group'],spec['logical'],digest,prior)
                    mem=Path(tmp)/f'{res["seq"]}.bin';before_cpu=cpu();before_wall=time.monotonic()
                    cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(path),'--logical',spec['logical'],'--memory-output',str(mem)]
                    try:
                        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=10)
                        raw=json.loads(p.stdout) if p.stdout.strip() else dict(completed=False,error='worker produced no result')
                        raw.update(process_exit=p.returncode,stderr=p.stderr)
                    except subprocess.TimeoutExpired as e:
                        raw=dict(completed=False,error='wall watchdog',stdout=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else e.stdout,stderr=(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else e.stderr,process_exit=None)
                    raw.update(seq=res['seq'],batch=batch,manifest_sha256=digest,execution_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),cpu_s=cpu()-before_cpu,active_wall_s=time.monotonic()-before_wall)
                    record_path=out/f'{res["seq"]:04}-{spec["logical"].replace("/","_")}.json';write_new(record_path,raw)
                    write_new(budget.base/'outcomes'/f'{res["seq"]:04}.json',dict(seq=res['seq'],batch=batch,completed=raw['completed'],cpu_s=raw['cpu_s'],active_wall_s=raw['active_wall_s'],record_path=str(record_path.relative_to(ROOT)),record_sha256=sha(record_path.read_bytes())))
                    results.append(dict(path=str(record_path.relative_to(ROOT)),sha256=sha(record_path.read_bytes())))
                    if not raw['completed'] or raw['process_exit']!=0:raise RuntimeError('invocation failed;preserved '+str(record_path))
                    assert raw['cpu_s']<=5 and raw['active_wall_s']<=10,'actual per-invocation resource overrun'
                    if spec.get('required_prediction') is not None:assert raw['observed']==spec['required_prediction'],('field prediction disagreement',spec['logical'],raw['observed'])
                    if spec['role']=='baseline':memories[spec['logical']]=mem.read_bytes()
                comparisons=[]
                for case in sorted({i['spec']['case'] for i in manifest['invocations'] if i['spec']['role']=='baseline'}):
                    for slot in sorted({i['spec'].get('slot',2) for i in manifest['invocations'] if i['spec']['role']=='baseline' and i['spec']['case']==case}):
                        selected=[(i['spec'],r) for i,r in zip(manifest['invocations'],results) if i['spec']['role']=='baseline' and i['spec']['case']==case and i['spec'].get('slot',2)==slot]
                        assert len(selected)==2
                        values={s['backend']:(s,json.loads((ROOT/r['path']).read_text()),r) for s,r in selected}
                        so,ro,po=values['original'];sp,rp,pp=values['port'];mo,mp=memories[so['logical']],memories[sp['logical']]
                        differences=[n for n,(a,b) in enumerate(zip(mo,mp)) if a!=b]
                        comparisons.append(dict(case=case,slot=slot,original_record=po,port_record=pp,memory_equal=mo==mp,memory_diff_count=len(differences),memory_diff_first_offsets=differences[:128],abi_equal=ro['abi_registers']==rp['abi_registers'] and not ((ro['registers']['eflags']^rp['registers']['eflags'])&0x400),register_differences=[n for n in ALL_REGS if ro['registers'][n]!=rp['registers'][n]],production_stub_entries=rp['production_stub_entries']))
                write_new(out/f'{batch}-comparisons.json',dict(manifest_sha256=digest,comparisons=comparisons,limits='Every byte compared,including dead stack;no masks. Production sound stub is disclosed,not claimed as native-body execution. Scratch register/flag differences listed separately from declared ABI.'))
        except Exception:
            error=traceback.format_exc()
        after=budget.finish(batch,error)
        write_new(out/f'{batch}-batch.json',dict(batch=batch,manifest_sha256=digest,records=results,budget=after,error=error))
        print(json.dumps(dict(batch=batch,invocations=len(results),budget=after,error=error),indent=2))
        if error:raise SystemExit(1)


def audit():
    budget=Budget();data=budget.audit()
    for row in budget.read('outcomes'):
        path=ROOT/row['record_path'];assert sha(path.read_bytes())==row['record_sha256']
        record=json.loads(path.read_text());assert record['seq']==row['seq'] and record['batch']==row['batch']
    assert not data['unclosed_batches'] and not data['unclosed_invocations'],'incomplete reservation/batch'
    print(json.dumps(dict(scope='Actual committed reservation/outcome integrity and resource accounting;not semantic proof',**data),indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',type=Path);ap.add_argument('--audit',action='store_true');ap.add_argument('--worker',type=Path);ap.add_argument('--logical');ap.add_argument('--memory-output');a=ap.parse_args()
    if a.worker:worker(a.worker,a.logical,a.memory_output)
    elif a.run:run_batch(a.run.resolve())
    elif a.audit:audit()
    else:ap.error('choose --run or --audit')


if __name__=='__main__':main()
