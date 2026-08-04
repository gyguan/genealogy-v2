#!/usr/bin/env python3
from __future__ import annotations
import json, os, urllib.request
from datetime import datetime
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def api(url,token,method='GET',body=None):
 data=json.dumps(body).encode() if body is not None else None; req=urllib.request.Request(url,data=data,method=method,headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'}); 
 with urllib.request.urlopen(req) as r: return json.load(r)
def main():
 token=os.getenv('GITHUB_TOKEN'); repo=os.getenv('GITHUB_REPOSITORY'); number=os.getenv('PR_NUMBER'); head=os.getenv('PR_HEAD_SHA')
 if not all((token,repo,number,head)): print('PR governance skipped outside pull request.'); return 0
 cfg=yaml.safe_load((ROOT/'.github/governance.yaml').read_text())
 if int(number) in cfg.get('bootstrap_pull_requests',[]): print(f'PR #{number} is an explicit bootstrap exception.'); return 0
 pr=api(f'https://api.github.com/repos/{repo}/pulls/{number}',token)
 if pr['head']['sha']!=head: print('PR head SHA mismatch.'); return 1
 reviews=api(f'https://api.github.com/repos/{repo}/pulls/{number}/reviews?per_page=100',token); rule=cfg.get('review',{}); actors=set(rule.get('actors',[])); states=set(rule.get('accepted_states',[])); current=[r for r in reviews if r.get('user',{}).get('login','').removesuffix('[bot]') in actors and r.get('commit_id')==head]
 if any(r.get('state')=='CHANGES_REQUESTED' for r in current): print('Current head has requested changes.'); return 1
 accepted=any(r.get('state') in states for r in current)
 if not accepted and rule.get('accept_positive_reaction'):
  reactions=api(f'https://api.github.com/repos/{repo}/issues/{number}/reactions?per_page=100',token); pushed=pr['head'].get('repo',{}).get('pushed_at'); committed=datetime.fromisoformat(pushed.replace('Z','+00:00')) if pushed else None; accepted=any(x.get('content')=='+1' and x.get('user',{}).get('login','').removesuffix('[bot]') in actors and (not committed or datetime.fromisoformat(x['created_at'].replace('Z','+00:00'))>=committed) for x in reactions)
 if not accepted: print('No configured review or positive reaction for current head.'); return 1
 if rule.get('require_resolved_threads'):
  owner,name=repo.split('/',1); query='''query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){reviewThreads(first:100){nodes{isResolved isOutdated}}}}}'''; result=api('https://api.github.com/graphql',token,'POST',{'query':query,'variables':{'owner':owner,'name':name,'number':int(number)}}); threads=result['data']['repository']['pullRequest']['reviewThreads']['nodes']
  if any(not t['isResolved'] and not t['isOutdated'] for t in threads): print('Unresolved current review threads remain.'); return 1
 print('PR governance passed.'); return 0
if __name__=='__main__': raise SystemExit(main())
