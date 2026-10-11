---
name: delegate
description: Choose who does a piece of work, and on which model. The main session or a Claude agent implements; OpenCode reviews code; Jev takes repeated decisions; models on OpenRouter make images and give other model families; ElevenLabs makes speech, sound effects and music. Use before doing work yourself that a cheaper or better-suited model could do, whenever a task needs an image, a sound or a voice, and whenever you are about to name a model id.
---

# /delegate: who does the work, and on which model

You are the main session. Your time and tokens are the scarce resource. Before doing work
yourself, check whether a delegate below does it better or cheaper.

## The delegates

| Work | Delegate | How | Key |
| --- | --- | --- | --- |
| Code: implement a task or a fix | The main session in its own worktree, or the `implementer` Claude agent (CLAUDE.md "Choosing models" rule 1); never OpenCode | `/run-task` → yourself, or `Agent(subagent_type: "implementer", isolation: "worktree")` | — |
| Review a PR | One OpenCode run: `harness.json`'s `reviewer.default`, or the model the user or the task file names; never the implementer's family | `/run-task` → `tools/harness/review.mjs [--reviewer <name>]` | OpenAI's login (`opencode auth login`) for Luna and Sol; Z.AI's for GLM; OpenCode Go's (`opencode console login`) for MiMo |
| Repeated decisions with known answers (triage, routing, gating, labelling) | Jev | `/jev` → `tools/harness/jev.mjs` | `OPENROUTER_API_KEY` |
| Images: sprites, icons, maps, mockups, illustrations | An image model on OpenRouter | pick one with `models.mjs openrouter --output image` | `OPENROUTER_API_KEY` |
| A second opinion from another model family, or reading audio or images | A model on OpenRouter | `models.mjs openrouter --input image` (or `audio`) | `OPENROUTER_API_KEY` |
| Speech, voices, sound effects, music | ElevenLabs | `models.mjs elevenlabs` | `ELEVENLABS_API_KEY` |
| Judgment that needs a written reason, design, planning | You, or a Claude agent | — | — |

The session-start report says which keys are set. A delegate without its key is off; do the work
another way, or tell the user what is missing (`docs/environment.md`).

## Picking a model

1. **Never from memory.** Model ids and prices change faster than any document. List them live:
   - `node tools/harness/models.mjs openrouter --output image`;
   - `node tools/harness/models.mjs elevenlabs`;
   - `opencode models openai` (and `zai-coding-plan`, `opencode-go`, `minimax`) for reviewers.

   Do the same when you are unsure a model still exists. (L25)
   To change the default reviewer, use `/switch-model`.
2. **Do not ask before a run** (CLAUDE.md "Choosing models", the owner, 2026-10-11). Code is
   implemented by the main session or a Claude agent, and reviewed by `harness.json`'s default
   reviewer; a task file or the user may name another reviewer (`review.mjs --reviewer <key or
   provider/model[@variant]>`). No quota is checked. Fixed: the reviewer is never the implementer's
   family; DeepSeek never (the scripts refuse it); Alibaba only when the user asks. Record on the
   PR which model reviewed. A provider that does not answer: diagnose and fix; another model only
   when the user names it (rule 5). Never use a free model for private content.
   *Superseded on 2026-10-11 and kept as history (L104):* asking the user one question before each
   implementation and review; quota-tracker's `/recommend` as a suggestion; the chains and
   `choose.mjs`; OpenCode implementing.
3. **Choose on the evidence you have.** In order of preference:
   - this project's own measurements (review rounds and tokens per task, from the merge comments);
   - a small trial;
   - the listed price and capabilities.

   Vendor benchmarks come last.
4. **Record the choice where it is used.** Who implements and who reviews, on which model, and the
   suggestion's reasons go in a comment on the issue or PR (rule 5). A generated asset gets a sidecar next to it, `<asset>.json`, with the provider, the
   model id, the prompt, the date and the cost. That records where it came from, and lets it be
   made again.
5. **Say the cost first.** Before a batch (many images, a long narration), tell the user the
   estimated cost from the listed prices, and ask when it is more than a few dollars.

## Making media

Call the provider's API directly, with `fetch` from Node. Read the API reference for the endpoint
before the first call in a project, because request shapes change. Then keep the working call in a
small script under `tools/`, so the next asset is one command. Starting points (check them first):
- **OpenRouter images:** `POST https://openrouter.ai/api/v1/chat/completions`, with an image-output
  model and `"modalities": ["image", "text"]`. The image comes back in the assistant message.
- **ElevenLabs:** `POST https://api.elevenlabs.io/v1/text-to-speech/<voice_id>` for speech, and
  `POST https://api.elevenlabs.io/v1/sound-generation` for sound effects. Both use the `xi-api-key`
  header and return audio bytes.

Generated assets are project content: commit them with their sidecar, and review them the way the
project reviews its UI (a person looks at the screen).

## Never

- Name a model id you have not just seen in a live list.
- Send private repository content or personal data to a provider the user has not cleared for it.
- Spend on a batch without saying the cost first.
