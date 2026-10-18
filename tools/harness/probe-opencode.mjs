#!/usr/bin/env node
// Non-billing capture of the installed OpenCode 2 CLI's protocol (#262; ported from goal2 PR 175/178,
// tools/harness/probe-opencode.mjs). It never sends a prompt: no `run`, no `prompt`, no `generate`.
// The only session it touches is one it creates, empty, in a throwaway data directory of its own (never
// the harness's v2 provider database, never the legacy v1 one), and it reads that session back through
// the API and the CLI. The old v1 commands are run against the v2 binary to record that they fail; the
// `run` among them names a model no provider has, so even a parse that accepted it could bill nothing.
//
//   node tools/harness/probe-opencode.mjs --out tests/fixtures/opencode/v2-live [--model minimax/MiniMax-M3#thinking]
//
// Every artefact is written exclusively (flag wx) into a new run-* folder under --out, and manifest.json
// records each one's SHA-256, the binary's and this script's. Request settings of the model and agent
// registries can carry provider keys, so those are projected to whitelisted fields before anything is
// written; the full responses are kept only as hashes.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { once } from 'node:events';
import assert from 'node:assert/strict';
import { resolveOpenCode } from './lib/opencode.mjs';

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const flag = (name, fallback) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : fallback; };
const outArg = flag('--out');
assert(outArg, 'usage: probe-opencode.mjs --out <directory> [--model provider/model#variant]');
const [modelId, variant] = flag('--model', 'minimax/MiniMax-M3#thinking').split('#');
const providerID = modelId.split('/')[0];
const modelName = modelId.slice(providerID.length + 1);
const out = path.resolve(outArg);
fs.mkdirSync(out, { recursive: true });
const run = fs.mkdtempSync(path.join(out, 'run-'));
const artifacts = {};
function save(name, value) {
  const bytes = typeof value === 'string' ? value : JSON.stringify(value, null, 2) + '\n';
  fs.writeFileSync(path.join(run, name), bytes, { flag: 'wx' });
  artifacts[name] = sha(bytes);
}
const cmd = resolveOpenCode();
assert.equal(cmd.prefix.length, 0, 'the probe needs the installed native binary, not a script');
const home = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-probe-home-'));
const env = { ...process.env, OPENCODE_DISABLE_PROJECT_CONFIG: '1' };
for (const [key, leaf] of Object.entries({ XDG_DATA_HOME: 'data', XDG_CACHE_HOME: 'cache', XDG_STATE_HOME: 'state' })) {
  env[key] = path.join(home, leaf); fs.mkdirSync(env[key]);
}
env.OPENCODE_DB = path.join(env.XDG_DATA_HOME, 'opencode', 'opencode.db');
for (const key of ['OPENCODE_CONFIG', 'OPENCODE_CONFIG_DIR', 'OPENCODE_CONFIG_CONTENT']) delete env[key];
const cwd = fs.realpathSync(process.cwd());
function cli(args) {
  const r = spawnSync(cmd.exe, args, { env, cwd, encoding: 'utf8', timeout: 60000, maxBuffer: 16e6 });
  assert(!r.error, `CLI did not finish: ${args.join(' ')}: ${r.error?.code}`);
  return { args, code: r.status, stdout: r.stdout, stderr: r.stderr };
}
const version = cli(['--version']);
assert.equal(version.code, 0); assert.match(version.stdout, /(?:v|^)2\./);
save('version.json', version);
for (const args of [['run', '--help'], ['serve', '--help'], ['models', '--help'], ['session', 'export', '--help'], ['session', 'list', '--help']]) {
  const r = cli(args); assert.equal(r.code, 0); save(`help-${args.slice(0, -1).join('-')}.json`, r);
}
const listed = cli(['models', '--standalone']);
assert.equal(listed.code, 0);
save('models-cli.json', { args: listed.args, code: listed.code, lines: listed.stdout.split('\n').filter(Boolean).length,
  selected: listed.stdout.split('\n').filter((l) => l.trim() === modelId), stderr: listed.stderr, stdoutSHA256: sha(listed.stdout) });

