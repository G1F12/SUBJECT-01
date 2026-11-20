"""EXP-0098: leave-one-participant-out recovery moment prediction."""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest=='a976a4a2797fce55fdaa1600ef7137d2e31867d7279c86d5baf8b4343ae9588b'
w=load_workbook(p,read_only=True,data_only=True);sheet=w['Feuil1'];rows=list(sheet.values);assert rows[0][1]=='MVC (Nm)' and list(rows[1][:5])==['Participant','Pre','Post','Post-5','Post-10']
values=[];seen=set();excluded=[]
for row in rows[2:]:
 ident=row[0]
 if ident is None:continue
 assert ident not in seen;seen.add(ident)
 vals=row[1:5]
 if not isinstance(ident,int) or not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in vals):excluded.append({'reason':'invalid_id_or_moment'});continue
 values.append(vals)
assert len(values)>=8
z=np.array(values,dtype=float);x=z[:,2]/z[:,0];y=z[:,3]/z[:,0]; n=len(z);prediction=np.empty(n)
for i in range(n):
 mask=np.arange(n)!=i;assert np.ptp(x[mask])>0;X=np.column_stack((np.ones(n-1),x[mask]));coef=np.linalg.lstsq(X,y[mask],rcond=None)[0];prediction[i]=z[i,0]*(coef[0]+coef[1]*x[i])
actual=z[:,3];baseline=z[:,2];model_error=abs(prediction-actual);base_error=abs(baseline-actual);delta=base_error-model_error
idx=np.random.default_rng(20261120).integers(0,n,(10000,n));ci=np.quantile(delta[idx].mean(axis=1),[.025,.975]);ratio=z[:,1:]/z[:,[0]]
result={'experiment_id':'EXP-0098','classification':'EXPLORATORY_WITHIN_COHORT_LOSO','source_sha256_bytes':digest,'source_git_commit':'16aec21efc7643c4b6b5619c5f4bb5dda6e6d6fb','protocol_sha256_lf':text_sha256(H/'PLANTAR_RECOVERY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'n':n,'excluded':excluded,'moment_ratio_means':dict(zip(['post','post_5','post_10'],map(float,ratio.mean(axis=0)))),'moment_ratio_ranges':{k:[float(ratio[:,j].min()),float(ratio[:,j].max())] for j,k in enumerate(['post','post_5','post_10'])},'linear_model_mae_Nm':float(model_error.mean()),'persistence_mae_Nm':float(base_error.mean()),'linear_model_mean_absolute_error_relative_to_pre_pct':float(100*np.mean(model_error/z[:,0])),'persistence_mean_absolute_error_relative_to_pre_pct':float(100*np.mean(base_error/z[:,0])),'linear_bias_Nm':float((prediction-actual).mean()),'persistence_bias_Nm':float((baseline-actual).mean()),'paired_mae_advantage_Nm':float(delta.mean()),'paired_bootstrap_95_Nm':ci.tolist(),'negative_prediction_count':int(np.sum(prediction<0)),'decision':'linear_superior' if ci[0]>0 else 'persistence_superior' if ci[1]<0 else 'uncertain','limitations':['published cohort; first rows and article viewed before protocol','LOSO training sets overlap; bootstrap holds fitted predictions fixed','selected 12 men and local isometric plantar flexion','stimulation and vibration preceding each MVC; no unstimulated control','no actual external mechanical work or equivalent task exposure, tissue or CPE45']}
(H/'PLANTAR_RECOVERY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
