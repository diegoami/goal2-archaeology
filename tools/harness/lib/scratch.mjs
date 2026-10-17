// The reviewer's scratch folder, and everything else a review writes, on the real disk (#311). /tmp on
// this machine is an 11 GB RAM-backed tmpfs shared with other projects; it hit 100% on 2026-10-17 and
// killed a review of PR 300 after an hour. A review's copies of main, family-run outputs and suite logs go
// to ~/goal2-review-tmp/<run>; the harness's own files (OpenCode's output logs, the finished review kept
// until it is posted) go to ~/goal2-review-tmp-harness (a sibling, outside the grant). .opencode/agents/reviewer.md grants the
// scratch path (and still /tmp); review.mjs points TMPDIR at the run's folder and removes it when the run
// ends well, keeps it when the run fails.
//
// Every directory the harness writes in is chosen by its RESOLVED path and filesystem (diskDir): a root
// that is, or contains, a symlink into a RAM-backed filesystem is refused, so "on disk" cannot silently be
// /tmp again. The path as written has no dot element either: Ghidra rejects a temp path with one.
// HARNESS_SCRATCH_ROOT overrides the root (the tests' seam); the reviewer.md grant is the default root.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const MB = 1024 * 1024;
export const SCRATCH_NAME = 'goal2-review-tmp';
// Below these a /tmp-only run is risky: the review is refused only when BOTH are short (#311).
export const MIN_TMP_MB = 500;
export const MIN_SCRATCH_MB = 2048;
// statfs f_type of the filesystems that live in memory (linux/magic.h: TMPFS_MAGIC, RAMFS_MAGIC).
const RAM_FS = new Map([[0x01021994, 'tmpfs'], [0x858458f6, 'ramfs']]);

export function scratchRoot(env = process.env) {
  if (env.HARNESS_SCRATCH_ROOT) return path.resolve(env.HARNESS_SCRATCH_ROOT);
  return path.join(env.HOME || env.USERPROFILE || os.homedir(), SCRATCH_NAME);
}

// Why a root cannot be used by its written path, or null: every element must be a plain name (Ghidra).
export function rootProblem(root) {
  const bad = root.split(/[\\/]+/).find((p) => p.startsWith('.'));
  return bad ? `the scratch folder ${root} has a dot element (${bad}); Ghidra rejects temp paths with one. Use a path without one (HARNESS_SCRATCH_ROOT).` : null;
}

// statfs of `p`'s nearest existing ancestor, or null when unknown.
function statfsOf(p) {
  let dir = path.resolve(p);
  for (;;) {
    try { return fs.statfsSync(dir); } catch {
      const up = path.dirname(dir);
      if (up === dir) return null;
      dir = up;
    }
  }
}

// Free bytes on the filesystem holding `p` (its nearest existing ancestor), or null when unknown.
export function freeBytes(p) {
  const s = statfsOf(p);
  return s ? s.bavail * s.bsize : null;
}

// The name of the in-memory filesystem holding `p`, or null.
export function ramFsOf(p) {
  const s = statfsOf(p);
  return s ? RAM_FS.get(s.type) ?? null : null;
}

// The path with every existing symlink followed (the nearest existing ancestor's real path + the rest).
export function realOf(p) {
  let dir = path.resolve(p);
  const rest = [];
  for (;;) {
    try { return path.join(fs.realpathSync(dir), ...rest.reverse()); } catch {
      const up = path.dirname(dir);
      if (up === dir) return path.resolve(p);
      rest.push(path.basename(dir));
      dir = up;
    }
  }
}

// Why `dir` is not a place for a review's files, by where it really is, or null. `ramFs(p)` names the
// in-memory filesystem under a real path (tmpfs, ramfs) or returns null.
export function diskProblem(dir, { ramFs = ramFsOf } = {}) {
  const real = realOf(dir);
  const ram = ramFs(real);
  if (ram) return `${dir} is really ${real}, on a ${ram} (RAM-backed, like /tmp): a review's files must go to the real disk. Point HARNESS_SCRATCH_ROOT (default ~/${SCRATCH_NAME}) at a folder on disk, and remove the symlink or mount that sends it there.`;
  return null;
}

