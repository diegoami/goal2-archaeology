"""Compute actual complete Actions runner minutes from every job, retaining raw timing input."""
import argparse,datetime,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('jobs');p.add_argument('timing');p.add_argument('--out',required=True);a=p.parse_args()
jobs_path=Path(a.jobs);timing_path=Path(a.timing);out=Path(a.out)
assert not out.exists()
data=json.loads(jobs_path.read_text());jobs=data['jobs'];timing=json.loads(timing_path.read_text())
assert len(jobs)==data['total_count']==33 and len({j['id'] for j in jobs})==33
assert all(j['status']=='completed' and j['conclusion']=='success' for j in jobs)
rows=[]
for job in jobs:
 start=datetime.datetime.fromisoformat(job['started_at'].replace('Z','+00:00'))
 end=datetime.datetime.fromisoformat(job['completed_at'].replace('Z','+00:00'))
 seconds=(end-start).total_seconds();assert seconds>=0
 rows.append({'id':job['id'],'name':job['name'],'started_at':job['started_at'],
              'completed_at':job['completed_at'],'runner_seconds':seconds})
seconds=sum(r['runner_seconds'] for r in rows)
report={'jobs':len(rows),'runner_seconds':seconds,'runner_minutes':seconds/60,
        'billable':timing.get('billable'),'jobs_sha256':hashlib.sha256(jobs_path.read_bytes()).hexdigest(),
        'timing_sha256':hashlib.sha256(timing_path.read_bytes()).hexdigest(),'rows':rows}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
