from __future__ import annotations
import os, subprocess, sys, unittest
from validation_test_utils import ROOT, copy_repo
class ToolTests(unittest.TestCase):
 def test_new_change_and_context(self):
  r=copy_repo(self); x=subprocess.run([sys.executable,'tools/new_change.py','CHG-0099','sample','--type','engineering','--issue','99'],cwd=r,text=True,capture_output=True); self.assertEqual(0,x.returncode,x.stdout+x.stderr); y=subprocess.run([sys.executable,'tools/context.py','CHG-0099'],cwd=r,text=True,capture_output=True); self.assertEqual(0,y.returncode); self.assertIn('CHG-0099-sample/change.yaml',y.stdout)
 def test_pr_skip(self):
  e=os.environ.copy(); [e.pop(k,None) for k in ('GITHUB_TOKEN','GITHUB_REPOSITORY','PR_NUMBER','PR_HEAD_SHA')]; x=subprocess.run([sys.executable,'tools/validate_pr.py'],cwd=ROOT,text=True,capture_output=True,env=e); self.assertEqual(0,x.returncode); self.assertIn('skipped',x.stdout)
if __name__=='__main__': unittest.main()
