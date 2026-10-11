# Restarting WSL (2026-10-11)

WSLg's compositor (weston) segfaults about every 1 min 43 s on this machine since 2026-10-10
(`grep -c "signal 11" /mnt/wslg/stderr.log`), so the desktop display `:0` hangs and a human
sitting cannot start (#117). Update WSL, then restart it. `wsl --shutdown` ends every Linux
session, Claude Code sessions included.

## In Windows PowerShell (Administrator if `wsl --update` asks)

```powershell
# 1. Check the version, update WSL (and WSLg with it), then show the new version
wsl --version
wsl --update
wsl --version

# 2. Stop every WSL distro and VM
wsl --shutdown

# 3. Confirm nothing is running
wsl --list --running

# 4. Start Ubuntu again
wsl -d Ubuntu
```

## Back in Ubuntu

```bash
# WSLg should stay up: this count should stay at 0 for a few minutes
grep -c "signal 11" /mnt/wslg/stderr.log

# the desktop display should answer
xdpyinfo -display :0 | head -2

# the recorder's preflight
cd ~/projects/goal2-archaeology && bash runtime/human/play.sh --self-test
```

If the `signal 11` count rises again after the update, WSLg is still crashing: look at the Windows
side (graphics driver, WSLg GPU acceleration).

## After the restart

- Record a sitting: `bash runtime/human/play.sh --video` (stop by closing the window or Ctrl+C).
- T36 (PR #123) is paused: launch the owner's re-check on gpt-6.1-sol (low) at the PR head.
