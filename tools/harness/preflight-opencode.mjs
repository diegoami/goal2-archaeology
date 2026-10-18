#!/usr/bin/env node
// Non-billing preflight of the OpenCode 2 review transport on the installed binary (#262; ported from
// goal2 PR 178's preflight-opencode.mjs). It never sends a prompt: no `run`, `prompt` or `generate`.
//
//   node tools/harness/preflight-opencode.mjs --out <dir> [--model minimax/MiniMax-M3#thinking --family minimax]
//
// With the real binary, the real guard plugin and THIS checkout's reviewer, it does what a review does
// before generation: pins the binary, stages the guard, surveys the config, starts a guard-free baseline
// and the guarded private server, checks the selected model, effort and family are advertised, checks
// the loaded reviewer profile against the trusted rules and the plugin inventory, compares the two
// catalogues; then creates one owned EMPTY session, exports it (zero cost, zero tokens), peeks it
// through a private standalone export, interrupts it (a no-op), and stops, while an unrelated private
// server of its own keeps its sessions. The runtime (a throwaway data directory: the model must come
// from an API key in the environment) is removed at the end; every result is written exclusively
// under a new preflight-* folder of --out. It does not prove a login, a billed call or the
// cancellation of an active generation.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { resolveOpenCode } from './lib/opencode.mjs';
import { privateHome, startPrivateServer, settledCatalogue, capture, hash } from './lib/opencode-transport.mjs';
import { peekRecord, renderPeek } from './lib/opencode-peek.mjs';
import { reviewerPolicy, trustedReviewEnv, verifyReviewer } from './lib/opencode-policy.mjs';
import { stageGuard, baselinePlugins, readyPlugins, selectGuardPlugins, pinGuardBinary, inspectConfig, catalogueParity } from './lib/opencode-guard.mjs';

