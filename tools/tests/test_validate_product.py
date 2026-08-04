from __future__ import annotations
import unittest, yaml
from validation_test_utils import ROOT, copy_repo, run
class ProductTests(unittest.TestCase):
 def test_current(self): self.assertEqual(0,run(ROOT,'tools/validate_product.py').returncode)
 def test_projection_forbidden(self):
  r=copy_repo(self); p=r/'product/capability-map.yaml'; d=yaml.safe_load(p.read_text()); d['capability_groups']=[]; p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('must not contain capability_groups',x.stdout)
 def test_exact_heading(self):
  r=copy_repo(self); p=r/'product/roadmap.md'; p.write_text(p.read_text().replace('### 成功指标','### 成功指标待补充',1)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('missing section ### 成功指标',x.stdout)
 def test_empty_heading_body(self):
  r=copy_repo(self); p=r/'product/roadmap.md'; p.write_text(p.read_text().replace('### 用户目标\n\n修谱人员','### 用户目标\n\n待补充\n\n修谱人员',1)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode)
 def test_later_closure(self):
  r=copy_repo(self); p=r/'product/releases.yaml'; d=yaml.safe_load(p.read_text()); d['releases'][0]['closure']['recovery']='CAP-PLATFORM-012'; p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('closure recovery uses later capability',x.stdout)
if __name__=='__main__': unittest.main()