const unrelated = http.createServer((req, res) => res.end('unrelated-server-alive'));
unrelated.listen(0, '127.0.0.1'); await once(unrelated, 'listening');
const unrelatedURL = `http://127.0.0.1:${unrelated.address().port}`;
let child; let exited; let url; let password; let logs = ''; let eventAbort; let eventTask;
const lifecycle = { unrelatedBefore: await (await fetch(unrelatedURL)).text() };
try {
  child = spawn(cmd.exe, ['serve', '--hostname', '127.0.0.1', '--port', '0'], { env, cwd, stdio: ['ignore', 'pipe', 'pipe'] });
  exited = once(child, 'exit');
  const log = (bytes) => {
    logs += bytes.toString();
    url ||= /server listening on (http:\/\/[^\s]+)/.exec(logs)?.[1];
    password ||= /server password (\S+)/.exec(logs)?.[1];
  };
  child.stdout.on('data', log); child.stderr.on('data', log);
  for (let i = 0; i < 300 && (!url || !password); i++) {
    assert.equal(child.exitCode, null, 'the probe server exited before it started'); await sleep(100);
  }
  assert(url && password, 'the probe server must print its URL and password');
  const headers = { Authorization: `Basic ${Buffer.from(`opencode:${password}`).toString('base64')}` };
  const request = async (route, body) => {
    const r = await fetch(url + route, { headers: { ...headers, ...(body === undefined ? {} : { 'Content-Type': 'application/json' }) }, method: body === undefined ? 'GET' : 'POST', ...(body === undefined ? {} : { body: JSON.stringify(body) }), signal: AbortSignal.timeout(15000) });
    assert.equal(r.status, 200, `HTTP status for ${route}`); return r.json();
  };
  const schemaText = await (await fetch(url + '/openapi.json', { headers, signal: AbortSignal.timeout(15000) })).text();
  const schema = JSON.parse(schemaText);
  const wanted = /^(Session\.Info|Session\.Message\.(Assistant|User|Idle|ToolState\.\w+)|Session\.StructuredError|Permission\.(Rule|Request|Source|Effect)|Agent\.Info|Model\.(Info|Ref|Variant)|TokenUsage\.Info|SessionTransfer\.Data|SessionInterruptResponse)$/;
  save('schema-selected.json', { openapiSHA256: sha(schemaText), version: schema.info?.version,
    paths: Object.keys(schema.paths), schemas: Object.fromEntries(Object.entries(schema.components.schemas).filter(([k]) => wanted.test(k))) });
  const timeline = []; let agents; let models; let selected;
  const started = Date.now();
  for (let i = 0; i < 150 && Date.now() - started < 30000; i++) {
    agents = await request('/api/agent'); models = await request('/api/model');
    selected = models.data.find((m) => m.providerID === providerID && m.id === modelName && m.enabled && (!variant || m.variants.some((v) => v.id === variant)));
    timeline.push({ elapsedMs: Date.now() - started, agents: agents.data.map((a) => a.id), selectedModelReady: Boolean(selected) });
    if (agents.data.some((a) => a.id === 'build') && selected) break;
    await sleep(200);
  }
  save('readiness.json', timeline);
  assert(selected, `${modelId}${variant ? '#' + variant : ''} must be advertised without generation (is its key in the environment?)`);
  // Whitelisted: an agent's request headers and body can hold secrets.
  save('agents.json', { location: agents.location, data: agents.data.map(({ request: _r, ...a }) => ({ ...a, request: { headers: {}, body: {}, settings: {} } })) });
  const projectModel = (m) => ({ id: m.id, modelID: m.modelID, providerID: m.providerID, family: m.family, enabled: m.enabled, variants: m.variants.map((v) => ({ id: v.id })) });
  save('models.json', { location: models.location, data: models.data.filter((m) => m.providerID === providerID).map(projectModel), projection: 'request settings and other providers left out' });
  save('model-source.json', { sha256: sha(JSON.stringify(models)), projection: 'full response hash only; request fields may hold secrets' });
  eventAbort = new AbortController(); const events = [];
  const response = await fetch(url + '/api/event', { headers, signal: eventAbort.signal }); assert.equal(response.status, 200);
  eventTask = (async () => {
    const decoder = new TextDecoder(); let buffer = '';
    for await (const chunk of response.body) {
      buffer += decoder.decode(chunk, { stream: true });
      let end;
      while ((end = buffer.indexOf('\n\n')) >= 0) { events.push(buffer.slice(0, end)); buffer = buffer.slice(end + 2); }
    }
  })().catch((e) => { if (!eventAbort.signal.aborted) throw e; });
  const model = { id: selected.id, providerID: selected.providerID, ...(variant ? { variant } : {}) };
  const created = await request('/api/session', { title: 'harness-probe-owned-empty-never-prompted', agent: 'build', model, location: { directory: cwd } });
  const sid = created.data.id; save('session-create.json', created);
  save('session-list-api.json', await request(`/api/session?directory=${encodeURIComponent(cwd)}`));
  save('session-get-api.json', await request(`/api/session/${sid}`));
  save('session-export-api.json', await request(`/api/experimental/session/${sid}/export`));
  save('messages.json', await request(`/api/session/${sid}/message`));
  save('permissions.json', await request(`/api/session/${sid}/permission`));
  const interrupted = await request(`/api/session/${sid}/interrupt`, {}); save('interrupt.json', interrupted);
  assert.equal(interrupted.interrupted, false, 'interrupting an idle owned session is a no-op');
  const listedCli = cli(['session', 'list', '--standalone', '--format', 'json']); save('session-list-cli.json', listedCli); assert.equal(listedCli.code, 0);
  const exported = cli(['session', 'export', '--standalone', sid]); save('session-export-cli.json', exported); assert.equal(exported.code, 0);
  const exportRecord = JSON.parse(exported.stdout); assert.equal(exportRecord.info.id, sid); assert.deepEqual(exportRecord.messages, []);
  assert.equal(exportRecord.info.cost, 0); assert.deepEqual(exportRecord.info.tokens, { input: 0, output: 0, reasoning: 0, cache: { read: 0, write: 0 } });
  // The v1 commands the 1.18 harness used, against this v2 binary: each must fail, and fail on its syntax.
  const old = {
    modelsProvider: cli(['models', providerID]),
    modelsVerbose: cli(['models', providerID, '--verbose']),
    topLevelExport: cli(['export', sid]),
    runDir: cli(['run', '--dir', cwd, '--model', 'harness-probe-none/none', '--title', 'never', 'never sent']),
    runVariant: cli(['run', '--standalone', '--model', 'harness-probe-none/none', '--variant', 'high', '--title', 'never', 'never sent']),
  };
  // Not re-run: the 1.18 lookup `session list --format json -n 20` SUCCEEDS on v2, through the managed
  // background service (`serve --service`), which it starts when none runs; run-EFh0VF/old-commands.json
  // recorded it once. The harness never takes that route (#262).
  save('old-commands.json', old);
  for (const [name, r] of Object.entries(old)) assert.notEqual(r.code, 0, `old v1 command ${name} must fail on v2`);
  for (let i = 0; i < 30 && !events.some((e) => e.includes(sid)); i++) await sleep(100);
  eventAbort.abort(); await eventTask;
  save('events.sse', events.join('\n\n') + '\n\n');
  assert(events.some((e) => e.includes(sid)), 'native events must name the owned empty session');
  lifecycle.sessionID = sid; lifecycle.zeroUsage = true;
  lifecycle.schemaSHA256 = sha(schemaText);
} finally {
  eventAbort?.abort(); if (eventTask) await eventTask;
  if (child && child.exitCode === null) { child.kill('SIGTERM'); await Promise.race([exited, sleep(5000)]); }
  if (child && child.exitCode === null && child.signalCode === null) { child.kill('SIGKILL'); await exited; }
  lifecycle.ownedExit = child?.exitCode; lifecycle.ownedSignal = child?.signalCode;
  if (url) {
    try { await fetch(url + '/api/info', { signal: AbortSignal.timeout(1500) }); lifecycle.ownedEndpointUnavailable = false; }
    catch { lifecycle.ownedEndpointUnavailable = true; }
  }
  lifecycle.unrelatedAfter = await (await fetch(unrelatedURL)).text(); unrelated.close();
  save('lifecycle.json', lifecycle);
  // Only the redacted server log: the generated password never reaches a file.
  save('serve-redacted.log', logs.replaceAll(password || '\0', '[REDACTED]'));
  save('manifest.json', { evidence: 'observed non-billing OpenCode 2 protocol; no run, prompt or generate', binary: cmd.exe,
    binarySHA256: sha(fs.readFileSync(cmd.exe)), probeSHA256: sha(fs.readFileSync(new URL(import.meta.url))), model: { modelId, variant: variant ?? null }, artifacts });
  fs.rmSync(home, { recursive: true, force: true }); // the throwaway database, not evidence
}
assert(child?.exitCode !== null || child?.signalCode !== null, 'the probe server must exit');
assert(lifecycle.ownedEndpointUnavailable, 'the probe endpoint must be gone after shutdown');
assert.equal(lifecycle.unrelatedAfter, lifecycle.unrelatedBefore);
console.log(`Protocol probe passed; artefacts in ${run}`);
