"""Registered E036 input snapshots; identities are bound before a match runs.

Only already-published assets are downloadable. T86's private delivered input
can be used from a hash-verified local cache; this module never publishes it.
"""
import hashlib,os,shutil,subprocess,tempfile
from pathlib import Path

DEFAULT='E006'
SOURCES={
 'E006':{'release':'E006','asset':'e0afff6751747233-e006-1000-r0001.sav','sha256':'e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d','memory_sha256':'87400f6a866e0798f61a9f3ab3bfcaa322469fa6b238b0061f1b7ab2b6a3f979'},
 'E031-stage8':{'release':'play-the-game-states','asset':'3ea57029282b849f-g1-03874-shootout-start.sav','sha256':'3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc','memory_sha256':'f0cd3e511544532a902a7b4378ef1260d44b3169270c02c94ab85f9f253ef79c'},
 'T86-stage8':{'release':None,'asset':'g13-b2497a51f41fa52a-g4c-loaded-manager.sav','sha256':'b2497a51f41fa52a733fe880e3b144b43db05d5de11f4da6e45c51dc76a715a0','memory_sha256':'c5172405e158817e07c3d7c276de38d4a504d9970b8d75de183eb7dc9b7ee26e'},
}

class SourceError(ValueError):pass

# Original GAME_PTR+28 has2393 calendar entries in each finals source,
# versus769 in E006. [DS:A92B]+8*count ends at P:5A3DE, so preserve
# the entire declared calendar, not only the observed changed score byte.
for _key in ('E031-stage8','T86-stage8'):
 SOURCES[_key]['records_length']=106640

def records_length(digest,default):
 return next((s.get('records_length',default) for s in SOURCES.values() if s['sha256']==digest),default)

def get(key):
 if not isinstance(key,str) or key not in SOURCES:raise SourceError(f'unknown registered image source {key!r}')
 return SOURCES[key]

def validate_image(image,key):
 source=get(key)
 if image.sha256()!=source['memory_sha256']:
  raise SourceError(f'image memory does not match registered source {key}; load its hash-verified snapshot')

def load(key,cache):
 from original_match import Image
 import fileopts
 source=get(key);cache=Path(cache);path=cache/source['asset']
 if os.path.lexists(path):fileopts.check_input(str(path),'--cache')
 else:
  if source['release'] is None:raise SourceError(f"private source {key} absent; retrieve by notes/400/delivery.json into {path}")
  fileopts.check_log_output(str(path),'--cache');cache.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=cache) as name:
   command=['gh','release','download',source['release'],'--repo','diegoami/goal2-archaeology','--pattern',source['asset'],'--dir',name]
   subprocess.run(command,check=True,capture_output=True)
   temp=Path(name)/source['asset'];raw=temp.read_bytes()
   if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise SourceError(f'wrong source hash for {key}')
   shutil.move(str(temp),str(path))
 raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise SourceError(f'wrong source hash for {key}')
 image=Image.from_bytes(raw);validate_image(image,key)
 return image
