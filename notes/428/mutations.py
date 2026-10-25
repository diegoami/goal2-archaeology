"""T94 in-memory negative controls; never edit the checked-out source."""
import importlib,io,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import runtime.decoders.country as m
import tests.test_country_decoder as t
assert len(sys.argv)==2 and not Path(sys.argv[1]).exists(), 'new output path required'
source=Path(m.__file__).read_text()
mutants={
 'swap_labels':source.replace('dict(status=country_status','dict(skill=country_status').replace('skill=manager_skill','status=manager_skill'),
 'wrong_country_table':source.replace('_label(read_ds,0x7884','_label(read_ds,0x7894'),
 'wrong_manager_table':source.replace('_label(read_ds,0x7894','_label(read_ds,0x7884'),
 'country_band_boundary':source.replace('(rating-1)//8','rating//8'),
 'manager_band_boundary':source.replace('(ability-1)//8','ability//8'),
 'manager_confidence_byte':source.replace('manager_record[1]','manager_record[2]'),
 'drop_manager_zero':source.replace('return None',"return ''"),
 'drop_unknown':source.replace('if ability==0:', 'if False:'),
 'clamp_ability':source.replace('(ability-1)//8','(min(128,ability)-1)//8'),
 'wrong_rating':source.replace('world_rank)//2','world_rank)//3'),
 'unbounded_label':source.replace('if record[0]>15:','if False:'),
}
rows=[]
try:
 for name,src in mutants.items():
  assert src!=source,name
  exec(compile(src,m.__file__,'exec'),m.__dict__);importlib.reload(t)
  r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
  assert not r.wasSuccessful(),name
  rows.append(dict(mutation=name,failures=len(r.failures),errors=len(r.errors)))
finally:
 exec(compile(source,m.__file__,'exec'),m.__dict__);importlib.reload(t)
r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t));assert r.wasSuccessful()
Path(sys.argv[1]).write_text(json.dumps(dict(baseline_tests=r.testsRun,mutants=rows),indent=2)+'\n')
print(f'baseline {r.testsRun}/{r.testsRun}; {len(rows)}/{len(rows)} mutants rejected')
