"""EXP-0106: conditional D2 threshold versus cycling time to task failure."""
import hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];p=Path(sys.argv[1]);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest=='978540bca4ad10a8c4dcda2389a57d4c41b800df78338dcd73085299418b75cc'
w=load_workbook(p,read_only=True,data_only=True);sh=w["Participants' info"];assert sh.cell(4,10).value=='PPO'; info={}
for row in list(sh.values)[4:]:
 key=row[2]
 if key is None:continue
 assert key not in info;info[key]=row[9]
t=w['Time to exh'];assert t.cell(2,5).value=='Control' and t.cell(2,6).value=='Stroop';data=[];seen=set();excluded=0
for row in list(t.values)[2:]:
 key=row[3]
 if key is None:continue
 assert key not in seen;seen.add(key);values=(info.get(key),row[4],row[5])
 if not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in values):excluded+=1;continue
 data.append(values)
assert len(data)==18 and excluded==0
z=np.array(data,float);assert abs(z[:,1].mean()-999)<2 and abs(z[:,2].mean()-887)<2
rec=ROOT/'research/recovery_2026_11_04';sys.path.insert(0,str(rec));engine=rec/'engine.py';assert text_sha256(engine)=='1711bde73191d16544b585adc3f357a9022c58494bb708209aa61f305068688b';spec=importlib.util.spec_from_file_location('souron_d2',engine);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
idx=np.random.default_rng(20261120).integers(0,len(z),(10000,len(z)));observed=np.minimum(z[:,1:],2700.);delta=z[:,2]-z[:,1];loso=(observed[:,0].sum()-observed[:,0])/(len(z)-1);baseline_err=np.abs(loso[:,None]-observed).mean(axis=1);out={};maxbalance=0.
for dt in (1.,.5):
 for rate in (0.,.001,.003):
  predictions=[];censored=[]
  for ppo,_,_ in z:
   demand=.8*ppo;_,summary,trace=mod.cycle(rest_s=0.,effort_s=2700.,repetitions=1,dt=dt,mode='corrected',overrides={'demand_W':float(demand),'fatigue_rate_s_inv':rate},trace=True);assert len(trace)==round(2700/dt) and abs(summary['energy_residual_J'])<.01;maxbalance=max(maxbalance,abs(summary['energy_residual_J']))
   a=np.array([r['output_W'] for r in trace]);length=round(5/dt);start=round(60/dt);below=a<.95*demand;run=0;event=None
   for i in range(start,len(a)):
    run=run+1 if below[i] else 0
    if run>=length:event=(i-length+1)*dt;break
   predictions.append(2700. if event is None else event);censored.append(event is None)
  preds=np.array(predictions);err=np.abs(preds[:,None]-observed).mean(axis=1);adv=baseline_err-err;ci=np.quantile(adv[idx].mean(axis=1),[.025,.975]);out[f'dt{dt}_rate{rate}']={'diagnostic_failure_time_mean_s':float(preds.mean()),'diagnostic_failure_time_median_s':float(np.median(preds)),'right_censored_at_2700':int(sum(censored)),'model_mae_s':float(err.mean()),'loso_control_mean_mae_s':float(baseline_err.mean()),'paired_baseline_minus_model_mae_s':float(adv.mean()),'paired_bootstrap_95_s':ci.tolist(),'model_predicted_stroop_minus_control_s':0.0}
result={'experiment_id':'EXP-0106','classification':'PARTIALLY_PREVIEWED_EXTERNAL_COHORT_CONDITIONAL_THRESHOLD','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'SOURON_ENDURANCE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(engine),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'participants':len(z),'excluded':excluded,'observed_control_mean_s':float(z[:,1].mean()),'observed_stroop_mean_s':float(z[:,2].mean()),'observed_stroop_minus_control_mean_s':float(delta.mean()),'observed_paired_bootstrap_95_s':np.quantile(delta[idx].mean(axis=1),[.025,.975]).tolist(),'observed_2700_s_counts':{'control':int((z[:,1]>=2700).sum()),'stroop':int((z[:,2]>=2700).sum())},'model_max_energy_balance_abs_error_J':maxbalance,'scenarios':out,'limits':['article and seven participant rows previewed before protocol','model 95% power criterion differs from voluntary/cadence endpoint','warmup and cognitive history omitted from model state','no actual power time-series or measured individual capacity','no full CPE45 profile, tissue or whole architecture outcome']}
(H/'SOURON_ENDURANCE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
