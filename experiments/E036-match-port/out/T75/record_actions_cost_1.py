"""Retain all34 completed job timestamps and the timing API's billing receipt."""
import datetime,json,subprocess,sys
from pathlib import Path
folder=Path(sys.argv[1]);runid='40079183920'
for label,url in [('jobs',f'repos/diegoami/goal2-archaeology/actions/runs/{runid}/jobs?per_page=100'),('timing',f'repos/diegoami/goal2-archaeology/actions/runs/{runid}/timing')]:
 path=folder/(label+'-final-1.json');assert not path.exists()
 data=subprocess.check_output(['gh','api',url],text=True);path.write_text(data)
jobs=json.loads((folder/'jobs-final-1.json').read_text());timing=json.loads((folder/'timing-final-1.json').read_text());assert jobs['total_count']==len(jobs['jobs'])==34
parse=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
rows=[]
for job in jobs['jobs']:
 assert job['status']=='completed' and job['conclusion']=='success',job['name']
 duration=(parse(job['completed_at'])-parse(job['started_at'])).total_seconds();assert duration>=0
 rows.append({'id':job['id'],'name':job['name'],'started_at':job['started_at'],'completed_at':job['completed_at'],'runner_seconds':duration})
seconds=sum(r['runner_seconds'] for r in rows)
receipt={'run_id':runid,'jobs':len(rows),'shards':32,'actual_runner_seconds':seconds,'actual_runner_minutes':seconds/60,'billable':timing.get('billable'),'run_duration_ms':timing.get('run_duration_ms'),'rows':rows}
(folder/'runner-minutes-final-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2))
