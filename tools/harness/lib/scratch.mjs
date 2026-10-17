// The reviewer's scratch folder on the real disk (#311). /tmp on this machine is an 11 GB RAM-backed
// tmpfs shared with other projects; it hit 100% on 2026-10-17 and killed a review of PR 300 after an
// hour. A review's copies of main, family-run outputs and suite logs go to ~/goal2-review-tmp/<run>
// instead: .opencode/agents/reviewer.md grants that path (and still /tmp), review.mjs points TMPDIR
// at the run's folder and removes it when the run ends well, keeps it when the run fails.
//
// The path has no dot element: Ghidra rejects a temp path with one (so not ~/.cache/..., and not a
// home directory whose path has a dot segment). HARNESS_SCRATCH_ROOT overrides the root (the tests'
// seam); the reviewer.md grant is the default root, so an override is for tests only.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const MB = 1024 * 1024;
export const SCRATCH_NAME = 'goal2-review-tmp';
// Below these a /tmp-only run is risky: the review is refused only when BOTH are short (#311).
export const MIN_TMP_MB = 500;
export const MIN_SCRATCH_MB = 2048;

export function scratchRoot(env = process.env) {
  if (env.HARNESS_SCRATCH_ROOT) return path.resolve(env.HARNESS_SCRATCH_ROOT);
  return path.join(env.HOME || env.USERPROFILE || os.homedir(), SCRATCH_NAME);
}

// Why a root cannot be used, or null: every element of the path must be a plain name (Ghidra).
export function rootProblem(root) {
  const bad = root.split(/[\\/]+/).find((p) => p.startsWith('.'));
  return bad ? `the scratch folder ${root} has a dot element (${bad}); Ghidra rejects temp paths with one. Use a path without one (HARNESS_SCRATCH_ROOT).` : null;
}

// Free bytes on the filesystem holding `p` (its nearest existing ancestor), or null when unknown.
export function freeBytes(p) {
  let dir = path.resolve(p);
  for (;;) {
    try {
      const s = fs.statfsSync(dir);
      return s.bavail * s.bsize;
    } catch {
      const up = path.dirname(dir);
      if (up === dir) return null;
      dir = up;
    }
  }
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

// A folder of this run's own under the root. `name` is the run's unit name.
export function makeScratch(root, name) {
  const dir = path.join(root, name);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

// Only a folder directly inside `root` is ever removed.
export function removeScratch(root, dir) {
  if (path.dirname(path.resolve(dir)) !== path.resolve(root)) throw new Error(`Refusing to remove ${dir}: not a folder directly in ${root}.`);
  fs.rmSync(dir, { recursive: true, force: true });
}

// Where the harness's own files go (its OpenCode logs, the review's comment body): os.tmpdir()'s
// folder while that is writable and has room; else a folder of the scratch root's, which stays after
// the run, so a full or read-only /tmp does not stop a review or lose it at the post.
export function harnessDir(root, { tmp = os.tmpdir(), free = freeBytes, minTmpMb = MIN_TMP_MB } = {}) {
  const preferred = path.join(tmp, 'harness-opencode');
  const f = free(tmp);
  try {
    if (f !== null && f < minTmpMb * MB) throw new Error('low');
    fs.mkdirSync(preferred, { recursive: true });
    fs.accessSync(preferred, fs.constants.W_OK);
    return preferred;
  } catch {
    const dir = path.join(root, 'harness-logs');
    fs.mkdirSync(dir, { recursive: true });
    return dir;
  }
}
