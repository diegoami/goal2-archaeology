"""Read-only derived progress dashboard; final case receipts remain authoritative.

Refreshes ignored .cache outputs, stops when every case exits or disappears.
Does not alter test/runtime source, scheduling, inputs or acceptance results.
"""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'experiments/E036-match-port/out/T78c'
LABELS={'e033-01':'Friendly baseline','e033-02':'Second fixture / seed','e033-03':'Manage opposing side',
        'e033-04':'Injury and substitution','e033-05':'Sendings off','e033-06':'All answers / refusals',
        'e033-07':'Watched to quick / ticks','e034-01':'Knockout / extra time / penalties',
        'e034-02':'Sudden-death penalties','e034-03':'Quick from half-time / penalties'}

def cpu_seconds(pid):
    # /proc stat's comm can contain spaces; fields14/15 follow the closing ')'.
    fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
    return (int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK')

def sample(previous):
    jobs={item['name']:item for item in json.loads((OUT/'launch-v1.json').read_text())}
    extension=OUT/'launch-seven-v1.json'
    if extension.exists():jobs.update({item['name']:item for item in json.loads(extension.read_text())['jobs']})
    now=time.time();rows=[]
    for name in LABELS:
        job=jobs[name];log=ROOT/job['log'];receipt=ROOT/job['receipt']
        text=log.read_text();lines=text.splitlines();boundaries=[s for s in lines if 'checkpoint PASS' in s]
        row={'scenario':name,'label':LABELS[name],'verified_boundaries':len(boundaries),
             'last_boundary':boundaries[-1] if boundaries else None,
             'last_output':lines[-1] if lines else '', 'seconds_since_log_update':round(now-log.stat().st_mtime),
             'wrapper_pid':job['pid'],'log':str(log),'receipt':str(receipt)}
        if receipt.exists():
            result=json.loads(receipt.read_text());row['state']='PASS' if result['exit_code']==0 and result['source_unchanged'] else 'FAILED'
            row['exit_code']=result['exit_code'];row['source_unchanged']=result['source_unchanged']
        else:
            try:
                pid=job['pid'];command=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
                if 'run_control.py' not in command or name not in command:raise ProcessLookupError()
                children=Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
                workers=[int(p) for p in children if 'unittest' in Path(f'/proc/{p}/cmdline').read_bytes().decode()]
                row['state']='RUNNING' if workers else 'QUEUED'
                if workers:
                    row['cpu_seconds']=round(sum(cpu_seconds(p) for p in workers),1)
                    old=previous.get(name,{})
                    row['cpu_advanced']=None if old.get('cpu_seconds') is None else row['cpu_seconds']>old['cpu_seconds']
            except (OSError,ProcessLookupError):row['state']='PROCESS MISSING; inspect receipt/log'
        rows.append(row)
    return {'updated_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Derived progress only; not an acceptance receipt',
            'passed':sum(r['state']=='PASS' for r in rows),'failed':sum(r['state']=='FAILED' for r in rows),
            'running':sum(r['state']=='RUNNING' for r in rows),'queued':sum(r['state']=='QUEUED' for r in rows),
            'verified_boundaries':sum(r['verified_boundaries'] for r in rows),'scenarios':rows}

def publish(report):
    folder=ROOT/'.cache';path=folder/'T78c-progress.json';tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(path)
    lines=['# Engine checkpoint progress','',f"Updated UTC: {report['updated_utc']}",'',
      f"{report['passed']}/10 scenarios passed; {report['running']} running; {report['queued']} queued; {report['failed']} failed.",
      f"Verified checkpoint boundaries: {report['verified_boundaries']}. Total boundary counts are not yet known for unfinished cases.",'',
      '| Scenario | State | Verified boundaries | CPU seconds | Last log update |',
      '|---|---|---:|---:|---:|']
    for r in report['scenarios']:
        lines.append(f"| {r['label']} | {r['state']} | {r['verified_boundaries']} | {r.get('cpu_seconds','—')} | {r['seconds_since_log_update']}s ago |")
    lines+=['','A quiet log does not by itself mean a stall: one boundary requires replay and completion of a match.',
            'Game saves are held in RAM; unfinished test jobs are not restartable. Final per-case exit/source receipts decide acceptance.','']
    path=folder/'T78c-progress.md';tmp=path.with_suffix('.tmp');tmp.write_text('\n'.join(lines));tmp.replace(path)
    with (folder/'T78c-progress-history-v1.jsonl').open('a') as stream:stream.write(json.dumps(report)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--once',action='store_true');args=parser.parse_args()
    previous={}
    while True:
        report=sample(previous);publish(report)
        print(json.dumps({k:report[k] for k in ('updated_utc','passed','failed','running','queued','verified_boundaries')}),flush=True)
        if args.once or not (report['running'] or report['queued']):break
        previous={row['scenario']:row for row in report['scenarios']}
        time.sleep(30)
