"""Map every original ALL-unvisited T73 block to tests and static boundary reasoning.

This does NOT report original-PC visitation by Python units. Removed bodies are
covered by explicit disposition tests. Retained Python branches have targeted
state/ABI tests and twins. The replay's excluded Yes/automatic body is marked
as outside the declared No-replay ALL boundary, not globally impossible.
"""
import argparse,ast,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
P='tests.test_port_display.'
def tests(*names):return [P+n for n in names]
M={
'0791:006C':tests('UnreachedStateBranchTests.test_empty_statistics_bar_and_nonempty_reached_twin'),
'0791:05C6':tests('Display.test_glyph_modes_keep_the_nested_slot_and_signed_clock'),
'0791:0C65':tests('Display.test_replay_no_path_preserves_the_original_question_call','Display.test_no_replay_boundary_clears_the_pending_change_flag'),
'0791:1829':tests('CommentaryMemoryTests.test_disabled_record_retains_only_pointer_frame','CommentaryMemoryTests.test_padding_and_top_rows_update_both_buffers'),
'0791:C50C':tests('NoticeMemoryTests.test_notice_uses_both_players_and_preserves_wait_key_restore_chain'),
'1771:0AF8':tests('TeamPanelHelperTests.test_manager_status_zero_guard_and_status_band_boundaries'),
'1771:11E1':tests('TeamLineBarTests.test_signed_line_division_clamps_and_preserves_interleaved_words'),
'1771:13D0':tests('TeamPanelHelperTests.test_team_aggregate_wraps_signed_bytes_and_skips_unavailable_starter'),
'1771:157D':tests('TeamPanelCompositeTests.test_panel_live_gate_second_side_and_country_flag_column_branches'),
'1771:2F37':tests('UnreachedStateBranchTests.test_empty_squad_row_and_nonempty_reached_twin'),
'1771:3827':tests('Display.test_performance_buckets_keep_encoded_scores_and_sentinel','UnreachedStateBranchTests.test_performance_brightness_uses_live_slot_then_status_bit'),
'1771:3AE2':tests('UnreachedStateBranchTests.test_mark_text_match_flag_and_side_flag_branches'),
'1771:3B3F':tests('UnreachedStateBranchTests.test_mark_row_position_zone_and_country_default_branches'),
'1771:3BD3':tests('UnreachedStateBranchTests.test_tactics_nonmatch_default_mark_row_skips_live_slot_lookup','Display.test_tactics_mark_target_uses_both_names_and_zone_marker','AdditionalUnreachedBranchTests.test_marked_target_without_zone_flag_skips_only_the_zone_marker'),
'1771:42BC':tests('Display.test_player_card_zero_guard_and_status_routes_keep_performance_tail','UnreachedStateBranchTests.test_card_two_feet_yellow_card_and_nonmatch_selection_label','AdditionalUnreachedBranchTests.test_injured_card_fitness_label_reads_energy_zero_instead_of_fitness','AdditionalUnreachedBranchTests.test_card_status_icons_keep_each_colour_and_column'),
'1771:4E22':tests('SquadScreenMemoryTests.test_nonlive_squad_modes_and_manager_templates','SquadScreenMemoryTests.test_live_squad_uses_the_correct_side_substitution_count'),
'1771:5AC4':tests('CompetitionRecordRenderingTests.test_stage_header_snapshot_round_and_leader_branches'),
'1771:76FA':tests('CompetitionFixtureTextTests.test_fixture_score_pending_guards_and_each_played_result_colour'),
'1771:8939':tests('CompetitionBoundaryTests.test_header_one_pass_and_interactive_snapshot_template_branches'),
'1771:8E9A':tests('CompetitionGroupTests.test_ninth_group_requires_continent_and_snapshot_then_uses_special_body','CompetitionGroupTests.test_regular_group_keeps_all_twelve_fixture_rows_and_selector'),
'1771:958D':tests('CompetitionBoundaryTests.test_table_selection_membership_and_finals_branches_keep_local_frame','CompetitionBoundaryTests.test_special_continent_and_late_stage_display_country','CompetitionBoundaryTests.test_table_navigation_and_snapshot_toggle_callees','AdditionalUnreachedBranchTests.test_interactive_table_repeats_then_exits_on_second_escape_key'),
'214B:0350':tests('UnreachedStateBranchTests.test_message_special_colour_and_yes_no_highlight_twins'),
}
TWINS={
'0791:006C':'zero and wrapped-zero sums versus nonzero1+3 split',
'0791:05C6':'modes0/1/2/3/4/255; slots11/12; equal/later clocks and signed-negative threshold',
'0791:0C65':'replay disabled or original question returns No; Yes/automatic requests rejected as outside this boundary',
'0791:1829':'FF disabled record versus active record; empty/3/30/35-character strings and rows4/5',
'0791:C50C':'key-pressed return0 versus1; guest read-key occurs only for1',
'1771:0AF8':'manager0; status0 versus1/9/255 bands; manager130 high-byte ABI',
'1771:11E1':'negative/zero lower clamp, exact256 and above256 upper clamp after signed division',
'1771:13D0':'available versus unavailable starter; positive/zero/negative energy; zero morale versus signed wrap',
'1771:157D':'both live flags versus either clear; first versus second country; optional flag columns',
'1771:2F37':'player word0 versus1',
'1771:3827':'score bucket thresholds/sentinel; slot11 versus12 and status-bit brightness',
'1771:3AE2':'live flag and mark flag0/1 cross-product',
'1771:3B3F':'position1 versus2; zone bit clear versus set; country default',
'1771:3BD3':'nonmatch versus live slot lookup; marked target with zone bit set versus clear',
'1771:42BC':'zero player; both feet versus single-foot lookup; zero versus positive energy; each status bit and nonmatch label',
'1771:4E22':'modes0/1/2; live/nonlive; managed/unmanaged; selected11/12; first/second-side count',
'1771:5AC4':'snapshot0/1 and matching/different game phase; no leader versus country7',
'1771:76FA':'kind0 and pendingFE guards versus played scores; result flags0/1/2',
'1771:8939':'one-pass versus interactive; remaining0/1; current versus snapshot',
'1771:8E9A':'group9 continent2/3 and snapshot0/1; ordinary twelve-row view; selector maximum8/9',
'1771:958D':'stage6/7, continent2/3, mode0/nonzero, membership/finals dispatch1/2/3; space/AE/AF/B6/B7; one pass versus interactive two-pass Esc exit',
'214B:0350':'normal versus special colour; yes/no locator and both highlight cells',
}
SPECIFIC={
'0791:1829':{'184E':tests('CommentaryMemoryTests.test_disabled_record_retains_only_pointer_frame'),'1879':tests('CommentaryMemoryTests.test_padding_and_top_rows_update_both_buffers')},
'1771:13D0':{'142E':tests('TeamPanelHelperTests.test_team_aggregate_wraps_signed_bytes_and_skips_unavailable_starter'),'151B':tests('TeamPanelHelperTests.test_team_aggregate_wraps_signed_bytes_and_skips_unavailable_starter')},
'1771:3BD3':{'3D18':tests('UnreachedStateBranchTests.test_tactics_nonmatch_default_mark_row_skips_live_slot_lookup'),'3DF1':tests('Display.test_tactics_mark_target_uses_both_names_and_zone_marker','AdditionalUnreachedBranchTests.test_marked_target_without_zone_flag_skips_only_the_zone_marker')},
'1771:42BC':{'42D8':tests('Display.test_player_card_zero_guard_and_status_routes_keep_performance_tail'),'43D8':tests('UnreachedStateBranchTests.test_card_two_feet_yellow_card_and_nonmatch_selection_label'),'449A':tests('AdditionalUnreachedBranchTests.test_injured_card_fitness_label_reads_energy_zero_instead_of_fitness'),'466B':tests('AdditionalUnreachedBranchTests.test_card_status_icons_keep_each_colour_and_column'),'46C9':tests('AdditionalUnreachedBranchTests.test_card_status_icons_keep_each_colour_and_column'),'46F8':tests('Display.test_player_card_zero_guard_and_status_routes_keep_performance_tail'),'471D':tests('Display.test_player_card_zero_guard_and_status_routes_keep_performance_tail'),'4781':tests('Display.test_player_card_zero_guard_and_status_routes_keep_performance_tail'),'47ED':tests('UnreachedStateBranchTests.test_card_two_feet_yellow_card_and_nonmatch_selection_label')},
'1771:958D':{**{a:tests('CompetitionBoundaryTests.test_special_continent_and_late_stage_display_country') for a in ('95AD','95BC','95D1','95E5')},**{a:tests('CompetitionBoundaryTests.test_table_selection_membership_and_finals_branches_keep_local_frame') for a in ('9609','9637','963C','9642','9647')},**{a:tests('CompetitionBoundaryTests.test_table_navigation_and_snapshot_toggle_callees') for a in ('9652','9672','9686','968A','968C','96A4','96AE','96B4','96B8','96BA')},**{a:tests('AdditionalUnreachedBranchTests.test_interactive_table_repeats_then_exits_on_second_escape_key') for a in ('96C3','96CA')}}}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True);a=ap.parse_args()
 coverage_path=ROOT/'experiments/E036-match-port/out/T73/coverage-summary-1.json';coverage=json.loads(coverage_path.read_text())
 inventory={r['address']:r for r in json.loads((ROOT/'experiments/E036-match-port/out/T73/static-inventory.json').read_text())}
 test_path=ROOT/'tests/test_port_display.py';tree=ast.parse(test_path.read_text());available={P+c.name+'.'+f.name for c in tree.body if isinstance(c,ast.ClassDef) for f in c.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_')}
 registry=port._module_registry('display');rows=[]
 for block in coverage['rows']:
  if block['calls']:continue
  address,routine=block['address'],block['routine'];entry=registry.entries[routine];static=inventory[routine]
  if entry.stub:
   disposition='removed body in declared ALL states';unit=tests('RemovedBodyDispositionTests.test_declared_removals_preserve_memory_registers_and_void_return','Display.test_registry_has_the_eighty_eight_listing_returns')
   twin='Python removal is exercised for empty, all-zero and all-FFFF argument vectors. No original branch execution is claimed.'
   entry_seen=any(r['address']==routine and r['calls'] for r in coverage['rows'])
   boundary=('Original entry is reached in ALL, but this block is unvisited; whole-body ALL ablation justifies the removal, not original-PC unit visitation.' if entry_seen else 'Original ALL entry is unvisited; the whole body is omitted, not translated branch-by-branch.')
  elif routine=='0791:0C65':
   disposition='excluded replay branch at retained No-replay boundary';unit=M[routine];twin=TWINS[routine]
   boundary='0C74-0C8E: disabled replay or the kit No answer bypasses0C91. Automatic/Yes replay is outside the declared ALL states, not claimed globally impossible or unit-executed.'
  else:
   disposition='retained Python branch';unit=SPECIFIC.get(routine,{}).get(address[5:],M[routine]);twin=TWINS[routine]
   boundary='Targeted Python branch/state tests and controlled guest-return twins; original ALL PC remains unexecuted.'
  assert unit and set(unit)<=available,(address,set(unit)-available)
  reached=[r['address'] for r in coverage['rows'] if r['routine']==routine and r['calls']]
  rows.append({'address':address,'routine':routine,'original_ALL_calls':0,'original_ALL_PC_executed':False,'disposition':disposition,
               'unit_tests':unit,'unit_boundary_twins':twin,'static_reasoning':boundary,'listing':f"{block['listing']}:{block['line']}",
               'static_block_instructions':block['instructions'],'original_direct_callers':static['callers'],'listing_return':static['returns'],
               'original_reached_blocks_in_same_routine':reached,'no_original_unit_PC_visitation_claim':True})
 assert len(rows)==273 and len({r['address'] for r in rows})==273
 report={'scope':'Original unhooked ALL reach only; units do not manufacture original-PC visits','coverage_sha256':hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
         'test_source_sha256':hashlib.sha256(test_path.read_bytes()).hexdigest(),'runtime_source_sha256':hashlib.sha256((ROOT/'runtime/original_match/port/display.py').read_bytes()).hexdigest(),
         'original_unreached_blocks':273,'all_mapped':True,'rows':rows}
 (ROOT/a.out).open('x').write(json.dumps(report,indent=2)+'\n')
 print('address\troutine\tdisposition\tunit tests\tlisting/callers/return')
 for r in rows:print(r['address']+'\t'+r['routine']+'\t'+r['disposition']+'\t'+', '.join(r['unit_tests'])+'\t'+r['listing']+'; callers='+','.join(r['original_direct_callers'])+'; return='+','.join(r['listing_return']))
if __name__=='__main__':main()
