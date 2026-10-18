// #262: ported from diegoami/goal2 PR 178 (squash e0cab8b); its [designed/confirmed: T72…] tags cite that repository's tasks and measurements/.
// [confirmed: OpenCode v1.18.32 packages/opencode/src/tool/shell.ts; rework1 source hashes]
// Copyright (c) 2025 opencode; MIT notice retained in LICENSE.opencode.
// Adapt its FILES/path operand selection, retaining best-effort static-path semantics, not an OS jail.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { Parser, Language } from 'web-tree-sitter';
const require = createRequire(import.meta.url);
const CWD = new Set(["cd", "chdir", "popd", "pushd", "push-location", "set-location"])
const FILES = new Set([
  ...CWD,
  "rm",
  "cp",
  "mv",
  "mkdir",
  "touch",
  "chmod",
  "chown",
  "cat",
  // Leave PowerShell aliases out for now. Common ones like cat/cp/mv/rm/mkdir
  // already hit the entries above, and alias normalization should happen in one
  // place later so we do not risk double-prompting.
  "get-content",
  "set-content",
  "add-content",
  "copy-item",
  "move-item",
  "remove-item",
  "new-item",
  "rename-item",
])
const CMD_FILES = new Set([
  "copy",
  "del",
  "dir",
  "erase",
  "md",
  "mkdir",
  "move",
  "rd",
  "ren",
  "rename",
  "rmdir",
  "type",
])
const FLAGS = new Set(["-destination", "-literalpath", "-path"])
const SWITCHES = new Set(["-confirm", "-debug", "-force", "-nonewline", "-recurse", "-verbose", "-whatif"])

function parts(node) {
  const out = []
  for (let i = 0; i < node.childCount; i++) {
    const child = node.child(i)
    if (!child) continue
    if (child.type === "command_elements") {
      for (let j = 0; j < child.childCount; j++) {
        const item = child.child(j)
        if (!item || item.type === "command_argument_sep" || item.type === "redirection") continue
        out.push({ type: item.type, text: item.text })
      }
      continue
    }
    if (
      child.type !== "command_name" &&
      child.type !== "command_name_expr" &&
      child.type !== "word" &&
      child.type !== "string" &&
      child.type !== "raw_string" &&
      child.type !== "concatenation"
    ) {
      continue
    }
    out.push({ type: child.type, text: child.text })
  }
  return out
}

function unquote(text) {
  if (text.length < 2) return text
  const first = text[0]
  const last = text[text.length - 1]
  if ((first === '"' || first === "'") && first === last) return text.slice(1, -1)
  return text
}

function home(text) {
  if (text === "~") return os.homedir()
  if (text.startsWith("~/") || text.startsWith("~\\")) return path.join(os.homedir(), text.slice(2))
  return text
}

function envValue(key) {
  if (process.platform !== "win32") return process.env[key]
  const name = Object.keys(process.env).find((item) => item.toLowerCase() === key.toLowerCase())
  return name ? process.env[name] : undefined
}

function auto(key, cwd, shell) {
  const name = key.toUpperCase()
  if (name === "HOME") return os.homedir()
  if (name === "PWD") return cwd
  if (name === "PSHOME") return path.dirname(shell)
}

function expand(text, cwd, shell) {
  const out = unquote(text)
    .replace(/\$\{env:([^}]+)\}/gi, (_, key) => envValue(key) || "")
    .replace(/\$env:([A-Za-z_][A-Za-z0-9_]*)/gi, (_, key) => envValue(key) || "")
    .replace(/\$(HOME|PWD|PSHOME)(?=$|[\\/])/gi, (_, key) => auto(key, cwd, shell) || "")
  return home(out)
}

function provider(text) {
  const match = text.match(/^([A-Za-z]+)::(.*)$/)
  if (match) {
    if (match[1].toLowerCase() !== "filesystem") return
    return match[2]
  }
  const prefix = text.match(/^([A-Za-z]+):(.*)$/)
  if (!prefix) return text
  if (prefix[1].length === 1) return text
  return
}

function dynamic(text, ps) {
  if (text.startsWith("(") || text.startsWith("@(")) return true
  if (text.includes("$(") || text.includes("${") || text.includes("`")) return true
  if (ps) return /\$(?!env:)/i.test(text)
  return text.includes("$")
}

