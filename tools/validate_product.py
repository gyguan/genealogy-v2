#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
ERRORS=[]
RELEASE_STATES={'candidate','planned','in-progress','delivered','deprecated'}
PLANNING_DEPTHS={'detailed','bounded','outcome-only','candidate-only'}
CAPABILITY_TYPES={'business','application','platform'}
CAPABILITY_STATES={'candidate','planned','in-progress','delivered','deprecated'}
RELEASE_PRIORITIES={'must','should','could'}
PLANNING_CONFIDENCE={'high','medium','low'}
ROADMAP_REQUIRED=('用户目标','纵向闭环','主要能力','明确不包含','版本验收','成功指标','核心风险')
PLACEHOLDERS={'待补充','待完善','tbd','todo','n/a','na','无'}
def fail(m): ERRORS.append(m)
def rel(p): return str(p.relative_to(ROOT))
def load(p):
 try:return yaml.safe_load(p.read_text(encoding='utf-8'))
 except Exception as e: fail(f'{rel(p)}: invalid YAML: {e}'); return None
def domain_ids():
 d=load(ROOT/'domains/context-map.yaml') or {}; return {x['id'] for x in d.get('contexts',[]) if isinstance(x,dict) and isinstance(x.get('id'),str)}
def releases():
 d=load(ROOT/'product/releases.yaml') or {}; items=d.get('releases',[]) if isinstance(d,dict) else []; result={}; order={}
 if not isinstance(items,list) or not items: fail('product/releases.yaml: releases must be a non-empty list'); return result,order
 for pos,item in enumerate(items):
  rid=item.get('id') if isinstance(item,dict) else None
  if not isinstance(rid,str) or not re.fullmatch(r'V\d+\.\d+',rid) or rid in result: fail(f'product/releases.yaml: invalid or duplicate release id {rid}'); continue
  result[rid]=item; order[rid]=pos
  if not isinstance(item.get('name'),str) or not item['name'].strip(): fail(f'product/releases.yaml: {rid} needs name')
  if not isinstance(item.get('goal'),str) or not item['goal'].strip(): fail(f'product/releases.yaml: {rid} needs goal')
  if item.get('status') not in RELEASE_STATES: fail(f'product/releases.yaml: {rid} has invalid status')
  if item.get('planning_confidence') not in PLANNING_CONFIDENCE: fail(f'product/releases.yaml: {rid} has invalid planning_confidence')
  if item.get('planning_depth') not in PLANNING_DEPTHS: fail(f'product/releases.yaml: {rid} has invalid planning_depth')
  if item.get('status')=='candidate' and item.get('planning_confidence')!='low': fail(f'product/releases.yaml: candidate {rid} must have low planning_confidence')
  if rid in {'V0.1','V0.2','V0.3','V0.4','V0.5'}:
   closure=item.get('closure'); required={'source','review','readback','portability','recovery'}
   if rid!='V0.1': required.add('authorization')
   if not isinstance(closure,dict): fail(f'product/releases.yaml: {rid} needs closure mapping')
   else:
    miss=sorted(required-set(closure))
    if miss: fail(f"product/releases.yaml: {rid} closure missing {', '.join(miss)}")
 return result,order
def roadmap_sections(block):
 hs=list(re.finditer(r'^###\s+(.+?)\s*$',block,re.M)); out={}
 for i,m in enumerate(hs): out[m.group(1).strip()]=block[m.end():hs[i+1].start() if i+1<len(hs) else len(block)].strip()
 return out
def meaningful(text):
 n=re.sub(r'<!--.*?-->','',text,flags=re.S).strip(); n=re.sub(r'^[\s\-*]+|[\s\-*]+$','',n).strip().lower(); return bool(n) and n not in PLACEHOLDERS
def roadmap():
 p=ROOT/'product/roadmap.md'; text=p.read_text(encoding='utf-8') if p.exists() else ''; hs=list(re.finditer(r'^##\s+(V\d+\.\d+)\b.*$',text,re.M)); blocks={}; titles={}
 for i,m in enumerate(hs): blocks[m.group(1)]=text[m.end():hs[i+1].start() if i+1<len(hs) else len(text)]; titles[m.group(1)]=m.group(0)
 for rid in ('V0.1','V0.2','V0.3','V0.4','V0.5'):
  b=blocks.get(rid)
  if b is None: fail(f'product/roadmap.md: missing release {rid}'); continue
  sec=roadmap_sections(b)
  for title in ROADMAP_REQUIRED:
   if title not in sec: fail(f'product/roadmap.md: {rid} missing exact section ### {title}')
   elif not meaningful(sec[title]): fail(f'product/roadmap.md: {rid} section ### {title} is empty or placeholder')
 for rid in ('V1.1','V1.2','V2.0'):
  if '候选' not in titles.get(rid,''): fail(f'product/roadmap.md: {rid} must be marked as candidate')
