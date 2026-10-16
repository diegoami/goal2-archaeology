#!/usr/bin/env python3
"""Run a DOS batch file unattended in DOSBox-X 2024.03.01 on a private Xvfb (never :99 or :0).
usage: dbx.py HOSTDIR BATCHNAME [TIMEOUT_S]
HOSTDIR is mounted as C:; BATCHNAME (a .bat in it) is run; DOSBox-X then exits. Third-party
compilers stay on the host scratch path, outside the repository."""
import os, subprocess, sys, time, tempfile

hostdir, bat = sys.argv[1], sys.argv[2]
timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 120
dbx = os.path.expanduser('~/tools/dosbox-x-2024.03.01/bin/dosbox-x')
if not os.path.isfile(dbx):
    dbx = 'dosbox-x'
disp = ':147'
conf = f"""[sdl]
fullscreen=false
output=surface
[dosbox]
memsize=16
[cpu]
core=normal
cputype=486
cycles=max
[sblaster]
sbtype=none
[midi]
mpu401=none
[autoexec]
@echo off
mount c {hostdir}
c:
{bat}
exit
"""
d = tempfile.mkdtemp(prefix='dbx')
cp = os.path.join(d, 'dosbox.conf')
open(cp, 'w').write(conf)
xv = subprocess.Popen(['Xvfb', disp, '-screen', '0', '800x600x24', '-nolisten', 'tcp'],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
time.sleep(1.5)
env = dict(os.environ, DISPLAY=disp, SDL_AUDIODRIVER='dummy')
p = subprocess.Popen([dbx, '-conf', cp, '-noprimaryconf', '-nolocalconf'], env=env,
                     stdout=open(os.path.join(d, 'out'), 'w'), stderr=subprocess.STDOUT, start_new_session=True)
try:
    p.wait(timeout=timeout)
    print('dosbox-x exit', p.returncode)
except subprocess.TimeoutExpired:
    print('TIMEOUT')
    os.killpg(p.pid, 15)
finally:
    try:
        os.killpg(xv.pid, 15)
    except ProcessLookupError:
        pass
