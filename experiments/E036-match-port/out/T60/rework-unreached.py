"""R1 follow-up: rerun the reviewer exact310 unreached-branch mutants with real original-image fuzz.
The historical reviewer ranges select source bytes unchanged by the correction.
Use a new private OUT directory for every measurement; no reviewed tree edits.
"""
import importlib.util, os, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(sys.argv[1]); OUT = Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("mutations", ROOT/"experiments/E036-match-port/out/T60/mutations.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
RANGES = {
 "runtime": [(634,641,"11E4 digits"),(660,673,"11E4 port"),(835,846,"0CCB"),(849,861,"0CF4"),(932,941,"1C86 neg"),(998,1015,"2000"),(1073,1130,"0294"),(1168,1199,"0676"),(1302,1337,"072F"),(1355,1445,"0787/07DB"),(1448,1458,"08BF")],
 "geometry": [(172,187,"2A6D"),(190,205,"2E82"),(347,356,"278A halving"),(556,603,"2A15"),(955,960,"2E82 port")],
}
tmp = OUT/"mutroot3"
assert not tmp.exists(), str(tmp) + " already exists; preserve prior measurement"
shutil.copytree(ROOT/"runtime", tmp/"runtime", ignore=shutil.ignore_patterns("__pycache__","spike","human","emul","driver","model"))
shutil.copy(ROOT/"runtime/fileopts.py", tmp/"runtime/fileopts.py")
(tmp/"tests").mkdir()
for t in ("test_port_runtime.py","test_port_geometry.py"): shutil.copy(ROOT/"tests"/t, tmp/"tests"/t)
d = tmp/"experiments/E036-match-port/out/T60"; d.mkdir(parents=True)
for f in ("fuzz.py","generators.py","generators_geometry.py","mutations.py"): shutil.copy(ROOT/"experiments/E036-match-port/out/T60"/f, d/f)
(tmp/".cache").mkdir(); os.symlink(ROOT/".cache/dl", tmp/".cache/dl")
def run(nofuzz):
    env = dict(os.environ)
    env.pop("T60_NO_FUZZ",None)
    if nofuzz: env["T60_NO_FUZZ"]="1"
    for t in ("tests.test_port_runtime","tests.test_port_geometry"):
        try:
            p = subprocess.run([sys.executable,"-B","-m","unittest",t],cwd=tmp,capture_output=True,text=True,env=env,timeout=120)
        except subprocess.TimeoutExpired:
            return False
        if p.returncode: return False
    return True
assert run(False), "base with fuzz fails"
q=subprocess.run([sys.executable,"-B","-m","unittest","-v","tests.test_port_geometry.FuzzAgainstOriginal"],cwd=tmp,capture_output=True,text=True,env=dict(os.environ))
assert "skipped" not in q.stderr+q.stdout, "fuzz skipped"
print("fuzz runs in the scratch tree", flush=True)
tot=hand=both=0
for mod, rngs in RANGES.items():
    path = tmp/"runtime/original_match/port"/f"{mod}.py"
    orig = path.read_text(); lines = orig.split("\n")
    try:
        for i,new,what in m.mutants(orig):
            ln=i+1
            lab=[l for a,b,l in rngs if a<=ln<=b]
            if not lab: continue
            tot+=1
            path.write_text("\n".join(lines[:i]+[new]+lines[i+1:]))
            if run(True):
                hand+=1
                if run(False):
                    both+=1
                    print(f"ESCAPES BOTH [{lab[0]}] {mod}.py:{ln}: {what}: {lines[i].strip()[:120]}",flush=True)
    finally:
        path.write_text(orig)
print(f"{tot} mutants, {hand} survived hand tests, {both} survived hand tests AND fuzz")
