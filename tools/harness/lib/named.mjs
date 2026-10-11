// A model named for a review (CLAUDE.md "Choosing models", the owner, 2026-10-11).
// harness.json's keys stay as short names; any other name of the form `provider/model`, with an
// optional `@variant`, is taken as the OpenCode model id the user chose. Its family, for the
// reviewer-family rule, is read from the model's own name. DeepSeek is refused on every route
// (rule 4); Alibaba runs only when named, which this is.

const FAMILIES = [
  [/^glm/, 'glm'],
  [/^gemini|^gemma/, 'google'],
  [/^llama/, 'meta'],
  [/^kimi/, 'moonshot'],
  [/^grok/, 'xai'],
  [/^(mistral|devstral|codestral|magistral)/, 'mistral'],
  [/^nemotron/, 'nvidia'],
  [/^mimo/, 'mimo'],
  [/^minimax/, 'minimax'],
  [/^(gpt|o\d)/, 'openai'],
  [/^qwen/, 'qwen'],
  [/^(claude|opus|sonnet|haiku)/, 'claude'],
];

// The family of a model id, read from its last segment only, so that one model reached through two
// routes ("google/gemini-2.5-pro", "openrouter/google/gemini-2.5-pro") is one family (Sol's R1 on
// PR 114): a known prefix, else the segment's leading word ("acme-widget-1" -> acme), never the
// provider or route.
export function familyOfId(id) {
  const base = id.split('/').pop().toLowerCase();
  return FAMILIES.find(([re]) => re.test(base))?.[1] ?? (base.match(/^[a-z]+/)?.[0] || base);
}

// harness.json's entry for `name`, else the model `name` spells, else null. Throws on DeepSeek.
export function namedModel(name, models) {
  const known = models[name];
  const m = known ? null : /^([\w.-]+\/[^@\s]+)(?:@([\w.-]+))?$/.exec(name);
  if (!known && !m) return null;
  const id = known ? known.id : m[1];
  if (/deepseek/i.test(id)) throw new Error(`${name}: DeepSeek is never used, on any route (CLAUDE.md, choosing models, rule 4).`);
  if (known) return known;
  return { id, family: familyOfId(id), ...(m[2] ? { variant: m[2] } : {}) };
}

// The family of a name as review.mjs meets it (a harness.json key, a model id, or a bare family
// from a `model:` label).
export function familyOfName(name, models) {
  if (models[name]) return models[name].family;
  return name.includes('/') ? familyOfId(name.replace(/@.*$/, '')) : name;
}

export function selfTest() {
  const failures = [];
  const ok = (what, cond) => { if (!cond) failures.push(what); };
  const models = { luna: { id: 'openai/gpt-5.6-luna', family: 'openai' } };
  ok('a harness.json key is its entry', namedModel('luna', models) === models.luna);
  const sol = namedModel('openai/gpt-6.1-sol@low', models);
  ok('a named id keeps its id', sol?.id === 'openai/gpt-6.1-sol');
  ok('a named id keeps its variant', sol?.variant === 'low');
  ok('a named id without variant has none', !('variant' in namedModel('minimax/MiniMax-M3', models)));
  ok('MiniMax family', namedModel('minimax/MiniMax-M3', models).family === 'minimax');
  ok('family from the last segment', namedModel('openrouter/xiaomi/mimo-v2.6-pro', models).family === 'mimo');
  ok('GLM on Alibaba is glm', namedModel('alibaba-token-plan/glm-5.3', models).family === 'glm');
  ok('an unknown model is its leading word', namedModel('acme/widget-1', models).family === 'widget');
  ok('one model on two routes is one family (Sol R1, PR 114)',
    namedModel('google/gemini-2.5-pro', models).family === namedModel('openrouter/google/gemini-2.5-pro', models).family);
  ok('an unknown model on two routes is one family',
    namedModel('acme/widget-1', models).family === namedModel('openrouter/acme/widget-1', models).family);
  ok('a bare unknown word is not a model', namedModel('sonnet-ish', models) === null);
  let threw = false;
  try { namedModel('opencode-go/deepseek-v4-pro', models); } catch { threw = true; }
  ok('DeepSeek is refused', threw);
  ok('label with an id maps to its family', familyOfName('openai/gpt-6.1-sol@low', models) === 'openai');
  ok('label with a key maps to its family', familyOfName('luna', models) === 'openai');
  ok('a bare family stays itself', familyOfName('minimax', models) === 'minimax');
  return failures;
}
