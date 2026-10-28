#!/usr/bin/env python3
"""Four source-pinned explanatory sketches and option comparison; strings are not executed."""
import argparse,copy,json
from pathlib import Path
from check import ROOT,sha,original,reference,pin,validate,write_new
DATA=json.loads(r'''[
  {
    "id": "record-view",
    "claim": "Name shared storage while preserving the existing address calculation, aliasing, read width and write sites.",
    "obligations": [
      "identities",
      "machine-state",
      "event-order"
    ],
    "validation": "Exact Rec address/read/write tests and later full boundary traces; this sketch is not executed.",
    "limits": [
      "The example fixes the starting address only; backend semantics of a multi-byte read are retained.",
      "Immutable snapshots are useful only at an explicit effect-free boundary, not as implicit replacements for live views."
    ],
    "sources": [
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "class Rec:"
      },
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "return (self.seg << 4)"
      },
      {
        "path": "runtime/original_match/port/engine.py",
        "needle": "def write_as("
      }
    ],
    "before": "off = (base_off + low_word(player_index * 0x14)) & 0xffff\nraw_energy = mem.u8((seg << 4) + ((off + 0x0e) & 0xffff))\nmem.w8((seg << 4) + ((off + 0x10) & 0xffff), status, at=writer_site)",
    "after": "player = PlayerView.bind_same_pointer_and_index(memory, pointer, player_index)\nraw_energy = player.read_u8(EnergyRaw)\nplayer.write_u8(StatusRaw, status, at=writer_site)\n# Every accessor delegates to the existing wrapped address and write hook.",
    "counterexample": "With seg=0x2000, record offset=0xfffe and field offset4, the start address is0x20002, not0x30002. A detached copy also stops reflecting an overlapping write.",
    "omitted_machine_effects": "No automatic cache refresh, field clamping, bit repacking, wide write substitution or re-resolution of a captured far pointer. Existing Rec behavior and writer-site identity remain in the adapter."
  },
  {
    "id": "strength-core",
    "claim": "Express the finite arithmetic of377E as a numerical core while keeping unavailable/placement queries and machine effects in their original order.",
    "obligations": [
      "arithmetic",
      "machine-state",
      "identities"
    ],
    "validation": "Reuse retained T98 cases, then require candidate-versus-accepted-port full boundary state/effect comparisons and independent original oracles before implementation claims.",
    "limits": [
      "Pseudocode below projects the numerical result only.",
      "The original wrapper's AX/DX, frame locals, caller-visible effects and exceptional behavior are not returned by this scalar sketch."
    ],
    "sources": [
      {
        "path": "static/goal-exe/named/seg_1771_03.c",
        "needle": "// ---- 1771:377E"
      },
      {
        "path": "static/goal-exe/code/seg_1771_05.asm",
        "needle": "37D6"
      },
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "def player_strength("
      },
      {
        "path": "notes/engine-study/T98/strength-v1.json",
        "needle": "\"examples\""
      }
    ],
    "before": "v = (p.u8(4) - 0x3e + (s8(p.u8(0x0e)) & 0xffff)) & 0xffff\nc = s8(p.u8(0x0c))\nif c >= 0x20:\n    q, dx = idiv(s16(v), 0x10)\n    v = (v - q) & 0xffff\nelse:\n    v = (v + c) & 0xffff\n# Signed clamp, original frame writes, placement query, optional halving follow.",
    "after": "word = U16(U8(ability_raw) + I8(energy_raw) - 62)\nif I8(form_raw) < 32:\n    word = U16(word + I8(form_raw))\nelse:\n    word = U16(word - trunc_toward_zero(I16(word), 16))\nclamped_strength = clamp(I16(word), 0, 256)\n# Adapter keeps unavailable query before this block, placement query after it,\n# then halves when required and reproduces original registers/locals/sites.",
    "counterexample": "Retained healthy/form32 rows give226 and183; form is not monotone across32. The clamp-before-placement row gives128. Clamping after halving or treating a byte as unsigned changes a branch.",
    "omitted_machine_effects": "A scalar return is insufficient: the adapter may need intermediate words, quotient/remainder and branch information, or retain explicit original operations until full boundary equality is shown."
  },
  {
    "id": "occupancy-step",
    "claim": "A named movement operation must retain per-attempt reset, character/attribute occupancy and conditional draw/effect ordering.",
    "obligations": [
      "occupancy",
      "random-order",
      "machine-state"
    ],
    "validation": "Reused T101 blocked-step/source controls; any later implementation needs ordered RNG, complete picture and write/site traces.",
    "limits": [
      "Supplied draw examples are not newly executed seeded fixtures.",
      "The sketch begins after8889's original target restriction/axis selection; it omits the update_player handler and energy tail."
    ],
    "sources": [
      {
        "path": "static/goal-exe/named/seg_0791_08.c",
        "needle": "// ---- 0791:86D0"
      },
      {
        "path": "static/goal-exe/code/seg_0791_14.asm",
        "needle": "86D0"
      },
      {
        "path": "static/goal-exe/code/seg_0791_14.asm",
        "needle": "8AD1"
      },
      {
        "path": "notes/engine-study/T101/T101c-v1.json",
        "needle": "\"blocked-step\""
      }
    ],
    "before": "current_word = old_drawn_word\napply_direction_byte_to_current()\nif direction != 5:\n    reject_if_outside_original_bounds()\n    if live_and_ordinary_nonholder_nonchallenger:\n        read_picture_character_and_attribute()\n        reject_if_attribute_not_13_and_character_in_original_set()\n#8889 draws rand(5) for each failure and calls this attempt again.",
    "after": "repeat:\n    candidate = step_from_same_drawn_position(direction)\n    accepted = direction_is_standstill(direction)\n    if not accepted:\n        accepted = inside_original_bounds(candidate)\n        if accepted and original_occupancy_guard_applies(player):\n            accepted = picture_allows(character(candidate), attribute(candidate))\n    reproduce_original_attempt_writes_and_sites(candidate, accepted)\n    if accepted: break\n    direction = draw_main_rng(5)\n# Retain the separate original sprite/background update after movement.",
    "counterexample": "The retained blocked-step starts at[0,0], rejects[1,0] and accepts[0,1] after two main draws. Ignoring occupancy accepts[1,0] with one draw. Character1/attribute7 and character1/attribute13 differ.",
    "omitted_machine_effects": "A pure legality predicate can help explanation, but candidate writes occur even on failure and reset from the drawn position every attempt. Preserve coordinate bounds, exemptions, packed bytes and restoration order; do not replace the picture with a boolean grid."
  },
  {
    "id": "event-continuation",
    "claim": "Name adapter phases while preserving pending event boundaries and F1F6-before-B7FA completion.",
    "obligations": [
      "phase-tail",
      "event-order",
      "decisions",
      "checkpoints",
      "public-api"
    ],
    "validation": "Existing whole-stream, answer/refusal and supported original-checkpoint comparisons; new phase representation needs its own complete reconstruction proof.",
    "limits": [
      "This is the admitted Match completion slice, not the full campaign router or a live-Core bridge.",
      "At m7 engine=port checkpoint save/load remains refused; no transition sketch implements T78c."
    ],
    "sources": [
      {
        "path": "runtime/original_match/match.py",
        "needle": "def _advance("
      },
      {
        "path": "runtime/original_match/match.py",
        "needle": "def _load_replay("
      },
      {
        "path": "runtime/original_match/match.py",
        "needle": "port/unknown engine checkpoint"
      }
    ],
    "before": "stopped = machine.run(current_return_boundary)\nclear_current_menu_context()\nif stopped is not None: return\nflush_pending_observed_writes()\nif phase == 'run_match':\n    capture_fixture_after()\n    phase = 'player_update'\n    call_original_boundary(B7FA)\nelse:\n    phase = 'done'\n    finish_public_result()",
    "after": "stop = resume_current_phase_without_reordering_effects()\nclear_current_menu_context()\nif stop.is_event_or_decision: return_pending_boundary()\nelse:\n    flush_pending_observed_writes()\n    on_run_match_return: capture_fixture_then_enter_player_update()\n    on_player_update_return: finish_public_result()\n# Remaining events/answers/frames/records/RNG must reconstruct exactly on supported load.",
    "counterexample": "Returning a completed result at the full-time board omits B7FA's later player update. Deferring events until result assembly loses their original write-time stamps. Match equality alone does not prove the #427 live-Core caller continuation.",
    "omitted_machine_effects": "The host call stack is not automatically serializable. Queues, waiting/refused answers, replay origin/actions, guest frames and return addresses are representation work; an enum alone does not preserve them."
  },
  {
    "id": "memory-views",
    "benefit": "Expose field meaning while reusing existing Rec/Mem and precise effect adapters.",
    "risk": "Copies, cache refreshes, packed-bit writes and accessor ordering can change storage semantics.",
    "dependencies": [
      "Field meanings/unknown bytes",
      "Existing wrapping/view helpers",
      "Boundary write/site tests"
    ],
    "contract": "Existing machine-boundary contract; extend names without adopting a weaker one.",
    "sources": [
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "class Rec:"
      }
    ],
    "obligations": [
      "identities",
      "machine-state"
    ],
    "claim": "Expose field meaning while reusing existing Rec/Mem and precise effect adapters.",
    "validation": "Compare against the twelve-obligation contract and the corresponding representative sketch; cost/prototype work follows in T110c.",
    "limits": [
      "These are design tradeoffs, not implemented alternatives, benchmarks or equivalence results."
    ]
  },
  {
    "id": "pure-rules",
    "benefit": "Make a small deterministic numerical rule testable and readable apart from guest plumbing.",
    "risk": "Inputs may be cached/context-dependent; a returned scalar omits frame/register/effect behavior.",
    "dependencies": [
      "Pure input/output boundary",
      "Independent numerical oracle",
      "An adapter whose required effects remain exact"
    ],
    "contract": "Existing boundary contract retained by a separately proved adapter; result-only parity is insufficient.",
    "sources": [
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "def player_strength("
      }
    ],
    "obligations": [
      "arithmetic",
      "machine-state"
    ],
    "claim": "Make a small deterministic numerical rule testable and readable apart from guest plumbing.",
    "validation": "Compare against the twelve-obligation contract and the corresponding representative sketch; cost/prototype work follows in T110c.",
    "limits": [
      "These are design tradeoffs, not implemented alternatives, benchmarks or equivalence results."
    ]
  },
  {
    "id": "explicit-transitions",
    "benefit": "Make match phases and pending decisions inspectable and potentially serializable.",
    "risk": "A phase enum hides nested generators, deferred events, menu/refusal state and original ordering.",
    "dependencies": [
      "Complete continuation model",
      "Pending event/answer state",
      "Checkpoint and replay proof"
    ],
    "contract": "Machine-boundary preservation unless the owner explicitly chooses a different public-API representation contract.",
    "sources": [
      {
        "path": "runtime/original_match/match.py",
        "needle": "def _advance("
      }
    ],
    "obligations": [
      "phase-tail",
      "decisions",
      "checkpoints"
    ],
    "claim": "Make match phases and pending decisions inspectable and potentially serializable.",
    "validation": "Compare against the twelve-obligation contract and the corresponding representative sketch; cost/prototype work follows in T110c.",
    "limits": [
      "These are design tradeoffs, not implemented alternatives, benchmarks or equivalence results."
    ]
  },
  {
    "id": "semantic-rewrite",
    "benefit": "Use domain records and algorithms throughout, potentially isolating all machine representation at adapters.",
    "risk": "Highest risk of lost finite arithmetic, occupancy, RNG consumption, rare paths and external continuation behavior.",
    "dependencies": [
      "Explicit owner compatibility choice",
      "Coverage and oracle inventory",
      "Numeric/runtime replacement",
      "End-to-end and downstream proof"
    ],
    "contract": "No automatic compatibility level: removing DOS state needs explicit owner scope; changed football semantics are a separate project.",
    "sources": [
      {
        "path": "docs/engine-study/inventory.md",
        "needle": "423 unique registered"
      },
      {
        "path": "runtime/original_match/port/engine.py",
        "needle": "class PortMachine"
      }
    ],
    "obligations": [
      "arithmetic",
      "occupancy",
      "random-order",
      "machine-state",
      "public-api"
    ],
    "claim": "Use domain records and algorithms throughout, potentially isolating all machine representation at adapters.",
    "validation": "Compare against the twelve-obligation contract and the corresponding representative sketch; cost/prototype work follows in T110c.",
    "limits": [
      "These are design tradeoffs, not implemented alternatives, benchmarks or equivalence results."
    ]
  }
]''')
def build():
 rows=copy.deepcopy(DATA)
 for r in rows:r['sources']=[reference(s['path'],s['needle']) for s in r['sources']]
 old=json.loads(original('notes/engine-study/T98/strength-v1.json'))
 selected=[r for r in old['examples'] if r['name'] in ['healthy','form32','upper-clamp','clamp-before-placement','available-zero-strength','injured-zero-energy']]
 move=json.loads(original('notes/engine-study/T101/T101c-v1.json'))
 return pin('T110b',__file__,rows,['How to read the sketches','Four representative changes','Four architecture options','What remains to prove'],
  support=['notes/engine-study/T110/T110a-v1.json','docs/engine-study/rewrite-contract.md'],
  reused_strength_cases=selected,reused_movement_case=next(r for r in move['examples'] if r['id']=='blocked-step'),
  research_engine_calls=0,prototype_implemented=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args();d=build()
 if a.check:
  p=ROOT/'notes/engine-study/T110/T110b-v1.json';old=json.loads(p.read_text());assert sha(Path(__file__).read_bytes())==old['producer']['sha256']
  d['producer']=old['producer'];assert d==old
  text=(ROOT/'docs/engine-study/rewrite-options.md').read_text();validate('T110b',old,text)
  for r in d['rows'][:4]:assert r['before'] in text and r['after'] in text,'pseudocode/document drift'
  assert {r['name']:r['trace']['value'] for r in d['reused_strength_cases']}=={'healthy':226,'form32':183,'upper-clamp':256,'clamp-before-placement':128,'available-zero-strength':0,'injured-zero-energy':0}
  assert d['reused_movement_case']['prediction']=={'direction':4,'final':[0,1],'main_draws':2}
  print('PASS:4 sketches/4 options;6 retained numerical cases/1 supplied-draw case reused; no prototype execution')
 else:
  assert a.out;write_new(a.out,d);print('WROTE:4 sketches/4 options; copied retained evidence only')
if __name__=='__main__':main()
