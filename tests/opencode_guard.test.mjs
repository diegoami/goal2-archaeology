// #262: the OpenCode 2 shell-operand guard (tools/harness/opencode-guard, lib/opencode-guard.mjs) and
// the trusted reviewer policy (lib/opencode-policy.mjs). Ported from goal2 PR 178's
// tests/opencode_guard.test.mjs and adapted to this repository's reviewer grants. No model is called.
//
// Why the guard exists: OpenCode 1.18's shell tool asked for external_directory approval for the file
// operands of cat, rm, cp, mv, mkdir, touch, chmod, chown and cd; 2.0.28 checks only directory changes,
// so `cat ~/.ssh/id_x` would run under `shell * allow`. The guard restores the 1.18 check: an operand
// outside the worktree and outside the granted folders turns the shell request into `ask`, which a
// noninteractive run rejects. It is a static check of the command text, not an OS jail.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';

const { operandDirectories, externalEffect, matches } = await import(process.env.GUARD_SCANNER || '../tools/harness/opencode-guard/scanner.mjs');
const { setup, verifyInventory } = await import(process.env.GUARD_PLUGIN || '../tools/harness/opencode-guard/guard.mjs');
const { stageGuard, verifyPlugins, selectGuardPlugins, couldMatchPlugin, inspectConfig, pinGuardBinary, verifyGuardDependencies, catalogueParity } = await import(process.env.GUARD_HELPER || '../tools/harness/lib/opencode-guard.mjs');
const { reviewerPolicy, trustedReviewEnv, verifyReviewer, effectOf, contractProbes } = await import(process.env.GUARD_POLICY || '../tools/harness/lib/opencode-policy.mjs');
const agentFile = fileURLToPath(new URL('../.opencode/agents/reviewer.md', import.meta.url));
const policy = reviewerPolicy(agentFile);
const home = os.homedir();
const root = path.resolve(fs.mkdtempSync(path.join(os.tmpdir(), 'harness-guard-')));
const outside = path.join(home, 'harness-guard-test-not-granted');

test('the 1.18 FILES grammar finds quoted, nested, relative and multi-command operands; ls stays unchecked', async () => {
  for (const command of ['cat', 'rm', 'cp', 'mv', 'mkdir', 'touch', 'chmod', 'chown', 'cd']) {
    const directories = await operandDirectories(`${command} '${outside}/file'`, root, [root]);
    assert(directories.includes(outside), command + ' external operand');
  }
  assert.deepEqual(await operandDirectories(`ls '${outside}'`, root, [root]), []);
  assert.deepEqual(await operandDirectories(`echo $(cat '${outside}/file')`, root, [root]), [outside]);
  assert.deepEqual(await operandDirectories(`cat ./inside && cat '${outside}/file'`, root, [root]), [outside]);
  assert.deepEqual(await operandDirectories(`cat '${root}/inside'`, root, [root]), []);
  assert.deepEqual(await operandDirectories('cat ~/harness-guard-test-not-granted/file', root, [root]), [outside]);
  assert.deepEqual(await operandDirectories(`Get-Content -LiteralPath '${outside}/file'`, root, [root], '/usr/bin/pwsh'), [outside]);
  await assert.rejects(() => operandDirectories("cat 'broken", root, [root]), /unsupported shell grammar/);
});

