import csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;dictionary=Path(sys.argv[2]);dictionary_hash=hashlib.sha256(dictionary.read_bytes()).hexdigest();assert dictionary_hash=='9d567399f6e997ed6990148fd3c56de823985e78e74239a8c7a57d10231b6246'
wb=load_workbook(dictionary,read_only=True,data_only=True); defs=[row for row in wb['Data_Dictionary'].values if len(row)>5 and row[1]=='Body_Mass_kg'];assert len(defs)==1 and defs[0][5]=='Baseline'
p=Path(sys.argv[1]);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest=='4031c155a906e669c6ebb96f214eabd197eafe51e4069e0465d6207e2aa7ff33'
with p.open(encoding='utf-8-sig',newline='') as f: raw=list(csv.DictReader(f))
assert {r['Group'] for r in raw}=={'CG','EG'} and {r['Timepoint'] for r in raw}=={'Pre','Post'}
fields=['Lateral_CMJ_Height_cm','RFD_Lateral_N_s','Reaction_Time_ms','Stroke_Accuracy_pct','Body_Mass_kg']; people={}; seen=set()
for row in raw:
 key=(row['ID'],row['Group'],row['Timepoint']);assert key not in seen;seen.add(key); people.setdefault(row['ID'],[]).append(row)
sets={'EG':[],'CG':[]}; excluded={}
for ident,rr in people.items():
 reason=None
 if len(rr)!=2 or {r['Timepoint'] for r in rr}!={'Pre','Post'}:reason='missing_or_duplicate_timepoint'
 elif len({r['Group'] for r in rr})!=1:reason='group_changed'
 else:
  try:
   pre=next(r for r in rr if r['Timepoint']=='Pre');post=next(r for r in rr if r['Timepoint']=='Post'); a=np.array([float(pre[k]) for k in fields]);b=np.array([float(post[k]) for k in fields]);
   if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)) or a[4]<=0:reason='invalid_values'
  except (ValueError,KeyError):reason='invalid_values'
 if reason:excluded[reason]=excluded.get(reason,0)+1;continue
 delta=b-a;mass_pct=100*delta[4]/a[4];component=[delta[0]>0,delta[1]>0,delta[2]<0,delta[3]>0];sets[pre['Group']].append((a,delta,mass_pct,component))
assert all(len(v)>=5 for v in sets.values())
rng=np.random.default_rng(20261120); output={};boot={}
for group,rows in sets.items():
 a=np.stack([r[0] for r in rows]); d=np.stack([r[1] for r in rows]);mass=np.array([r[2] for r in rows]);flags=np.array([r[3] for r in rows]); joint=np.all(flags,axis=1).astype(float);inds=rng.integers(0,len(rows),(10000,len(rows)));boot[group]=joint[inds].mean(axis=1)
 output[group]={'n':len(rows),'four_direction_count':int(joint.sum()),'four_direction_fraction':float(joint.mean()),'component_counts':{k:int(flags[:,i].sum()) for i,k in enumerate(fields[:4])},'initial_mean':{k:float(a[:,i].mean()) for i,k in enumerate(fields)},'change_mean':{k:float(d[:,i].mean()) for i,k in enumerate(fields)},'change_median':{k:float(np.median(d[:,i])) for i,k in enumerate(fields)},'duplicated_baseline_mass_relative_change_pct_range':[float(mass.min()),float(mass.max())],'duplicated_baseline_mass_outside_5pct':int(np.sum(abs(mass)>5))}
diff=output['EG']['four_direction_fraction']-output['CG']['four_direction_fraction'];ci=np.quantile(boot['EG']-boot['CG'],[.025,.975]);result={'experiment_id':'EXP-0096','classification':'OBSERVATIONAL_SECONDARY_MULTIFUNCTIONAL_PROFILE','data_sha256_bytes':digest,'dictionary_sha256_bytes':dictionary_hash,'mass_comparability_status':'DATA_BLOCKED_BASELINE_ONLY_FIELD','joint_fraction_interpretation':'four directional components only; recorded repeated mass is baseline, not an observed post measurement','protocol_sha256_lf':text_sha256(H/'TABLE_TENNIS_PROFILE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'source_rows':len(raw),'source_people':len(people),'excluded_by_reason':excluded,'groups':output,'four_direction_fraction_difference_eg_minus_cg':diff,'four_direction_fraction_difference_95_percentile_bootstrap':ci.tolist(),'limitations':['exploratory published trial; underlying randomization and device reliability unverified','zero-change boundaries are not measurement-error thresholds','mass field is documented baseline only and copied into post rows; prespecified mass-comparability gate is unassessable' ,'RFD is not maximal functional force; no CPE45, tissue, or post-load outcome','not architecture A or causal evidence of human enhancement']}
(H/'TABLE_TENNIS_PROFILE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
