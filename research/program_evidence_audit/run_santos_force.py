"""EXP-0087: narrow cross-protocol force check and within-person trajectory."""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]; path=Path(sys.argv[1]); digest=hashlib.sha256(path.read_bytes()).hexdigest(); assert digest=='8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe'
b=load_workbook(path,read_only=True,data_only=True); sheet=b['Mechanical+EMG']; rows=list(sheet.values); assert rows[1][2]=="PF'" and rows[1][7]=="RFDmax'"
records={}; person=None; sessions={}
for row in rows[2:]:
 if row[0] is not None:person=str(row[0]).strip()
 session=row[1]
 if session is None:continue
 assert person and session not in records.setdefault(person,{}), 'missing subject or duplicate session'
 sessions[str(session)]=sessions.get(str(session),0)+1
 records[person][session]=(row[2],row[7])
valid=[]; missing=0
for person,row in sorted(records.items()):
 try:
  a,ar=row['W0']; b,br=row['POS']
  if not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in (a,b,ar,br)):raise ValueError('invalid')
  valid.append((a,b,ar,br))
 except (KeyError,ValueError):missing+=1
assert len(valid)>=5
z=np.array(valid); initial=z[:,0]; end=z[:,1]; n=len(z); nompath=ROOT/'research/exp0061_multijoint_legpress/RESULTS.json'; nom=json.loads(nompath.read_text(encoding='utf-8'))['part_c_closed_chain_3dof_model']['scenarios']['baseline']['postures']['flexed_100deg_int']['compatible_lp_solution']['bilateral_footplate_force_N']; assert abs(nom-2601.1)<.01
mean_without=(initial.sum()-initial)/(n-1); residual_model=nom-initial; residual_baseline=mean_without-initial; delta=np.abs(residual_baseline)-np.abs(residual_model); pct=100*(end/initial-1); force_delta=end-initial; rfd_delta=z[:,3]-z[:,2]
idx=np.random.default_rng(20261120).integers(0,n,(10000,n))
def interval(x):return np.quantile(x[idx].mean(axis=1),[.025,.975]).tolist()
result={'experiment_id':'EXP-0087','classification':'EXPLORATORY_CROSS_PROTOCOL_FORCE_CHECK','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'SANTOS_FORCE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'exp0061_result_sha256_lf':text_sha256(nompath),'participants':n,'excluded_count':missing,'session_counts':sessions,'nominal_model_force_N':nom,'cohort_initial_mean_N':float(initial.mean()),'cohort_initial_sd_N':float(initial.std(ddof=1)),'primary':{'model_mae_N':float(np.abs(residual_model).mean()),'loso_mean_mae_N':float(np.abs(residual_baseline).mean()),'model_rmse_N':float(np.sqrt(np.mean(residual_model**2))),'loso_mean_rmse_N':float(np.sqrt(np.mean(residual_baseline**2))),'model_bias_N':float(residual_model.mean()),'loso_mean_bias_N':float(residual_baseline.mean()),'paired_loso_minus_model_mae_N':float(delta.mean()),'paired_ci95_N':interval(delta)},'within_person_post_vs_baseline':{'mean_change_N':float(force_delta.mean()),'mean_change_N_ci95':interval(force_delta),'mean_relative_change_pct':float(pct.mean()),'mean_relative_change_ci95_pct':interval(pct),'median_relative_change_pct':float(np.median(pct)),'count_at_least_20pct':int(np.sum(pct>=20)),'peak_rfd_w0_mean_source_units':float(z[:,2].mean()),'peak_rfd_pos_mean_source_units':float(z[:,3].mean()),'mean_peak_rfd_change_source_units':float(rfd_delta.mean()),'rfd_units_status':'N/ms inferred from article table and matching session means, XLSX has no unit dictionary','control_group':'none_parallel'},'limits':['knee angle, instrument and unmeasured individual geometry differ from model','no parallel control','no individual body mass','no augmentation, tissue, CPE45 or whole-system outcome']}
(H/'SANTOS_FORCE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