// #262 round 2 (Sol's R1, R2): every word is evaluated to its static value first, in the command
// position and in the operands; what cannot be evaluated fails closed. Each row: a form, applied to an
// inside and an outside path (operands) or to the command name (with an outside operand).
const dirOut = outside; const fileOut = `${outside}/secret.txt`; const fileIn = `${root}/inside.txt`;
const frag = (p) => { const i = p.lastIndexOf('/'); return [p.slice(0, i), p.slice(i)]; };
const OPERAND_FORMS = {
  plain: (p) => p,
  'single quotes': (p) => `'${p}'`,
  'double quotes': (p) => `"${p}"`,
  'backslash escapes': (p) => p.replaceAll('/', '\\/'),
  'quoted directory fragment (R2)': (p) => { const [d, f] = frag(p); return `"${d}"${f}`; },
  'single-quoted directory fragment': (p) => { const [d, f] = frag(p); return `'${d}'${f}`; },
  'three fragments "a"\'b\'c': (p) => `"${p.slice(0, 3)}"'${p.slice(3, 8)}'${p.slice(8)}`,
  'ANSI-C quoting': (p) => `$'${p}'`,
  'ANSI-C hex escape for a slash': (p) => `$'${p.replaceAll('/', '\\x2f')}'`,
  'ANSI-C octal escape for a slash': (p) => `$'${p.replaceAll('/', '\\057')}'`,
  'empty fragments': (p) => `""${p}''`,
  'option value': (p) => `--target-directory=${p}`,
};
const COMMAND_FORMS = {
  'double-quoted name (R1)': '"cat"', 'single-quoted name': "'cat'", 'empty fragment c""at': 'c""at', "split c'a't": "c'a't",
  'backslash \\cat': '\\cat', "ANSI-C $'cat'": "$'cat'", 'path /bin/cat': '/bin/cat', 'relative ./cat': './cat',
};
const FAIL_CLOSED = {
  'parameter $X': '$X', 'parameter ${X}': '${X}', 'command substitution $(…)': '$(echo x)', 'backticks': '`echo x`',
  'arithmetic $((…))': '$((1))', 'process substitution': '<(true)', 'locale $"…"': '$"x"', '~user': '~nobody/x',
  'brace {a,b}': '{a,b}', 'expansion in double quotes': '"$X"', 'substitution in double quotes': '"$(echo x)"',
  'glob before a slash': '*/secret.txt', 'dot glob': '.*', 'bracket glob': '[ab]/x',
};
test('every static word form is evaluated before the check: operands, inside and outside', async () => {
  for (const [form, make] of Object.entries(OPERAND_FORMS)) {
    assert.deepEqual(await operandDirectories(`cat ${make(fileOut)}`, root, [root]), [dirOut], `${form}: outside`);
    assert.deepEqual(await operandDirectories(`cat ${make(fileIn)}`, root, [root]), [], `${form}: inside`);
  }
  assert.deepEqual(await operandDirectories('cat ~/harness-guard-test-not-granted/secret.txt', root, [root]), [dirOut], 'tilde');
  assert.deepEqual(await operandDirectories(`cat -- ${fileOut}`, root, [root]), [dirOut], 'after --');
  assert.deepEqual(await operandDirectories('cd', root, [root]), [home], 'a bare cd goes home');
});
test('every static form of the command name is the command it names', async () => {
  for (const [form, name] of Object.entries(COMMAND_FORMS)) {
    assert.deepEqual(await operandDirectories(`${name} ${fileOut}`, root, [root]), [dirOut], form);
    assert.deepEqual(await operandDirectories(`${name} inside.txt`, root, [root]), [], `${form}: inside`);
  }
});
test('a word that cannot be evaluated statically fails closed, as an operand and as the command name', async () => {
  for (const [form, word] of Object.entries(FAIL_CLOSED)) {
    await assert.rejects(() => operandDirectories(`cat ${word}`, root, [root]), /not statically resolvable|unsupported shell grammar/, `${form}: operand`);
    await assert.rejects(() => operandDirectories(`${word} ${fileOut}`, root, [root]), /not statically resolvable|unsupported shell grammar/, `${form}: command name`);
  }
});
test('a line continuation inside a word joins it, in the operand and in the command name', async () => {
  assert.deepEqual(await operandDirectories(`cat ${fileOut.slice(0, 6)}\\\n${fileOut.slice(6)}`, root, [root]), [dirOut], 'operand');
  assert.deepEqual(await operandDirectories(`c\\\nat ${fileOut}`, root, [root]), [dirOut], 'command name');
  assert.deepEqual(await operandDirectories(`cat "${fileOut.slice(0, 6)}\\\n${fileOut.slice(6)}"`, root, [root]), [dirOut], 'inside double quotes');
});
test('what the guard allowed stays allowed: inside globs, other commands\' dynamic words', async () => {
  for (const command of ['cat docs/*.md', 'cat src/a?.js', 'ls $X', 'echo "$HOME" $(date)', 'rm -rf build', 'chmod +x run.sh', `mkdir -p ${root}/out`, 'git -C x log', '[ -f x ] && cat x']) {
    assert.deepEqual(await operandDirectories(command, root, [root]), [], command);
  }
});

