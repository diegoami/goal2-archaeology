// #262: the OpenCode 2 run (lib/opencode-workflow.mjs through lib/opencode.mjs runOpenCodeWatched), its
// transport, peek and the review CLI, against tests/helpers/opencode-stub.mjs: a nonbilling simulator of
// the v2 CLI and API with v2-shaped records (and the 1.18 commands for the explicit v1 path). Ported
// from goal2 PR 178's tests/opencode_workflow.test.mjs and adapted to this repository. No model is
// called and no provider is reached; the stub is admitted only inside node --test, by its hash.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn, spawnSync } from 'node:child_process';

const { capture, killOwned, delay, startPrivateServer, privateHome, catalogueFamily } = await import(process.env.WF_TRANSPORT_MODULE || '../tools/harness/lib/opencode-transport.mjs');
const { runOpenCodeWatched, resolveOpenCode } = await import(process.env.WF_OPENCODE_MODULE || '../tools/harness/lib/opencode.mjs');
const { findReceipt, peekRecord, renderPeek } = await import(process.env.WF_PEEK_MODULE || '../tools/harness/lib/opencode-peek.mjs');
const agentFile = fileURLToPath(new URL('../.opencode/agents/reviewer.md', import.meta.url));
const stub = fileURLToPath(new URL('./helpers/opencode-stub.mjs', import.meta.url));
const REPO = fileURLToPath(new URL('..', import.meta.url));
const selection = { id: 'minimax/MiniMax-M3', family: 'minimax', variant: 'thinking' };
const stat = (pid) => `/proc/${pid}/stat`;
const gone = (pid) => !fs.existsSync(stat(pid)) || fs.readFileSync(stat(pid), 'utf8').split(' ')[2] === 'Z';

function workflowOptions(mode = 'complete') {
  const dir = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'harness-workflow-')));
  return { args: ['run'], model: selection, agent: 'reviewer', agentFile,
    opencode: { exe: process.execPath, prefix: [stub] }, prompt: 'Synthetic nonbilling brief', workDir: dir, title: 'stub',
    startupTimeoutMs: mode === 'startup' ? 700 : 4000, totalTimeoutMs: 8000, idleTimeoutMs: 350, pollMs: 20, logDir: path.join(dir, 'receipts'),
    env: { ...process.env, HARNESS_OPENCODE_HOME: path.join(dir, 'runtime'), STUB_MODE: mode, STUB_TRACE: path.join(dir, 'trace.jsonl') } };
}
const traceOf = (options) => (fs.existsSync(options.env.STUB_TRACE) ? fs.readFileSync(options.env.STUB_TRACE, 'utf8') : '');

test('capture kills an exited leader\'s descendants at its deadline; an unrelated process survives', async () => {
  if (process.platform === 'win32') return;
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-pipes-'));
  const fixture = path.join(scratch, 'leader.mjs'); const pidFile = path.join(scratch, 'descendant.pid');
  fs.writeFileSync(fixture, `import {spawn} from 'node:child_process'; import fs from 'node:fs';
const child=spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{stdio:'inherit'});
fs.writeFileSync(${JSON.stringify(pidFile)},String(child.pid)); child.unref();
process.exit(0);
`);
  const sentinel = spawn(process.execPath, ['-e', 'setInterval(()=>{},1000)'], { detached: true, stdio: 'ignore' });
  try {
    const start = Date.now(); const result = await capture({ exe: process.execPath, prefix: [] }, [fixture], { timeoutMs: 100 });
    assert(Date.now() - start < 1000, 'descendant-held pipes must settle within the bounded deadline');
    assert.equal(result.timedOut, true); assert.notEqual(result.code, 0);
    const descendant = Number(fs.readFileSync(pidFile, 'utf8'));
    await delay(25);
    assert(gone(descendant), 'owned descendant must terminate even after leader exit');
    assert.equal(sentinel.exitCode, null); process.kill(sentinel.pid, 0);
  } finally {
    killOwned(sentinel);
    if (fs.existsSync(pidFile)) try { process.kill(Number(fs.readFileSync(pidFile, 'utf8')), 'SIGKILL'); } catch { /* gone */ }
    await delay(25);
  }
});

