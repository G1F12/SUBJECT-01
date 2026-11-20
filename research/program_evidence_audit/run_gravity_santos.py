"""EXP-0091: compare gravity-only corrected scenarios on reused Santos data."""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;path=Path(sys.argv[1]);digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest=='8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe'
prior_path=H/'HIP_POSTURE_RESULTS.json';audit_path=H/'GRAVITY_AUDIT_RESULTS.json';rebuilt_path=H/'GRAVITY_REBUILD_RESULTS.json';prior=json.loads(prior_path.read_text(encoding='utf-8'));audit=json.loads(audit_path.read_text(encoding='utf-8'));rebuilt=json.loads(rebuilt_path.read_text(encoding='utf-8'))
def number(pose,gravity):return next(x['force_N'] for x in audit['scenarios'] if x['pose_deg']==pose and x['gravity']==gravity and x['variant']=='baseline')
old100=prior['baseline100_force_N'];old110=prior['baseline110_force_N'];fixed100=rebuilt['outputs']['chain']['scenarios']['baseline']['postures']['flexed_100deg_int']['compatible_lp_solution']['bilateral_footplate_force_N'];fixed110=number(110,'corrected');assert old100==number(100,'original') and old110==number(110,'original') and fixed100==number(100,'corrected')
rows=list(load_workbook(path,read_only=True,data_only=True)['Mechanical+EMG'].values);assert rows[1][2]=="PF'" and rows[1][7]=="RFDmax'";people={};person=None;sessions={}
for row in rows[2:]:
 if row[0] is not None:person=str(row[0]).strip()
 if row[1] is None:continue
 assert person and row[1] not in people.setdefault(person,{})
 people[person][row[1]]=(row[2],row[7]);sessions[str(row[1])]=sessions.get(str(row[1]),0)+1
valid=[];excluded=0
for p,v in sorted(people.items()):
 try:
  a,ar=v['W0'];b,br=v['POS']
  if not all(isinstance(x,(int,float)) and math.isfinite(x) and x>0 for x in (a,b,ar,br)):raise ValueError('invalid')
  valid.append(float(a))
 except (KeyError,ValueError):excluded+=1
x=np.array(valid);n=len(x);assert n==11
predictions={'archive100':np.full(n,old100),'corrected100':np.full(n,fixed100),'archive110':np.full(n,old110),'corrected110':np.full(n,fixed110),'loso_mean':(x.sum()-x)/(n-1)};errors={k:np.abs(v-x) for k,v in predictions.items()};idx=np.random.default_rng(20261120).integers(0,n,(10000,n));contrasts={}
for reference,test in [('archive100','corrected100'),('archive110','corrected110'),('loso_mean','corrected100'),('loso_mean','corrected110')]:
 d=errors[reference]-errors[test];contrasts[reference+'_minus_'+test]={'paired_mae_N':float(d.mean()),'ci95_N':np.quantile(d[idx].mean(axis=1),[.025,.975]).tolist()}
result={'experiment_id':'EXP-0091','classification':'EXPLORATORY_REUSED_COHORT_GRAVITY_REBUILD','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'GRAVITY_SANTOS_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'prior_hip_result_sha256_lf':text_sha256(prior_path),'gravity_audit_sha256_lf':text_sha256(audit_path),'gravity_rebuild_sha256_lf':text_sha256(rebuilt_path),'participants':n,'excluded_count':excluded,'session_counts':sessions,'cohort_mean_N':float(x.mean()),'fixed_model_forces_N':{'archive100':old100,'corrected100':fixed100,'archive110':old110,'corrected110':fixed110},'metrics':{k:{'mae_N':float(v.mean()),'rmse_N':float(np.sqrt(np.mean((predictions[k]-x)**2))),'bias_N':float(np.mean(predictions[k]-x))} for k,v in errors.items()},'paired_comparisons':contrasts,'whole_architecture':'NOT_ASSESSED','exact_geometry_validation':'DATA_BLOCKED'}
(H/'GRAVITY_SANTOS_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
