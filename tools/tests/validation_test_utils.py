from __future__ import annotations
import shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def copy_repo(test):
    target=Path(tempfile.mkdtemp(prefix='genealogy-validation-'))/'repo'
    shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    test.addCleanup(lambda: shutil.rmtree(target.parent,ignore_errors=True)); return target
def run(path, script): return subprocess.run([sys.executable,script],cwd=path,text=True,capture_output=True,check=False)
