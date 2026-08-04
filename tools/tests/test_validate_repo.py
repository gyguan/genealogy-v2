from __future__ import annotations
import unittest, yaml
from validation_test_utils import ROOT, copy_repo, run
class RepoTests(unittest.TestCase):
 def test_current(self): self.assertEqual(0,run(ROOT,'tools/validate_repo.py').returncode)
 def test_v2_gate_source(self):
  r=copy_repo(self); p=r/'changes/CHG-0004-v01-recovery-loop/change.yaml'; d=yaml.safe_load(p.read_text()); d['gates']['spec_review']['source']=None; p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False)); x=run(r,'tools/validate_repo.py'); self.assertNotEqual(0,x.returncode); self.assertIn('needs source',x.stdout)
 def test_product_profile(self):
  r=copy_repo(self); p=r/'changes/CHG-0004-v01-recovery-loop/change.yaml'; d=yaml.safe_load(p.read_text()); d['change_profile']='standard'; p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False)); x=run(r,'tools/validate_repo.py'); self.assertNotEqual(0,x.returncode); self.assertIn('must use high-risk',x.stdout)
if __name__=='__main__': unittest.main()