test('the server\'s generated password, split across chunks, is redacted from what stop returns and from startup errors', async () => {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-redaction-'));
  const fixture = path.join(scratch, 'server.mjs');
  fs.writeFileSync(fixture, `const key=process.env.OPENCODE_PASSWORD;
if(!process.env.NO_READY) console.log(JSON.stringify({url:'http://127.0.0.1:4321'}));
process.stderr.write('NONCE='+key.slice(0,20));
if(!process.env.NO_READY) process.stdout.write(key.slice(0,20));
setTimeout(()=>{process.stderr.write(key.slice(20));if(!process.env.NO_READY)process.stdout.write(key.slice(20));},70);
process.stdin.resume();process.stdin.on('end',()=>setTimeout(()=>process.exit(0),100));
`);
  const cmd = { exe: process.execPath, prefix: [fixture] };
  const server = await startPrivateServer(cmd, { env: process.env, cwd: scratch, timeoutMs: 500 });
  const nonce = server.clientEnv.OPENCODE_PASSWORD; await delay(100);
  const stopped = await server.stop();
  assert.equal(stopped.stdout.includes(nonce), false); assert.equal(stopped.stderr.includes(nonce), false);
  assert.equal(stopped.stderr.includes('NONCE=[REDACTED]'), true);
  await assert.rejects(() => startPrivateServer(cmd, { env: { ...process.env, NO_READY: '1' }, cwd: scratch, timeoutMs: 200 }), (error) => {
    assert.equal(error.message.includes('NONCE=[REDACTED]'), true, 'startup error must redact the generated password');
    return true;
  });
});

test('a v2 run recovers the complete final text, usage and receipts from the export; a resume keeps its session', async () => {
  const options = workflowOptions(); const logs = []; options.log = (line) => logs.push(line);
  const result = await runOpenCodeWatched(options);
  assert.equal(result.reviewText, 'Complete recovered final\nFinal pass done\napprove\n');
  assert.doesNotMatch(result.stdout, /Complete recovered final/, 'the console never decides');
  assert.equal(result.normalized.tokens.input, 10); assert.equal(result.normalized.cost, 0.002);
  assert.equal(result.normalized.messages[0].parts.filter((p) => p.type === 'tool').length, 1);
  const receipt = JSON.parse(fs.readFileSync(result.manifest));
  assert.equal(receipt.phase, 'complete'); assert.equal(receipt.completed, true); assert.deepEqual(receipt.usage.tokens.cache, { read: 3, write: 1 });
  assert(receipt.guard?.sourceSHA256, 'the operand guard is pinned before generation');
  assert.equal(receipt.binarySHA256.length, 64); assert.equal(receipt.policySHA256.length, 64);
  assert(result.manifest.startsWith(options.logDir + path.sep), 'receipts are kept under logDir');
  for (const name of ['stdout.txt', 'stderr.txt', 'export-response.json', 'export.json', 'final.txt', 'brief.md', 'profile.json', 'model.json', 'plugins.json', 'baseline.json']) {
    assert(fs.existsSync(receipt.files[name]), name);
    if (name !== 'run.json') assert.equal(createHash('sha256').update(fs.readFileSync(receipt.files[name])).digest('hex'), receipt.artifactSHA256[name], name);
  }
  assert.equal(fs.readFileSync(receipt.files['final.txt'], 'utf8'), result.reviewText);
  assert.equal(fs.readFileSync(receipt.files['brief.md'], 'utf8'), options.prompt);
  assert.deepEqual(fs.readdirSync(options.workDir).filter((f) => f.startsWith('.harness-brief-')), [], 'the brief leaves the worktree; brief.md keeps it');
  assert(logs.some((line) => line.includes(`session ${result.sessionId} started`)), 'the log names the session (peek.sh reads it)');
  const noEffort = await runOpenCodeWatched({ ...options, model: { id: selection.id, family: selection.family } });
  assert.equal(noEffort.normalized.model.variant, undefined, 'absent effort stays absent instead of a default variant');
  const independent = await runOpenCodeWatched(options);
  assert.notEqual(independent.sessionId, result.sessionId);
  assert.equal(JSON.parse(fs.readFileSync(independent.manifest)).dataHome, receipt.dataHome, 'one v2 provider DB for distinct owned runs');
  const resumed = await runOpenCodeWatched({ ...options, sessionId: result.sessionId, resumeManifest: result.manifest });
  assert.equal(resumed.sessionId, result.sessionId); assert.notEqual(resumed.manifest, result.manifest);
  assert.equal(JSON.parse(fs.readFileSync(resumed.manifest)).dataRoot, receipt.dataRoot);
  await assert.rejects(() => runOpenCodeWatched({ ...options, sessionId: result.sessionId }), /retained run manifest/);
  await assert.rejects(() => runOpenCodeWatched({ ...options, sessionId: result.sessionId, resumeManifest: result.manifest, model: { ...selection, variant: 'none' } }), /resume manifest identity/);
  const trace = traceOf(options).trim().split('\n').map(JSON.parse);
  assert(trace.every((t) => !t.args || !['--dir', '--variant'].some((f) => t.args.includes(f))), 'no v1 flag reaches the v2 CLI');
  assert(trace.filter((t) => t.args?.[0] === 'run').every((t) => t.args.includes('--server') && !t.args.includes('--standalone')), 'the client attaches to our own server');
  assert(trace.filter((t) => t.args?.[0] === 'serve').every((t) => t.args.includes('--stdio')), 'only private stdio servers are started');
  assert(trace.filter((t) => t.dataHome).every((t) => t.dataHome.includes(`${path.sep}v2${path.sep}data`)), 'v2 never opens the legacy v1 data directory');
});