def capabilities(domains,release_data,release_order):
 mp=ROOT/'product/capability-map.yaml'; manifest=load(mp) or {}
 if isinstance(manifest,dict) and 'capability_groups' in manifest: fail('product/capability-map.yaml: hand-maintained compatibility projection is forbidden')
 files=manifest.get('group_files',[]) if isinstance(manifest,dict) else []
 if manifest.get('release_source')!='releases.yaml': fail('product/capability-map.yaml: release_source must be releases.yaml')
 if manifest.get('capability_directory')!='capabilities': fail('product/capability-map.yaml: capability_directory must be capabilities')
 if not isinstance(files,list) or not files: fail('product/capability-map.yaml: group_files must be a non-empty list'); return {}
 listed={str(v) for v in files}; actual={str(p.relative_to(ROOT/'product')) for p in (ROOT/'product/capabilities').glob('*.yaml')}
 for v in sorted(listed-actual): fail(f'product/capability-map.yaml: listed capability file does not exist: {v}')
 for v in sorted(actual-listed): fail(f'product/{v}: capability file is not listed in capability-map.yaml')
 ids=set(); groups=set(); records={}; paths={}; required={'id','name','description','capability_type','primary_domain','supporting_domains','target_release','release_priority','status','planning_confidence','depends_on'}
 for fn in files:
  p=ROOT/'product'/str(fn)
  if not p.exists(): continue
  data=load(p) or {}; group=data.get('group') if isinstance(data,dict) else None; gid=group.get('id') if isinstance(group,dict) else None
  if not isinstance(gid,str) or not gid.startswith('CAP-GROUP-') or gid in groups: fail(f'{rel(p)}: invalid or duplicate group id {gid}'); continue
  groups.add(gid); items=group.get('capabilities',[])
  if not isinstance(items,list) or not items: fail(f'{rel(p)}: capabilities must be a non-empty list'); continue
  for item in items:
   iid=item.get('id') if isinstance(item,dict) else None
   if not isinstance(iid,str) or not re.fullmatch(r'CAP-[A-Z0-9-]+',iid) or iid in ids: fail(f'{rel(p)}: invalid or duplicate capability id {iid}'); continue
   ids.add(iid); records[iid]=item; paths[iid]=rel(p); miss=sorted(required-set(item))
   if miss: fail(f"{rel(p)}: {iid} missing fields {', '.join(miss)}")
   kind=item.get('capability_type')
   if kind not in CAPABILITY_TYPES: fail(f'{rel(p)}: {iid} has invalid capability_type')
   if kind=='platform' and (not isinstance(item.get('platform_area'),str) or not item['platform_area'].strip()): fail(f'{rel(p)}: platform capability {iid} needs platform_area')
   primary=item.get('primary_domain'); supporting=item.get('supporting_domains')
   if primary not in domains: fail(f'{rel(p)}: {iid} has invalid primary_domain {primary}')
   if not isinstance(supporting,list) or any(v not in domains for v in supporting): fail(f'{rel(p)}: {iid} has invalid supporting_domains')
   rid=item.get('target_release')
   if rid not in release_data: fail(f'{rel(p)}: {iid} has unknown target_release {rid}')
   if item.get('release_priority') not in RELEASE_PRIORITIES: fail(f'{rel(p)}: {iid} has invalid release_priority')
   if item.get('status') not in CAPABILITY_STATES: fail(f'{rel(p)}: {iid} has invalid status')
   if item.get('planning_confidence') not in PLANNING_CONFIDENCE: fail(f'{rel(p)}: {iid} has invalid planning_confidence')
   if release_data.get(rid,{}).get('status')=='candidate' and (item.get('status')!='candidate' or item.get('planning_confidence')!='low'): fail(f'{rel(p)}: candidate {iid} must have low confidence and candidate status')
   if not isinstance(item.get('depends_on'),list): fail(f'{rel(p)}: {iid}.depends_on must be a list')
 graph={}
 for iid,item in records.items():
  graph[iid]=[]
  for target in item.get('depends_on',[]):
   if target not in records: fail(f'{paths[iid]}: {iid} depends on unknown capability {target}'); continue
   graph[iid].append(target); cr=item.get('target_release'); tr=records[target].get('target_release')
   if cr in release_order and tr in release_order and release_order[tr]>release_order[cr]: fail(f'{paths[iid]}: {iid} depends on later capability {target} ({tr})')
 visiting=set(); visited=set()
 def visit(node,trail):
  if node in visiting: fail('product capabilities: dependency cycle '+' -> '.join(trail+[node])); return
  if node in visited:return
  visiting.add(node)
  for target in graph.get(node,[]): visit(target,trail+[node])
  visiting.remove(node); visited.add(node)
 for node in sorted(graph):visit(node,[])
 return records
def validate_closure(release_data,release_order,records):
 for rid,release in release_data.items():
  closure=release.get('closure')
  if not isinstance(closure,dict): continue
  for role,cid in closure.items():
   if cid not in records: fail(f'product/releases.yaml: {rid} closure {role} references unknown capability {cid}'); continue
   tr=records[cid].get('target_release')
   if rid in release_order and tr in release_order and release_order[tr]>release_order[rid]: fail(f'product/releases.yaml: {rid} closure {role} uses later capability {cid} ({tr})')
def main():
 ERRORS.clear(); domains=domain_ids(); release_data,release_order=releases(); roadmap(); records=capabilities(domains,release_data,release_order); validate_closure(release_data,release_order,records)
 if ERRORS:
  print('Product validation failed:'); [print(f'- {m}') for m in ERRORS]; return 1
 print('Product validation passed.'); return 0
if __name__=='__main__': raise SystemExit(main())
