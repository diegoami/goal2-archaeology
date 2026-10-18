// #262: the explicit OpenCode v1/v2 protocol adapter (tools/harness/lib/opencode-protocol.mjs, ported
// from goal2 PR 175). Never calls a model. The v2 identities come from the nonbilling live capture of
// the installed 2.0.28 (tests/fixtures/opencode/v2-live/run-3Ai73R, made by tools/harness/probe-opencode.mjs);
// the synthetic outcomes (tests/fixtures/opencode/*.json) are schema-shaped and take that capture's
// session id and directory, so no constant of another machine decides a match.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const p = await import(process.env.PROTOCOL_MODULE || '../tools/harness/lib/opencode-protocol.mjs');
const LIVE = new URL('fixtures/opencode/v2-live/run-3Ai73R/', import.meta.url);
const evidence = (name) => JSON.parse(fs.readFileSync(new URL(name, LIVE)));
const actual = evidence('session-export-api.json').data;
const sessionID = actual.info.id;
const directory = actual.info.location.directory;
const liveModel = actual.info.model;
const expected = { sessionID, directory, agent: 'reviewer', model: liveModel };
const copy = (x) => structuredClone(x);
// The synthetic outcomes, re-identified as the live capture's session and directory.
function fixture(name) {
  const r = JSON.parse(fs.readFileSync(new URL(`fixtures/opencode/${name}`, import.meta.url)));
  if (!r.info) return r;
  r.info.id = sessionID;
  if (r.info.location) r.info.location.directory = directory;
  if ('directory' in r.info) r.info.directory = directory;
  for (const m of r.messages ?? []) {
    if (m.info) m.info.sessionID = sessionID;
    for (const part of m.parts ?? []) if ('sessionID' in part) part.sessionID = sessionID;
  }
  return r;
}
const options = { ...expected, title: 'fixture', prompt: 'Read the brief', provider: 'minimax' };

test('commands keep v1 syntax explicit and select v2 syntax', () => {
  assert.deepEqual(p.command(1, 'models', options).args, ['models', 'minimax', '--verbose']);
  assert.deepEqual(p.command(2, 'models', options).args, ['api', '--standalone', 'model.list']);
  assert.deepEqual(p.command(1, 'export', options).args, ['export', sessionID]);
  assert.deepEqual(p.command(2, 'export', options).args, ['session', 'export', '--standalone', sessionID]);
  assert.deepEqual(p.command(1, 'list', options).args, ['session', 'list', '--format', 'json']);
  assert.deepEqual(p.command(2, 'list', options).args, ['session', 'list', '--standalone', '--format', 'json']);
  assert.deepEqual(p.command(2, 'run', options), { cwd: directory, args: ['run', '--standalone', '--agent', 'reviewer', '--model', 'minimax/MiniMax-M3#thinking', '--session', sessionID, 'Read the brief'] });
  assert.deepEqual(p.command(1, 'run', { ...options, sessionID: null }).args, ['run', '--dir', directory, '--agent', 'reviewer', '--model', 'minimax/MiniMax-M3', '--variant', 'thinking', '--title', 'fixture', 'Read the brief']);
  assert.deepEqual(p.command(2, 'run', { ...options, sessionID: null, model: { ...options.model, variant: undefined } }).args, ['run', '--standalone', '--agent', 'reviewer', '--model', 'minimax/MiniMax-M3', '--title', 'fixture', 'Read the brief']);
  assert.deepEqual(p.command(2, 'interrupt', { ...options, server: 'http://127.0.0.1:4321' }).args, ['api', '--server', 'http://127.0.0.1:4321', 'session.interrupt', '--param', `sessionID=${sessionID}`, '--data', '{}']);
  assert.throws(() => p.command(2, 'interrupt', options), /owned loopback/);
  assert.throws(() => p.command(1, 'interrupt', options), /no supported interrupt/);
  assert.throws(() => p.command(2, 'run', { ...options, directory: 'relative' }), /absolute/);
  assert.throws(() => p.command(2, 'run', { ...options, model: { ...options.model, id: 'bad#variant' } }), /ambiguous/);
});