const flag = (name, fallback) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : fallback; };
const outArg = flag('--out');
assert(outArg, 'usage: preflight-opencode.mjs --out <dir> [--model provider/model#variant --family F]');
const [modelId, variant] = flag('--model', 'minimax/MiniMax-M3#thinking').split('#');
const family = flag('--family', 'minimax');
const out = path.resolve(outArg); fs.mkdirSync(out, { recursive: true });
const dest = fs.mkdtempSync(path.join(out, 'preflight-'));
const save = (name, value) => fs.writeFileSync(path.join(dest, name), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
const runtime = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-preflight-'));
const cwd = fs.realpathSync(process.cwd());
const cmd = resolveOpenCode(); const transportIdentity = pinGuardBinary(cmd);
const policy = reviewerPolicy(path.join(cwd, '.opencode/agents/reviewer.md'));
const home = privateHome({ ...process.env, HARNESS_OPENCODE_HOME: path.join(runtime, 'runtime') });
const guard = stageGuard(home.root, policy);
const baseEnv = trustedReviewEnv(home.env, policy, 'reviewer', guard, { baseline: true });
let env = trustedReviewEnv(home.env, policy, 'reviewer', guard);
const version = await capture(cmd, ['--version'], { env, cwd });
assert.equal(version.code, 0); assert.match(version.stdout, /(?:^|v)2\./);
const modelRef = { id: modelName(), providerID: modelId.split('/')[0], ...(variant ? { variant } : {}) };
function modelName() { return modelId.slice(modelId.indexOf('/') + 1); }
save('identity.json', { version: version.stdout.trim(), binary: cmd.exe, binarySHA256: hash(fs.readFileSync(cmd.exe)), transportIdentity,
  sourceSHA256: hash(fs.readFileSync(new URL(import.meta.url))), policySHA256: policy.sourceSHA256, directory: cwd, model: { modelId, variant: variant ?? null, family },
  sources: Object.fromEntries(['opencode-protocol.mjs', 'opencode-policy.mjs', 'opencode-transport.mjs', 'opencode-peek.mjs', 'opencode-guard.mjs', 'opencode-workflow.mjs'].map((f) => [f, hash(fs.readFileSync(new URL('./lib/' + f, import.meta.url)))])),
  guard: { files: guard.files, dependencies: Object.keys(guard.dependencies).length } });
let server; let unrelated; let baseline;
try {
  const otherHome = privateHome({ ...process.env, HARNESS_OPENCODE_HOME: path.join(runtime, 'unrelated') });
  unrelated = await startPrivateServer(cmd, { env: trustedReviewEnv(otherHome.env, policy), cwd });
  const otherSession = await unrelated.request('/api/session', { body: { title: 'preflight-unrelated', agent: 'build', model: modelRef, location: { directory: cwd } } });
  const unrelatedBefore = await unrelated.request(`/api/session/${otherSession.data.id}`);
  baseline = await baselinePlugins(cmd, { env: baseEnv, cwd, guard, retain: true });
  save('baseline-config.json', { survey: baseline.config, actual: baseline.actualConfig, plugins: baseline.plugins.map((p) => p.id) });
  selectGuardPlugins(guard, baseline.plugins.map((p) => p.id)); env = trustedReviewEnv(home.env, policy, 'reviewer', guard);
  server = await startPrivateServer(cmd, { env, cwd });
  save('actual-config.json', inspectConfig(await server.request('/api/config'), guard));
  save('plugins.json', (await readyPlugins(server, guard)).map((p) => ({ id: p.id, source: p.source?.type, status: p.state?.status })));
  const schema = await server.request('/openapi.json');
  save('schema-identity.json', { source: '/openapi.json', sha256: hash(JSON.stringify(schema)), version: schema.info?.version });
  const found = await settledCatalogue(server, { model: { id: modelId, ...(variant ? { variant } : {}), family }, agent: 'reviewer', verifyAgent: (profile) => verifyReviewer(profile, policy, 'reviewer') });
  const parity = await catalogueParity(baseline.server, server, { timeoutMs: 30000 });
  save('catalogue-parity.json', { models: parity.length, selected: parity.filter((m) => `${m.providerID}/${m.id}` === modelId) });
  await baseline.server.stop(); baseline = null;
  save('profile.json', { id: found.profile.id, mode: found.profile.mode, hidden: found.profile.hidden, system: found.profile.system, permissions: found.profile.permissions });
  save('selected-model.json', { id: found.selected.id, providerID: found.selected.providerID, family: found.selected.family, variants: found.selected.variants.map((v) => v.id), enabled: found.selected.enabled });
  const session = await server.request('/api/session', { body: { title: 'harness-preflight-owned-empty', agent: 'reviewer', model: modelRef, location: { directory: cwd } } });
  const record = await server.request(`/api/experimental/session/${session.data.id}/export`);
  assert.equal(record.data.info.location.directory, cwd); assert.equal(record.data.info.agent, 'reviewer'); assert.deepEqual(record.data.info.model, modelRef);
  assert.equal(record.data.info.cost, 0); assert.deepEqual(record.data.info.tokens, { input: 0, output: 0, reasoning: 0, cache: { read: 0, write: 0 } }); assert.deepEqual(record.data.messages, []);
  save('empty-export.json', record.data);
  const peek = await peekRecord(cmd, { record: { major: 2, phase: 'running', dataRoot: home.root, sessionID: session.data.id, directory: cwd, agent: 'reviewer', model: { id: modelId, ...(variant ? { variant } : {}) }, files: {} } }, { env });
  assert.deepEqual(peek.info, record.data.info); save('peek.json', { record: peek, rendered: renderPeek(peek, 2) });
  const idle = await server.request(`/api/session/${session.data.id}/interrupt`, { body: {} });
  assert.equal(idle.interrupted, false, 'an empty idle session has nothing to interrupt'); save('idle-interrupt.json', idle);
  const stopped = await server.stop(); server = null;
  save('shutdown.json', { exitCode: stopped.exitCode, signal: stopped.signal, stderrSHA256: hash(stopped.stderr) });
  const unrelatedAfter = await unrelated.request(`/api/session/${otherSession.data.id}`);
  assert.deepEqual(unrelatedAfter, unrelatedBefore, 'an unrelated private server and its session survive our shutdown');
  save('unrelated-survived.json', { before: unrelatedBefore, after: unrelatedAfter });
} finally {
  if (baseline?.server) await baseline.server.stop();
  if (server) await server.stop();
  if (unrelated) await unrelated.stop();
  fs.rmSync(runtime, { recursive: true, force: true }); // a throwaway data directory, not evidence
}
console.log(`Non-billing reviewer preflight passed: ${dest}`);
