// git, gh, the config and argument parsing, for review.mjs, post-review.mjs and switch-model.mjs.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { openCodeHome, listedModels, loginHint, openCodeVersion, versionProblem } from './opencode.mjs';
import { privateHome } from './opencode-transport.mjs';

// The command that runs a tool. HARNESS_GH_EXE names the gh to run (the tests' fake, #2); a .mjs or
// .js one runs through Node, since Windows cannot execute a script.
export function toolCommand(cmd, env = process.env) {
  const over = cmd === 'gh' ? env.HARNESS_GH_EXE : null;
  if (!over) return [cmd, []];
  return /\.m?js$/.test(over) ? [process.execPath, [over]] : [over, []];
}

export function sh(cmd, args, { cwd, allowFail = false, env } = {}) {
  const [exe, pre] = toolCommand(cmd, env ?? process.env);
  const r = spawnSync(exe, [...pre, ...args], { cwd, env, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  if (r.error) throw new Error(`${cmd} could not run: ${r.error.message}`);
  if (r.status !== 0 && !allowFail) throw new Error(`${cmd} ${args.join(' ')} failed (${r.status}):\n${r.stderr}`);
  return r.status === 0 ? r.stdout.trim() : '';
}

export function requireTools(...tools) {
  for (const t of tools) {
    const [exe, pre] = toolCommand(t);
    const r = spawnSync(exe, [...pre, '--version'], { stdio: 'ignore' });
    if (r.error) throw new Error(`${t} is not on PATH.`);
  }
}

// The main checkout, even when run from a worktree, and the directory agents' worktrees live in.
export function repoPaths(config) {
  const top = sh('git', ['rev-parse', '--show-toplevel']);
  const commonDir = sh('git', ['-C', top, 'rev-parse', '--path-format=absolute', '--git-common-dir']);
  const mainRoot = path.dirname(commonDir);
  const rel = (config.worktreeRoot ?? '../{repo}-work').replaceAll('{repo}', path.basename(mainRoot));
  return { top, commonDir, mainRoot, workRoot: path.resolve(mainRoot, rel) };
}

export function loadConfig(top) {
  const file = path.join(top, 'harness.json');
  if (!fs.existsSync(file)) throw new Error(`harness.json not found at ${file}`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

// A model's note in harness.json (what to look for, its login, its effort), printed when it runs.
export function watchLine(name, model) {
  const note = model.note ?? model.watch;
  return note ? `note: ${name} (${model.id}): ${note}` : null;
}

// --name value, --flag, and repeatable --env KEY=VALUE / --copy path.
export function parseArgs(argv, { flags = [], repeatable = [] } = {}) {
  const out = {};
  for (const r of repeatable) out[r] = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) throw new Error(`Unexpected argument: ${a}`);
    const key = a.slice(2);
    if (flags.includes(key)) { out[key] = true; continue; }
    const val = argv[++i];
    if (val === undefined) throw new Error(`${a} needs a value`);
    if (repeatable.includes(key)) out[key].push(val); else out[key] = val;
  }
  return out;
}

export function envWith(pairs) {
  const env = { ...process.env };
  for (const p of pairs) {
    const i = p.indexOf('=');
    if (i < 1) throw new Error(`--env takes KEY=VALUE; got ${p}`);
    env[p.slice(0, i)] = p.slice(i + 1);
  }
  return env;
}

// OpenCode silently falls back to its default, full-permission agent when --agent names one it
// cannot find, and a branch cut before the agent file existed does not carry it (IC2 #480). Copy
// the agent into the worktree, and keep the copy out of git so the model cannot commit it.
export function ensureAgent({ top, commonDir, worktree, agent }) {
  const rel = `.opencode/agents/${agent}.md`;
  const src = path.join(top, rel);
  if (!fs.existsSync(src)) throw new Error(`Agent file not found: ${src}`);
  if (sh('git', ['-C', worktree, 'ls-files', '--', rel], { allowFail: true })) return;
  fs.mkdirSync(path.join(worktree, '.opencode', 'agents'), { recursive: true });
  fs.copyFileSync(src, path.join(worktree, rel));
  const exclude = path.join(commonDir, 'info', 'exclude');
  const text = fs.existsSync(exclude) ? fs.readFileSync(exclude, 'utf8') : '';
  if (!text.split(/\r?\n/).includes(rel)) {
    fs.mkdirSync(path.dirname(exclude), { recursive: true });
    fs.appendFileSync(exclude, `${text && !text.endsWith('\n') ? '\n' : ''}${rel}\n`);
  }
}

// Before anything is billed: the scripts' own data directory, the OpenCode version (any major but
// the supported one is refused, #26), and which models of `chain` OpenCode lists there. A model it
// does not list (an unknown id, or a provider not logged in in that directory) is dropped, with the
// command that fixes it. Quota is not checked (the owner, 2026-10-11: the model named runs).
// Returns { env, usable, problems }.
// The version is read BEFORE any data directory is opened (#262): a v2 process never opens the legacy
// v1 directory (whose database a 2.x would migrate, IC2 #540) and never copies auth.json; it lists models
// from the v2-only root (lib/opencode-transport.mjs privateHome), where its logins live. The returned
// env is the caller's for v2 (the run makes its own private root), the legacy one for v1.
export async function prepareOpenCode({ opencode, chain, models, env, cwd, log }) {
  const version = await openCodeVersion(opencode, { env, cwd });
  log(`opencode: ${version ?? 'unknown version'} (${opencode.binary ?? opencode.exe})`);
  const bad = versionProblem(version, opencode.exe);
  if (bad) return { env, usable: [], problems: [bad], version };
  const v2 = version.startsWith('2.');
  const oc = v2 ? (() => { const h = privateHome(env); return { env: h.env, dataHome: h.env.XDG_DATA_HOME }; })() : openCodeHome(env, { log });
  if (v2) log(`opencode: v2 data directory ${oc.dataHome} (provider logins and sessions; the legacy v1 directory is not opened)`);
  const { listed, errors } = await listedModels(opencode, chain.map((m) => models[m].id.split('/')[0]), { env: oc.env, cwd });
  const problems = [];
  const usable = chain.filter((m) => {
    if (listed.has(models[m].id)) return true;
    problems.push(`${m}: ${v2 ? loginHintV2(models[m].id, listed, oc.dataHome, errors) : loginHint(models[m].id, listed, oc.dataHome, errors)}`);
    return false;
  });
  return { env: v2 ? env : oc.env, usable, problems, version };
}

// Why a v2 catalogue lacks a model, and the one-time login that fixes it (never a credential copy).
export function loginHintV2(modelId, listed, dataHome, errors = new Map()) {
  const provider = modelId.split('/')[0];
  if (errors.has(provider)) return `${errors.get(provider)}. That is OpenCode failing in ${dataHome}, not a missing login; nothing billed`;
  if ([...listed].some((id) => id.startsWith(`${provider}/`))) return `${modelId} is not in \`opencode models --standalone\`: check the id in harness.json; nothing billed`;
  const db = path.join(dataHome, 'opencode', 'opencode.db');
  return `${provider} lists no models in the v2 data directory ${dataHome}: log in once there, in a terminal of your own `
    + `(XDG_DATA_HOME="${dataHome}" OPENCODE_DB="${db}" opencode auth login --standalone ${provider}), or set its API key in the environment. `
    + 'Nothing billed, no other model tried';
}

// The family of the main session, and so of every Claude Code agent it spawns (an agent runs through
// the same endpoint). The session is set only by the Anthropic environment variables: with
// ANTHROPIC_BASE_URL unset or at anthropic.com it is Claude; when Claude's tokens are out the owner
// points it at another provider that speaks the same API: Z.AI's GLM, MiniMax, or Moonshot's Kimi
// (the owner, 2026-10-12), and the family rule must then keep that family out of the reviewer's
// seat. The names match the families the reviewer models get (glm, minimax, kimi). HARNESS_SESSION_FAMILY
// overrides the guess; an endpoint this list does not know returns null, and the caller refuses
// to review until it is set. Only the URL's host is read, on domain boundaries: a path, a query or
// a host that merely contains a name (api.anthropic.com.proxy.example) is unknown (Sol's R4 on PR 149).
// The owner's endpoints: https://api.z.ai/api/anthropic, https://api.minimax.io/anthropic.
const ENDPOINT_FAMILIES = [[['anthropic.com'], 'claude'], [['z.ai', 'bigmodel.cn'], 'glm'],
  [['minimax.io', 'minimaxi.com'], 'minimax'], [['moonshot.ai', 'moonshot.cn', 'kimi.com'], 'kimi'],
  [['deepseek.com'], 'deepseek'], [['aliyuncs.com'], 'qwen'], [['xiaomimimo.com'], 'mimo']];
export function sessionFamily(env = process.env) {
  if (env.HARNESS_SESSION_FAMILY) return env.HARNESS_SESSION_FAMILY.trim().toLowerCase();
  if (env.CODEX_THREAD_ID || env.CODEX_CI === '1') return 'openai';
  if (!env.ANTHROPIC_BASE_URL) return 'claude';
  let host;
  try { host = new URL(env.ANTHROPIC_BASE_URL).hostname.toLowerCase(); } catch { return null; }
  return ENDPOINT_FAMILIES.find(([ds]) => ds.some((d) => host === d || host.endsWith(`.${d}`)))?.[1] ?? null;
}

export const ocArgs = (worktree, agent, model) =>
  ['run', '--dir', worktree, '--agent', agent, '--model', model.id, ...(model.variant ? ['--variant', model.variant] : [])];
