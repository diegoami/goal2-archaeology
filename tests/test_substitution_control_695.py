"""#695 synthetic protocol/key-plan controls; actual opcode corroboration is separate."""
import copy
import inspect
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from original_match import screens as S
from original_match.match import Match,SITE_NOTICE,VERSION
from tests import test_stopped_edit_663 as stopped
from tests import test_live_player_records_682 as live


class SubstitutionControl(unittest.TestCase):
    def coordinator(self,context='pause',allowed=False,enabled=True):
        match=stopped.StoppedEdit().match(context,allowed)
        match.opts['substitution_control']=enabled
        match.actions=[]
        match._replay_action=lambda *args:match.actions.append(copy.deepcopy(args))
        return match

    def test_option_is_strict_boolean_and_default_options_remain_identical(self):
        self.assertIn('substitution_control',inspect.signature(Match).parameters)
        build=live.LivePlayers().construct
        before=build().opts
        self.assertEqual(build(substitution_control=False).opts,before)
        self.assertEqual(build(substitution_control=True).opts,{**before,'substitution_control':True})
        for value in (None,0,1,'yes',[]):
            with self.subTest(value=value),self.assertRaises(ValueError):build(substitution_control=value)

    def test_request_and_cancel_are_explicit_desired_booleans_retained_in_replay(self):
        for desired in (True,False):
            match=self.coordinator()
            match.answer(request_substitution=desired,edit_only=True)
            self.assertIs(match.st['answer']['request_substitution'],desired)
            self.assertIs(match.actions[0][1]['request_substitution'],desired)
            self.assertEqual(match.st['answer']['substitutions'],[])
            self.assertIsNone(match.st['waiting'])

    def test_invalid_request_context_values_and_play_inputs_fail_before_consumption(self):
        for context,allowed,enabled in [('half_time',True,True),('substitution',True,True),('extra_time',False,True),('pause',False,False),('pause',True,True)]:
            match=self.coordinator(context,allowed,enabled);before=copy.deepcopy(match.st)
            with self.subTest(context=context,enabled=enabled),self.assertRaises(ValueError):
                match.answer(request_substitution=True,edit_only=True)
            self.assertEqual(match.st,before)
        for value in (0,1,'true',[]):
            match=self.coordinator();before=copy.deepcopy(match.st)
            with self.assertRaises(ValueError):match.answer(request_substitution=value,edit_only=True)
            self.assertEqual(match.st,before)
        for extra in ({},{'edit_only':True,'substitutions':[(105,112)]},{'edit_only':True,'quick':True}):
            match=self.coordinator();before=copy.deepcopy(match.st)
            with self.assertRaises(ValueError):match.answer(request_substitution=True,**extra)
            self.assertEqual(match.st,before)

    def test_request_plan_uses_one_real_enter_and_never_constructs_a_pair(self):
        state=dict(cursor=1,squad=list(range(101,121)),allowed=0,request=0,subs_left=5,position=lambda p:3)
        for desired,initial in ((True,0),(False,1)):
            plan=S.MenuPlan(0,request_substitution=desired)
            state['request']=initial
            self.assertEqual(plan.jobs,[])
            self.assertEqual(plan.steps,['select','play'])
            self.assertEqual(plan.select_key(state),S.ENTER)
            state['request']=int(desired)
            self.assertEqual(plan.select_key(state),S.ESC)
            self.assertEqual(plan.done,[])
            self.assertFalse(plan.requested,'legacy pair-request event is not a standalone request')

    def test_repeated_desired_state_is_idempotent_and_zero_budget_does_not_spin(self):
        state=dict(cursor=1,squad=list(range(101,121)),allowed=0,request=0,subs_left=0,position=lambda p:3)
        plan=S.MenuPlan(0,request_substitution=True)
        self.assertEqual(plan.select_key(state),S.ENTER)
        self.assertEqual(plan.select_key(state),S.ESC,'original budget refusal must return authoritative false')
        for desired in (False,True):
            state.update(request=int(desired),subs_left=5)
            self.assertEqual(S.MenuPlan(0,request_substitution=desired).select_key(state),S.ESC)

    def test_opportunity_requires_explicit_valid_response_and_retains_literal_key_choice(self):
        for response in ('accept','dismiss','timeout'):
            match=self.coordinator('substitution_opportunity',True)
            match.answer(opportunity=response)
            self.assertEqual(match.st['answer'],{'opportunity':response})
            self.assertEqual(match.actions[0],('answer',{'opportunity':response}))
        for args in ({},{'opportunity':True},{'opportunity':'escape'},{'opportunity':'accept','edit_only':True}):
            match=self.coordinator('substitution_opportunity',True);before=copy.deepcopy(match.st)
            with self.assertRaises(ValueError):match.answer(**args)
            self.assertEqual(match.st,before)
        match=self.coordinator();before=copy.deepcopy(match.st)
        with self.assertRaises(ValueError):match.answer(opportunity='accept')
        self.assertEqual(match.st,before)

    def test_notice_publishes_original_timeout_metadata_before_running_wait(self):
        match=self.coordinator('pause',False)
        match.m=SimpleNamespace(stack_word=lambda offset:0,rd=lambda addr,*args:400 if addr==0x087C else 1)
        match._on_notice(False)
        self.assertEqual(match.decisions,[('substitution_opportunity',dict(keeper_unavailable=False,timeout_polls=400,poll_ms=10,substitutions_now=True))])
        for response,key in [('accept',S.ENTER),('dismiss',S.ESC),('timeout',None)]:
            match.st['answer']={'opportunity':response}
            match._on_notice(True)
            self.assertEqual(match.st['prompt'],{'kind':'notice','key':key})
            if key is not None:self.assertEqual(match._key_for(SITE_NOTICE),key)

    def test_notice_keeper_argument_is_second_near_argument_not_side(self):
        for side,keeper,polls in [(1,0,400),(0,1,1000)]:
            match=self.coordinator()
            match.m=SimpleNamespace(stack_word=lambda offset: {2:side,4:keeper}[offset],
                rd=lambda addr,*args: polls if addr==0x087C+2*keeper else 1)
            match._on_notice(False)
            self.assertEqual(match.decisions[0][1]['keeper_unavailable'],bool(keeper))
            self.assertEqual(match.decisions[0][1]['timeout_polls'],polls)

    def test_checkpoint_rejects_non_boolean_profile_before_loading_a_backend(self):
        for value in (None,0,1,'yes'):
            data=Match._encode_save({'version':VERSION,'opts':{'substitution_control':value}},b'synthetic')
            with self.assertRaisesRegex(ValueError,'substitution_control'):Match._checkpoint_state(data)

if __name__=='__main__':unittest.main()