test('the heavy-job queue file keeps the idle clock from firing while a command waits (#318)', async () => {
  const options = workflowOptions('idle');
  const queueFile = path.join(options.workDir, 'run.queue'); fs.writeFileSync(queueFile, '');
  const toucher = setInterval(() => { const t = new Date(); fs.utimesSync(queueFile, t, t); }, 50);
  options.idleTimeoutMs = 300; options.totalTimeoutMs = 2500; options.queueFile = queueFile;
  try {
    await assert.rejects(() => runOpenCodeWatched(options), (e) => { assert.equal(e.reason, 'total-timeout', e.message); return true; });
  } finally { clearInterval(toucher); }
  const idle = workflowOptions('idle'); idle.idleTimeoutMs = 300; idle.totalTimeoutMs = 2500; idle.queueFile = path.join(idle.workDir, 'none.queue');
  await assert.rejects(() => runOpenCodeWatched(idle), (e) => { assert.equal(e.reason, 'idle', e.message); return true; });
});

test('discovery fails before generation on the chosen family, effort, agent or loaded policy', async () => {
  for (const mode of ['family', 'effort', 'agent', 'policy']) {
    const options = workflowOptions(mode); options.startupTimeoutMs = 1500;
    await assert.rejects(() => runOpenCodeWatched(options), (e) => { assert.equal(e.reason, 'preflight', `${mode}: ${e.message}`); return true; });
    assert.doesNotMatch(traceOf(options), /generation/, mode);
  }
});

test('export identity, rejection, completion and JSON checks refuse approval-looking outcomes, with receipts kept', async () => {
  const cases = { 'wrong-session': 'session mismatch', 'wrong-directory': 'directory mismatch', 'wrong-model': 'model mismatch', 'wrong-agent': 'agent mismatch', 'wrong-effort': 'effort mismatch', malformed: 'malformed assistant text', truncated: 'invalid JSON', partial: 'complete final', pending: 'complete final', rejected: 'permission rejected in complete session export: shell', nonzero: 'exit 7' };
  for (const [mode, expected] of Object.entries(cases)) {
    await assert.rejects(() => runOpenCodeWatched(workflowOptions(mode)), (e) => {
      assert.match(e.message, new RegExp(expected), mode); assert(fs.existsSync(e.manifest), mode);
      assert.match(e.message, /files kept: /, mode);
      const receipt = JSON.parse(fs.readFileSync(e.manifest)); assert.equal(receipt.phase, 'failed', mode);
      assert(fs.existsSync(receipt.files['export-response.json']), mode); return true;
    });
  }
});

test('startup, idle and total limits end with a failure receipt; an unrelated server and its session survive', async () => {
  const sentinel = await startPrivateServer({ exe: process.execPath, prefix: [stub] }, { env: { ...process.env, XDG_DATA_HOME: fs.mkdtempSync(path.join(os.tmpdir(), 'harness-sentinel-')), OPENCODE_CONFIG_CONTENT: '{}' }, cwd: os.tmpdir(), timeoutMs: 700 });
  try {
    for (const [mode, reason] of [['startup', 'startup'], ['idle', 'idle'], ['total', 'total-timeout']]) {
      const options = workflowOptions(mode); if (mode === 'total') { options.totalTimeoutMs = 1500; options.idleTimeoutMs = 0; }
      await assert.rejects(() => runOpenCodeWatched(options), (e) => { assert.equal(e.reason, reason, e.message); assert(fs.existsSync(e.manifest)); return true; });
      assert.deepEqual((await sentinel.request('/api/session')).data, []);
    }
  } finally { await sentinel.stop(); }
});

