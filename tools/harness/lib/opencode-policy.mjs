// The reviewer's permissions for an OpenCode 2 run, taken from the LAUNCHING checkout's
// .opencode/agents/reviewer.md, never from the PR under review (#262; ported from goal2 PR 178's
// opencode-policy.mjs and adapted to this repository's reviewer, whose grants differ).
//
// OpenCode 2 no longer reads a v1 agent file's `permission:` map; it takes ordered
// { action, resource, effect } rules, last match wins, and puts its own defaults FIRST, beginning with
// `* * allow` (tests/fixtures/opencode/v2-live/run-3Ai73R/agents.json). So the frontmatter is translated
// rule by rule, in order, with v2's action names (the v2 binary's own default ruleset names read, grep,
// glob, shell, subagent, edit, external_directory, webfetch, websearch, browser), and passed through
// OPENCODE_CONFIG_CONTENT. Because v2's default is allow, the reviewer file must say
// `external_directory: "*": ask` itself (v1's default was ask): reviewerPolicy refuses a file without it.
//
// The contract is checked by evaluating the translated rules, not by pinning their text: whatever the
// file says, edits and subagents are denied, an unknown directory outside the worktree is asked (which a
// noninteractive run rejects), pushes, commits, merges and posts are denied, /etc stays closed but for
// /etc/timezone, and the outside grants are exactly the ones tests/test_agent_permissions.py allows.
import fs from 'node:fs';
import os from 'node:os';
import { hash, OpenCodeInfraError } from './opencode-transport.mjs';

const ACTION = { bash: 'shell', task: 'subagent', edit: 'edit', external_directory: 'external_directory', read: 'read', grep: 'grep', glob: 'glob' };

// OpenCode 2's wildcard match (util/wildcard.ts as goal2's guard ported it): `*` any run, `?` one
// character, and a trailing ` *` also matches the bare command.
export function matches(input, pattern) {
  const normalized = String(input).replaceAll('\\', '/');
  let escaped = String(pattern).replaceAll('\\', '/').replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.');
  if (escaped.endsWith(' .*')) escaped = escaped.slice(0, -3) + '( .*)?';
  return new RegExp('^' + escaped + '$', process.platform === 'win32' ? 'si' : 's').test(normalized);
}
// The effect of ordered rules for one request: the last rule whose action and resource match.
export function effectOf(rules, action, resource) {
  return rules.findLast((r) => matches(action, r.action) && matches(resource, r.resource))?.effect ?? 'ask';
}

// The outside grants this repository allows (tests/test_agent_permissions.py says why each is there).
export function allowedGrants(home) {
  return ['/tmp/opencode/*', '/tmp', '/tmp/*', `${home}/goal2-review-tmp`, `${home}/goal2-review-tmp/*`, '/etc/*',
    `${home}/tools/dosbox-x-2024.03.01`, `${home}/tools/dosbox-x-2024.03.01/*`].sort();
}
const WRITE_DENIES = ['git push origin main', 'git -C /x push origin main', 'git commit -m x', 'git -C /x commit -m x', 'gh pr merge 1',
  'gh pr comment 1 --body x', 'gh pr review 1 --approve', 'gh pr edit 1', 'gh issue edit 1', 'gh issue comment 1 --body x'];

// The checks every translated profile must pass, as [action, resource, effect]. Exported for the tests.
export function contractProbes(home) {
  return [
    ['edit', 'README.md', 'deny'], ['edit', '/tmp/x', 'deny'],
    ['subagent', 'general', 'deny'],
    ['external_directory', `${home}/.ssh/*`, 'ask'], [ 'external_directory', `${home}/projects/goal2-archaeology/*`, 'ask'], ['external_directory', '/var/*', 'ask'],
    ['external_directory', '/tmp/*', 'allow'], ['external_directory', `${home}/goal2-review-tmp/*`, 'allow'],
    ...WRITE_DENIES.map((c) => ['shell', c, 'deny']),
    ['shell', 'cat /etc/hostname', 'deny'], ['shell', 'printf x > /etc/timezone', 'deny'], ['shell', 'cat /etc/timezone', 'allow'],
    ['read', '/etc/hostname', 'deny'], ['read', '/etc', 'deny'], ['read', '/etc/timezone', 'allow'],
    ['grep', 'timezone', 'deny'], ['glob', '*', 'deny'], ['browser', 'https://example.invalid', 'deny'],
  ];
}

