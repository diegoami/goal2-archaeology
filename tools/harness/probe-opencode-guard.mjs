#!/usr/bin/env node
// Native nonbilling proof of the OpenCode 2 review run (#262; ported from goal2 PR 178's
// probe-opencode-guard.mjs and adapted to this repository's grants). The real 2.0.28 binary runs a real
// review session through runOpenCodeWatched (private server, trusted reviewer, the operand guard), but
// its only "model" is a deterministic fake provider on 127.0.0.1 started by this script: no provider
// is contacted, nothing is billed, and the fake reports zero tokens.
//
//   node tools/harness/probe-opencode-guard.mjs --out <dir>                  rejections (default)
//   node tools/harness/probe-opencode-guard.mjs --complete --out <dir>       a clean review comes back
//   node tools/harness/probe-opencode-guard.mjs --active-cancel --out <dir>  idle limit cancels a live tool
//
// The worktree and an "outside" folder are made under ~/goal2-review-tmp-harness (on disk, outside every
// reviewer grant: under /tmp everything would be granted). Results are written exclusively under a new
// native-* folder of --out; the run's own receipts stay in the work folder, whose path result.json names.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { resolveOpenCode, runOpenCodeWatched } from './lib/opencode.mjs';
import { hash, privateHome, startPrivateServer, settledCatalogue } from './lib/opencode-transport.mjs';
import { reviewerPolicy, trustedReviewEnv, verifyReviewer } from './lib/opencode-policy.mjs';
import { scratchRoot, harnessDir } from './lib/scratch.mjs';