test('cancelling interrupts only our session, ends our descendants, and leaves an unrelated server\'s session alone', async () => {
  const progress = workflowOptions('progress'); const logs = []; progress.log = (line) => logs.push(line);
  await runOpenCodeWatched(progress);
  assert(logs.some((line) => /session .* progress/.test(line)), 'the session\'s updated time drives progress');
  const active = workflowOptions('active'); let receipt;
  const otherHome = privateHome(active.env);
  const unrelated = await startPrivateServer(active.opencode, { env: { ...otherHome.env, OPENCODE_CONFIG_CONTENT: '{}' }, cwd: active.workDir, timeoutMs: 700 });
  const other = await unrelated.request('/api/session', { body: { title: 'unrelated', agent: 'reviewer', model: { providerID: 'minimax', id: 'MiniMax-M3', variant: 'thinking' }, location: { directory: active.workDir } } });
  let worker;
  try {
    await assert.rejects(() => runOpenCodeWatched(active), (error) => { assert.equal(error.reason, 'idle'); receipt = JSON.parse(fs.readFileSync(error.manifest)); return true; });
    assert.equal(receipt.completed, false); assert.equal(receipt.phase, 'failed'); assert.deepEqual(receipt.interrupt, { interrupted: true });
    const trace = traceOf(active).trim().split('\n').map(JSON.parse);
    assert(trace.some((entry) => entry.interrupt === receipt.sessionID), 'only our own session is interrupted');
    assert(!trace.some((entry) => entry.interrupt && entry.interrupt !== receipt.sessionID));
    worker = trace.find((entry) => entry.workerPID)?.workerPID; assert(worker);
    assert.deepEqual((await unrelated.request(`/api/session/${other.data.id}`)).data, other.data, 'an unrelated session on the same v2 DB survives');
    assert(gone(worker), 'our generation descendant terminates');
  } finally {
    await unrelated.stop();
    if (worker) try { process.kill(worker, 'SIGKILL'); } catch { /* gone */ }
  }
});

test('peek reads a finished run\'s retained export and a running one through a private export; it refuses a foreign session', async () => {
  const options = workflowOptions(); const result = await runOpenCodeWatched(options);
  const cmd = options.opencode; const receipt = findReceipt(result.sessionId, options.env);
  assert.equal(receipt.manifest, result.manifest);
  const record = await peekRecord(cmd, receipt, { env: options.env });
  assert.match(renderPeek(record, 2), /Complete recovered final/);
  assert.match(renderPeek(record, 2), /tool shell \[completed\]/);
  const live = { ...receipt, record: { ...receipt.record, phase: 'running' } };
  assert.deepEqual(await peekRecord(cmd, live, { env: options.env }), record, 'the live private export equals the retained one');
  assert(traceOf(options).includes('"session","export","--standalone"'), 'live peek uses a private standalone export');
  await assert.rejects(() => peekRecord(cmd, { record: { ...receipt.record, sessionID: 'ses_foreign' } }, { env: options.env }), /session mismatch/);
  assert.throws(() => findReceipt('not-a-session', options.env), /valid session/);
  assert.deepEqual(findReceipt('ses_unknown', options.env), { sessionID: 'ses_unknown' });
  const env = { ...options.env, HARNESS_OPENCODE_EXE: stub }; delete env.OPENCODE_BIN;
  for (const target of [result.manifest, result.sessionId]) {
    const viaSh = spawnSync('bash', [path.join(REPO, 'tools/harness/peek.sh'), target, '-n', '5'], { env, encoding: 'utf8' });
    assert.equal(viaSh.status, 0, viaSh.stderr); assert.match(viaSh.stdout, /tool shell \[completed\]/); assert.match(viaSh.stdout, /says: Complete recovered final/);
  }
  const unknown = spawnSync(process.execPath, [path.join(REPO, 'tools/harness/peek.mjs'), 'ses_unknown'], { env, encoding: 'utf8' });
  assert.equal(unknown.status, 1); assert.match(unknown.stderr, /no retained v2 run receipt/);
});

