"""EXP-0105: external passive-control sprint prediction on a new dataset."""
import hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];p=Path(sys.argv[1]);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest=='f5d1033ac70b1692fb8294bfba3c000c33f4c4056f4da33e3265cffcfc8e175d'
w=load_workbook(p,read_only=True,data_only=True);s=w['Sprint power'];assert s.cell(6,4).value=='Mean';labels=[s.cell(6,col).value for col in range(5,17)];assert labels==[f'CON-{i}' for i in range(1,13)];assert [s.cell(r,4).value for r in range(7,12)]==[f'S{i}' for i in range(1,6)]
observed=[];excluded=0
for col in range(5,17):
 values=[s.cell(row,col).value for row in range(7,12)]
 if not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in values):excluded+=1;continue
 observed.append(values)
assert len(observed)>=8
rec=ROOT/'research/recovery_2026_11_04';sys.path.insert(0,str(rec));engine=rec/'engine.py';assert text_sha256(engine)=='1711bde73191d16544b585adc3f357a9022c58494bb708209aa61f305068688b';spec=importlib.util.spec_from_file_location('chang_engine',engine);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
z=np.array(observed,float);n=len(z);idx=np.random.default_rng(20261120).integers(0,n,(10000,n));out={};maxbalance=0.
for dt in (1.,.5,.25,.125,.0625,.03125):
 for rate in (.003,0.):
  raw=[];scaled=[];ledgerwork=[]
  for row in z:
   bouts,summary,_=mod.cycle(rest_s=60.,effort_s=10.,repetitions=5,dt=dt,mode='corrected',overrides={'demand_W':float(row[0]),'fatigue_rate_s_inv':rate});assert len(bouts)==5 and bouts[0]>0 and abs(summary['energy_residual_J'])<.01;maxbalance=max(maxbalance,abs(summary['energy_residual_J']));raw.append(float(bouts[4]));scaled.append(float(row[0]*bouts[4]/bouts[0]));ledgerwork.append(float(summary['external_J']))
  raw=np.array(raw);scaled=np.array(scaled);actual=z[:,4];base=z[:,0];baseerr=abs(base-actual);scalederr=abs(scaled-actual);delta=baseerr-scalederr;ci=np.quantile(delta[idx].mean(axis=1),[.025,.975]);out[f'dt{dt}_rate{rate}']={'n':n,'mae_raw_assuming_W':float(abs(raw-actual).mean()),'mae_scaled_assuming_W':float(scalederr.mean()),'mae_persistence_assuming_W':float(baseerr.mean()),'bias_raw_assuming_W':float((raw-actual).mean()),'bias_scaled_assuming_W':float((scaled-actual).mean()),'bias_persistence_assuming_W':float((base-actual).mean()),'relative_shape_mae_percentage_points':float((100*abs(scaled/ base-actual/base)).mean()),'persistence_minus_scaled_mae_assuming_W':float(delta.mean()),'paired_ci95_assuming_W':ci.tolist(),'mean_observed_five_sprint_work_assuming_J':float(np.mean(10*z.sum(axis=1))),'mean_original_ledger_work_J':float(np.mean(ledgerwork)),'negative_predictions':int((scaled<0).sum()),'decision':'scaled_D2_advantage' if ci[0]>0 else 'persistence_advantage' if ci[1]<0 else 'uncertain'}
result={'experiment_id':'EXP-0105','classification':'NEW_EXTERNAL_COHORT_PARTIAL_PREVIEW_CONDITION_ONLY','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'CHANG_SPRINT_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(engine),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'source_subjects':12,'admitted_subjects':n,'excluded_subjects':excluded,'max_energy_balance_abs_error_J':maxbalance,'scenarios':out,'posthoc_step_sensitivity':'dt=0.25, 0.125, 0.0625 and 0.03125 added after seeing nontrivial 1-to-0.5s change', 'limits':['first three control participant columns previewed before protocol','mean power units inferred as W, author confirmation needed','initial D2 stores full despite prior fatiguing work','prediction normalized to first sprint is empirical and not energy balanced','small selected men only, no CPE45 tissue temperature force or architecture outcome']}
(H/'CHANG_SPRINT_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
