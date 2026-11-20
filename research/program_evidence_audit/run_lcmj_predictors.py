"""EXP-0115: source gate and exploratory leave-one-person-out predictions."""
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);b=p.read_bytes();sha=hashlib.sha256(b).hexdigest();md5=hashlib.md5(b).hexdigest();assert sha=='e09cd2da52060ad0caf72a8aaf58f03afc415ef6b13696192058bfd34187f184' and md5=='2c10a95978c5be4acbe20a95d0b036dd'
rows=list(csv.DictReader(b.decode('utf-8-sig').splitlines()));assert len(rows)==10 and len({r['Participant'] for r in rows})==10
def col(name):
 z=np.array([float(r[name]) for r in rows]);assert np.isfinite(z).all() and (z>0).all();return z
mass=col('Body Mass (kg) ');squat=col('Half Squat Predicted 1RM (kg) ');strength=col('Relative Half Squat Predicted 1RM (kg/kg)');sprint=col('RSA % Decrement');y=col('LCMJ20 (%)');assert np.max(np.abs(strength-squat/mass))<.02
corr_strength=float(np.corrcoef(strength,y)[0,1]);corr_sprint=float(np.corrcoef(sprint,y)[0,1]);assert abs(corr_strength+.728)<.02 and abs(corr_sprint-.736)<.02 and abs(y.mean()-26.81)<.15 and abs(y.std(ddof=1)-3.8)<.15
base=np.zeros(10);models={'relative_strength':np.zeros(10),'repeat_sprint_decrement':np.zeros(10)}
for i in range(10):
 mask=np.arange(10)!=i;base[i]=np.mean(y[mask])
 for key,x in [('relative_strength',strength),('repeat_sprint_decrement',sprint)]:
  A=np.column_stack([np.ones(9),x[mask]]);coeff=np.linalg.lstsq(A,y[mask],rcond=None)[0];models[key][i]=coeff[0]+coeff[1]*x[i]
idx=np.random.default_rng(20261120).integers(0,10,(10000,10));baseerr=np.abs(base-y);out={}
for key,pred in models.items():
 err=np.abs(pred-y);adv=baseerr-err;out[key]={'loocv_mae_pp':float(err.mean()),'loocv_bias_pp':float((pred-y).mean()),'mean_base_minus_model_mae_pp':float(adv.mean()),'paired_bootstrap_95_pp':np.quantile(adv[idx].mean(axis=1),[.025,.975]).tolist()}
r={'experiment_id':'EXP-0115','classification':'PARTIALLY_PREVIEWED_POST_SELECTION_LOPO','source_sha256_bytes':sha,'source_md5_bytes':md5,'protocol_sha256_lf':text_sha256(H/'LCMJ_PREDICTORS_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'n':10,'source_gate':{'relative_strength_corr':corr_strength,'repeat_sprint_corr':corr_sprint,'lc_mean_percent':float(y.mean()),'lc_sd_percent':float(y.std(ddof=1)),'maximum_relative_strength_rounding_difference':float(np.max(np.abs(strength-squat/mass)))},'baseline_loocv_mae_pp':float(baseerr.mean()),'models':out,'limits':['paper outcome associations and feature selection viewed before protocol','n=10 overlapping LOPO training folds; bootstrap treats predictions as fixed','power decrement is derived and filter provenance differs across related work','squat strength sets jumping load so association is not causal','overlap with SRC-0108 unknown; no CPE45 or whole-profile inference']};(H/'LCMJ_PREDICTORS_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