test('peek renders the schema\'s streaming and running tool states and refuses a malformed input', () => {
  const schema = JSON.parse(fs.readFileSync(new URL('fixtures/opencode/v2-live/run-3Ai73R/schema-selected.json', import.meta.url))).schemas;
  assert.equal(schema['Session.Message.ToolState.Streaming'].properties.input.type, 'string');
  assert.equal(schema['Session.Message.ToolState.Running'].properties.input.type, 'object');
  const record = { info: { title: 'synthetic', location: { directory: '/synthetic' } }, messages: [{ type: 'assistant', content: [
    { type: 'tool', id: 'stream', name: 'shell', state: { status: 'streaming', input: '{"command":' } },
    { type: 'tool', id: 'run', name: 'shell', state: { status: 'running', input: { command: 'pwd' }, metadata: {} } },
  ] }] };
  assert.match(renderPeek(record, 2), /tool shell \[streaming\]/); assert.match(renderPeek(record, 2), /tool shell \[running\]/);
  delete record.messages[0].content[1].state.input;
  assert.throws(() => renderPeek(record, 2), /malformed native tool state\/input/);
});

test('the explicit v1 path still runs the 1.18 commands, unchanged, and reports a rejected tool call', async () => {
  const options = workflowOptions(); const dir = options.workDir;
  options.env.STUB_VERSION = '1.18.34'; options.env.STUB_V1_DIR = dir;
  options.args = ['run', '--dir', dir, '--agent', 'reviewer', '--model', selection.id, '--variant', selection.variant];
  const result = await runOpenCodeWatched(options);
  assert.equal(result.exitCode, 0); assert.match(result.sessionId, /^ses_v1_/);
  assert.equal(result.reviewText, undefined, 'v1 keeps reading stdout, as before #262');
  const trace = traceOf(options).trim().split('\n').map(JSON.parse);
  assert(trace.some((t) => t.args?.[0] === 'run' && t.args.includes('--dir') && t.args.includes('--variant')), 'v1 gets --dir and --variant');
  assert(trace.some((t) => t.args?.[0] === 'export'), 'v1 reads the top-level export');
  assert(!trace.some((t) => t.args?.[0] === 'serve'), 'v1 starts no v2 server');
  const rejected = await runOpenCodeWatched({ ...options, env: { ...options.env, STUB_MODE: 'rejected' } });
  assert.equal(rejected.permissionRejected, 'a tool call (in the session record)');
  await assert.rejects(() => runOpenCodeWatched({ ...options, model: { ...selection, variant: 'none' } }), (e) => { assert.equal(e.reason, 'selection'); return true; });
});

test('an unsupported major or an unaudited 2.x build is refused before any server or model starts', async () => {
  for (const version of ['3.0.0', '2.0.29', 'garbage', '0.9.1']) {
    const options = workflowOptions(); options.env.STUB_VERSION = version;
    await assert.rejects(() => runOpenCodeWatched(options), (e) => { assert.equal(e.reason, 'unsupported version', `${version}: ${e.message}`); return true; });
    assert.doesNotMatch(traceOf(options), /"serve"|"run"/, version);
  }
});

test('a missing or malformed model, agent or effort fails before generation, without defaults', async () => {
  for (const [change, message] of [
    [{ agent: undefined }, 'selected agent'],
    [{ agentFile: undefined }, 'explicit trusted agentFile'],
    [{ model: undefined }, 'selected provider/model'],
    [{ model: { id: selection.id } }, 'selected policy family'],
    [{ model: { ...selection, variant: '' } }, 'valid explicit effort'],
    [{ model: { ...selection, variant: 3 } }, 'valid explicit effort'],
    [{ args: ['run', '--model'] }, 'explicit value'],
    [{ args: ['run', '--agent'] }, 'explicit value'],
    [{ args: ['run', '--variant'] }, 'explicit value'],
  ]) {
    const options = { ...workflowOptions(), ...change };
    await assert.rejects(() => runOpenCodeWatched(options), (e) => { assert.equal(e.reason, 'selection', e.message); assert.match(e.message, new RegExp(message)); return true; });
    assert.doesNotMatch(traceOf(options), /generation|"serve"/, 'no selected identity means no execution server');
  }
});

