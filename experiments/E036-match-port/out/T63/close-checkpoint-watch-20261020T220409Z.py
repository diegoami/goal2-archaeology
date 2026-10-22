"""Save only the two existing T63 integrated jobs; no new scientific run/review/merge."""
from pathlib import Path
import datetime, hashlib, json, subprocess, time
root = Path('/home/diego/projects/goal2-archaeology')
work = root / '.claude/worktrees/task-T63-port-positioning'
out = work / 'experiments/E036-match-port/out/T63'
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
units = [f'goal2-t63-all-main53-cbbfb28-{h}.service' for h in 'ab']
hashes = {str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted((work/'runtime/original_match').rglob('*.py'))}
owned = [out/f'all-rework-main53-cbbfb28-{h}{suffix}' for h in 'ab' for suffix in ('.jsonl', '-run.txt')]
method = out/f'close-checkpoint-watch-{stamp}.py'
method.write_bytes(Path(__file__).read_bytes())
receipt = out/f'close-checkpoint-input-{stamp}.json'
receipt.write_text(json.dumps({'source_sha256': hashes, 'units': units,
    'scope': 'Checkpoint existing integrated workers every20minutes, then retain journals. No finalizer, review, merge or new batch.'}, indent=2)+'\n')
owned.extend((method, receipt))
assert subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode == 0
def save(message):
    assert all(hashlib.sha256((work/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items()), 'Frozen runtime changed'
    names = [str(p.relative_to(work)) for p in owned if p.exists()]
    subprocess.run(['git','add','--',*names],cwd=work,check=True)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode:
        subprocess.run(['git','commit','-m','T63: '+message],cwd=work,check=True)
        subprocess.run(['git','push','origin','HEAD'],cwd=work,check=True)
        with (work/'RUN-NOTES.md').open('a') as f:
            f.write('\n'+datetime.datetime.now(datetime.timezone.utc).isoformat()+' checkpoint-only watcher pushed existing integrated raw output; no comparison/acceptance claimed.\n')
def active(unit):
    return subprocess.run(['systemctl','--user','is-active','--quiet',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
save('record checkpoint-only watcher for existing integrated jobs')
last = time.monotonic()
while any(active(unit) for unit in units):
    if time.monotonic()-last>=1200:
        save('checkpoint existing integrated raw progress during session close')
        last=time.monotonic()
    time.sleep(20)
for unit in units:
    path=out/f'{unit.removesuffix(".service")}-{stamp}-journal.txt'
    path.write_text(subprocess.check_output(['journalctl','--user','-u',unit,'--no-pager'],text=True))
    owned.append(path)
save('retain completed integrated worker output and journals')
print('Existing integrated units ended. Next session must inspect actual exits/logs, then run rework-finalize-all.py; no automatic approval or merge.',flush=True)
