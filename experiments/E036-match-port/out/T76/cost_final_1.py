"""Actual time from every completed Actions job; billing remains a separate value."""
import datetime,json
from pathlib import Path
OUT=Path(__file__).resolve().parent/'all-actions-1-40084230548'
jobs=json.loads((OUT/'jobs-final-1.json').read_text())
timing=json.loads((OUT/'timing-final-1.json').read_text())
assert jobs['total_count']==len(jobs['jobs'])==34
assert len({j['id'] for j in jobs['jobs']})==34
rows=[]
for j in jobs['jobs']:
    assert j['status']=='completed' and j['conclusion']=='success',j['name']
    duration=(datetime.datetime.fromisoformat(j['completed_at'])-datetime.datetime.fromisoformat(j['started_at'])).total_seconds()
    assert duration>=0
    rows.append({'id':j['id'],'name':j['name'],'started_at':j['started_at'],
                 'completed_at':j['completed_at'],'runner_seconds':duration})
seconds=sum(r['runner_seconds'] for r in rows)
receipt={'run_id':'40084230548','jobs':34,'shards':32,'actual_runner_seconds':seconds,
         'actual_runner_minutes':seconds/60,'billable':timing['billable'],
         'run_duration_ms':timing['run_duration_ms'],'rows':rows}
(OUT/'runner-minutes-final-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('rows','billable')},indent=2))
print('billable Ubuntu milliseconds:',timing['billable']['UBUNTU']['total_ms'])