test('native series-family labels map to policy families without admitting another family', async () => {
  for (const [native, policy] of [['glm-flash', 'glm'], ['gpt-luna', 'openai'], ['gpt-sol', 'openai'], ['o', 'openai'], ['kimi-k2', 'kimi'], ['claude-sonnet', 'claude'], ['minimax-m3', 'minimax'], ['mimo-v2.5', 'mimo']]) assert.equal(catalogueFamily(native), policy, native);
  const options = workflowOptions(); options.env.STUB_FAMILY = 'minimax-m3';
  const result = await runOpenCodeWatched(options); assert.equal(result.normalized.model.id, 'MiniMax-M3');
  assert.equal(JSON.parse(fs.readFileSync(JSON.parse(fs.readFileSync(result.manifest)).files['model.json'])).family, 'minimax-m3', 'the raw advertised family stays in the receipt');
  const wrong = workflowOptions('family'); wrong.startupTimeoutMs = 1500;
  await assert.rejects(() => runOpenCodeWatched(wrong), /selected model family mismatch/);
});

test('the server\'s password is redacted from exports, final text, returned records and hashes, even after split echoes', async () => {
  for (const mode of ['nonce', 'nonce-nonzero']) {
    const options = workflowOptions(mode);
    let result; let failure;
    try { result = await runOpenCodeWatched(options); } catch (error) { failure = error; }
    if (mode === 'nonce-nonzero') assert.equal(failure?.reason, 'non-zero-exit'); else assert(result, failure?.message);
    const receipt = JSON.parse(fs.readFileSync((result ?? failure).manifest));
    assert(receipt.redactions.some((value) => value.includes('owned-server transport nonce')));
    const safe = (text) => !/CONTROLLED_NONCE:[A-Za-z0-9_-]{43}/.test(text);
    if (result) {
      assert(safe(result.stdout) && safe(result.stderr) && safe(result.reviewText) && safe(result.normalized.assistantText), 'returned records must not expose own nonce');
      assert(result.reviewText.includes('CONTROLLED_NONCE:[REDACTED]'));
    }
    for (const file of Object.values(receipt.files)) {
      if (!fs.existsSync(file)) continue;
      const text = fs.readFileSync(file, 'utf8');
      assert(safe(text), `${path.basename(file)} must redact the server password`);
      if (receipt.artifactSHA256[path.basename(file)]) assert.equal(createHash('sha256').update(text).digest('hex'), receipt.artifactSHA256[path.basename(file)]);
    }
  }
});

test('spawn errors are explicit infrastructure failures before any generation', async () => {
  const cmd = { exe: '/missing/harness-opencode', prefix: [] };
  const result = await capture(cmd, ['--version'], { timeoutMs: 300 });
  assert.equal(result.code, null); assert.match(result.error, /ENOENT/); assert.equal(result.timedOut, false);
  await assert.rejects(() => startPrivateServer(cmd, { env: process.env, cwd: os.tmpdir(), timeoutMs: 300 }), (e) => { assert.equal(e.reason, 'startup'); assert.match(e.message, /ENOENT/); return true; });
});

test('resume refuses a missing or wrong-major root as an ownership error before a database opens', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-ownership-')); const env = { ...process.env, HARNESS_OPENCODE_HOME: dir };
  assert.throws(() => privateHome(env, { resumeRoot: path.join(dir, 'missing') }), (e) => e.reason === 'ownership');
  const home = privateHome(env);
  fs.writeFileSync(path.join(home.root, 'data-home'), path.join(dir, 'data'));
  assert.throws(() => privateHome(env, { resumeRoot: home.root }), (e) => e.reason === 'ownership');
  fs.writeFileSync(path.join(home.root, 'protocol-major'), '1\n');
  assert.throws(() => privateHome(env, { resumeRoot: home.root }), (e) => e.reason === 'ownership');
});

