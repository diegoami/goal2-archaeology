"""Read-only second inventory, includes the original manager's80 pool words.

1771:027B block14 is pool_indices; the table DS:6D1A..6D24 gives
1,81,161,241,321,401 for managers1..6 (data/ds_2581_02.hex).
"""
import hashlib,json,subprocess
from pathlib import Path
from inventory import ROOT,SIZES,sha
out=ROOT/'notes/400-next/pool-inventory-r1.json';assert not out.exists()
rows=[]
for a in json.loads((ROOT/'notes/400-next/inventory-r1.json').read_text())['assets']:
    raw=(Path('/tmp/goal2-archaeology-390/.cache/390/assets')/a['file']).read_bytes();assert sha(raw)==a['sha256']
    pool=raw[sum(SIZES[:13]):sum(SIZES[:14])];managed=[]
    for country in a['managed']:
        manager=country['manager_byte']-0x80;base=(manager-1)*80+1
        assert 1<=manager<=6
        managed.append(dict(country=country['country'],manager=manager,pool_empty_rows=[k+1 for k in range(80) if int.from_bytes(pool[2*(base+k):2*(base+k)+2],'little')==0]))
    rows.append(dict(file=a['file'],sha256=a['sha256'],managed=managed))
out.write_text(json.dumps(dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),assets=rows),indent=2)+'\n')
print('read-only pool inventory:',len(rows),'retained saves')
