"""EXP-0099: reproduce the pre-specified data gate and diagnostic aggregation."""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest=='a7bd93d472be62049f782598a28d34536199e6515b58b136da099507b3c63b1f'
w=load_workbook(p,read_only=True,data_only=True);it=iter(w['MVC PPT'].values);headers=next(it);assert len(headers)==len(set(headers)); data=[];seen=set();invalid_sessions=0;excluded_people=0
for row in it:
 r=dict(zip(headers,row));ident=r['FPnr']
 if ident is None:continue
 assert isinstance(ident,int) and ident not in seen;seen.add(ident);sessions=[]
 for c in (1,2,3):
  tri=[[r[f'Bp{t}{j}MVCm{c}'] for j in (1,2,3)] for t in (1,2,3)]
  if not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for x in tri for v in x):invalid_sessions+=1;continue
  sessions.append((c,tri))
 if len(sessions)>=2:data.append(sessions)
 else:excluded_people+=1
assert len(data)>=8
reported={1:[662,596,625],2:[642,608,622],3:[645,634,582]}; summaries={};gate=True
for c in (1,2,3):
 tri=[r[1] for a in data for r in a if r[0]==c];assert len(tri)>=8
 best=np.array([[max(x)*9.80665 for x in a] for a in tri]).mean(axis=0);mean=np.array([[np.mean(x)*9.80665 for x in a] for a in tri]).mean(axis=0);delta=best-np.array(reported[c]);gate &= bool(np.max(np.abs(delta))<2)
 summaries[str(c)]={'n':len(tri),'published_rounded_N':reported[c],'prespecified_best_of_three_mean_N':best.tolist(),'best_minus_published_N':delta.tolist(),'posthoc_mean_of_three_mean_N':mean.tolist(),'posthoc_mean_minus_published_N':(mean-np.array(reported[c])).tolist()}
assert not gate,'If gate passes, implement preregistered analysis instead of blocked report'
result={'experiment_id':'EXP-0099','classification':'PRESPECIFIED_QUALITY_GATE_FAILED_DIAGNOSTIC_ONLY','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'MANUAL_WORK_RECOVERY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'unique_numeric_ids':len(seen),'admitted_people':len(data),'invalid_sessions':invalid_sessions,'excluded_people_lt_two_sessions':excluded_people,'unit_conversion_N_per_kilogram_force':9.80665,'condition_summaries':summaries,'preregistered_table_agreement_gate':'FAIL','primary_predictive_analysis':'DATA_BLOCKED','alternative_mean_aggregation':'POST_HOC_DIAGNOSTIC_NOT_PRIMARY','limitations':['published article, table and initial rows seen','best vs mean discrepancy not a proof of incorrect source','trial field mapping or processing may differ from the assumed interpretation','no actual force-displacement work or CPE45','no architecture or human enhancement outcome']}
(H/'MANUAL_WORK_RECOVERY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