const flag = (name) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : undefined; };
assert(flag('--out'), '--out required');
const active = process.argv.includes('--active-cancel');
const complete = process.argv.includes('--complete');
const out = path.resolve(flag('--out')); fs.mkdirSync(out, { recursive: true });
const results = fs.mkdtempSync(path.join(out, `native-${active ? 'cancel' : complete ? 'complete' : 'reject'}-`));
const save = (name, value) => fs.writeFileSync(path.join(results, name), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
const root = fs.realpathSync(fs.mkdtempSync(path.join(harnessDir(scratchRoot()), 'native-probe-')));
const work = path.join(root, 'work'); const outside = path.join(root, 'outside'); const config = path.join(root, 'config', 'opencode');
for (const d of [work, outside, config]) fs.mkdirSync(d, { recursive: true });
fs.writeFileSync(path.join(work, 'inside.txt'), 'INSIDE_SENTINEL\n');
fs.writeFileSync(path.join(outside, 'secret.txt'), 'OUTSIDE_SENTINEL\n');
const tag = randomBytes(8).toString('hex');
const tmpFile = `/tmp/harness-guard-${tag}.txt`; fs.writeFileSync(tmpFile, 'TMP_SENTINEL\n', { flag: 'wx' });
const scratchFile = path.join(scratchRoot(), `harness-guard-${tag}.txt`); fs.mkdirSync(scratchRoot(), { recursive: true }); fs.writeFileSync(scratchFile, 'SCRATCH_SENTINEL\n', { flag: 'wx' });
const agentFile = path.resolve(new URL('../../.opencode/agents/reviewer.md', import.meta.url).pathname);
const header = 'T99 review (loopback)';
// round 2 (Sol's R1, R2 on PR 332): quoted command names and quoted path fragments are evaluated first
const external = ['external-cat', 'external-quoted', 'external-nested', 'external-relative', 'external-proc',
  'quoted-name-R1', 'quoted-fragment-R2', 'empty-fragment-name', 'single-quoted-fragment', 'dynamic-operand', 'ansi-nul-name'];
const allowed = ['inside-cat', 'tmp-cat', 'scratch-cat', 'quoted-name-inside', ...(fs.existsSync('/etc/timezone') ? ['timezone-cat'] : [])];
const commands = {
  'external-cat': `cat ${path.join(outside, 'secret.txt')}`, 'external-quoted': `cat "${path.join(outside, 'secret.txt')}"`,
  'external-nested': `echo $(cat ${path.join(outside, 'secret.txt')})`, 'external-relative': 'cat ../outside/secret.txt', 'external-proc': 'cat /proc/self/comm',
  'quoted-name-R1': `"cat" ${path.join(outside, 'secret.txt')}`, 'quoted-fragment-R2': `cat "${outside}"/secret.txt`,
  'empty-fragment-name': `c""at ${path.join(outside, 'secret.txt')}`, 'single-quoted-fragment': `cat '${outside}'/secret.txt`,
  'dynamic-operand': `cat "$(printf %s ${outside})"/secret.txt`, 'quoted-name-inside': '"cat" inside.txt',
  'ansi-nul-name': `$'cat\\0junk' ${path.join(outside, 'secret.txt')}`, // round 3 (Sol's R1): Bash stops at the NUL
  'etc-deny': 'cat /etc/hostname', 'git-deny': 'git push harness-probe-no-remote',
  'inside-cat': 'cat inside.txt', 'tmp-cat': `cat ${tmpFile}`, 'scratch-cat': `cat ${scratchFile}`, 'timezone-cat': 'cat /etc/timezone',
  'active-cancel': `${process.execPath} -e ${JSON.stringify("require('node:fs').writeFileSync('active.pid',String(process.pid));setInterval(()=>{},1000)")}`,
};
const planned = active ? ['active-cancel'] : complete ? allowed : [...external, 'etc-deny', 'git-deny', ...allowed];
const requests = []; const responses = []; let sent = false;
// The OpenAI-compatible chat route and stream the native openai-compatible provider speaks.
const fake = http.createServer(async (request, response) => {
  try {
    assert.equal(request.socket.remoteAddress, '127.0.0.1'); assert.equal(request.url, '/v1/chat/completions');
    let raw = ''; for await (const chunk of request) raw += chunk;
    const body = JSON.parse(raw); assert.equal(body.model, 'guard'); requests.push({ model: body.model, tools: (body.tools ?? []).map((t) => t.function?.name), messages: body.messages?.length });
    const toolCall = Array.isArray(body.tools) && body.tools.length > 0 && !sent;
    if (toolCall) sent = true;
    const final = `${header}\napprove\nDW1: ran the loopback probe → pass\nFinal pass done\napprove\n`;
    const delta = toolCall ? { tool_calls: planned.map((id, index) => ({ index, id, type: 'function', function: { name: 'shell', arguments: JSON.stringify({ command: commands[id], timeout: 2000 }) } })) } : { content: final };
    const chunks = [{ id: 'fake', choices: [{ index: 0, delta, finish_reason: null }] },
      { id: 'fake', choices: [{ index: 0, delta: {}, finish_reason: toolCall ? 'tool_calls' : 'stop' }], usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 } }];
    responses.push(chunks);
    response.writeHead(200, { 'content-type': 'text/event-stream' });
    for (const chunk of chunks) response.write('data: ' + JSON.stringify(chunk) + '\n\n');
    response.end('data: [DONE]\n\n');
  } catch (error) { response.writeHead(500); response.end(JSON.stringify({ error: { message: error.message } })); }
});
await new Promise((resolve) => fake.listen(0, '127.0.0.1', resolve));
fs.writeFileSync(path.join(config, 'opencode.json'), JSON.stringify({ shell: '/bin/sh', providers: { 'harness-loopback': {
  name: 'harness nonbilling deterministic fake', package: '@opencode/ai/providers/openai-compatible',
  settings: { baseURL: `http://127.0.0.1:${fake.address().port}/v1`, apiKey: 'HARNESS-FAKE-NOT-A-CREDENTIAL' },
  models: { guard: { name: 'Deterministic fake', family: 'minimax', capabilities: { tools: true, input: ['text'], output: ['text'] }, cost: { input: 0, output: 0 }, limit: { context: 100000, output: 4096 } } },
} } }, null, 2));
const env = { ...process.env, XDG_CONFIG_HOME: path.dirname(config), HARNESS_OPENCODE_HOME: path.join(root, 'runtime') };
const command = resolveOpenCode();
const model = { id: 'harness-loopback/guard', family: 'minimax', variant: 'medium' };
let unrelated; let sentinel; let before; let receipt; let outcome; let result;
try {
  if (active) {
    const policy = reviewerPolicy(agentFile); const home = privateHome(env);
    unrelated = await startPrivateServer(command, { env: trustedReviewEnv(home.env, policy), cwd: work });
    await settledCatalogue(unrelated, { model, agent: 'reviewer', verifyAgent: (profile) => verifyReviewer(profile, policy, 'reviewer') });
    sentinel = (await unrelated.request('/api/session', { body: { title: 'harness-unrelated-empty', agent: 'reviewer', model: { id: 'guard', providerID: 'harness-loopback', variant: 'medium' }, location: { directory: work } } })).data;
    before = await unrelated.request('/api/session/' + sentinel.id);
  }
  try {
    result = await runOpenCodeWatched({ opencode: command, args: ['run'], model, agent: 'reviewer', agentFile,
      prompt: 'Only the deterministic loopback fake responds; planned shell tool permission probe.', workDir: work, title: 'harness-native-guard',
      startupTimeoutMs: 60000, totalTimeoutMs: 120000, idleTimeoutMs: active ? 1500 : 30000, pollMs: 100, logDir: path.join(root, 'receipts'), env, log: (l) => console.log(l) });
    receipt = JSON.parse(fs.readFileSync(result.manifest)); outcome = { reason: 'complete', reviewText: result.reviewText, exitCode: result.exitCode };
  } catch (error) {
    if (error.manifest) receipt = JSON.parse(fs.readFileSync(error.manifest));
    outcome = { reason: error.reason, message: error.message };
  }
  save('outcome.json', outcome); save('requests.json', requests); save('responses.json', responses);
  assert(receipt, `a retained receipt is required: ${outcome.message}`);
  const exported = JSON.parse(fs.readFileSync(receipt.files['export.json']));
  const tools = exported.messages.filter((m) => m.type === 'assistant').flatMap((m) => m.content).filter((p) => p.type === 'tool');
  save('tool-outcomes.json', tools.map((t) => ({ id: t.id, command: t.state.input?.command, status: t.state.status, error: t.state.error ?? null, text: (t.state.content ?? []).filter((p) => p.type === 'text').map((p) => p.text).join('') })));
  const text = (id) => tools.find((t) => t.id === id).state.content.filter((p) => p.type === 'text').map((p) => p.text).join('');
  if (active) {
    assert.equal(outcome.reason, 'idle', outcome.message);
    const pid = Number(fs.readFileSync(path.join(work, 'active.pid'), 'utf8'));
    const stat = `/proc/${pid}/stat`;
    assert(!fs.existsSync(stat) || fs.readFileSync(stat, 'utf8').split(' ')[2] === 'Z', 'the live tool worker must terminate');
    assert.equal(receipt.interrupt?.interrupted, true, 'the native execution must actually be interrupted');
    const after = await unrelated.request('/api/session/' + sentinel.id);
    assert.deepEqual(after, before, 'an unrelated session on the same v2 DB survives');
    save('active-cancellation.json', { workerPID: pid, terminated: true, interrupt: receipt.interrupt, unrelatedBefore: before, unrelatedAfter: after });
  } else if (complete) {
    assert.equal(outcome.reason, 'complete', outcome.message);
    assert.equal(result.reviewText.split('\n')[0], header); assert.match(result.reviewText, /Final pass done\napprove\n$/);
    for (const id of allowed) assert.equal(tools.find((t) => t.id === id)?.state.status, 'completed', `${id} must run`);
    assert.equal(text('inside-cat'), 'INSIDE_SENTINEL\n'); assert.equal(text('tmp-cat'), 'TMP_SENTINEL\n'); assert.equal(text('scratch-cat'), 'SCRATCH_SENTINEL\n');
    assert.equal(receipt.phase, 'complete'); assert.equal(fs.readFileSync(receipt.files['final.txt'], 'utf8'), result.reviewText);
  } else {
    assert.equal(outcome.reason, 'permission-rejected', outcome.message);
    for (const id of [...external, 'etc-deny', 'git-deny']) assert.equal(tools.find((t) => t.id === id)?.state.status, 'error', `${id} must be rejected`);
    for (const id of allowed) assert.equal(tools.find((t) => t.id === id)?.state.status, 'completed', `${id} must run`);
    assert.equal(text('inside-cat'), 'INSIDE_SENTINEL\n'); assert.equal(text('tmp-cat'), 'TMP_SENTINEL\n'); assert.equal(text('scratch-cat'), 'SCRATCH_SENTINEL\n');
    for (const t of tools.filter((x) => external.includes(x.id))) assert(!JSON.stringify(t.state.content ?? []).includes('OUTSIDE_SENTINEL'), `${t.id} must not return the outside file`);
  }
  const shellEvidence = fs.existsSync(receipt.files['shell-guard.jsonl']) ? fs.readFileSync(receipt.files['shell-guard.jsonl'], 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : [];
  assert(shellEvidence.length > 0 && shellEvidence.every((e) => e.shell === '/bin/sh' && e.grammar === 'bash'), 'the guard must have scanned the actual native shell');
  assert.equal(receipt.usage.cost, 0); assert.equal(receipt.usage.tokens.input, 0); assert.equal(receipt.usage.tokens.output, 0);
  save('result.json', { classification: 'actual native OpenCode 2 dispatch with a deterministic loopback provider; no provider contacted; the fake reports zero tokens',
    externalModelCalls: 0, requests: requests.length, receipt: receipt.files['run.json'], binarySHA256: receipt.binarySHA256, policySHA256: receipt.policySHA256,
    guardSHA256: receipt.guard?.sourceSHA256, probeSHA256: hash(fs.readFileSync(new URL(import.meta.url))), calls: planned, shellScans: shellEvidence.length, passed: true });
} finally {
  if (unrelated) await unrelated.stop();
  await new Promise((resolve) => fake.close(resolve));
  fs.rmSync(tmpFile, { force: true }); fs.rmSync(scratchFile, { force: true }); // this probe's own sentinels
}
console.log(`Native guard nonbilling proof passed: ${results} (run folder ${root})`);
