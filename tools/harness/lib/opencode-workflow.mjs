// One OpenCode 2 run, owned end to end (#262; ported from goal2 PR 178's opencode-workflow.mjs and
// adapted to this repository's scratch folders, heavy-job queue and brief handling). Verdict parsing
// stays in review.mjs; this module returns the complete final text from the session export.
//
//   1. The worktree is at the exact PR head before anything starts (reviewedHead), else nothing runs.
//   2. The binary is the audited native 2.0.28 (lib/opencode-guard.mjs pinGuardBinary); the reviewer's
//      permissions come from the launching checkout (lib/opencode-policy.mjs), never from the PR.
//   3. The harness starts its OWN private server (`serve --stdio`, lib/opencode-transport.mjs), never
//      the managed background service, with the trusted profile and the shell-operand guard
//      (tools/harness/opencode-guard) staged. Before any generation: the selected model, its effort and
//      its family are advertised; the reviewer the server loaded matches the trusted rules; only builtin
//      plugins and the guard are active; the provider catalogue matches a guard-free baseline.
//   4. A new session, unique to this run (not listed before, our title, created after we started), is
//      created with the exact model, effort, agent and directory; then `opencode run --server <ours>
//      --session <it>` sends the one-line pointer to the brief file.
//   5. Watch: the total deadline; the idle limit on the session's `updated` time, or the later touch of
//      the heavy-job queue file (#318: queue time is not idle time); the server staying alive; the plugin
//      inventory staying the same.
//   6. On every outcome, the complete export decides: identity (session, directory, agent, model,
//      effort), a complete final assistant turn, no rejected tool call, usage. A failure interrupts only
//      this session at this server, recovers the export, then closes this server's lease; another
//      session or service is never touched.
//   7. Everything is retained before cleanup, under <logDir>/<title>-*/: stdout, stderr, the raw export
//      response, the export, final.txt, the brief, the loaded profile and model, plugins, the baseline,
//      the guard's evidence and run.json (identities, hashes, phase, usage, duration). The only text
//      redacted is the server's own generated password, if anything echoed it.
import fs from 'node:fs';
import path from 'node:path';
import { randomBytes } from 'node:crypto';
import { command, normalizeSession, usage } from './opencode-protocol.mjs';
import { privateHome, startPrivateServer, settledCatalogue, capture, spawnOwned, killOwned, delay, hash, OpenCodeInfraError } from './opencode-transport.mjs';
import { reviewerPolicy, trustedReviewEnv, verifyReviewer } from './opencode-policy.mjs';
import { stageGuard, baselinePlugins, readyPlugins, verifyPlugins, selectGuardPlugins, pinGuardBinary, inspectConfig, catalogueParity } from './opencode-guard.mjs';
import { harnessDir, scratchRoot, writeFresh } from './scratch.mjs';

const json = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
const touched = (file) => { try { return fs.statSync(file).mtimeMs; } catch { return 0; } };

// The text of the last assistant message: the review (an earlier message's text is working notes).
export function finalReviewText(normalized) {
  const last = normalized.messages.filter((m) => m.type === 'assistant').at(-1);
  return last?.parts.filter((p) => p.type === 'text').map((p) => p.text).join('') ?? '';
}
// The rejected tool calls of a complete export, named for the failure message.
export function rejectedCalls(normalized) {
  return normalized.messages.filter((m) => m.type === 'assistant').flatMap((m) => m.parts)
    .filter((p) => p.type === 'tool' && p.rejected)
    .map((p) => `${p.name} ${JSON.stringify(p.input).slice(0, 160)}: ${p.error?.type ?? ''} ${String(p.error?.message ?? '').slice(0, 160)}`.trim());
}