function prefix(text) {
  const match = /[?*[]/.exec(text)
  if (!match) return text
  if (match.index === 0) return
  return text.slice(0, match.index)
}

function pathArgs(list, ps, cmd = false) {
  if (!ps) {
    return list
      .slice(1)
      .filter(
        (item) =>
          !item.text.startsWith("-") &&
          !(cmd && item.text.startsWith("/")) &&
          !(list[0]?.text === "chmod" && item.text.startsWith("+")),
      )
      .map((item) => item.text)
  }

  const out = []
  let want = false
  for (const item of list.slice(1)) {
    if (want) {
      out.push(item.text)
      want = false
      continue
    }
    if (item.type === "command_parameter") {
      const flag = item.text.toLowerCase()
      if (SWITCHES.has(flag)) continue
      want = FLAGS.has(flag)
      continue
    }
    out.push(item.text)
  }
  return out
}


let ready;
async function parsers() {
  return ready ||= (async () => {
    await Parser.init();
    const root = name => path.dirname(require.resolve(name + '/package.json'));
    const bash = new Parser();
    bash.setLanguage(await Language.load(path.join(root('tree-sitter-bash'), 'tree-sitter-bash.wasm')));
    const ps = new Parser();
    ps.setLanguage(await Language.load(path.join(root('tree-sitter-powershell'), 'tree-sitter-powershell.wasm')));
    return { bash, ps };
  })();
}
export function contains(root, file) {
  const relative = path.relative(root, file);
  return relative === '' || (relative !== '..' && !relative.startsWith('..' + path.sep) && !path.isAbsolute(relative));
}
// [confirmed: native2.0.28 util/wildcard.ts; source hashes] Same ordered-rule matching semantics.
export function matches(input, pattern) {
  const normalized = input.replaceAll('\\', '/');
  let escaped = pattern.replaceAll('\\', '/').replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*/g, '.*').replace(/\?/g, '.');
  if (escaped.endsWith(' .*')) escaped = escaped.slice(0, -3) + '( .*)?';
  return new RegExp('^' + escaped + '$', process.platform === 'win32' ? 'si' : 's').test(normalized);
}
export function externalEffect(directory, rules) {
  const resource = path.join(directory, '*').replaceAll('\\', '/');
  return rules.findLast(rule => rule.action === 'external_directory' && matches(resource, rule.resource))?.effect || 'ask';
}
// #262 round 2 (Sol's R1, R2 on PR 332): every Bash word is evaluated to its static value before any
// check, in the command position and in the operands; a word whose value cannot be established
// statically makes the whole scan fail, which the guard turns into `ask` (a noninteractive run then
// rejects). The 1.18 code compared the raw source text, so a quoted command name or a quoted path
// fragment escaped the check. Static forms: plain words with backslash escapes, '...', "..." without
// expansions, $'...' with the escapes decoded below, adjacent fragments, and a leading ~ or ~/.
// Everything else fails closed: $VAR, ${...}, $(...), `...`, $((...)), <(...), $"...", ~user, an
// unquoted { or }, and a glob whose pattern could leave its directory.
export class Unresolved extends Error {}
const unresolved = (why) => { throw new Unresolved(`not statically resolvable: ${why}`); };
const GLOB = new Set(['*', '?', '[']);
// A plain word: backslash escapes; unescaped glob characters are kept and marked (positions in `glob`).
function plainWord(text, out) {
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '\\') {
      if (i + 1 >= text.length) unresolved('trailing backslash');
      if (text[i + 1] !== '\n') out.push(text[i + 1], false); // a line continuation is nothing
      i++;
    } else if (c === '$' || c === '`') unresolved('expansion');
    else if (c === '{' || c === '}') unresolved('brace');
    else out.push(c, GLOB.has(c));
  }
}
const ANSI = { a: '\x07', b: '\b', e: '\x1b', E: '\x1b', f: '\f', n: '\n', r: '\r', t: '\t', v: '\v', '\\': '\\', "'": "'", '"': '"', '?': '?' };
function ansiC(text, out) {
  const body = text.slice(2, -1);
  for (let i = 0; i < body.length; i++) {
    const c = body[i];
    if (c !== '\\') { out.push(c, false); continue; }
    const n = body[++i];
    if (n === undefined) unresolved('$\'\' trailing backslash');
    if (ANSI[n] !== undefined) { out.push(ANSI[n], false); continue; }
    let m;
    if ((m = /^x([0-9A-Fa-f]{1,2})/.exec(body.slice(i)))) { out.push(String.fromCharCode(parseInt(m[1], 16)), false); i += m[0].length - 1; continue; }
    if ((m = /^[0-7]{1,3}/.exec(body.slice(i)))) { out.push(String.fromCharCode(parseInt(m[0], 8) & 0xff), false); i += m[0].length - 1; continue; }
    unresolved(`$'' escape \\${n}`);
  }
}
// The characters of one word node into `out` ({ chars, glob }).
function collect(node, out, first) {
  switch (node.type) {
    case 'word': case 'number': {
      if (first && node.text.startsWith('~')) {
        const m = /^~(\/|$)/.exec(node.text);
        if (!m) unresolved('~user');
        for (const ch of os.homedir()) out.push(ch, false);
        plainWord(node.text.slice(1), out);
      } else plainWord(node.text, out);
      return;
    }
    case 'raw_string': for (const ch of node.text.slice(1, -1)) out.push(ch, false); return;
    case 'ansi_c_string': ansiC(node.text, out); return;
    case 'string':
      for (let i = 0; i < node.childCount; i++) {
        const child = node.child(i);
        if (child.type === '"') continue;
        if (child.type !== 'string_content') unresolved(`${child.type} in a double-quoted string`);
        const text = child.text;
        for (let j = 0; j < text.length; j++) {
          if (text[j] === '\\' && '$`"\\\n'.includes(text[j + 1] ?? '')) { if (text[j + 1] !== '\n') out.push(text[j + 1], false); j++; }
          else if (text[j] === '$' || text[j] === '`') unresolved('expansion in a double-quoted string');
          else out.push(text[j], false);
        }
      }
      return;
    case 'concatenation':
      for (let i = 0; i < node.childCount; i++) collect(node.child(i), out, first && i === 0);
      return;
    default: unresolved(node.type);
  }
}
// The static value of a word node: { value, globAt } (globAt: index of the first unquoted glob character, or -1).
export function staticWord(node) {
  const chars = []; let globAt = -1;
  const out = { push(ch, glob) { if (glob && globAt < 0) globAt = chars.length; chars.push(ch); } };
  collect(node, out, true);
  return { value: chars.join(''), globAt };
}
const WORD_TYPES = new Set(['word', 'number', 'string', 'raw_string', 'ansi_c_string', 'concatenation', 'simple_expansion', 'expansion', 'command_substitution', 'process_substitution', 'arithmetic_expansion', 'translated_string', 'brace_expression']);
// The words of a command: its name and arguments (redirections and assignments are not arguments);
// any other child (a stray `$` of $"...", an unknown node) fails closed.
function bashWords(node) {
  const words = [];
  for (let i = 0; i < node.childCount; i++) {
    const child = node.child(i);
    if (child.type === 'command_name') { words.push(child.child(0)); continue; }
    if (child.type === 'variable_assignment' || child.type === 'file_redirect' || child.type === 'herestring_redirect' || child.type === 'heredoc_redirect' || child.type === 'comment') continue;
    if (!WORD_TYPES.has(child.type)) unresolved(`${child.type} in a command`);
    words.push(child);
  }
  return words;
}
// The file a static operand can name: its directory for a glob whose pattern stays in its last path
// component and cannot match `.` or `..`; any other glob fails closed.
function operandPath({ value, globAt }) {
  if (globAt < 0) return { file: value, glob: false };
  const slash = value.lastIndexOf('/', globAt);
  if (value.indexOf('/', globAt) >= 0) unresolved('glob before a path separator');
  if (value[slash + 1] === '.' || value[slash + 1] === '[') unresolved('glob that could match . or ..');
  return { file: slash < 0 ? '.' : value.slice(0, slash + 1) || '/', glob: true };
}
async function bashOperandDirectories(tree, cwd, roots, directories) {
  for (const node of tree.rootNode.descendantsOfType('command')) {
    let nameNode = null;
    for (let i = 0; i < node.childCount && !nameNode; i++) if (node.child(i).type === 'command_name') nameNode = node.child(i).child(0);
    if (!nameNode) continue; // assignments or redirections only
    // The command name must have a static value: a name that cannot be established could be any command.
    const head = staticWord(nameNode);
    if (head.globAt >= 0 && head.value !== '[') unresolved('glob in the command name');
    const name = path.posix.basename(head.value);
    if (!FILES.has(name)) continue;
    const words = bashWords(node);
    if (name === 'cd' && words.length === 1) directories.add(os.homedir()); // a bare cd goes home
    let operandsOnly = false;
    for (const word of words.slice(1)) {
      const parsed = staticWord(word);
      let { value } = parsed;
      if (!operandsOnly && value === '--') { operandsOnly = true; continue; }
      if (!operandsOnly && value.startsWith('-')) {
        const eq = value.indexOf('=');
        if (eq < 0) continue; // a flag; --opt=value is checked as a path
        if (parsed.globAt >= 0 && parsed.globAt < eq) unresolved('glob in an option name');
        value = value.slice(eq + 1); parsed.globAt = parsed.globAt < 0 ? -1 : parsed.globAt - eq - 1;
      }
      if (!operandsOnly && name === 'chmod' && value.startsWith('+')) continue;
      if (!value) continue;
      const { file, glob } = operandPath({ value, globAt: parsed.globAt });
      const absolute = path.resolve(cwd, file);
      if (roots.some((root) => contains(root, absolute))) continue;
      const isDirectory = glob || await fs.stat(absolute).then((stat) => stat.isDirectory()).catch((error) => {
        if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return false;
        throw error;
      });
      directories.add(isDirectory ? absolute : path.dirname(absolute));
    }
  }
}
// Bash removes a backslash-newline before it splits words (outside single quotes and $'...'), so
// `ca\<newline>t` is `cat`; tree-sitter splits the word there instead. Join first, as Bash does.
export function joinContinuations(text) {
  let out = ''; let single = false; let ansi = false; let double = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (single) { out += c; if (c === "'") single = false; continue; }
    if (ansi) { out += c; if (c === '\\') { out += text[++i] ?? ''; } else if (c === "'") ansi = false; continue; }
    if (c === '\\') {
      if (text[i + 1] === '\n') { i++; continue; }
      out += c + (text[++i] ?? ''); continue;
    }
    if (!double && c === '$' && text[i + 1] === "'") { out += "$'"; i++; ansi = true; continue; }
    if (!double && c === "'") single = true;
    if (c === '"') double = !double;
    out += c;
  }
  return out;
}
export async function operandDirectories(command, cwd, roots, shell = process.platform === 'win32' ? 'powershell.exe' : '/bin/bash') {
  if (typeof command !== 'string' || typeof cwd !== 'string' || !path.isAbsolute(cwd)) throw Error('malformed shell scan input');
  const ps = /(?:powershell|pwsh)(?:\.exe)?$/i.test(shell);
  const cmd = /(?:^|[\\/])cmd\.exe$/i.test(shell);
  if (!ps && !cmd) command = joinContinuations(command);
  const parser = await parsers();
  const tree = (ps ? parser.ps : parser.bash).parse(command);
  if (!tree || tree.rootNode.hasError) {
    tree?.delete();
    throw Error('unsupported shell grammar');
  }
  const directories = new Set();
  try {
    if (!ps && !cmd) { await bashOperandDirectories(tree, cwd, roots, directories); return [...directories]; }
    for (const node of tree.rootNode.descendantsOfType('command')) {
      const list = parts(node);
      const name = ps || cmd ? list[0]?.text.toLowerCase() : list[0]?.text;
      if (!FILES.has(name) && !(cmd && CMD_FILES.has(name))) continue;
      for (const arg of pathArgs(list, ps, cmd)) {
        const text = ps ? expand(arg, cwd, shell) : home(unquote(arg));
        const file = text && prefix(text);
        if (!file || dynamic(file, ps)) continue;
        const next = ps ? provider(file) : file;
        if (!next) continue;
        const absolute = path.resolve(cwd, next);
        if (roots.some(root => contains(root, absolute))) continue;
        const isDirectory = await fs.stat(absolute).then(stat => stat.isDirectory()).catch(error => {
          if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return false;
          throw error;
        });
        directories.add(isDirectory ? absolute : path.dirname(absolute));
      }
    }
    return [...directories];
  } finally { tree.delete(); }
}
