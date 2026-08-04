#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]; ERR=[]
CHANGE_TYPES={'product','domain','engineering','governance','security'}; CHANGE_STATES={'draft','review','approved','implementing','completed','cancelled'}; PROFILES={'lightweight','standard','high-risk'}; GATES={'blocked','pending','approved','rejected'}; SOURCES={'github-issue','github-pull-request','github-review','automated-check'}; TASKS={'planned','ready','in-progress','completed','blocked','cancelled'}
def fail(m):ERR.append(m)
def rel(p):return str(p.relative_to(ROOT))
def load(p):
 try:return yaml.safe_load(p.read_text(encoding='utf-8'))
 except Exception as e:fail(f'{rel(p)}: invalid YAML: {e}');return None
def fm(p):
 t=p.read_text(encoding='utf-8')
 if not t.startswith('---\n') or '\n---\n' not in t[4:]:fail(f'{rel(p)}: missing YAML frontmatter');return None
 try:v=yaml.safe_load(t[4:].split('\n---\n',1)[0])
 except Exception as e:fail(f'{rel(p)}: invalid frontmatter: {e}');return None
 return v if isinstance(v,dict) else None
def headings(p,required):
 if not p.exists():return
 hs={m.group(1).strip() for m in re.finditer(r'^##\s+(.+?)\s*$',p.read_text(encoding='utf-8'),re.M)}
 for x in required:
  if x not in hs:fail(f'{rel(p)}: missing section ## {x}')
def domains():
 d=load(ROOT/'domains/context-map.yaml') or {}; rows=d.get('contexts',[]); ids=set(); graph={}
 for x in rows if isinstance(rows,list) else []:
  i=x.get('id') if isinstance(x,dict) else None
  if not isinstance(i,str) or i in ids:fail(f'domains/context-map.yaml: invalid or duplicate context {i}');continue
  ids.add(i);graph[i]=[]
  for dep in x.get('dependencies',[]):
   target=dep.get('target') if isinstance(dep,dict) else None
   if not isinstance(target,str):fail(f'domains/context-map.yaml: {i} invalid dependency');continue
   graph[i].append(target)
 for i,targets in graph.items():
  for t in targets:
   if t not in ids:fail(f'domains/context-map.yaml: {i} depends on unknown domain {t}')
 visiting=set();done=set()
 def visit(n):
  if n in visiting:fail(f'domains/context-map.yaml: dependency cycle at {n}');return
  if n in done:return
  visiting.add(n)
  for t in graph.get(n,[]):visit(t)
  visiting.remove(n);done.add(n)
 for i in ids:visit(i)
 for i in ids:
  p=ROOT/f'domains/{i}.md'
  if not p.exists():fail(f'missing domains/{i}.md');continue
  m=fm(p)
  if m and (m.get('id')!=i or m.get('status') not in {'draft','review','approved','deprecated'}):fail(f'{rel(p)}: invalid id or status')
  if m and ('depends_on' in m or 'dependencies' in m):fail(f'{rel(p)}: dependencies belong only in context-map')
  headings(p,['职责','非职责','关键不变量','主要用例'])
 return ids
def capability_ids():
 m=load(ROOT/'product/capability-map.yaml') or {}; ids=set()
 for fn in m.get('group_files',[]):
  p=ROOT/'product'/str(fn); d=load(p) or {}; items=d.get('group',{}).get('capabilities',[])
  for x in items:
   i=x.get('id') if isinstance(x,dict) else None
   if not isinstance(i,str) or i in ids:fail(f'{rel(p)}: invalid or duplicate capability {i}')
   else:ids.add(i)
 return ids
def decisions(domain_ids):
 ids=set(); data={}
 for p in sorted((ROOT/'decisions').glob('DEC-*.md')):
  m=fm(p)
  if not m:continue
  i=m.get('id')
  if not isinstance(i,str) or not re.fullmatch(r'DEC-\d{4}',i) or i in ids:fail(f'{rel(p)}: invalid decision id');continue
  ids.add(i);data[i]=m
  if m.get('status') not in {'proposed','accepted','rejected','superseded','deprecated'}:fail(f'{rel(p)}: invalid status')
  if any(x not in domain_ids for x in m.get('affected_domains',[])):fail(f'{rel(p)}: invalid affected_domains')
  headings(p,['背景','决策','原因','备选方案','影响','迁移与回退','关联 Change'])
 return ids,data
def task_blocks(p):
 if not p.exists():return []
 t=p.read_text(encoding='utf-8'); ms=list(re.finditer(r'^##\s+(TASK-[A-Z0-9-]+).*$',t,re.M)); out=[]
 for n,m in enumerate(ms):
  b=t[m.end():ms[n+1].start() if n+1<len(ms) else len(t)]; x={'id':m.group(1)}
  for label,key in [('Specs','specs'),('Status','status'),('Tests','tests'),('Evidence','evidence')]:
   q=re.search(rf'^- {label}:\s*(.+?)\s*$',b,re.M)
   if q:x[key]=q.group(1).strip()
  out.append(x)
 return out