test('the translated reviewer keeps this repository\'s grants and asks for every other outside folder', () => {
  for (const directory of ['/tmp', '/tmp/opencode', '/tmp/another', path.join(home, 'goal2-review-tmp'), path.join(home, 'goal2-review-tmp/1-review-abcd'),
    '/etc', path.join(home, 'tools/dosbox-x-2024.03.01'), path.join(home, 'tools/dosbox-x-2024.03.01/bin')]) {
    assert.equal(externalEffect(directory, policy.profile.permissions), 'allow', directory);
  }
  // the harness's own files sit beside the scratch folder, outside the grant (#311)
  for (const directory of [path.join(home, 'goal2-review-tmp-harness'), path.join(home, 'projects/goal2-archaeology'), path.join(home, '.ssh'), '/var/lib', outside]) {
    assert.equal(externalEffect(directory, policy.profile.permissions), 'ask', directory);
  }
  assert(matches('plugin:/controlled/source', 'plug*'));
  assert(matches('cat', 'cat *'), 'a trailing " *" grant also matches the bare command');
  for (const [action, resource, effect] of contractProbes(home)) assert.equal(effectOf([{ action: '*', resource: '*', effect: 'allow' }, ...policy.profile.permissions], action, resource), effect, `${action} ${resource}`);
});

test('the reviewer file must keep its denies, its ask default and exactly its grants', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-policy-')); const file = path.join(dir, 'reviewer.md');
  const original = fs.readFileSync(agentFile, 'utf8');
  fs.writeFileSync(file, original.replaceAll('\n', '\r\n'));
  assert.deepEqual(reviewerPolicy(file).profile, policy.profile, 'CRLF keeps the same policy');
  for (const [before, after, why] of [
    ['    "*": ask\n', '', /external_directory "\*": ask/],
    ['  edit: deny', '  edit: allow', /edit/],
    ['    "git push *": deny', '    "git push *": allow', /git push/],
    ['    "gh pr merge *": deny\n', '', /gh pr merge/],
    ['    "/tmp/*": allow', '    "/home/*": allow', /grants differ|must keep/],
    ['    "/tmp/*": allow', '    "/tmp/*": allow\n    "/opt/*": allow', /grants differ/],
    ['    "/etc/timezone": allow', '    "/etc/*": allow', /must keep read/],
    ['permission:', 'permit:', /unsupported reviewer frontmatter root/],
    ['mode: all', 'mode: primary', /unsupported reviewer frontmatter root/],
    ['  glob:', '  webfetch:', /unsupported reviewer permission webfetch|must keep glob/],
    ['    "gh issue comment *": deny', '    "gh issue comment *": deny\n    "*": allow', /must keep/],
  ]) {
    assert(original.includes(before), `mutation applies: ${before}`);
    fs.writeFileSync(file, original.replace(before, after));
    assert.throws(() => reviewerPolicy(file), why, `${before} -> ${after}`);
  }
});

test('the loaded profile must end with exactly the trusted rules; the PR config never decides', () => {
  const env = trustedReviewEnv({ OPENCODE_CONFIG_DIR: '/untrusted', OPENCODE_CONFIG: '/untrusted', OPENCODE_CONFIG_CONTENT: 'untrusted', KEEP: 'yes' }, policy);
  assert.equal(env.OPENCODE_CONFIG_DIR, undefined); assert.equal(env.OPENCODE_CONFIG, undefined);
  assert.equal(env.OPENCODE_DISABLE_PROJECT_CONFIG, '1'); assert.equal(env.KEEP, 'yes');
  assert.deepEqual(JSON.parse(env.OPENCODE_CONFIG_CONTENT).agents.reviewer, policy.profile);
  const v2Defaults = JSON.parse(fs.readFileSync(new URL('fixtures/opencode/v2-live/run-3Ai73R/agents.json', import.meta.url))).data.find((a) => a.id === 'build').permissions.slice(0, 4);
  const profile = { id: 'reviewer', ...policy.profile, permissions: [...v2Defaults, ...policy.profile.permissions] };
  verifyReviewer(profile, policy, 'reviewer');
  verifyReviewer({ ...profile, permissions: [...profile.permissions, profile.permissions.at(-1)] }, policy, 'reviewer');
  assert.throws(() => verifyReviewer({ ...profile, permissions: [...profile.permissions, { action: 'edit', resource: '*', effect: 'allow' }] }, policy, 'reviewer'), /effective reviewer/);
  assert.throws(() => verifyReviewer({ ...profile, id: 'build' }, policy, 'reviewer'), /effective reviewer/);
  assert.throws(() => verifyReviewer({ ...profile, system: 'other' }, policy, 'reviewer'), /effective reviewer/);
});

