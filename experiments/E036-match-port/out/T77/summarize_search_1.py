"""Validate original search records and retain exact journal timings/counters."""
from pathlib import Path
import collections,hashlib,json,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'experiments/E036-match-port'))
import records,compare
summary=[];journal_all=[]
for version,planned in [(3,48),(4,32),(5,100),(6,96)]:
 p=OUT/f'search-native-{version}.jsonl';rows=records.read_log(p)
 assert all(records.is_completed(r) and not r.get('ports') and not r.get('variant') for r in rows)
 counters=collections.Counter()
 for r in rows:counters.update(r['counts'])
 command=['journalctl','--user','-u',f't77-search-{version}','--no-pager','-o','json']
 raw=subprocess.check_output(command,text=True);journals=[json.loads(l) for l in raw.splitlines()]
 assert journals
 stamps=[int(r['__REALTIME_TIMESTAMP']) for r in journals]
 start,end=min(stamps),max(stamps)
 journal_all.extend(journals)
 summary.append({'search':version,'planned':planned,'completed':len(rows),'stopped':version==4,
                 'record_path':str(p.relative_to(ROOT)),'record_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                 'first_journal_utc':datetime.datetime.fromtimestamp(start/1e6,datetime.timezone.utc).isoformat(),
                 'last_journal_utc':datetime.datetime.fromtimestamp(end/1e6,datetime.timezone.utc).isoformat(),
                 'journal_elapsed_s':(end-start)/1e6,'completed_match_cpu_s':sum(r['cpu_s'] for r in rows),
                 'original_entry_counts':dict(counters),'all_original_unhooked_completed':True})
(OUT/'bounded-search-journal-final-1.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in journal_all))
receipt={'searches':summary,'completed_executions':sum(s['completed'] for s in summary),
         'keeper_entry_count':sum(s['original_entry_counts']['0791:C24D'] for s in summary),
         'elapsed_definition':'First to last retained journal timestamp per supervised search unit, including queued time; CPU sum covers completed matches only.',
         'classification':'C24D READ: not reached in these declared searches, not claimed impossible.'}
(OUT/'bounded-search-summary-final-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
for s in summary:print(s['search'],s['completed'],s['journal_elapsed_s'],s['completed_match_cpu_s'])