def gate(cdir,name,v,version):
 if not isinstance(v,dict) or v.get('status') not in GATES:fail(f'{rel(cdir)}/change.yaml: invalid gate {name}');return None
 if v['status']=='approved':
  fields=['approved_by','approved_at','evidence']+(['source','reference'] if version>=2 else [])
  for f in fields:
   if not v.get(f):fail(f'{rel(cdir)}/change.yaml: approved gate {name} needs {f}')
  if version>=2 and v.get('source') not in SOURCES:fail(f'{rel(cdir)}/change.yaml: gate {name} invalid source')
  if v.get('evidence') and not (cdir/v['evidence']).is_file():fail(f'{rel(cdir)}/change.yaml: missing gate evidence {v["evidence"]}')
 return v['status']
def change(cdir,domain_ids,caps,decs,seen):
 d=load(cdir/'change.yaml') or {}; i=d.get('id'); kind=d.get('change_type'); state=d.get('status'); version=d.get('version',1)
 if not isinstance(i,str) or not re.fullmatch(r'CHG-\d{4}',i) or i in seen:fail(f'{rel(cdir)}/change.yaml: invalid or duplicate id');return
 seen.add(i)
 if not cdir.name.startswith(i+'-') or kind not in CHANGE_TYPES or state not in CHANGE_STATES:fail(f'{rel(cdir)}/change.yaml: invalid directory/type/status')
 profile=d.get('change_profile')
 if version>=2:
  if profile not in PROFILES:fail(f'{rel(cdir)}/change.yaml: version 2 needs valid change_profile')
  if kind in {'product','domain','security'} and profile!='high-risk':fail(f'{rel(cdir)}/change.yaml: {kind} change must use high-risk')
  if kind=='governance' and profile=='lightweight':fail(f'{rel(cdir)}/change.yaml: governance change cannot use lightweight')
 for field,known in [('capabilities',caps),('affected_domains',domain_ids),('affected_decisions',decs)]:
  vals=d.get(field,[])
  if not isinstance(vals,list):fail(f'{rel(cdir)}/change.yaml: {field} must be list');continue
  for x in vals:
   if x not in known:fail(f'{rel(cdir)}/change.yaml: unknown {field} {x}')
 gs=d.get('gates',{}); states={x:gate(cdir,x,gs.get(x),version) for x in ('spec_review','implementation_approval','release_approval')}
 scopes={'product':{'product'},'engineering':{'engineering'},'governance':{'repository-governance'},'security':{'security'},'domain':set()}[kind]
 specs=[]; specids=set(); sd=cdir/'specs'
 if sd.exists():
  for p in sd.glob('*.md'):
   if p.name=='README.md':continue
   specs.append(p)
   if p.stem not in d.get('affected_domains',[]) and p.stem not in scopes:fail(f'{rel(p)}: invalid Spec scope')
   for sid in re.findall(r'^##\s+(SPEC-[A-Z0-9-]+)',p.read_text(encoding='utf-8'),re.M):specids.add(sid)
 ts=task_blocks(cdir/'tasks.md')
 for x in ts:
  if x.get('status') not in TASKS:fail(f'{rel(cdir)}/tasks.md: {x["id"]} invalid status')
  for sid in [v.strip() for v in x.get('specs','').split(',') if v.strip()]:
   if sid not in specids:fail(f'{rel(cdir)}/tasks.md: {x["id"]} unknown Spec {sid}')
  if not x.get('tests'):fail(f'{rel(cdir)}/tasks.md: {x["id"]} needs Tests')
  if x.get('status')=='completed' and (not x.get('evidence') or not (cdir/x['evidence']).is_file()):fail(f'{rel(cdir)}/tasks.md: {x["id"]} evidence missing')
 headings(cdir/'proposal.md',['背景与问题','关联产品能力','目标','非目标','范围与影响领域','关联 Decision','风险','成功标准']); headings(cdir/'design.md',['方案概览','领域与数据影响','接口与模块边界','安全与隐私','测试 Seam','失败、补偿与回滚','迁移方案','备选方案与权衡'])
 if state in {'review','approved','implementing','completed'} and not specs:fail(f'{rel(cdir)}: active change needs Specs')
 if state in {'approved','implementing','completed'} and states['spec_review']!='approved':fail(f'{rel(cdir)}/change.yaml: {state} requires approved spec_review')
 if state in {'implementing','completed'} and states['implementation_approval']!='approved':fail(f'{rel(cdir)}/change.yaml: {state} requires approved implementation_approval')
 if state=='completed' and (states['release_approval']!='approved' or any(x.get('status')!='completed' for x in ts)):fail(f'{rel(cdir)}: completed change requires release gate and completed tasks')
def main():
 ERR.clear(); required=['README.md','AGENTS.md','SECURITY.md','product/releases.yaml','product/capability-map.yaml','domains/context-map.yaml','domains/glossary.yaml','changes/_template/change.yaml','tools/check.py','tools/context.py','tools/new_change.py','tools/validate_product.py','tools/validate_pr.py']
 for x in required:
  if not (ROOT/x).exists():fail(f'missing required file: {x}')
 ds=domains(); caps=capability_ids(); decs,_=decisions(ds); seen=set()
 for p in sorted((ROOT/'changes').iterdir()):
  if p.is_dir() and p.name!='_template':change(p,ds,caps,decs,seen)
 if ERR:
  print('Repository validation failed:');[print(f'- {x}') for x in ERR];return 1
 print('Repository validation passed.');return 0
if __name__=='__main__':raise SystemExit(main())