function context() {
  const options = { id: 'guard.test', source: '/guard/server.js', nativeIDs: ['builtin'], permissions: policy.profile.permissions };
  const hooks = {};
  const ctx = {
    options, location: { directory: root },
    plugin: { list: async () => ({ data: [
      { id: 'builtin', source: { type: 'builtin' }, state: { status: 'active' } },
      { id: options.id, source: { type: 'local', path: options.source }, state: { status: 'active' } },
    ] }) },
  };
  for (const domain of ['tool', 'permission', 'shell']) ctx[domain] = {
    hook: async (name, callback) => {
      hooks[domain + '.' + name] = callback;
      return { dispose: async () => { delete hooks[domain + '.' + name]; } };
    },
  };
  return { ctx, hooks };
}

test('the native hooks turn an outside operand into ask, keep deny and ask, and refuse a missing or mismatched scan', async () => {
  const { ctx, hooks } = context();
  const cleanup = await setup(ctx);
  const call = { tool: 'shell', sessionID: 's', id: 'c', agent: 'reviewer', input: { command: `cat '${outside}/key'` } };
  await hooks['tool.execute.before'](call);
  await hooks['shell.create.before']({ command: call.input.command, cwd: root, shell: '/bin/bash' });
  for (const effect of ['allow', 'ask', 'deny']) {
    const event = { action: 'shell', sessionID: 's', agent: 'reviewer', source: { id: 'c' }, resources: [call.input.command], effect };
    await hooks['permission.evaluate'](event);
    assert.equal(event.effect, effect === 'deny' ? 'deny' : 'ask');
  }
  for (const [id, command] of [['in', 'cat inside'], ['tmp', 'cat /tmp/x'], ['scratch', `cat ${home}/goal2-review-tmp/1-review-abcd/log`], ['tz', 'cat /etc/timezone']]) {
    const allowed = { ...call, id, input: { command } };
    await hooks['tool.execute.before'](allowed);
    await hooks['shell.create.before']({ command, cwd: root, shell: '/bin/sh' });
    const event = { action: 'shell', sessionID: 's', agent: 'reviewer', source: { id }, resources: [command], effect: 'allow' };
    await hooks['permission.evaluate'](event);
    assert.equal(event.effect, 'allow', command);
    await hooks['tool.execute.after'](allowed);
  }
  const allowed = { ...call, id: 'allowed', input: { command: 'cat inside' } };
  await hooks['tool.execute.before'](allowed);
  await hooks['shell.create.before']({ command: allowed.input.command, cwd: root, shell: '/bin/sh' });
  const template = { action: 'shell', sessionID: 's', agent: 'reviewer', source: { id: 'allowed' }, resources: ['cat inside'], effect: 'allow' };
  for (const change of [{ agent: 'other' }, { source: { id: 'missing' } }, { resources: ['cat /etc/file'] }]) {
    const changed = { ...template, ...change };
    await hooks['permission.evaluate'](changed);
    assert.equal(changed.effect, 'ask', JSON.stringify(change));
  }
  await hooks['tool.execute.after'](allowed);
  const missing = { ...template };
  await hooks['permission.evaluate'](missing);
  assert.equal(missing.effect, 'ask', 'a call with no scan is asked');
  await cleanup();
});

test('the actual shell and cwd choose the grammar; an unknown or absent shell cannot make an allow', async () => {
  for (const shell of ['/usr/bin/pwsh', '/custom/unknown-shell', null]) {
    const { ctx, hooks } = context();
    const cleanup = await setup(ctx);
    const command = shell === '/usr/bin/pwsh' ? `Get-Content -LiteralPath ${outside}/key` : 'cat inside';
    await hooks['tool.execute.before']({ tool: 'shell', sessionID: 's', id: 'c', agent: 'reviewer', input: { command } });
    if (shell) await hooks['shell.create.before']({ command, cwd: root, shell });
    const event = { action: 'shell', sessionID: 's', agent: 'reviewer', source: { id: 'c' }, resources: [command], effect: 'allow' };
    await hooks['permission.evaluate'](event);
    assert.equal(event.effect, 'ask', String(shell));
    await cleanup();
  }
});

