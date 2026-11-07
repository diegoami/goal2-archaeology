"""Real missing-cache download plus actual original/PyPy entry comparison."""
import argparse,hashlib,importlib.util,json,subprocess,sys,tempfile,types
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools'),str(HERE)]
import pairs as P

def main(out):
    from port_test_runtime import call_in_pypy
    from original_match.image import Image
    from original_match.port.tables import to_record
    from tests import test_route_sealed as tests
    F=tests._fixtures();row=next(c for c in F.runner.CASES if c[0]=='E040-r0004');downloads=[]
    original_download=F._download
    def downloaded(actual,directory):downloads.append(actual[3]);return original_download(actual,directory)
    with tempfile.TemporaryDirectory() as directory:
        cache=Path(directory);assert not (cache/row[3]).exists()
        raw=F.published_bytes(row,cache_dir=cache,fetch=downloaded)
        assert hashlib.sha256(raw).hexdigest()==F.runner.expected(row[3]) and downloads==[row[3]]
        with patch.object(F.runner,'DL',cache):
            source=F.image();original,context,fixture=F.entry()
        actual_state,actual_regs=call_in_pypy('test_route_sealed','_entry_comparison',args=(source.state(source.tables),to_record(source.tables)))
        assert actual_state==original.state(original.tables) and actual_regs==context
    names=['OuterFrames','ReachedRouteLeaves','ReachedFalsifiers','SummaryBars','FullClosureFrames']
    old_source=subprocess.check_output(['git','show','82a86d9e5d2a5148c0924fa4d9ce63a5bb10484e:tests/test_route_sealed.py'],text=True,cwd=ROOT)
    old=types.ModuleType('_t123_pre_ci_test');old.__file__=str(ROOT/'tests/test_route_sealed.py')
    with patch.object(tests._Calls,'__unittest_skip__',True,create=True):
        exec(compile(old_source,old.__file__,'exec'),old.__dict__)
        assert all(getattr(getattr(old,name),'__unittest_skip__') for name in names)
        assert not any(getattr(getattr(tests,name),'__unittest_skip__') for name in names)
    result={'schema':'t123-real-ci-asset/1','status':'passed','published_asset':row[3],'published_sha256':F.runner.expected(row[3]),
      'real_gh_downloads':1,'missing_cache_populated_exactly':True,'same_original_asset_no_substitution':True,
      'actual_original_pending_state_and_all16_regs_equal':True,'required_original_classes_no_skip':names,
      'sources':{**P.sources(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    with Path(out).open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();main(a.out)