export async function runV2Workflow({ opencode, model, agent, agentFile, prompt, workDir, title, sessionId, resumeManifest, reviewedHead, reviewPR,
  startupTimeoutMs = 180000, totalTimeoutMs = 3600000, idleTimeoutMs = 600000, pollMs = 10000, logDir, env = process.env, log = () => {}, queueFile = null }) {
  if (!agentFile) throw new OpenCodeInfraError('selection', 'requires the explicit trusted agentFile');
  if (typeof agent !== 'string' || !agent) throw new OpenCodeInfraError('selection', 'requires the exact selected agent');
  workDir = fs.realpathSync(workDir);
  if (reviewedHead) {
    const proof = await capture({ exe: 'git', prefix: [] }, ['rev-parse', 'HEAD'], { cwd: workDir, env, timeoutMs: 5000 });
    if (proof.code !== 0 || proof.stdout.trim() !== reviewedHead) throw new OpenCodeInfraError('head', 'review worktree differs from exact PR head before billing');
  }
  const transportIdentity = pinGuardBinary(opencode);
  const policy = reviewerPolicy(agentFile); let previous;
  if (sessionId) {
    if (!resumeManifest) throw new OpenCodeInfraError('ownership', 'v2 resume requires its retained run manifest');
    previous = JSON.parse(fs.readFileSync(resumeManifest, 'utf8'));
    if (previous.major !== 2 || previous.sessionID !== sessionId || previous.directory !== workDir || previous.agent !== agent || JSON.stringify(previous.model) !== JSON.stringify(model) || previous.phase === 'running') throw new OpenCodeInfraError('ownership', 'resume manifest identity differs from this run');
  }
  const home = privateHome(env, { resumeRoot: previous?.dataRoot });
  const guard = stageGuard(home.root, policy);
  const baseEnv = trustedReviewEnv(home.env, policy, agent, guard, { baseline: true });
  let runEnv;
  const runTitle = `${title}-${randomBytes(6).toString('hex')}`;
  const logRoot = path.resolve(logDir ?? harnessDir(scratchRoot(env)));
  fs.mkdirSync(logRoot, { recursive: true });
  const artifactRoot = fs.mkdtempSync(path.join(logRoot, `${runTitle}-`));
  const files = Object.fromEntries(['stdout.txt', 'stderr.txt', 'export-response.json', 'export.json', 'final.txt', 'assistant.txt', 'profile.json', 'plugins.json', 'baseline.json', 'shell-guard.jsonl', 'model.json', 'openapi.raw.json', 'server.json', 'brief.md', 'run.json'].map((name) => [name, path.join(artifactRoot, name)]));
  // The brief: inside the worktree, where the agent's tools reach (L36/#501), written exclusively (#311);
  // its retained copy is brief.md, and the worktree's copy goes when the run ends (never left as work, #87).
  const briefFile = path.join(workDir, `.harness-brief-${runTitle}.md`);
  writeFresh(briefFile, prompt, { disk: false }); fs.writeFileSync(files['brief.md'], prompt);
  const pointer = `Your complete brief for this run is the file ${path.basename(briefFile)} at the root of this worktree.`
    + ' Read that file first and follow it exactly; never edit, commit or delete it.';
  const start = Date.now(); let server; let baseline; let client; let clientClosed = false; let exitCode = null; let spawnError; let normalized; let raw; let failure;
  const manifest = { major: 2, ...(reviewedHead ? { reviewedHead, reviewPR } : {}), title: runTitle, directory: workDir, agent, model, dataRoot: home.root, dataHome: home.env.XDG_DATA_HOME, policySHA256: policy.sourceSHA256, transportIdentity, guard, command: { exe: opencode.exe, prefix: opencode.prefix }, binarySHA256: hash(fs.readFileSync(opencode.binary ?? opencode.exe)), sourceSHA256: hash(fs.readFileSync(new URL(import.meta.url))), sources: Object.fromEntries(['opencode.mjs', 'opencode-workflow.mjs', 'opencode-transport.mjs', 'opencode-policy.mjs', 'opencode-guard.mjs', 'opencode-protocol.mjs', '../review.mjs'].map((name) => [name, hash(fs.readFileSync(new URL(name, import.meta.url)))])), phase: 'preflight', started: start, files, briefFile };
  const persist = () => {
    json(files['run.json'], server ? JSON.parse(server.redact(JSON.stringify(manifest))) : manifest);
    // A per-run receipt index lets peek find a bare session id's run, its major and data root.
    const index = path.join(home.root, 'receipts'); fs.mkdirSync(index, { recursive: true });
    json(path.join(index, `${runTitle}.json`), { manifest: files['run.json'], sessionID: manifest.sessionID });
  };
  persist(); log(`opencode: manifest ${files['run.json']}`);
  const left = () => Math.max(1, totalTimeoutMs - (Date.now() - start));
  const startupLeft = () => Math.max(1, Math.min(startupTimeoutMs - (Date.now() - start), left()));
  const expected = () => ({ sessionID: manifest.sessionID, directory: workDir, agent, model: { providerID: model.id.split('/')[0], id: model.id.slice(model.id.indexOf('/') + 1), ...(model.variant ? { variant: model.variant } : {}) } });
  const exportFinal = async () => {
    const result = await server.request(`/api/experimental/session/${manifest.sessionID}/export`, { timeoutMs: 5000, outFile: files['export-response.json'] });
    raw = JSON.parse(server.redact(JSON.stringify(result.data))); json(files['export.json'], raw);
    // The session's own usage counts even when the export is not a complete turn (a cancelled run's
    // assistant message never finished, and normalizeSession refuses it below).
    try { manifest.usage = { cost: raw.info.cost, tokens: usage(raw.info.tokens), source: 'session info' }; } catch (e) { manifest.usageError = e.message; }
    normalized = normalizeSession(2, raw, expected());
    fs.writeFileSync(files['assistant.txt'], normalized.assistantText);
    fs.writeFileSync(files['final.txt'], finalReviewText(normalized));
    manifest.usage = { cost: normalized.cost, tokens: normalized.tokens }; manifest.completed = normalized.completed; manifest.rejected = normalized.rejected;
  };
  try {
    baseline = await baselinePlugins(opencode, { env: baseEnv, cwd: workDir, guard, retain: true, timeoutMs: startupLeft() });
    json(files['baseline.json'], baseline);
    selectGuardPlugins(guard, baseline.plugins.map((p) => p.id), files['shell-guard.jsonl']);
    runEnv = trustedReviewEnv(home.env, policy, agent, guard);
    server = await startPrivateServer(opencode, { env: runEnv, cwd: workDir, timeoutMs: startupLeft(), log });
    manifest.config = inspectConfig(await server.request('/api/config', { timeoutMs: left() }), guard);
    await server.request('/openapi.json', { timeoutMs: startupLeft(), outFile: files['openapi.raw.json'] });
    manifest.schemaSHA256 = hash(fs.readFileSync(files['openapi.raw.json']));
    const found = await settledCatalogue(server, { timeoutMs: startupLeft(), model, agent, verifyAgent: (profile) => verifyReviewer(profile, policy, agent) });
    const plugins = await readyPlugins(server, guard, { timeoutMs: startupLeft() });
    json(files['plugins.json'], plugins);
    baseline.models = await catalogueParity(baseline.server, server, { timeoutMs: startupLeft() });
    baseline.shutdown = await baseline.server.stop();
    json(files['baseline.json'], baseline);
    baseline = null;
    json(files['profile.json'], { id: found.profile.id, mode: found.profile.mode, hidden: found.profile.hidden, system: found.profile.system, permissions: found.profile.permissions });
    json(files['model.json'], { id: found.selected.id, modelID: found.selected.modelID, providerID: found.selected.providerID, family: found.selected.family, variants: found.selected.variants.map((v) => v.id), enabled: found.selected.enabled });
    let info;
    if (sessionId) {
      info = (await server.request(`/api/session/${sessionId}`, { timeoutMs: left() })).data;
      manifest.sessionID = sessionId;
    } else {
      const before = await server.request('/api/session', { timeoutMs: left() });
      const occupied = new Set(before.data.map((s) => s.id));
      info = (await server.request('/api/session', { body: { title: runTitle, agent, model: expected().model, location: { directory: workDir } }, timeoutMs: left() })).data;
      if (!info || occupied.has(info.id) || info.title !== runTitle || info.time?.created < start - 1000) throw new OpenCodeInfraError('ownership', 'new session is not unique to this invocation');
      manifest.sessionID = info.id;
    }
    // The stored selection is checked only after the effective profile was verified on its own.
    normalizeSession(2, { info, messages: [] }, expected());
    if (Date.now() - start >= totalTimeoutMs) throw new OpenCodeInfraError('total-timeout', 'total deadline before generation');
    persist(); log(`opencode: session ${manifest.sessionID} started; manifest ${files['run.json']}`);
    const args = command(2, 'run', { directory: workDir, agent, model: expected().model, sessionID: manifest.sessionID, prompt: pointer }).args;
    args.splice(1, 1, '--server', server.url);
    const out = fs.openSync(files['stdout.txt'], 'w'); const err = fs.openSync(files['stderr.txt'], 'w');
    try { client = spawnOwned(opencode, args, { cwd: workDir, env: server.clientEnv, stdio: ['ignore', out, err] }); } finally { fs.closeSync(out); fs.closeSync(err); }
    client.on('error', (e) => { spawnError = e; clientClosed = true; });
    client.on('close', (code, signal) => { exitCode = code ?? (signal ? 128 : 1); clientClosed = true; });
    manifest.phase = 'running'; manifest.clientPID = client.pid; manifest.serverPID = server.child.pid; persist();
    let updated = Math.max(info.time.updated, Date.now());
    while (!clientClosed) {
      await delay(Math.max(1, Math.min(pollMs, idleTimeoutMs > 0 ? Math.max(10, idleTimeoutMs / 5) : pollMs, left())));
      if (Date.now() - start >= totalTimeoutMs) throw new OpenCodeInfraError('total-timeout', 'total deadline; cancelling owned session');
      if (clientClosed) break;
      if (!server.isAlive()) throw new OpenCodeInfraError('server-exit', 'owned execution server exited');
      verifyPlugins((await server.request('/api/plugin', { timeoutMs: Math.min(5000, left()) })).data, guard);
      const state = (await server.request(`/api/session/${manifest.sessionID}`, { timeoutMs: Math.min(5000, left()) })).data;
      normalizeSession(2, { info: state, messages: [] }, expected());
      if (state.time.updated > updated) { updated = state.time.updated; log(`opencode: session ${manifest.sessionID} progress`); }
      // Time a reviewer's command waits for a heavy-job slot is not idleness (#318): heavy.sh touches the file.
      const queued = queueFile ? touched(queueFile) : 0;
      if (queued > updated) updated = queued;
      if (idleTimeoutMs > 0 && Date.now() - updated >= idleTimeoutMs) throw new OpenCodeInfraError('idle', `session idle for ${Math.round(idleTimeoutMs / 1000)} s; cancelling owned session`);
    }
    if (spawnError) throw new OpenCodeInfraError('spawn', `could not start private client: ${spawnError.message}`);
    await exportFinal();
    if (exitCode !== 0) throw new OpenCodeInfraError('non-zero-exit', `exit ${exitCode}`);
    if (!normalized.completed) throw new OpenCodeInfraError('incomplete', 'export has no complete final assistant outcome');
    if (normalized.rejected) throw new OpenCodeInfraError('permission-rejected', `permission rejected in complete session export: ${rejectedCalls(normalized).join('; ')}`);
    manifest.phase = 'complete';
  } catch (error) {
    failure = Date.now() - start >= totalTimeoutMs ? new OpenCodeInfraError('total-timeout', 'total deadline; cancelling owned session')
      : error instanceof OpenCodeInfraError ? error : new OpenCodeInfraError('protocol', error.message);
    manifest.phase = 'failed'; manifest.failure = { reason: failure.reason, message: failure.message };
    // Interrupt only this session at this owned endpoint, then recover its export before closing the lease.
    if (server?.isAlive() && manifest.sessionID) {
      try { manifest.interrupt = await server.request(`/api/session/${manifest.sessionID}/interrupt`, { body: {}, timeoutMs: 2000 }); } catch (e) { manifest.interruptError = e.message; }
      if (!raw) try { await exportFinal(); } catch (e) { manifest.exportError = e.message; }
    }
  } finally {
    if (baseline?.server) { baseline.shutdown = await baseline.server.stop(); json(files['baseline.json'], baseline); }
    if (server) try { json(files['server.json'], await server.stop()); } catch (e) { manifest.shutdownError = e.message; failure ||= e; }
    if (client && !clientClosed) {
      for (let i = 0; i < 20 && !clientClosed; i++) await delay(25);
      if (!clientClosed) { killOwned(client); for (let i = 0; i < 20 && !clientClosed; i++) await delay(25); }
      if (!clientClosed) { failure ||= new OpenCodeInfraError('shutdown', 'owned client did not exit'); manifest.phase = 'failed'; }
    }
    if (client) { killOwned(client); await delay(25); }
    fs.rmSync(briefFile, { force: true }); // retained as brief.md
    // The server's generated password is removed even where a child echoed it in split chunks.
    if (server) for (const file of Object.values(files).filter((f) => f !== files['run.json'])) if (fs.existsSync(file)) fs.writeFileSync(file, server.redact(fs.readFileSync(file, 'utf8')));
    if (server) {
      manifest.redactions = ['known generated owned-server transport nonce; no other text omitted'];
      if (failure) failure.message = server.redact(failure.message);
    }
    manifest.exitCode = exitCode; manifest.finished = Date.now(); manifest.durationMs = manifest.finished - start;
    manifest.artifactSHA256 = Object.fromEntries(Object.values(files).filter((f) => f !== files['run.json'] && fs.existsSync(f)).map((f) => [path.basename(f), hash(fs.readFileSync(f))]));
    persist();
  }
  const kept = Object.values(files).filter((f) => fs.existsSync(f));
  if (failure) {
    failure.message = `${failure.message}; files kept: ${artifactRoot} (run.json)`;
    throw Object.assign(failure, { sessionId: manifest.sessionID, manifest: files['run.json'], files: kept });
  }
  log(`opencode: complete; files kept: ${artifactRoot}`);
  const stdout = fs.readFileSync(files['stdout.txt'], 'utf8'); const stderr = fs.readFileSync(files['stderr.txt'], 'utf8');
  return { stdout, stderr, output: `${stdout.trimEnd()}\n${stderr.trimEnd()}`.trim(), reviewText: finalReviewText(normalized), exitCode, sessionId: manifest.sessionID, title: runTitle, agentFallback: false, sessionAgent: normalized.agent, permissionRejected: null, permissionHint: null, files: kept, briefFile: files['brief.md'], manifest: files['run.json'], normalized, seconds: Math.round(manifest.durationMs / 1000) };
}