test('the trusted activation overlay pins dependencies and rejects foreign, failed, duplicate or missing plugins', () => {
  const guard = stageGuard(root, policy);
  const env = trustedReviewEnv({}, policy, 'reviewer', guard);
  const content = JSON.parse(env.OPENCODE_CONFIG_CONTENT);
  assert.equal(content.plugins[0], '-*', 'arbitrary global hooks must be disabled on every reload');
  assert.equal(content.plugins.at(-1).package, guard.directory, 'trusted guard must be activated');
  assert.deepEqual(content.experimental.policies, [
    { action: 'integration.use', resource: 'plugin:*', effect: 'deny' },
    { action: 'integration.use', resource: 'plugin:' + guard.directory, effect: 'allow' },
  ], 'untrusted sources must be denied before import');
  assert.equal(env.OPENCODE_FILEWATCHER_DISABLE, '1');
  const rows = guard.nativeIDs.map((id) => ({ id, source: { type: 'builtin' }, state: { status: 'active' } }));
  rows.push({ id: guard.id, source: { type: 'local', path: guard.source }, state: { status: 'active' } });
  verifyPlugins(rows, guard);
  verifyInventory(rows, guard);
  for (const invalid of [
    rows.slice(0, -1), [...rows, { id: 'foreign', source: { type: 'package' }, state: { status: 'active' } }],
    rows.map((row, number) => number ? row : { ...row, state: { status: 'failed' } }),
    rows.map((row, number) => number ? row : { ...row, source: { type: 'package' } }),
  ]) assert.throws(() => verifyPlugins(invalid, guard), /plugin|guard|builtin/);
  const baseline = rows.filter((row) => row.source.type === 'builtin' && row.id !== 'opencode.warming');
  verifyPlugins(baseline, guard, { baseline: true });
  selectGuardPlugins(guard, baseline.map((row) => row.id));
  assert(!guard.plugins.includes('opencode.warming'), 'native disables must not be re-enabled');
});

test('the config survey rejects every allow glob that could match a plugin, and unverified shells', () => {
  const guard = stageGuard(root, policy);
  const trusted = { type: 'document', info: JSON.parse(trustedReviewEnv({}, policy, 'reviewer', guard).OPENCODE_CONFIG_CONTENT) };
  for (const resource of ['*', 'plugin:*', 'plugin*', 'plug*', '*:*', 'p?ugin:*', 'PLUGIN*']) {
    assert(couldMatchPlugin(resource));
    assert.throws(() => inspectConfig([{ type: 'document', info: { experimental: { policies: [{ action: 'integration.use', resource, effect: 'allow' }] } } }, trusted], guard), /higher-authority plugin allow policy/);
  }
  for (const resource of ['mcp:*', 'skill:*', 'provider:*']) assert.equal(couldMatchPlugin(resource), false);
  assert.throws(() => inspectConfig([{ type: 'document', info: { shell: '/custom/unknown-shell' } }, trusted], guard), /configured shell/);
  assert.throws(() => inspectConfig([{ type: 'document', info: { plugins: ['some-npm-plugin'] } }, trusted], guard), /external executable plugins/);
  assert.equal(inspectConfig([{ type: 'document', info: { shell: '/usr/bin/pwsh', plugins: ['-opencode.warming'] } }, trusted], guard).shell, '/usr/bin/pwsh');
  // the owner's global config of this machine, as the live capture saw it: providers only, no plugin
  const live = JSON.parse(fs.readFileSync(new URL('fixtures/opencode/v2-live/run-3Ai73R/agents.json', import.meta.url)));
  assert(live.location.directory);
});

test('the nonbilling simulator is admitted by the hash of the stub as it is (update the pin with the stub)', async () => {
  const { testStubSHA256 } = await import(process.env.GUARD_HELPER || '../tools/harness/lib/opencode-guard.mjs');
  const { createHash } = await import('node:crypto');
  const stubFile = new URL('helpers/opencode-stub.mjs', import.meta.url);
  assert.equal(createHash('sha256').update(fs.readFileSync(stubFile)).digest('hex'), testStubSHA256, 'lib/opencode-guard.mjs testStubSHA256 must name tests/helpers/opencode-stub.mjs');
  assert.equal(pinGuardBinary({ exe: process.execPath, prefix: [fileURLToPath(stubFile)] }), 'explicit hashed Node-test simulator; no native enforcement claim');
});

