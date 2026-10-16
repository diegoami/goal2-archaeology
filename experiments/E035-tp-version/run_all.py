#!/usr/bin/env python3
"""E035: which Turbo Pascal built GOAL.EXE?  End to end, in a scratch directory outside the repository.

usage: run_all.py SCRATCH_DIR OUT_DIR
  1. unpack GOAL.EXE (tools/static/unlzexe.py), read the TP floppy images with fat12.py (+ unzip), take
     TPC.EXE and TURBO.TPL of 4.0, 5.0, 5.5, 6.0, 7.0 and 7.01
  2. compile probes/t4.pas with each (DOSBox-X, dbx.py), recording every input's and output's sha256
  3. compare each candidate's System-unit segment with GOAL's 23E4 segment (cover.py, bytecmp.py, gaps.py)
Everything third-party stays in SCRATCH_DIR; OUT_DIR gets only our text outputs (hashes, tables)."""
import glob, hashlib, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
KEEP = '/home/diego/projects/goal2-archaeology-keep'
TP = KEEP + '/tools/turbo-pascal/extracted/'
SCR, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(SCR, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
log = open(OUT + '/run.log', 'w')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    log.write(s + '\n')
    log.flush()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    return r.stdout + r.stderr


# 1. inputs
goal_in = KEEP + '/releases/goal2-original/GOAL.EXE'
goal = SCR + '/GOAL.unp.exe'
run(['python3', '-I', REPO + '/tools/static/unlzexe.py', goal_in, goal])
say('GOAL.EXE packed', sha(goal_in), '| unpacked', sha(goal))
sets = {  # version -> (dir, [images], [zips to unzip])
    '40': ('Borland_Turbo_Pascal_4.0__11-17-1987__5.25-360k_alt', ['Disk1 - Compiler.img'], []),
    '50': ('Borland_Turbo_Pascal_5.0__5.25-360k_', ['disk01.img'], []),
    '55': ('Turbo_Pascal_5.5__5.25_', ['Install.img'], []),
    '60': ('Borland_Turbo_Pascal_6.0__6-11-1991___5.25-360k_', ['disk01.img'], ['TURBO.ZIP']),
    '70': ('Borland_Turbo_Pascal_7.0__1992___3.5-720k_', ['Disk01.img'], ['TPC.ZIP', 'TPL.ZIP']),
    '701': ('Borland_Turbo_Pascal_7.01__3.5-720k_', ['Disk01.img'], ['TPC.ZIP', 'TPL.ZIP']),
}
runs = SCR + '/run'
os.makedirs(runs, exist_ok=True)
bat = ''
for v, (d, imgs, zips) in sets.items():
    img = glob.glob(TP + d + '/*/' + imgs[0])[0]
    say('image', v, os.path.basename(img), sha(img))
    raw = SCR + '/raw' + v
    os.makedirs(raw, exist_ok=True)
    run(['python3', '-I', HERE + '/fat12.py', 'x', img, raw])
    ex = SCR + '/ex' + v
    os.makedirs(ex, exist_ok=True)
    for z in zips:
        run(['unzip', '-o', '-q', raw + '/' + z, '-d', ex])
    src = ex if zips else raw
    wd = runs + '/' + v
    os.makedirs(wd, exist_ok=True)
    for f in ('TPC.EXE', 'TURBO.TPL'):
        shutil.copy(src + '/' + f, wd + '/' + f)
        say('  ', v, f, os.path.getsize(wd + '/' + f), sha(wd + '/' + f))
    shutil.copy(HERE + '/probes/t4_40.pas' if v == '40' else HERE + '/probes/t4.pas', wd + '/T4.PAS')  # 4.0's Dos has no GetEnv, EnvStr or SwapVectors, so the probe for 4.0 leaves it out
    shutil.copy(HERE + '/probes/t1.pas', wd + '/T1.PAS')
    bat += 'cd \\%s\r\ntpc t1.pas\r\ntpc t4.pas > t4.log\r\ncd \\\r\n' % v
bat += 'echo ok > DONE.TXT\r\n'
open(runs + '/c.bat', 'w', newline='').write(bat)

# 2. compile
say(run(['python3', '-I', HERE + '/dbx.py', runs, 'c.bat', '90']).strip())
for v in sets:
    for t in ('T1.EXE', 'T4.EXE'):
        p = runs + '/' + v + '/' + t
        if not os.path.exists(p):
            say('NOT BUILT', v, t, open(runs + '/' + v + '/T4.LOG', errors='replace').read()[-300:])
            continue
        say('built', v, t, os.path.getsize(p), sha(p))

# 3. compare
cands = [runs + '/%s/T4.EXE' % v for v in sets if os.path.exists(runs + '/%s/T4.EXE' % v)]
for tool in ('cover.py', 'bytecmp.py', 'gaps.py'):
    for c in cands:
        if tool == 'bytecmp.py' and not c.endswith('/55/T4.EXE'):
            continue
        if tool == 'gaps.py' and not (c.endswith('/55/T4.EXE') or c.endswith('/50/T4.EXE')):
            continue
        out = run(['python3', '-I', HERE + '/' + tool, goal, c])
        open(OUT + '/%s.%s.txt' % (tool[:-3], c.rsplit('/', 2)[1]), 'w').write(out)
say(run(['python3', '-I', HERE + '/cover.py', goal] + cands).strip())
say(run(['python3', '-I', HERE + '/units.py', goal] + cands).strip())
say(run(['python3', '-I', HERE + '/routines.py', goal, REPO] + [c for c in cands if '/701/' not in c]).strip())
