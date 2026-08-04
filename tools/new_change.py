#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/'changes'/'_template'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('id', help='CHG-0001')
    p.add_argument('slug', help='stable-kebab-name')
    args=p.parse_args()
    if not args.id.startswith('CHG-') or len(args.id)!=8 or not args.id[4:].isdigit():
        raise SystemExit('id must match CHG-0001')
    target=ROOT/'changes'/'active'/f'{args.id}-{args.slug}'
    if target.exists(): raise SystemExit(f'already exists: {target}')
    shutil.copytree(TEMPLATE,target)
    change=target/'change.yaml'
    text=change.read_text(encoding='utf-8').replace('CHG-0000',args.id).replace('change-name',args.slug)
    change.write_text(text,encoding='utf-8')
    print(target.relative_to(ROOT))
if __name__=='__main__': main()