// null when the review may start; else the message. `free(p)` returns bytes or null (unknown counts as
// enough: the check never blocks on a filesystem it cannot read, e.g. no /tmp on Windows).
export function spaceProblem({ tmp = '/tmp', root, minTmpMb = MIN_TMP_MB, minScratchMb = MIN_SCRATCH_MB, free = freeBytes }) {
  const t = free(tmp);
  const s = free(root);
  const tmpLow = t !== null && t < minTmpMb * MB;
  const scratchLow = s !== null && s < minScratchMb * MB;
  if (!(tmpLow && scratchLow)) return null;
  const mb = (b) => Math.floor(b / MB);
  return `Refused: ${tmp} has ${mb(t)} MB free (under ${minTmpMb}) and the scratch folder ${root} has ${mb(s)} MB free `
    + `(under ${minScratchMb}), so a review has nowhere to put its files. Free space on either, then run again. Nothing was run or posted.`;
}

// The thresholds, from HARNESS_MIN_TMP_MB / HARNESS_MIN_SCRATCH_MB (the tests' seam) or the defaults.
export function thresholds(env = process.env) {
  const n = (v, d) => (v !== undefined && v !== '' && Number.isFinite(Number(v)) ? Number(v) : d);
  return { minTmpMb: n(env.HARNESS_MIN_TMP_MB, MIN_TMP_MB), minScratchMb: n(env.HARNESS_MIN_SCRATCH_MB, MIN_SCRATCH_MB) };
}

// The variables a run's tools honour for their temporary files (Node reads TMPDIR, TMP, TEMP in that
// order; Python's tempfile TMPDIR, TEMP, TMP).
export const tmpEnv = (dir) => ({ TMPDIR: dir, TMP: dir, TEMP: dir });

// Creates `dir` (and parents) and throws unless it really is on disk. Used for every folder the harness
// writes in: the root, the harness folder, a run's scratch folder. Returns `dir` as given.
export function diskDir(dir, opts) {
  fs.mkdirSync(dir, { recursive: true });
  const bad = diskProblem(dir, opts);
  if (bad) throw new Error(bad);
  return dir;
}

// A folder of this run's own under the root. `name` is the run's id.
export function makeScratch(root, name, opts) {
  return diskDir(path.join(root, name), opts);
}

// The folder of the harness's own files (OpenCode's output logs, the finished review): a SIBLING of the
// root, `<root>-harness`, outside what reviewer.md grants (`<root>/*`), so the reviewer's tools cannot
// write there. A model with a shell could still reach it (the grant is a tool-layer rule, not an OS
// boundary), so every file the harness creates there is also created exclusively (openFresh).
export const harnessDir = (root, opts) => diskDir(`${root}-harness`, opts);

// Opens a NEW file for writing at a name the model may know. It never follows a symlink and never writes
// into an existing file: O_EXCL fails on an existing name, a dangling or live symlink included; a name
// that is taken (planted, or left by an earlier run) is removed as a name (the target is not touched) and
// created again, and a second collision is an error. `disk` (default) also checks that the folder is
// really on disk, by its resolved path, at the moment of the write.
const NOFOLLOW = fs.constants.O_NOFOLLOW ?? 0;
export function openFresh(file, { disk = true, ramFs } = {}) {
  if (disk) {
    const bad = diskProblem(path.dirname(file), ramFs ? { ramFs } : undefined);
    if (bad) throw new Error(bad);
  }
  const flags = fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | NOFOLLOW;
  for (let tries = 0; ; tries++) {
    try { return fs.openSync(file, flags, 0o644); } catch (e) {
      if (e.code !== 'EEXIST' || tries > 0) throw e;
      fs.rmSync(file, { force: true });
    }
  }
}

export function writeFresh(file, data, opts) {
  const fd = openFresh(file, opts);
  try { fs.writeSync(fd, data); } finally { fs.closeSync(fd); }
}

// Only a folder directly inside `root` is ever removed.
export function removeScratch(root, dir) {
  if (path.dirname(path.resolve(dir)) !== path.resolve(root)) throw new Error(`Refusing to remove ${dir}: not a folder directly in ${root}.`);
  fs.rmSync(dir, { recursive: true, force: true });
}

// Writes the finished review where it survives a failed post. Returns the file, or null when even the
// disk would not take it (the caller then prints the review whole).
export function keepReview(dir, runId, body, opts) {
  try {
    const file = path.join(diskDir(dir, opts), `review-${runId}.md`);
    writeFresh(file, body.endsWith('\n') ? body : `${body}\n`, opts);
    return file;
  } catch {
    return null;
  }
}