export function reviewerPolicy(agentFile, { home = process.env.HOME || os.homedir() } = {}) {
  const rawSource = fs.readFileSync(agentFile, 'utf8');
  const source = rawSource.replaceAll('\r\n', '\n');
  const match = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(source);
  if (!match) throw new Error('reviewer frontmatter is missing');
  const [, front, system] = match;
  const permissions = []; let action; let inPermissions = false; const roots = new Set();
  for (const line of front.split('\n')) {
    let m;
    if (!line.trim()) continue;
    if (!/^\s/.test(line)) {
      const root = /^(description: .+|mode: all|permission:)$/.exec(line);
      const name = line.split(':')[0];
      if (!root || roots.has(name)) throw new Error('unsupported reviewer frontmatter root');
      roots.add(name); inPermissions = name === 'permission'; action = null; continue;
    }
    if (!inPermissions) throw new Error('reviewer permission outside permission section');
    if ((m = /^ {2}([a-z_]+): (allow|ask|deny)$/.exec(line))) {
      if (!ACTION[m[1]]) throw new Error(`unsupported reviewer permission ${m[1]}`);
      permissions.push({ action: ACTION[m[1]], resource: '*', effect: m[2] }); action = null;
    } else if ((m = /^ {2}([a-z_]+):$/.exec(line))) {
      action = ACTION[m[1]]; if (!action) throw new Error(`unsupported reviewer permission ${m[1]}`);
    } else if ((m = /^ {4}"([^"\n]+)": (allow|ask|deny)$/.exec(line))) {
      if (!action) throw new Error('reviewer permission resource has no action');
      permissions.push({ action, resource: m[1].replace(/^~(?=\/|$)/, home), effect: m[2] });
    } else throw new Error('unsupported reviewer permission syntax');
  }
  if (!['description', 'mode', 'permission'].every((name) => roots.has(name))) throw new Error('reviewer frontmatter must define description, mode and permission');
  // v1 had no browser tool; v2 has one, and the read-only reviewer never needs it (goal2 T72a).
  permissions.push({ action: 'browser', resource: '*', effect: 'deny' });
  if (!permissions.some((r) => r.action === 'external_directory' && r.resource === '*' && r.effect === 'ask')) {
    throw new Error('reviewer must keep external_directory "*": ask (OpenCode 2 defaults to allow)');
  }
  // The rules as v2 will hold them: its defaults first, then these (goal2's live profile, and ours).
  const effective = [{ action: '*', resource: '*', effect: 'allow' }, ...permissions];
  for (const [a, resource, effect] of contractProbes(home)) {
    const got = effectOf(effective, a, resource);
    if (got !== effect) throw new Error(`reviewer must keep ${a} ${resource} ${effect} (the file gives ${got})`);
  }
  const grants = permissions.filter((r) => r.action === 'external_directory' && r.effect === 'allow').map((r) => r.resource).sort();
  if (JSON.stringify(grants) !== JSON.stringify(allowedGrants(home))) throw new Error('reviewer external grants differ from the allowed /tmp, scratch, /etc and DOSBox-X grants');
  return { sourceSHA256: hash(rawSource), profile: { mode: 'all', hidden: false, system: system.trim(), permissions } };
}

export function trustedReviewEnv(env, policy, agent = 'reviewer', guard, { baseline = false } = {}) {
  const next = { ...env };
  for (const key of ['OPENCODE_CONFIG_DIR', 'OPENCODE_CONFIG', 'OPENCODE_CONFIG_CONTENT', 'OPENCODE_CONFIG_PROJECT_DISABLE']) delete next[key];
  const content = { agents: { [agent]: policy.profile } };
  if (guard) {
    // Block external plugin modules before they are imported (goal2: native 2.0.28 managed policy).
    content.experimental = { policies: [
      { action: 'integration.use', resource: 'plugin:*', effect: 'deny' },
      { action: 'integration.use', resource: 'plugin:' + guard.directory, effect: 'allow' },
    ] };
    if (!baseline) content.plugins = guard.plugins;
  }
  return {
    ...next, OPENCODE_DISABLE_PROJECT_CONFIG: '1',
    // Freeze this run's loaded configuration (goal2: native server process / filesystem watcher).
    ...(guard ? { OPENCODE_FILEWATCHER_DISABLE: '1', OPENCODE_DISABLE_FILEWATCHER: '1' } : {}),
    OPENCODE_CONFIG_CONTENT: JSON.stringify(content),
  };
}

// The profile OpenCode actually loaded must end with exactly the trusted rules (its own defaults come
// first); consecutive duplicate rules have the same last-match effect, so they are folded.
export function verifyReviewer(profile, policy, agent) {
  const expected = policy.profile;
  const canonical = (rules) => rules.map(({ action, resource, effect }) => ({ action, resource, effect })).filter((r, i, rows) => i === 0 || JSON.stringify(r) !== JSON.stringify(rows[i - 1]));
  const actualRules = canonical(profile.permissions); const expectedRules = canonical(expected.permissions);
  if (profile.id !== agent || profile.mode !== expected.mode || profile.hidden !== false || profile.system !== expected.system || JSON.stringify(actualRules.slice(-expectedRules.length)) !== JSON.stringify(expectedRules)) {
    throw new OpenCodeInfraError('profile', 'effective reviewer differs from the trusted permission contract');
  }
}