test('a wrapper or an unaudited binary fails closed; missing dependencies are never fetched', () => {
  assert.throws(() => pinGuardBinary({ exe: process.execPath, prefix: [] }), /audited OpenCode/);
  assert.throws(() => pinGuardBinary({ exe: process.execPath, prefix: [fileURLToPath(import.meta.url)] }), /wrapped native binaries/);
  assert.throws(() => verifyGuardDependencies(root), /npm ci --prefix tools\/harness\/opencode-guard --ignore-scripts/);
});

test('full catalogue parity waits for delayed providers and fails within its deadline', async () => {
  const selected = { id: 'selected', modelID: 'selected', providerID: 'minimax', family: 'minimax', enabled: true, variants: [] };
  const custom = { ...selected, id: 'custom', providerID: 'custom' };
  let polls = 0;
  const baseline = { request: async () => ({ data: [selected, custom] }) };
  const guarded = { request: async () => ({ data: ++polls < 4 ? [selected] : [selected, custom] }) };
  const result = await catalogueParity(baseline, guarded, { timeoutMs: 500, stableMs: 20, pollMs: 10 });
  assert.equal(result.length, 2, 'nonselected custom provider must survive parity');
  assert(polls >= 5, 'selected readiness must not end discovery');
  const start = Date.now();
  await assert.rejects(catalogueParity(baseline, { request: async () => ({ data: [selected] }) }, { timeoutMs: 40, stableMs: 10, pollMs: 5 }), /startup deadline/);
  assert(Date.now() - start < 300, 'catalogue parity respects caller deadline');
});

