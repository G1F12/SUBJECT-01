#!/usr/bin/env python3
"""Structure and SHA256 provenance validation, stdlib only. Exit nonzero on failure."""
from pathlib import Path
import json, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
REG={'hypotheses':'HYP','experiments':'EXP','findings':'FND','negative_results':'NEG','decisions':'DEC','issues':'ISS','sources':'SRC'}
all_ids=set(); datas={}; problems=[]
for name,prefix in REG.items():
    try: a=json.loads((ROOT/'registry'/f'{name}.json').read_text('utf-8'))
    except Exception as e: problems.append(f'cannot read {name}: {e}');continue
    if not isinstance(a,list): problems.append(f'{name}: not list');continue
    datas[name]=a
    for d in a:
        k=d.get('id','')
        if not k.startswith(prefix+'-') or len(k)!=8 or not k[4:].isdigit():problems.append(f'bad ID: {k}')
        if k in all_ids:problems.append(f'duplicate ID: {k}')
        all_ids.add(k)
for e in datas.get('experiments',[]):
    for k in ['model','inputs','report']:
        if not (ROOT/e[k]).is_file():problems.append(f'missing {e["id"]}:{k}: {e[k]}')
    for op in e['outputs']:
        if not (ROOT/op).is_file():problems.append(f'missing output {e["id"]}: {op}')
for name in ['findings','negative_results']:
    for e in datas.get(name,[]):
        if e.get('experiment_id') not in all_ids:problems.append(f'bad experiment ref in {e["id"]}')
for e in datas.get('hypotheses',[]):
    for ref in e.get('related_experiments',[]):
        if ref not in all_ids:problems.append(f'bad exp ref {ref}')
if any(e.get('verification')!='not_independently_checked' for e in datas.get('sources',[])):
    print('INFO: independently verified source(s) present; ensure check reports exist')
try: manifest=json.loads((ROOT/'provenance/import_manifest.json').read_text('utf-8'))
except Exception as e:problems.append('missing manifest: '+str(e));manifest=[]
for entry in manifest:
    p=ROOT/entry['path']
    if not p.is_file():problems.append(f'manifest file missing: {p}');continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=entry['sha256']:problems.append(f'hash mismatch: {p}')
for rel in ['PROJECT_STATE.md','GOVERNANCE.md','CHANGELOG.md','handoffs/CURRENT.md']:
    if not (ROOT/rel).is_file():problems.append(f'missing governing file: {rel}')
if problems:
    print('FAIL: '+'; '.join(problems));sys.exit(1)
print('PASS: registries', ', '.join(f'{k}={len(v)}' for k,v in datas.items()))
print(f'PASS: {len(manifest)} imported file checksums match; references/files consistent')
