from __future__ import annotations
import re, unittest, yaml
from validation_test_utils import ROOT, copy_repo, run
class ProductTests(unittest.TestCase):
 def test_current(self): self.assertEqual(0,run(ROOT,'tools/validate_product.py').returncode)
 def test_projection_forbidden(self):
  r=copy_repo(self); p=r/'product/capability-map.yaml'; d=yaml.safe_load(p.read_text()); d['capability_groups']=[]; p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('compatibility projection is forbidden',x.stdout)
 def test_exact_heading(self):
  r=copy_repo(self); p=r/'product/roadmap.md'; p.write_text(p.read_text().replace('### 成功指标','### 成功指标待补充',1)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('missing exact section ### 成功指标',x.stdout)
 def test_placeholder_body(self):
  r=copy_repo(self); p=r/'product/roadmap.md'; text=p.read_text(); text=re.sub(r'(## V0\.1[\s\S]*?### 用户目标\n\n)[\s\S]*?(\n### 纵向闭环)',r'\1待补充\2',text,count=1); p.write_text(text); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('empty or placeholder',x.stdout)
 def test_later_closure(self):
  r=copy_repo(self); p=r/'product/releases.yaml'; d=yaml.safe_load(p.read_text()); d['releases'][0]['closure']['recovery']='CAP-PLATFORM-012'; p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False)); x=run(r,'tools/validate_product.py'); self.assertNotEqual(0,x.returncode); self.assertIn('closure recovery uses later capability',x.stdout)
if __name__=='__main__': unittest.main()