// Each guard above fails its own assertion when it is removed (a scratch copy is mutated, never the tracked file).
test('guard mutation controls fail the operand, approval, activation, preload and policy assertions', () => {
  for (const [name, file, before, after, pattern, assertion] of [
    ['operand loss', 'opencode-guard/scanner.mjs', 'directories.add(isDirectory ? absolute : path.dirname(absolute));', ';', 'FILES grammar', 'cat external operand'],
    ['approval loss', 'opencode-guard/guard.mjs', "if (!matches || scanned.outcome !== 'allow') {", 'if (false) {', 'native hooks turn', 'Expected values to be strictly equal'],
    ['activation loss', 'lib/opencode-guard.mjs', 'package: guard.directory,', "package: '/untrusted-source',", 'trusted activation overlay', 'trusted guard must be activated'],
    ['catalogue readiness loss', 'lib/opencode-guard.mjs', 'const deadline = Date.now() + timeoutMs;\n  let previous;', "return catalogueProjection((await baseline.request('/api/model')).data);\n  let previous;", 'full catalogue parity', 'selected readiness must not end discovery'],
    // the static word normalizer (round 2): each stage removed makes its own row fail
    ['single-quote stage', 'opencode-guard/scanner.mjs', "case 'raw_string': for (const ch of node.text.slice(1, -1))", "case 'raw_string': for (const ch of node.text)", 'every static word form', 'single quotes: outside'],
    ['double-quote stage', 'opencode-guard/scanner.mjs', `if (child.type === '"') continue;`, `if (child.type === '"') { out.push('"', false); continue; }`, 'every static word form', 'double quotes: outside'],
    ['ANSI-C stage', 'opencode-guard/scanner.mjs', "case 'ansi_c_string': ansiC(node.text, out); return;", "case 'ansi_c_string': for (const ch of node.text) out.push(ch, false); return;", 'every static word form', 'ANSI-C quoting: outside'],
    ['ANSI-C hex stage', 'opencode-guard/scanner.mjs', 'if ((m = /^x([0-9A-Fa-f]{1,2})/.exec(body.slice(i))))', 'if (false)', 'every static word form', 'not statically resolvable'],
    ['concatenation stage', 'opencode-guard/scanner.mjs', 'for (let i = 0; i < node.childCount; i++) collect(node.child(i), out, first && i === 0);', 'collect(node.child(0), out, first);', 'every static word form', 'quoted directory fragment (R2): outside'],
    ['backslash stage', 'opencode-guard/scanner.mjs', "if (c === '\\\\') {\n      if (i + 1 >= text.length)", "if (false) {\n      if (i + 1 >= text.length)", 'every static word form', 'backslash escapes: outside'],
    ['tilde stage', 'opencode-guard/scanner.mjs', 'for (const ch of os.homedir()) out.push(ch, false);', "out.push('~', false);", 'every static word form', 'tilde'],
    ['command-name stage (R1)', 'opencode-guard/scanner.mjs', 'const name = path.posix.basename(head.value);', 'const name = nameNode.text;', 'static form of the command name', 'double-quoted name (R1)'],
    ['continuation stage', 'opencode-guard/scanner.mjs', 'if (!ps && !cmd) command = joinContinuations(command);', '', 'line continuation', 'operand'],
    ['fail-closed default', 'opencode-guard/scanner.mjs', 'default: unresolved(node.type);', 'default: return;', 'cannot be evaluated statically', 'Missing expected rejection'],
    ['fail-closed double-quoted expansion', 'opencode-guard/scanner.mjs', "if (child.type !== 'string_content') unresolved(`${child.type} in a double-quoted string`);", "if (child.type !== 'string_content') continue;", 'cannot be evaluated statically', 'expansion in double quotes'],
    ['glob-before-slash stage', 'opencode-guard/scanner.mjs', "if (value.indexOf('/', globAt) >= 0) unresolved('glob before a path separator');", '', 'cannot be evaluated statically', 'glob before a slash'],
    ['dot-glob stage', 'opencode-guard/scanner.mjs', "if (value[slash + 1] === '.' || value[slash + 1] === '[') unresolved('glob that could match . or ..');", '', 'cannot be evaluated statically', 'dot glob'],
    ['option-value stage', 'opencode-guard/scanner.mjs', 'if (eq < 0) continue; // a flag', 'continue; // a flag', 'every static word form', 'option value: outside'],
    ['preload loss', 'lib/opencode-policy.mjs', "resource: 'plugin:*', effect: 'deny'", "resource: 'unrelated:*', effect: 'deny'", 'trusted activation overlay', 'untrusted sources must be denied before import'],
    ['ask-default loss', 'lib/opencode-policy.mjs', "if (!permissions.some((r) => r.action === 'external_directory' && r.resource === '*' && r.effect === 'ask')) {", 'if (false) {', 'must keep its denies', 'must keep external_directory'],
    ['grant contract loss', 'lib/opencode-policy.mjs', 'if (JSON.stringify(grants) !== JSON.stringify(allowedGrants(home)))', 'if (false)', 'must keep its denies', 'Missing expected exception'],
  ]) {
    const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-guard-mutant-'));
    try {
      fs.cpSync(new URL('../tools/harness/lib/', import.meta.url), path.join(scratch, 'lib'), { recursive: true });
      fs.cpSync(new URL('../tools/harness/opencode-guard/', import.meta.url), path.join(scratch, 'opencode-guard'), { recursive: true });
      const target = path.join(scratch, file);
      const original = fs.readFileSync(target, 'utf8');
      assert(original.includes(before), `${name}: mutation applies`);
      fs.writeFileSync(target, original.replace(before, after));
      const environment = { ...process.env }; delete environment.NODE_TEST_CONTEXT;
      const result = spawnSync(process.execPath, ['--test', '--test-name-pattern=' + pattern, fileURLToPath(import.meta.url)], {
        encoding: 'utf8', timeout: 30000, env: { ...environment,
          GUARD_SCANNER: pathToFileURL(path.join(scratch, 'opencode-guard/scanner.mjs')).href,
          GUARD_PLUGIN: pathToFileURL(path.join(scratch, 'opencode-guard/guard.mjs')).href,
          GUARD_HELPER: pathToFileURL(path.join(scratch, 'lib/opencode-guard.mjs')).href,
          GUARD_POLICY: pathToFileURL(path.join(scratch, 'lib/opencode-policy.mjs')).href,
        },
      });
      assert.equal(result.status, 1, `${name}: ${result.stdout.slice(-300)}`);
      assert((result.stdout + result.stderr).includes(assertion), name + ' intended assertion');
      assert(!/ERR_MODULE_NOT_FOUND|MODULE_NOT_FOUND|timed out/.test(result.stdout + result.stderr), name + ' must fail on behaviour');
    } finally { fs.rmSync(scratch, { recursive: true, force: true }); }
  }
});