test('the v2 commands the adapter emits are the ones the installed CLI lists in its help', () => {
  const run = evidence('help-run.json').stdout;
  for (const flagName of ['--standalone', '--server', '--session', '--model', '--agent', '--title']) assert.match(run, new RegExp(`${flagName}\\b`), flagName);
  assert.match(run, /provider\/model#variant/);
  for (const absent of ['--dir', '--variant']) assert.doesNotMatch(run, new RegExp(`${absent}\\b`), absent);
  assert.match(evidence('help-session-export.json').stdout, /--standalone/);
  assert.match(evidence('help-serve.json').stdout, /--stdio/);
});

test('the old v1 commands fail on the installed v2 binary, on their syntax (negative controls)', () => {
  const old = evidence('old-commands.json');
  for (const [name, r] of Object.entries(old)) {
    assert.notEqual(r.code, 0, name);
    assert.match(r.stderr, /Unexpected positional argument|Unrecognized flag/, name);
  }
  assert.match(old.runDir.stderr, /--dir/); assert.match(old.runVariant.stderr, /--variant/);
  assert.match(old.topLevelExport.stderr, /Unexpected positional argument/);
  // The 1.18 session lookup is the hazard, not a failure: it answers through the managed service.
  const first = JSON.parse(fs.readFileSync(new URL('fixtures/opencode/v2-live/run-EFh0VF/old-commands.json', import.meta.url)));
  assert.equal(first.sessionListLimit.code, 0, 'v1 `session list -n 20` succeeds on v2 via the shared background service');
  assert.equal(evidence('session-export-cli.json').code, 0);
});

test('unknown majors never downgrade', () => {
  for (const major of [0, 3, '2', undefined, NaN]) {
    for (const fn of [() => p.command(major, 'run', options), () => p.normalizeSession(major, actual, expected), () => p.normalizeModels(major, {}, {}), () => p.normalizeAgents(major, {}, {}), () => p.normalizePermissions(major, [], ''), () => p.normalizeSessionList(major, [], directory), () => p.normalizeEvents(major, '', expected)]) assert.throws(fn, /unsupported major/);
  }
});

test('the live empty export, list (API and CLI) and events keep identity and zero usage', () => {
  const want = { ...expected, agent: actual.info.agent };
  const normalized = p.normalizeSession(2, actual, want);
  assert.equal(normalized.sessionID, sessionID); assert.equal(normalized.completed, false);
  assert.equal(normalized.assistantText, ''); assert.equal(normalized.rejected, false); assert.equal(normalized.cost, 0);
  assert.deepEqual(normalized.tokens, actual.info.tokens); assert.deepEqual(normalized.model, liveModel);
  const cli = JSON.parse(evidence('session-export-cli.json').stdout);
  assert.deepEqual(p.normalizeSession(2, cli, want).tokens, normalized.tokens, 'CLI and API exports agree');
  assert.deepEqual(p.normalizeSessionList(2, evidence('session-list-api.json'), directory), p.normalizeSessionList(2, JSON.parse(evidence('session-list-cli.json').stdout), directory));
  const sse = fs.readFileSync(new URL('events.sse', LIVE), 'utf8');
  const events = p.normalizeEvents(2, sse, expected);
  assert(events.some((e) => e.data.sessionID === sessionID));
  assert.throws(() => p.normalizeEvents(2, sse.slice(0, -1), expected), /truncated/);
  assert.throws(() => p.normalizeEvents(2, sse, { ...expected, sessionID: 'ses_other' }), /event session/);
  assert.throws(() => p.normalizeEvents(2, sse, { ...expected, directory: '/other' }), /event directory/);
  assert.throws(() => p.normalizeSessionList(2, evidence('session-list-api.json'), '/other'), /directory mismatch/);
  assert.throws(() => p.normalizeSession(2, actual, { ...want, agent: 'reviewer' }), /agent mismatch/);
});

test('live model variants and family, and explicit v1 parsed metadata', () => {
  const want = { ...liveModel, directory };
  assert.deepEqual(p.normalizeModels(2, evidence('models.json'), want), { providerID: 'minimax', id: 'MiniMax-M3', modelID: 'MiniMax-M3', family: 'minimax', enabled: true, variants: ['none', 'thinking'] });
  assert.equal(p.normalizeModels(1, { models: [{ id: 'MiniMax-M3', providerID: 'minimax', family: 'minimax', variants: { none: {}, thinking: {} } }] }, want).variants.length, 2);
  for (const change of [{ id: 'missing' }, { providerID: 'other' }, { variant: 'high' }, { directory: '/other' }]) assert.throws(() => p.normalizeModels(2, evidence('models.json'), { ...want, ...change }));
  const bad = evidence('models.json'); bad.data.find((m) => m.id === 'MiniMax-M3').variants = {}; assert.throws(() => p.normalizeModels(2, bad, want), /variants/);
  const duplicate = evidence('models.json'); duplicate.data.push(duplicate.data.find((m) => m.id === 'MiniMax-M3')); assert.throws(() => p.normalizeModels(2, duplicate, want), /ambiguous/);
  const disabled = evidence('models.json'); disabled.data.find((m) => m.id === 'MiniMax-M3').enabled = false; assert.throws(() => p.normalizeModels(2, disabled, want), /disabled/);
});

test('effective agent permissions keep their order; the v2 default allows every action first', () => {
  const live = evidence('agents.json');
  const build = p.normalizeAgents(2, live, { ...expected, agent: 'build' });
  assert.deepEqual(build.permissions[0], { action: '*', resource: '*', effect: 'allow' }, 'v2 prepends allow-all: external_directory must be denied or asked explicitly');
  assert.deepEqual(build.permissions, live.data.find((a) => a.id === 'build').permissions);
  assert.throws(() => p.normalizeAgents(2, { location: { directory }, data: [] }, expected), /missing/);
  assert.throws(() => p.normalizeAgents(2, live, { ...expected, agent: 'general' }), /primary/);
  assert.throws(() => p.normalizeAgents(2, live, { ...expected, agent: 'build', directory: '/other' }), /directory mismatch/);
  const v1 = { agents: [{ name: 'reviewer', mode: 'all', prompt: 'Review', permission: { edit: 'deny', bash: { '*': 'allow', 'git push *': 'deny' } } }] };
  assert.deepEqual(p.normalizeAgents(1, v1, expected).permissions, [{ action: 'edit', resource: '*', effect: 'deny' }, { action: 'bash', resource: '*', effect: 'allow' }, { action: 'bash', resource: 'git push *', effect: 'deny' }]);
});

test('full text, usage and rejected tool outcomes survive both protocols', () => {
  for (const major of [1, 2]) {
    const normalized = p.normalizeSession(major, fixture(`v${major}-synthetic-export.json`), expected);
    assert.equal(normalized.assistantText, 'Header\napprove\nFinal pass done\napprove\n', 'complete assistant text');
    assert.equal(normalized.rejected, true, 'rejected outcome must survive approval-looking text');
    assert.equal(normalized.completed, true); assert.equal(normalized.cost, 0.002);
    assert.deepEqual(normalized.tokens, { input: 10, output: 4, reasoning: 2, cache: { read: 3, write: 1 } });
    assert.equal(normalized.messages[0].parts[2].name, 'shell'); assert.equal(normalized.messages[0].parts[2].status, 'error');
    assert.match(normalized.messages[0].parts[2].error.message, /rejected permission/);
    assert.equal(normalized.messages[0].parts[3].status, 'completed');
    const noEffort = fixture(`v${major}-synthetic-export.json`);
    const modelWithoutEffort = { providerID: 'minimax', id: 'MiniMax-M3' };
    if (major === 2) { delete noEffort.info.model.variant; delete noEffort.messages[0].model.variant; } else delete noEffort.messages[0].info.variant;
    const noEffortResult = p.normalizeSession(major, noEffort, { ...expected, model: modelWithoutEffort });
    assert.deepEqual(noEffortResult.model, modelWithoutEffort, 'absent effort stays absent');
    const multiple = fixture(`v${major}-synthetic-export.json`);
    const next = copy(multiple.messages[0]);
    if (major === 2) { next.id = 'msg_fixture_final'; multiple.messages[0].finish = 'tool-calls'; } else {
      next.info.id = 'msg_fixture_final'; multiple.messages[0].info.finish = 'tool-calls';
      for (const part of next.parts) part.messageID = next.info.id;
    }
    multiple.messages.push(next);
    const both = p.normalizeSession(major, multiple, expected);
    assert.equal(both.assistantText, normalized.assistantText.repeat(2), 'all assistant messages must survive');
    assert.equal(both.completed, true, 'final stop completes a tool-call sequence');
    const user = major === 2 ? { id: 'msg_fixture_later_user', type: 'user', time: { created: actual.info.time.created }, text: 'pending' } : { info: { id: 'msg_fixture_later_user', sessionID, role: 'user', time: { created: actual.info.time.created } }, parts: [] };
    multiple.messages.push(user);
    assert.equal(p.normalizeSession(major, multiple, expected).completed, false, 'later user input is not completed by prior approval');
    if (major === 2) {
      const idle = fixture('v2-synthetic-idle.json');
      multiple.messages.push(idle);
      assert.equal(p.normalizeSession(2, multiple, expected).completed, false, 'pending user followed by idle must not complete');
      const stopped = fixture('v2-synthetic-export.json'); stopped.messages.push(idle);
      assert.equal(p.normalizeSession(2, stopped, expected).completed, true);
      for (const outcome of ['failed', 'interrupted']) { stopped.messages.at(-1).outcome = outcome; assert.equal(p.normalizeSession(2, stopped, expected).completed, false); }
      stopped.messages.at(-1).outcome = 'succeeded';
      stopped.messages.at(-1).error = { type: 'APIError', message: 'failed' };
      assert.equal(p.normalizeSession(2, stopped, expected).completed, false);
    }
  }
});

test('wrong session, directory, agent, model and effort fail closed', () => {
  for (const major of [1, 2]) {
    const record = fixture(`v${major}-synthetic-export.json`);
    for (const change of [{ sessionID: 'ses_other' }, { directory: '/other' }, { agent: 'build' }, { model: { ...expected.model, id: 'other' } }, { model: { ...expected.model, providerID: 'other' } }, { model: { ...expected.model, variant: 'none' } }]) {
      assert.throws(() => p.normalizeSession(major, record, { ...expected, ...change }), /mismatch/, `identity ${JSON.stringify(change)}`);
    }
    const bad = copy(record); if (major === 2) bad.messages[0].agent = 'build'; else bad.messages[0].info.agent = 'build';
    assert.throws(() => p.normalizeSession(major, bad, expected), /message agent/);
  }
});

test('malformed, truncated and incomplete records never become success', () => {
  for (const major of [1, 2]) {
    const base = fixture(`v${major}-synthetic-export.json`);
    for (const mutate of [
      (r) => delete r.messages, (r) => delete r.info.agent,
      (r) => delete (major === 2 ? r.messages[0] : r.messages[0].info).time.completed,
      (r) => { (major === 2 ? r.messages[0] : r.messages[0].info).finish = 'length'; },
      (r) => { (major === 2 ? r.messages[0].content : r.messages[0].parts)[2].state.status = 'running'; },
      (r) => delete (major === 2 ? r.messages[0].content : r.messages[0].parts)[2].state.error,
      (r) => { (major === 2 ? r.messages[0] : r.messages[0].info).tokens.output = -1; },
    ]) { const bad = copy(base); mutate(bad); assert.throws(() => p.normalizeSession(major, bad, expected)); }
    assert.throws(() => p.normalizeSession(major, null, expected), /object/);
  }
  const text = JSON.stringify(fixture('v2-synthetic-export.json'));
  assert.throws(() => JSON.parse(text.slice(0, text.length / 2)), 'a truncated export is not JSON');
  assert.throws(() => p.normalizeSession(1, fixture('v1-synthetic-export.json').info, expected), /session info/);
  assert.throws(() => p.normalizeSession(2, JSON.parse('{"info":{}}'), expected));
});

test('structured rejection tags and failed outcomes stay explicit', () => {
  for (const type of ['Permission.DeclinedError', 'Permission.BlockedError', 'Permission.CorrectedError']) {
    const record = fixture('v2-synthetic-export.json');
    record.messages[0].content[2].state.error = { type, message: 'No' };
    assert.equal(p.normalizeSession(2, record, expected).rejected, true, type);
  }
  for (const outcome of ['failed', 'interrupted']) {
    const record = fixture('v2-synthetic-export.json'); record.info.outcome = outcome;
    const normalized = p.normalizeSession(2, record, expected);
    assert.equal(normalized.outcome, outcome); assert.equal(normalized.completed, false);
  }
  const duplicate = fixture('v2-synthetic-export.json'); duplicate.messages.push(copy(duplicate.messages[0]));
  assert.throws(() => p.normalizeSession(2, duplicate, expected), /duplicate/);
});

test('v1 step metadata survives, and unfinished or errored assistants never complete', () => {
  const projection = JSON.parse(fs.readFileSync(new URL('fixtures/opencode/v1-actual-metadata-step-projection.json', import.meta.url))); // read as given: its ids are its own
  const record = { info: { id: projection.info.sessionID, agent: 'reviewer', directory, time: { created: projection.info.time.created, updated: projection.info.time.completed } }, messages: [{ info: projection.info, parts: projection.parts }] };
  const want = { ...expected, sessionID: projection.info.sessionID };
  const normalized = p.normalizeSession(1, record, want);
  assert.deepEqual(normalized.messages[0].parts, projection.parts);
  assert.equal(normalized.completed, false, 'tool-calls is not final completion');
  const wrong = copy(record); wrong.messages[0].parts[0].sessionID = 'ses_other';
  assert.throws(() => p.normalizeSession(1, wrong, want), /part session/);
  for (const major of [1, 2]) {
    for (const finish of ['tool-calls', 'stop']) {
      const value = fixture(`v${major}-synthetic-export.json`);
      const meta = major === 2 ? value.messages[0] : value.messages[0].info;
      meta.finish = finish;
      if (finish === 'stop') meta.error = major === 2 ? { type: 'APIError', message: 'failed' } : { name: 'APIError', data: { message: 'failed' } };
      const result = p.normalizeSession(major, value, expected);
      assert.equal(result.completed, false, 'unfinished or assistant error must not complete');
    }
  }
});

test('permission requests keep source, resource and session ownership', () => {
  const record = fixture('synthetic-permissions.json');
  for (const r of record.data) r.sessionID = sessionID;
  const normalized = p.normalizePermissions(2, record, sessionID);
  assert.deepEqual(normalized[0], { ...record.data[0] });
  assert.throws(() => p.normalizePermissions(2, record, 'ses_other'), /session mismatch/);
  const v1 = [{ id: 'per_fixture', sessionID, permission: 'external_directory', patterns: ['/outside/*'] }];
  assert.equal(p.normalizePermissions(1, v1, sessionID)[0].action, 'external_directory');
  assert.deepEqual(p.normalizePermissions(2, evidence('permissions.json'), sessionID), []);
});

// Each guard above fails its own assertion when it is removed: a copy of the module is mutated in a
// scratch folder (never the tracked file) and this file is re-run against the copy.
test('mutation controls fail the specific identity, rejection and completion assertions', () => {
  const source = fs.readFileSync(new URL('../tools/harness/lib/opencode-protocol.mjs', import.meta.url), 'utf8');
  const mutations = [
    { name: 'identity-loss', before: "equal(a.providerID, e.providerID, 'provider'); equal(a.id, e.id, 'model'); equal(a.variant, e.variant, 'effort');", after: '', pattern: 'wrong session, directory', assertion: /Missing expected exception/ },
    { name: 'rejection-loss', before: "rejected: assistants.some((m) => m.parts.some((p) => p.type === 'tool' && p.rejected))", after: 'rejected: false', pattern: 'full text, usage', assertion: /rejected outcome must survive/ },
    { name: 'unfinished-completion', before: "assistants.at(-1).finish === 'stop'", after: 'true', pattern: 'v1 step metadata', assertion: /tool-calls is not final completion/ },
    { name: 'assistant-error-loss', before: '!assistants.some((m) => m.error)', after: 'true', pattern: 'v1 step metadata', assertion: /unfinished or assistant error must not complete/ },
    { name: 'pending-user-idle-loss', before: "normalized[lastMeaningful]?.type === 'assistant' && trailingIdleSucceeded", after: "['assistant', 'idle'].includes(normalized.at(-1).type)", pattern: 'full text, usage', assertion: /pending user followed by idle must not complete/ },
    { name: 'earlier-assistant-loss', before: "const assistants = normalized.filter((m) => m.type === 'assistant');", after: "const assistants = normalized.filter((m) => m.type === 'assistant').slice(-1);", pattern: 'full text, usage', assertion: /all assistant messages must survive/ },
    { name: 'session-loss', before: "equal(sessionID, string(expected.sessionID, 'expected session id'), 'session');", after: '', pattern: 'wrong session, directory', assertion: /Missing expected exception/ },
    { name: 'event-session-loss', before: "equal(event.data.sessionID, expected.sessionID, 'event session'); ", after: '', pattern: 'live empty export', assertion: /Missing expected exception/ },
  ];
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-protocol-mutant-'));
  try {
    for (const m of mutations) {
      assert(source.includes(m.before), `mutation ${m.name} must apply`);
      const file = path.join(dir, `${m.name}.mjs`);
      fs.writeFileSync(file, source.replace(m.before, m.after));
      const childEnv = { ...process.env, PROTOCOL_MODULE: pathToFileURL(file).href }; delete childEnv.NODE_TEST_CONTEXT;
      const r = spawnSync(process.execPath, ['--test', '--test-name-pattern', m.pattern, fileURLToPath(import.meta.url)], { encoding: 'utf8', timeout: 30000, env: childEnv });
      assert(!r.error, `${m.name}: the mutant run must finish`); assert.equal(r.status, 1, `${m.name}: ${r.stdout.slice(-400)}`);
      assert.match(r.stdout + r.stderr, m.assertion, m.name); assert.doesNotMatch(r.stdout + r.stderr, /MODULE_NOT_FOUND|SyntaxError/, m.name);
    }
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});
