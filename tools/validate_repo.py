#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
ERRORS=[]
def err(msg): ERRORS.append(msg)
def load_yaml(path):
    try: return yaml.safe_load(path.read_text(encoding='utf-8'))
    except Exception as e: err(f'{path.relative_to(ROOT)}: invalid YAML: {e}'); return None
def validate_schema(data,schema_name,label):
    schema=json.loads((ROOT/'schemas'/'repository'/schema_name).read_text(encoding='utf-8'))
    for e in Draft202012Validator(schema).iter_errors(data): err(f'{label}: {e.message}')
def authority_check(data,label):
    if not isinstance(data,dict): return
    if data.get('lifecycle')=='draft' and data.get('authority')=='canonical': err(f'{label}: draft cannot be canonical')

def main():
    required=['AGENTS.md','ai/repo-map.yaml','skills/catalog.yaml','product/capability-map.yaml','domains/glossary.yaml','domains/context-map.yaml']
    for p in required:
        if not (ROOT/p).exists(): err(f'missing required file: {p}')

    for p,schema in [(ROOT/'product/capability-map.yaml','capability-map.schema.json'),(ROOT/'skills/catalog.yaml','skill-catalog.schema.json')]:
        data=load_yaml(p)
        if data is not None:
            authority_check(data,str(p.relative_to(ROOT)))
            validate_schema(data,schema,str(p.relative_to(ROOT)))

    context=load_yaml(ROOT/'domains/context-map.yaml') or {}
    authority_check(context,'domains/context-map.yaml')
    ids={x.get('id') for x in context.get('contexts',[]) if isinstance(x,dict)}
    for d in sorted((ROOT/'domains').iterdir()):
        if not d.is_dir() or d.name.startswith('_'): continue
        manifest=d/'manifest.yaml'
        if not manifest.exists(): err(f'{d.relative_to(ROOT)}: missing manifest.yaml'); continue
        data=load_yaml(manifest)
        if data is None: continue
        authority_check(data,str(manifest.relative_to(ROOT)))
        validate_schema(data,'domain-manifest.schema.json',str(manifest.relative_to(ROOT)))
        if data.get('id')!=d.name: err(f'{manifest.relative_to(ROOT)}: id must match directory')
        if d.name not in ids: err(f'{manifest.relative_to(ROOT)}: domain absent from context-map.yaml')
        if not (d/'AGENTS.md').exists(): err(f'{d.relative_to(ROOT)}: missing AGENTS.md')

    catalog=load_yaml(ROOT/'skills/catalog.yaml') or {}
    names=set()
    for s in catalog.get('skills',[]):
        name=s.get('name'); path=ROOT/'skills'/s.get('path','')/'SKILL.md'
        if name in names: err(f'skills/catalog.yaml: duplicate skill {name}')
        names.add(name)
        if not path.exists(): err(f'skills/catalog.yaml: missing {path.relative_to(ROOT)}')
        elif not path.read_text(encoding='utf-8').startswith('---\n'): err(f'{path.relative_to(ROOT)}: missing YAML frontmatter')

    for d in sorted((ROOT/'changes'/'active').iterdir()):
        if not d.is_dir(): continue
        change=d/'change.yaml'
        if not change.exists(): err(f'{d.relative_to(ROOT)}: missing change.yaml'); continue
        data=load_yaml(change)
        if data is None: continue
        authority_check(data,str(change.relative_to(ROOT)))
        validate_schema(data,'change.schema.json',str(change.relative_to(ROOT)))
        if not d.name.startswith(data.get('id','')+'-'): err(f'{d.relative_to(ROOT)}: directory must start with change id')
        for rel in ['context.md','proposal.md','specs','design.md','tasks.md','implementation','validation','reviews','evidence']:
            if not (d/rel).exists(): err(f'{d.relative_to(ROOT)}: missing {rel}')

    forbidden=[ROOT/'skills'/'engineering',ROOT/'skills'/'task-breakdown',ROOT/'skills'/'proposal-generation',ROOT/'skills'/'spec-delta-generation',ROOT/'skills'/'design-generation',ROOT/'skills'/'dev-task-package',ROOT/'knowledge'/'snapshots',ROOT/'knowledge'/'extracted',ROOT/'evals'/'domain']
    for p in forbidden:
        if p.exists(): err(f'legacy path must be removed: {p.relative_to(ROOT)}')

    if ERRORS:
        print('Repository validation failed:')
        for e in ERRORS: print(f'- {e}')
        return 1
    print('Repository validation passed.')
    return 0
if __name__=='__main__': sys.exit(main())
