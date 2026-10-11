// The command a stopped run prints for its continuation (Sol's R1 on PR 114, round 2): built from the
// script's own original arguments, so a resume never silently changes the run's permissions or setup
// (--dry-run, --env, --copy, --exclude ...). It drops only what the resume replaces and appends the
// replacements; a replacement written <like-this> is a placeholder the user fills in, and is not quoted.
const shq = (s) => (/^[\w@%+=:,./-]+$/.test(s) ? s : `'${s.replace(/'/g, `'\\''`)}'`);
const holder = (s) => /^<[^<>']+>$/.test(s);

// argv: the original arguments (process.argv.slice(2)); flags: the value-less options (as parseArgs's);
// drop: option names to remove, with their value; set: [name, value] pairs appended after the kept
// ones (an option of the same name in argv is replaced).
export function resumeCommand({ script, argv, flags = [], drop = [], set = [] }) {
  const gone = new Set([...drop, ...set.map(([k]) => k)]);
  const kept = [];
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i].slice(2);
    const isFlag = flags.includes(key);
    if (!gone.has(key)) kept.push(argv[i], ...(isFlag ? [] : [argv[i + 1]]));
    if (!isFlag) i++;
  }
  const added = set.flatMap(([k, v]) => [`--${k}`, v]);
  return ['node', script, ...kept.map(shq), ...added.map((t) => (holder(t) ? t : shq(t)))].join(' ');
}

export function resumeCommandSelfTest() {
  const failures = [];
  const ok = (what, cond) => { if (!cond) failures.push(what); };
  const flags = ['dry-run', 'second-opinion'];
  const cmd = resumeCommand({
    script: 's.mjs', flags, drop: ['second-opinion', 'session'],
    argv: ['--pr', '7', '--dry-run', '--env', 'A=b c', '--second-opinion', '--total-timeout-sec', '60', '--session', 'ses_x'],
    set: [['reviewer', 'rev'], ['total-timeout-sec', '<longer>']],
  });
  ok('resume: keeps a value-less flag', / --dry-run /.test(cmd));
  ok('resume: keeps and quotes an option value', cmd.includes(`--env 'A=b c'`));
  ok('resume: drops a replaced option and its value', !/ses_x|second-opinion|--total-timeout-sec 60/.test(cmd));
  ok('resume: appends the replacements, a placeholder unquoted', cmd.endsWith('--reviewer rev --total-timeout-sec <longer>'));
  ok('resume: a flag is not mistaken for a value', resumeCommand({ script: 's', flags, argv: ['--dry-run', '--pr', '7'] }) === 'node s --dry-run --pr 7');
  return failures;
}
