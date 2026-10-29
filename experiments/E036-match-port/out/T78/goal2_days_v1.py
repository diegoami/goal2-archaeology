"""T78d Done-when 4 input, run in a goal2 checkout (it uses goal2's Core on Unicorn):

    cd <goal2> && source .cache/cloud.env && python3 <this file> --out <new json>

E006-r0001's fresh career (goal2.tests.test_core_round_t108.start, Denmark): the day sizes from its
fixture list (a day, as play_round runs it, is the fixtures from +0x26 up to and including the next
fixture of the managed country), then the first three days played and timed. The simulated-fixture
cost is the third day's time over the first's, per extra fixture."""
import argparse, json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, '.')
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
out = open(a.out, 'x')
from goal2.tests.test_core_round_t108 import start
from goal2.core import views
d = start(); st = d.core.wait.state
managed = views.team(st)['country']
sizes, run = [], 0
for r in views.fixture_list(st)['rows']:
    run += 1
    if managed in (r['first'], r['second']):
        sizes.append(run); run = 0
days = []
for _ in range(3):
    first = views.Memory(d.core.wait.state).game(0x26, 2)
    t, c = time.monotonic(), time.process_time()
    d.play_round(captain=None)
    days.append(dict(fixtures=views.Memory(d.core.wait.state).game(0x26, 2) - first,
                     wall_s=round(time.monotonic() - t, 2), cpu_s=round(time.process_time() - c, 2)))
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
per = (days[2]['cpu_s'] - days[0]['cpu_s']) / (days[2]['fixtures'] - days[0]['fixtures'])
json.dump(dict(source=f'goal2 {head}, E006-r0001 fresh career managing {views.Memory(st).country_name(managed)}',
               sizes=sizes, unicorn_days=days, unicorn_simulated_fixture_s=round(per, 3)), out, indent=2); out.close()
print(open(a.out).read())
