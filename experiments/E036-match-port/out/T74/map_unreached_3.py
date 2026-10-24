"""Map every unvisited original block to explicit synthetic tests/static service limits."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
summary=json.loads((OUT/'coverage-summary-1.json').read_text())
groups={
 '0791:7FCF':['test_timed_notice_keeper_template_and_key_or_escape'],
 '0791:92FC':['test_quick_result_guards_and_deferred_notice','test_quick_result_commits_flags_and_calls_board_with_zero_low_byte'],
 '0791:9372':['test_poll_dispatches_board_menu_sound_help_and_pitch','test_poll_speed_arrows_clamp_at_zero_and_five'],
 '0791:ED8A':['test_team_menu_tactics_refresh_changed_and_unchanged','test_team_menu_submenu_routes_board_tables_and_space','test_team_menu_home_end_horizontal_and_display_toggle','test_team_menu_escape_before_used_and_invalid_eleven_retry'],
 '1771:1981':['test_team_tactics_view_only_for_computer_or_locked_game','test_team_tactics_toggles_selected_element_and_refreshes_marking'],
 '1771:4859':['test_zero_player_own_tactics_and_name_edit_do_nothing','test_name_editor_unchanged_changed_and_empty_surname_paths'],
 '1771:4925':['test_position_next_wraps13_to0_and_clears_key'],
 '1771:4952':['test_position_club_reset_and_zero_player','test_position_rotation_and_no_refresh_flags'],
 '1771:49B8':['test_marking_cycle_default_opponent_wrap_and_skip_unavailable','test_marking_goalkeeper_clears_flag_without_touching_word','test_marking_second_side_uses_first_country_and_second_mark_array'],
 '1771:4B61':['test_zero_player_own_tactics_and_name_edit_do_nothing','test_own_tactic_three_states_and_return_to_team_value','test_own_tactics_marking_visibility_and_row5_dispatch'],
 '214B:0566':['test_yes_no_returns_uppercase_y_only_and_clears_current_key'],
 '214B:0723':['test_key_pressed_service_preserves_frame_and_high_ax'],
 '214B:08DD':['test_key_read_service_and_pushed_key_are_distinct_paths','test_cached_key_is_consumed_once_and_board_is_not_emitted_twice','test_entry_hook_leaves_python_unstarted_while_decision_waits'],
 '214B:09A7':['test_wait_key_set_rejects_first_key_then_accepts_second'],
 '214B:13F6':['test_byte_and_word_clamp_boundaries'],
 '214B:1452':['test_wrap_up_down_and_delegated_keys'],
 '214B:14AC':['test_byte_and_word_clamp_boundaries'],
 '214B:1507':['test_wrap_up_down_and_delegated_keys'],
 '214B:158E':['test_list_pair_writes_parent_far_pointers_in_order'],
 '214B:15B1':['test_list_navigation_edges_pages_home_end','test_list_short_page_end_uses_long_signed_max','test_short_list_page_down_clamps_cursor_to_count'],
 '235C:0000':['test_msdos_fallthrough_adds_int21_without_changing_pointer_cleanup'],
 '235C:000B':['test_interrupt_wrapper_actual_iret_preserves_record_and_flags','test_retf_handler_does_not_masquerade_as_iret'],
}
# A wholly unvisited routine has no original-PC twin within itself. The declared
# reached counterpart is a shared service/operation, not a fabricated original hit.
counterparts={
 '1771:4859':('214B:1765','Pascal string copy/comparison services shared with the reached message path'),
 '1771:4925':('214B:1507','byte position cycling vs the reached word cursor cycling'),
 '1771:4952':('1771:1981','player-position change vs reached team-tactic change/refresh'),
 '1771:49B8':('1771:1A33','player marking/status bits vs reached team tactic-bit update'),
 '1771:4B61':('1771:1A33','player override bits vs reached team tactic toggling'),
 '214B:0566':('214B:04F8','yes/no prompt vs reached wait-message prompt'),
 '214B:09A7':('214B:08DD','key-set filtering vs reached semantic key entry'),
 '214B:13F6':('214B:14AC','byte clamp vs reached word clamp'),
 '214B:1452':('214B:1507','byte wrap vs reached word wrap'),
 '214B:158E':('214B:1507','scrolling pair writes vs reached single-word cursor writes'),
 '214B:15B1':('214B:1507','scrolling viewport vs reached bounded cursor movement'),
 '235C:0000':('214B:08DD','raw IVT wrapper below the reached key-service entry'),
 '235C:000B':('214B:0723','raw IVT wrapper below the reached poll-service entry'),
}
byaddr={row['address']:row for row in summary['rows']}
functions={n.name for n in ast.walk(ast.parse((ROOT/'tests/test_port_menus.py').read_text())) if isinstance(n,ast.FunctionDef)}
rows=[]
for row in summary['rows']:
 if row['calls']:continue
 tests=groups[row['routine']]
 assert all(t in functions for t in tests)
 reached=next((x['address'] for x in summary['rows'] if x['routine']==row['routine'] and x['calls']),None)
 reason='original reached branch in the same routine; synthetic tests assert the unvisited alternatives'
 if reached is None:reached,reason=counterparts[row['routine']]
 assert byaddr[reached]['calls']>0,(row['address'],reached)
 classification='synthetic branch test; no original-PC visitation claimed'
 if row['routine'] in ('214B:0723','214B:08DD'):
  classification='existing kit semantic key boundary bypasses native BIOS body; service ABI/stack tests cover the port'
 if row['address'] in ('214B:0951','214B:0957'):
  classification='static constant-zero native08DD branch:0951 moval0,0953 oral,0955 je always bypasses0957'
 rows.append({**row,'tests':tests,'reached_counterpart':reached,'counterpart_reason':reason,'classification':classification})
assert len(rows)==209
report={'original_coverage_sha256':hashlib.sha256((OUT/'coverage-unhooked-1.jsonl').read_bytes()).hexdigest(),
 'tests_sha256':hashlib.sha256((ROOT/'tests/test_port_menus.py').read_bytes()).hexdigest(),
 'unreached_blocks':len(rows),'rows':rows}
(OUT/'unreached-map-2.json').open('x').write(json.dumps(report,indent=2)+'\n')
print(f'{len(rows)} unvisited original blocks explicitly mapped; no Python test represented as original-PC coverage')
