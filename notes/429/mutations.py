import importlib,io,json,unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import runtime.decoders.manager as m
import tests.test_manager_decoder as t
source=Path(m.__file__).read_text()
mutants={'nul_control':source.replace("' ' if b == 0", "'\\x00' if b == 0"),'period':source.replace("b' ' + surname_record", "b'. ' + surname_record"),'short_store':source.replace('[:14]','[:13]'),'c_terminator':source.replace('screen_text(manager_payload(initial, surname_record))',"screen_text(manager_payload(initial, surname_record).split(b'\\x00')[0])"),'ignore_length':source.replace('surname_record[1:1+surname_record[0]]','surname_record[1:].rstrip(bytes([0]))'),'width':source.replace('!= 13','!= 14')}
assert len(sys.argv) == 2 and not Path(sys.argv[1]).exists(), 'new output path required'
rows=[]
for name,src in mutants.items():
 exec(compile(src,m.__file__,'exec'),m.__dict__)
 importlib.reload(t)
 result=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
 assert not result.wasSuccessful(),name
 rows.append(dict(mutation=name,failures=len(result.failures),errors=len(result.errors)))
exec(compile(source,m.__file__,'exec'),m.__dict__)
importlib.reload(t)
r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t));assert r.wasSuccessful()
Path(sys.argv[1]).write_text(json.dumps(dict(baseline_tests=r.testsRun,mutants=rows),indent=2)+'\n')
print('baseline5/5; 6/6 mutants rejected; no source files mutated')