// The review CLI end to end on the v2 path, in a throwaway repository on the real disk (review.mjs
// refuses a scratch root on tmpfs, #311), with a fake gh and the stub.
test('review.mjs on v2 reviews the exact fetched head with the trusted profile and reads the complete export', () => {
  const disk = path.join(os.homedir(), 'goal2-review-tmp'); fs.mkdirSync(disk, { recursive: true });
  const tmp = fs.realpathSync(fs.mkdtempSync(path.join(disk, 'workflow-review-test-')));
  try {
    const origin = path.join(tmp, 'origin.git'); const repo = path.join(tmp, 'repo');
    const gitEnv = { ...process.env, GIT_AUTHOR_NAME: 't', GIT_AUTHOR_EMAIL: 't@t', GIT_COMMITTER_NAME: 't', GIT_COMMITTER_EMAIL: 't@t' };
    const git = (...args) => { const r = spawnSync('git', args, { cwd: repo, encoding: 'utf8', env: gitEnv }); assert.equal(r.status, 0, r.stderr); return r.stdout.trim(); };
    spawnSync('git', ['init', '-q', '--bare', origin]); spawnSync('git', ['clone', '-q', origin, repo]);
    fs.mkdirSync(path.join(repo, '.opencode', 'agents'), { recursive: true });
    fs.copyFileSync(agentFile, path.join(repo, '.opencode', 'agents', 'reviewer.md'));
    const cfg = JSON.parse(fs.readFileSync(path.join(REPO, 'harness.json'), 'utf8')); cfg.jail = { enabled: false };
    fs.writeFileSync(path.join(repo, 'harness.json'), JSON.stringify(cfg));
    git('add', '-A'); git('commit', '-q', '-m', 'fixture'); git('push', '-q', 'origin', 'HEAD:main');
    const head = git('rev-parse', 'HEAD');
    spawnSync('git', ['--git-dir', origin, 'update-ref', 'refs/pull/1/head', head]);
    fs.writeFileSync(path.join(tmp, 'gh.mjs'), `const a = process.argv.slice(2).join(' ');
if (a === '--version') process.exit(0);
if (/^pr view \\d+ --json headRefOid/.test(a)) console.log(process.env.FAKE_HEAD);
else if (/^(pr|issue) view \\d+ --json labels/.test(a)) console.log('');
else { console.error('fake gh: unexpected ' + a); process.exit(1); }`);
    const brief = path.join(tmp, 'brief.md'); fs.writeFileSync(brief, 'T99 review (mm-m3)\nSynthetic read-only review.\n');
    const env = { ...process.env, FAKE_HEAD: head, HARNESS_GH_EXE: path.join(tmp, 'gh.mjs'), HARNESS_OPENCODE_EXE: stub,
      HARNESS_OPENCODE_HOME: path.join(tmp, 'ochome'), HARNESS_SESSION_FAMILY: 'claude', ANTHROPIC_BASE_URL: '', HARNESS_SCRATCH_ROOT: path.join(tmp, 'scratch'),
      STUB_TRACE: path.join(tmp, 'trace.jsonl'), STUB_FINAL: 'T99 review (mm-m3)\napprove\nDW1: ran stub → pass\nFinal pass done\napprove\n' };
    delete env.STUB_VERSION; delete env.STUB_MODE;
    const run = (b) => spawnSync(process.execPath, [process.env.WF_REVIEW_SCRIPT || path.join(REPO, 'tools/harness/review.mjs'), '--pr', '1', '--brief', b, '--reviewer', 'mm-m3', '--done-when', '1', '--dry-run'], { cwd: repo, env, encoding: 'utf8', timeout: 30000 });
    const result = run(brief);
    assert.equal(result.status, 0, result.stderr + result.stdout);
    assert.match(result.stdout, /dry run: would post/); assert.match(result.stdout, /DW1: ran stub/);
    assert.doesNotMatch(result.stdout, /volatile output/i, 'the console output is not the review');
    const manifest = result.stdout.match(/manifest (\S+run\.json)/)?.[1]; assert(manifest, result.stdout);
    const receipt = JSON.parse(fs.readFileSync(manifest));
    assert.equal(receipt.reviewedHead, head); assert.equal(receipt.reviewPR, '1');
    assert(manifest.startsWith(path.join(tmp, 'scratch-harness') + path.sep), 'receipts go to the harness folder, outside the reviewer grant');
    assert(fs.existsSync(receipt.files['profile.json']) && fs.existsSync(receipt.files['export.json']));
    assert.equal(JSON.parse(fs.readFileSync(receipt.files['profile.json'])).id, 'reviewer');
    assert(!receipt.dataHome.startsWith(tmp + path.sep + 'repo'), 'the provider DB stays outside the worktree');
    const trace = fs.readFileSync(env.STUB_TRACE, 'utf8').trim().split('\n').map(JSON.parse);
    const client = trace.find((t) => t.args?.[0] === 'run');
    assert.equal(client.args[client.args.indexOf('--agent') + 1], 'reviewer');
    assert.equal(client.args[client.args.indexOf('--model') + 1], 'minimax/MiniMax-M3#thinking');
    const stale = path.join(tmp, 'stale.md'); fs.writeFileSync(stale, `T99 review (mm-m3)\nHEAD is ${'a'.repeat(40)}\n`);
    const refused = run(stale);
    assert.equal(refused.status, 2, refused.stderr); assert.match(refused.stderr, /brief names/);
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});

// Each check above fails its own assertion when it is removed: the lib folder is copied to a scratch
// folder, one line is mutated there (never in the tracked file), and this file is re-run against it.
test('mutation controls: removing an identity, rejection, transport, redaction or final-text check fails its test', () => {
  const root = new URL('../tools/harness/lib/', import.meta.url);
  for (const [name, file, before, after, pattern, failure] of [
    ['session identity', 'opencode-protocol.mjs', "equal(sessionID, string(expected.sessionID, 'expected session id'), 'session');", '', 'export identity', 'Missing expected rejection'],
    ['rejection', 'opencode-workflow.mjs', 'if (normalized.rejected) throw', 'if (false) throw', 'export identity', 'Missing expected rejection'],
    ['owned descendants', 'opencode-transport.mjs', 'if (!child?.pid) return;', 'if (!child?.pid || child.exitCode !== null || child.signalCode !== null) return;', 'capture kills', 'owned descendant must terminate'],
    ['old run command', 'opencode-workflow.mjs', "args.splice(1, 1, '--server', server.url);", '', 'recovers the complete final', 'exit 2'],
    ['own nonce returned text', 'opencode-workflow.mjs', 'raw = JSON.parse(server.redact(JSON.stringify(result.data)));', 'raw = result.data;', 'password is redacted from exports', 'returned records must not expose own nonce'],
    ['queue clock', 'opencode-workflow.mjs', 'if (queued > updated) updated = queued;', '', 'heavy-job queue file', "'idle'"],
    ['v2 dispatch', 'opencode.mjs', "if (version !== AUDITED_V2) throw", 'if (false) throw', 'unaudited 2.x build', 'Missing expected rejection'],
    ['complete final recovery', '../review.mjs', 'readReview(run.reviewText ?? run.stdout, header', 'readReview(run.stdout, header', 'review.mjs on v2', 'No review from'],
  ]) {
    const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-workflow-mutant-'));
    try {
      const dir = path.join(scratch, 'lib'); fs.mkdirSync(dir);
      for (const item of fs.readdirSync(root)) if (item.endsWith('.mjs')) fs.copyFileSync(new URL(item, root), path.join(dir, item));
      fs.copyFileSync(new URL('../tools/harness/review.mjs', import.meta.url), path.join(scratch, 'review.mjs'));
      fs.cpSync(new URL('../tools/harness/opencode-guard/', import.meta.url), path.join(scratch, 'opencode-guard'), { recursive: true });
      const target = path.join(dir, file); const source = fs.readFileSync(target, 'utf8');
      assert(source.includes(before), `${name}: mutation applies`); fs.writeFileSync(target, source.replace(before, after));
      const testEnv = { ...process.env }; delete testEnv.NODE_TEST_CONTEXT;
      const result = spawnSync(process.execPath, ['--test', '--test-name-pattern=' + pattern, fileURLToPath(import.meta.url)], { env: { ...testEnv,
        WF_TRANSPORT_MODULE: pathToFileURL(path.join(dir, 'opencode-transport.mjs')).href, WF_OPENCODE_MODULE: pathToFileURL(path.join(dir, 'opencode.mjs')).href,
        WF_PEEK_MODULE: pathToFileURL(path.join(dir, 'opencode-peek.mjs')).href, WF_REVIEW_SCRIPT: path.join(scratch, 'review.mjs') }, encoding: 'utf8', timeout: 120000 });
      assert.equal(result.status, 1, `${name}: ${result.stdout.slice(-600)}${result.stderr.slice(-300)}`);
      assert.match(result.stdout + result.stderr, new RegExp(failure.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), name);
      assert.doesNotMatch(result.stdout + result.stderr, /MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND/, name);
    } finally { fs.rmSync(scratch, { recursive: true, force: true }); }
  }
});
