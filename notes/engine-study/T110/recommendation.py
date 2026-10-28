#!/usr/bin/env python3
"""Design cost arithmetic and conditional prototype proposal, not executed implementation."""
import argparse,copy,json
from pathlib import Path
from check import ROOT,sha,reference,pin,validate,write_new
DATA=json.loads(r'''[
  {
    "id": "memory-views",
    "claim": "Recommend incremental named views over existing storage/helpers; preserve the current boundary contract.",
    "obligations": [
      "identities",
      "machine-state",
      "event-order"
    ],
    "scope": "Three record families (player, country, pitch), shared accessor naming and two representative integration boundaries; not all unknown fields or the live-Core bridge.",
    "disposition": "recommend",
    "assumptions": [
      "Three families are a designed rollout scope, not a measured count of independent implementations.",
      "Reuse Rec/Mem; no copied replacement storage, cache refresh or reordered writer effects.",
      "Rates are uncalibrated active-hour inputs for planning, not measured productivity."
    ],
    "dependencies": [
      "Accepted field meanings/opaque bytes",
      "Aliasing/wrapping and write-site audit",
      "Boundary regression infrastructure"
    ],
    "sources": [
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "class Rec:"
      }
    ],
    "work": [
      {
        "activity": "implementation",
        "units": 3,
        "hours_per_unit": [
          4,
          8
        ],
        "basis": "Name one shared-storage record family"
      },
      {
        "activity": "implementation",
        "units": 1,
        "hours_per_unit": [
          2,
          4
        ],
        "basis": "Shared accessor/schema integration"
      },
      {
        "activity": "validation",
        "units": 3,
        "hours_per_unit": [
          3,
          6
        ],
        "basis": "Alias/wrapping/reserved-byte/write-site audit per family"
      },
      {
        "activity": "validation",
        "units": 2,
        "hours_per_unit": [
          3,
          6
        ],
        "basis": "Two representative integration boundaries; more consumers add cost"
      }
    ],
    "estimate_kind": "designed active-engineering-hour assumptions, not measured productivity",
    "compute": "not budgeted; no execution authorised",
    "total_hours": [
      29,
      58
    ],
    "double_validation_and_implementation_hours": [
      58,
      116
    ],
    "validation": "Recompute the work breakdown; independently challenge the scope/rates and fidelity/oracle assumptions. Arithmetic consistency is not forecast calibration.",
    "limits": [
      "Different scopes, not equal-feature bids; totals are not a ranking by cost.",
      "CPU, runner elapsed time, later delivery and unresolved proof work are separate and unbudgeted."
    ]
  },
  {
    "id": "pure-rules",
    "claim": "Conditionally extract numerical blocks behind explicit ABI/effect adapters after one meaningful prototype.",
    "obligations": [
      "arithmetic",
      "machine-state",
      "identities"
    ],
    "scope": "Four candidate numerical blocks:377E strength,3A06 derived skill,278A effective-skill arithmetic,34C1 geometry arithmetic. Whole routines are not claimed pure.",
    "disposition": "conditional",
    "assumptions": [
      "Four blocks are selected work scope, not a purity census or all numeric engine code.",
      "Existing wrappers/calls/sites remain until an adapter passes exact boundary checks.",
      "No extrapolation of T106's small-call timings into match performance."
    ],
    "dependencies": [
      "Independent numerical oracles and targeted boundary witnesses",
      "Adapter preserving intermediate/register/frame effects",
      "Original/accepted-port comparison harness"
    ],
    "sources": [
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "def player_strength("
      },
      {
        "path": "runtime/original_match/port/geometry.py",
        "needle": "def skill_of_pitch_record("
      },
      {
        "path": "runtime/original_match/port/ball.py",
        "needle": "@PORTS.port(\"0791:34C1\""
      }
    ],
    "work": [
      {
        "activity": "implementation",
        "units": 4,
        "hours_per_unit": [
          3,
          6
        ],
        "basis": "One candidate numerical block plus its adapter"
      },
      {
        "activity": "implementation",
        "units": 1,
        "hours_per_unit": [
          4,
          8
        ],
        "basis": "Shared input/trace/helper infrastructure"
      },
      {
        "activity": "validation",
        "units": 4,
        "hours_per_unit": [
          4,
          8
        ],
        "basis": "Per-block retained/original/accepted-port boundary and negative controls"
      },
      {
        "activity": "validation",
        "units": 1,
        "hours_per_unit": [
          4,
          8
        ],
        "basis": "Shared integration and independent review fixes"
      }
    ],
    "estimate_kind": "designed active-engineering-hour assumptions, not measured productivity",
    "compute": "not budgeted; no execution authorised",
    "total_hours": [
      36,
      72
    ],
    "double_validation_and_implementation_hours": [
      72,
      144
    ],
    "validation": "Recompute the work breakdown; independently challenge the scope/rates and fidelity/oracle assumptions. Arithmetic consistency is not forecast calibration.",
    "limits": [
      "Different scopes, not equal-feature bids; totals are not a ranking by cost.",
      "CPU, runner elapsed time, later delivery and unresolved proof work are separate and unbudgeted."
    ]
  },
  {
    "id": "explicit-transitions",
    "claim": "Defer broad state-representation replacement until pending decisions and checkpoint obligations have a complete model.",
    "obligations": [
      "phase-tail",
      "decisions",
      "checkpoints",
      "event-order",
      "modes"
    ],
    "scope": "Four designed phase workgroups (setup,run_match,player_update,terminal), six public decision contexts, three checkpoint workgroups (ordinary,pending/refused,queued). Counts are planning groups, not measured states.",
    "disposition": "defer",
    "assumptions": [
      "Context count follows the six documented public decision kinds; extra-time halves/refusal subpaths still need separate cases.",
      "At m7 plain-port checkpoints are refused; this option does not take credit for later independent T78c work.",
      "Nested generator/caller state may force redesign; a phase enum alone is insufficient."
    ],
    "dependencies": [
      "Complete continuation/state representation",
      "Exact event/answer/refusal order",
      "Pending frame/queue/RNG checkpoint proof",
      "Reassessment against later accepted delivery if any"
    ],
    "sources": [
      {
        "path": "runtime/original_match/match.py",
        "needle": "def _advance("
      },
      {
        "path": "runtime/original_match/README.md",
        "needle": "**Decisions**"
      },
      {
        "path": "runtime/original_match/match.py",
        "needle": "port/unknown engine checkpoint"
      }
    ],
    "work": [
      {
        "activity": "implementation",
        "units": 4,
        "hours_per_unit": [
          6,
          12
        ],
        "basis": "Designed phase workgroup"
      },
      {
        "activity": "implementation",
        "units": 6,
        "hours_per_unit": [
          4,
          8
        ],
        "basis": "Public decision context with refusal/default path"
      },
      {
        "activity": "implementation",
        "units": 3,
        "hours_per_unit": [
          6,
          12
        ],
        "basis": "Checkpoint workgroup"
      },
      {
        "activity": "validation",
        "units": 4,
        "hours_per_unit": [
          8,
          16
        ],
        "basis": "Phase boundary/order evidence"
      },
      {
        "activity": "validation",
        "units": 6,
        "hours_per_unit": [
          6,
          12
        ],
        "basis": "Decision/refusal/continuation evidence"
      },
      {
        "activity": "validation",
        "units": 3,
        "hours_per_unit": [
          8,
          16
        ],
        "basis": "Checkpoint queue/frame/RNG evidence"
      }
    ],
    "estimate_kind": "designed active-engineering-hour assumptions, not measured productivity",
    "compute": "not budgeted; no execution authorised",
    "total_hours": [
      158,
      316
    ],
    "double_validation_and_implementation_hours": [
      316,
      632
    ],
    "validation": "Recompute the work breakdown; independently challenge the scope/rates and fidelity/oracle assumptions. Arithmetic consistency is not forecast calibration.",
    "limits": [
      "Different scopes, not equal-feature bids; totals are not a ranking by cost.",
      "CPU, runner elapsed time, later delivery and unresolved proof work are separate and unbudgeted."
    ]
  },
  {
    "id": "semantic-rewrite",
    "claim": "No-go now for substituting a full domain rewrite under the present fidelity contract; technical feasibility is not disproved.",
    "obligations": [
      "arithmetic",
      "random-order",
      "occupancy",
      "machine-state",
      "public-api",
      "checkpoints",
      "evidence-scope"
    ],
    "scope": "Initial rewrite/validation attempt across all23m7 registry modules plus six cross-module workgroups. Not a complete release estimate, exhaustive proof or live-Core bridge/sealed delivery.",
    "disposition": "no-go-now",
    "assumptions": [
      "Partition actual modules into10numeric/policy,10state/effect/lifecycle and3interaction/assembly groups; rates intentionally differ.",
      "Per-module effort varies widely; module count is a work-allocation input, not a complexity metric.",
      "Unresolved oracle/coverage/representation obligations can exceed every range here; no confidence bound is claimed.",
      "A public-API-only representation contract would need explicit owner adoption; it is not assumed."
    ],
    "dependencies": [
      "Owner compatibility decision and consumer audit",
      "Independent numeric/RNG/occupancy replacements",
      "Rare-path and genuine-key oracle coverage",
      "Whole API/record/continuation proof",
      "Separate #427,T79,T80 delivery decisions"
    ],
    "sources": [
      {
        "path": "runtime/original_match/port/engine.py",
        "needle": "class PortMachine"
      },
      {
        "path": "docs/engine-study/micro-probes.md",
        "needle": "0/18"
      },
      {
        "path": "docs/engine-study/audit-boundaries.md",
        "needle": "complete transitive liveness"
      }
    ],
    "work": [
      {
        "activity": "implementation",
        "units": 10,
        "hours_per_unit": [
          12,
          24
        ],
        "basis": "Numeric/policy registry-module group"
      },
      {
        "activity": "implementation",
        "units": 10,
        "hours_per_unit": [
          16,
          32
        ],
        "basis": "State/effect/lifecycle registry-module group"
      },
      {
        "activity": "implementation",
        "units": 3,
        "hours_per_unit": [
          16,
          32
        ],
        "basis": "Interaction/assembly registry-module group"
      },
      {
        "activity": "implementation",
        "units": 6,
        "hours_per_unit": [
          8,
          16
        ],
        "basis": "Cross-module workgroup"
      },
      {
        "activity": "validation",
        "units": 10,
        "hours_per_unit": [
          16,
          32
        ],
        "basis": "Numeric/policy module original-oracle evidence"
      },
      {
        "activity": "validation",
        "units": 10,
        "hours_per_unit": [
          24,
          48
        ],
        "basis": "State/effect/lifecycle module evidence"
      },
      {
        "activity": "validation",
        "units": 3,
        "hours_per_unit": [
          24,
          48
        ],
        "basis": "Interaction/assembly module evidence"
      },
      {
        "activity": "validation",
        "units": 6,
        "hours_per_unit": [
          16,
          32
        ],
        "basis": "RNG/events/decisions/checkpoints/modes/post-tail integration evidence"
      }
    ],
    "estimate_kind": "designed active-engineering-hour assumptions, not measured productivity",
    "compute": "not budgeted; no execution authorised",
    "total_hours": [
      944,
      1888
    ],
    "double_validation_and_implementation_hours": [
      1888,
      3776
    ],
    "validation": "Recompute the work breakdown; independently challenge the scope/rates and fidelity/oracle assumptions. Arithmetic consistency is not forecast calibration.",
    "limits": [
      "Different scopes, not equal-feature bids; totals are not a ranking by cost.",
      "CPU, runner elapsed time, later delivery and unresolved proof work are separate and unbudgeted."
    ]
  },
  {
    "id": "prototype",
    "claim": "Propose only the after-availability numerical strength block of377E with its existing machine-effect adapter; do not implement it here.",
    "obligations": [
      "arithmetic",
      "machine-state",
      "identities",
      "evidence-scope"
    ],
    "validation": "Future T111 must preregister inputs, source/oracle pins, ordinary/boundary cases, actual failing controls, exact boundary observations and separate CPU cap before execution.",
    "limits": [
      "6-12active engineering hours are a provisional prototype planning allowance, not approval or production-readiness estimate.",
      "Selected-case equivalence does not establish the whole engine, natural frequency, performance or live-Core integration."
    ],
    "sources": [
      {
        "path": "runtime/original_match/port/attributes.py",
        "needle": "def player_strength("
      },
      {
        "path": "notes/engine-study/T98/strength-v1.json",
        "needle": "\"clamp-before-placement\""
      }
    ],
    "oracle": "Retained376original numerical returns cover only their recorded projection. Also compare the complete wrapper's captured registers/memory/ordered writes/sites/draws against unchanged accepted port and independent original behavior under explicitly disclosed existing limits; never use the new helper on both sides.",
    "negative_controls": [
      "Form cutoff33 against a declared form32 witness",
      "Clamp after placement against the retained clamp-before-placement witness",
      "Correct scalar with a deliberately wrong adapter word/register/site; require an actual sensitive witness before crediting the control"
    ],
    "readability_questions": [
      "Can an independent reader locate the signed form32 branch and finite-width arithmetic?",
      "Can they distinguish unavailable from available-zero strength?",
      "Can they identify which effects stay in the wrapper and why placement is queried after clamping?",
      "Does adapter/trace complexity eliminate the proposed readability benefit?"
    ],
    "stop": [
      "Any unexplained new original/reference boundary or trace difference blocks success.",
      "If only scalar parity is available, do not claim adapter equivalence.",
      "If necessary effects require duplicating most arithmetic/plumbing, stop and prefer views rather than hiding it.",
      "No performance benefit without a preregistered comparable measurement; no repeated scope/threshold changes after results."
    ],
    "owner_decisions": [
      "Choose existing machine-boundary target or a separately specified alternate contract.",
      "Approve/defer this prototype and its active-effort allowance; optional T111 may be omitted.",
      "Approve exact input/oracle/negative-control scope and separate CPU/runner budget before any engine call."
    ],
    "authorised": false,
    "work": [
      {
        "activity": "implementation",
        "units": 1,
        "hours_per_unit": [
          1,
          2
        ],
        "basis": "One known numerical block, documentation only until approved"
      },
      {
        "activity": "implementation",
        "units": 1,
        "hours_per_unit": [
          1,
          2
        ],
        "basis": "Preserve/adapt the existing wrapper effects"
      },
      {
        "activity": "validation",
        "units": 1,
        "hours_per_unit": [
          2,
          4
        ],
        "basis": "Selected ordinary/boundary oracle and failing-control set"
      },
      {
        "activity": "validation",
        "units": 1,
        "hours_per_unit": [
          2,
          4
        ],
        "basis": "Boundary trace/readability assessment and review fixes"
      }
    ],
    "total_hours": [
      6,
      12
    ]
  }
]''')
GROUPS=json.loads(r'''{"numeric_policy":["attributes","contests","duels","geometry","positioning","quick","rare","runtime","selection","real"],"state_effect_lifecycle":["ball","discipline","frame","motion","pilot","postmatch","restarts","setup","takers","update"],"interaction_assembly":["display","menus","entrypoints"]}''')
def build():
 rows=copy.deepcopy(DATA)
 for r in rows:r['sources']=[reference(s['path'],s['needle']) for s in r['sources']]
 contract=json.loads((ROOT/'notes/engine-study/T110/T110a-v1.json').read_text())
 actual={m['name'] for m in contract['inventory']['modules']}
 assert set(sum(GROUPS.values(),[]))==actual and len(sum(GROUPS.values(),[]))==len(actual)==23
 return pin('T110c',__file__,rows,['Recommendation and owner choices','Cost model and exclusions','Four cost plans','Smallest meaningful prototype','Validation and review boundary'],
  support=['notes/engine-study/T110/T110a-v1.json','notes/engine-study/T110/T110b-v2.json','docs/engine-study/rewrite-contract.md','docs/engine-study/rewrite-options.md'],
  module_workgroups=GROUPS,research_engine_calls=0,prototype_implemented=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args();d=build()
 if a.check:
  old=json.loads((ROOT/'notes/engine-study/T110/T110c-v1.json').read_text());assert sha(Path(__file__).read_bytes())==old['producer']['sha256']
  d['producer']=old['producer'];assert d==old
  text=(ROOT/'docs/engine-study/rewrite-assessment.md').read_text();validate('T110c',old,text)
  p=old['rows'][-1];assert [sum(w['units']*w['hours_per_unit'][i] for w in p['work']) for i in range(2)]==p['total_hours']
  for r in old['rows'][:4]:assert str(r['total_hours'][0])+'–'+str(r['total_hours'][1]) in text
  print('PASS:4 cost plans and sensitivity sums;23module partition;1unapproved prototype;no implementation or engine call')
 else:
  assert a.out;write_new(a.out,d);print(json.dumps({r['id']:r['total_hours'] for r in d['rows']}))
if __name__=='__main__':main()
