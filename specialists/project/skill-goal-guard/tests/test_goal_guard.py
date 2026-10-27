"""Unit tests for the GoalGuard v0.1 prototype CLI (scripts/goal_guard.py) against examples/portfolio.json.

Run: just test   (or: python -m unittest discover -s tests)
Safety: read-only; loads the example JSON and calls the functions in memory; writes nothing.
"""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from goal_guard import validate,next_actions,assess
DATA=json.loads((ROOT/'examples/portfolio.json').read_text())
class Checks(unittest.TestCase):
 def test_baseline(self): self.assertEqual(validate(DATA),[])
 def test_portfolio_next(self): self.assertEqual(next_actions(DATA,'2026-10-27')['portfolio_next']['task'],'UNC-1')
 def test_task_next(self): self.assertEqual(next_actions(DATA)['task_next']['SMC-1']['next_action'],'Draft power cut and boot-loop acceptance tests')
 def test_park_unlinked(self): self.assertEqual(assess(DATA,{'task_id':'UNC-1','criterion_id':'NEW'})['decision'],'park')
 def test_review_scope(self): self.assertEqual(assess(DATA,{'task_id':'UNC-1','criterion_id':'UNC-C1','adds_scope':True})['decision'],'review')
 def test_proceed(self): self.assertEqual(assess(DATA,{'task_id':'UNC-1','criterion_id':'UNC-C1','adds_scope':False})['decision'],'proceed')
 def test_cycle(self):
  d=copy.deepcopy(DATA);d['projects'][0]['tasks'][0]['depends_on']=['SMC-1'];d['projects'][1]['tasks'][0]['depends_on']=['UNC-1'];self.assertTrue(any('cycle' in i for i in validate(d)))
 def test_done_without_evidence(self):
  d=copy.deepcopy(DATA);d['projects'][0]['tasks'][0]['status']='done';self.assertTrue(any('evidence' in i for i in validate(d)))
 def test_wip(self):
  d=copy.deepcopy(DATA);d['projects'][0]['tasks'][0]['status']='in_progress';d['projects'][1]['tasks'][0]['status']='in_progress';self.assertTrue(any('WIP' in i for i in validate(d)))
 def test_blocked_dep(self):
  d=copy.deepcopy(DATA);d['projects'][1]['tasks'][0]['depends_on']=['UNC-1'];self.assertEqual(next_actions(d)['task_next']['SMC-1']['blocked_by'],['UNC-1'])
if __name__=='__main__':unittest.main()
