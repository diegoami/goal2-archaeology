"""[designed: T138a/#727] Synthetic roster invariants, no original-rule claim."""
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import patch
from runtime.original_match.extended_roster import ExtendedRoster


class Roster(unittest.TestCase):
    def setUp(self):
        self.core=list(range(1,21));self.pool=list(range(21,101))

    def plan(self,n=4):
        return ExtendedRoster.from_squads(self.core,self.pool,self.pool[:n])

    def test_twenty_twenty_two_twenty_four_and_partial_choices(self):
        for count in range(5):
            with self.subTest(count=count):
                roster=self.plan(count)
                self.assertEqual(roster.squad(self.core),tuple(range(1,21+count)))
                self.assertEqual(roster.bench(self.core),tuple(range(12,21+count)))

    def test_input_and_projection_are_detached_and_immutable(self):
        extra=[21,22];r=ExtendedRoster.from_squads(self.core,self.pool,extra)
        self.core[0]=100;self.pool[0]=200;extra[0]=300
        self.assertEqual(r.members,tuple(range(1,23)))
        with self.assertRaises(FrozenInstanceError):r.members=()

    def test_promotion_exchanges_only_a_native_bench_slot(self):
        r=self.plan();p=r.promotion(24,self.core,self.pool)
        self.assertEqual((p.incoming,p.displaced,p.squad_index,p.pool_index),(24,20,19,3))
        core=list(self.core);pool=list(self.pool)
        core[p.squad_index],pool[p.pool_index]=pool[p.pool_index],core[p.squad_index]
        self.assertEqual(core[:11],self.core[:11])
        self.assertEqual(set(r.squad(core)),set(r.members))
        self.assertEqual(len(r.bench(core)),13)
        self.assertIn(20,r.bench(core))
        # A displaced ordinary bench member remains selectable through the same plan.
        next_plan=r.promotion(20,core,pool,unavailable=(24,))
        self.assertEqual(next_plan.displaced,24)
        self.assertEqual(next_plan.squad_index,19)
        self.assertEqual(r.members,tuple(range(1,25)))

    def test_unavailable_bench_preference_is_deterministic(self):
        p=self.plan().promotion(21,self.core,self.pool,unavailable=(12,16))
        self.assertEqual((p.squad_index,p.displaced),(15,16))
        self.assertIsNone(self.plan().promotion(12,self.core,self.pool))

    def test_observed_external_recruitment_replaces_exactly_one_member(self):
        r=self.plan();core=list(self.core);core[4]=50
        changed=r.replaced(5,50,core)
        self.assertEqual(set(changed.members),(set(r.members)-{5})|{50})
        self.assertEqual(len(changed.bench(core)),13)
        self.assertEqual(r.members,tuple(range(1,25)))

    def test_selected_member_swap_never_recruits(self):
        r=self.plan();core=list(self.core);core[-1]=24
        self.assertIs(r.replaced(20,24,core),r)
        self.assertEqual(set(r.squad(core)),set(r.members))

    def test_malformed_creation_rejects_all_word_and_size_edges(self):
        bad=[(self.core,self.pool,[True]),(self.core,self.pool,[0]),
             (self.core,self.pool,[3061]),(self.core,self.pool,[21,21]),
             (self.core,self.pool,[1]),(self.core,self.pool,[21,22,23,24,25]),
             (self.core[:-1],self.pool,[21]),(self.core,self.pool+[101],[21]),
             (self.core,[1]+self.pool[1:],[22]),(self.core,self.pool,'21')]
        for args in bad:
            with self.subTest(args=args):self.assertRaises(ValueError,ExtendedRoster.from_squads,*args)

    def test_stale_core_pool_and_preference_are_pure_refusals(self):
        r=self.plan();before=r.members
        bad=[lambda:r.bench(self.core[:-1]),lambda:r.bench(self.core[:-1]+[99]),
             lambda:r.promotion(99,self.core,self.pool),lambda:r.promotion(True,self.core,self.pool),
             lambda:r.promotion(21,self.core,self.pool[1:]),
             lambda:r.promotion(21,self.core,self.pool,unavailable=(1,)),
             lambda:r.replaced(5,50,self.core),lambda:r.replaced(5,5,self.core),
             lambda:r.replaced(99,50,self.core)]
        for action in bad:
            with self.subTest(action=action):self.assertRaises(ValueError,action)
            self.assertEqual(r.members,before)

    def test_planning_cannot_construct_a_backend(self):
        with patch('runtime.original_match.port.engine.PortMachine',side_effect=AssertionError('backend forbidden')):
            r=self.plan();self.assertEqual(len(r.bench(self.core)),13)
            self.assertEqual(r.promotion(21,self.core,self.pool).incoming,21)
