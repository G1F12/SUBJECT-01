"""EXP-0102: fixed-demand D2 scenario on previously viewed submaximal cycling."""
import hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];path=Path(sys.argv[1]);digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest=='499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531'
book=load_workbook(path,read_only=True,data_only=True);temp=list(book['Core Temp'].values);work=list(book['Exercise Data'].values);env=list(book['Environmental Conditions'].values);demo=list(book['Demographics'].values)
def cols(row,start,end):
 pairs=[(v,i) for i,v in enumerate(row[start:end],start) if isinstance(v,int)];assert len(pairs)==len(dict(pairs));return dict(pairs)
tc=cols(temp[1],2,27);pc=cols(work[1],77,101);ac=cols(env[1],2,27);rc=cols(env[1],27,51);mass={r[0]:r[4] for r in demo[1:] if isinstance(r[0],int)};temperatures={r[1]:r for r in temp[2:] if isinstance(r[1],int)};powers={}
for r in work[2:]:
 label=r[1];label=f'{label-1}-{label}' if isinstance(label,int) else label
 if isinstance(label,str) and '-' in label:assert label not in powers;powers[label]=r
climates={r[1]:r for r in env[2:] if isinstance(r[1],str)};eligible=[];excluded=0
for ident in sorted(set(tc)|set(pc)|set(ac)|set(rc)):
 try:
  weight=mass[ident];t1,t45,t60=(temperatures[t][tc[ident]] for t in (1,45,60));air=climates['5-6'][ac[ident]];rh=climates['5-6'][rc[ident]];initial=powers['0-1'][pc[ident]];series=[powers[f'{m}-{m+1}'][pc[ident]] for m in range(1,60)];vals=[weight,t1,t45,t60,air,rh,initial,*series]
  if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in vals):raise ValueError('missing')
  if not (30<=weight<=200 and all(34<=v<=43 for v in (t1,t45,t60)) and 0<=air<=50 and 0<=rh<=100 and all(0<v<600 for v in [initial,*series])):raise ValueError('range')
  eligible.append((initial,series[:44]))
 except (KeyError,IndexError,ValueError):excluded+=1
assert len(eligible)==23
rec=ROOT/'research/recovery_2026_11_04';sys.path.insert(0,str(rec));spec=importlib.util.spec_from_file_location('subject01_d2_external',rec/'engine.py');engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
rng=np.random.default_rng(20261120);idx=rng.integers(0,len(eligible),(10000,len(eligible)));results=[]
for rate in (0.,.001,.003):
 errors=[];baselines=[];bias=[];work_errors=[];base_work_errors=[];d2_work=[];observed_work=[];balances=[]
 for initial,seq in eligible:
  _,summary,trace=engine.cycle(rest_s=0.,effort_s=2700.,repetitions=1,dt=1.,mode='corrected',overrides={'demand_W':float(initial),'fatigue_rate_s_inv':rate},trace=True);assert len(trace)==2700 and abs(summary['energy_residual_J'])<.01
  predicted=np.array([q['output_W'] for q in trace]).reshape(45,60).mean(axis=1)[1:];actual=np.array(seq,float);assert len(predicted)==len(actual)==44
  residual=predicted-actual;constant=initial-actual;errors.append(float(abs(residual).mean()));baselines.append(float(abs(constant).mean()));bias.append(float(residual.mean()));work_errors.append(float(abs(residual.sum()*60)));base_work_errors.append(float(abs(constant.sum()*60)));d2_work.append(float(predicted.sum()*60));observed_work.append(float(actual.sum()*60));balances.append(abs(summary['energy_residual_J']))
 errors=np.array(errors);baselines=np.array(baselines);delta=baselines-errors;ci=np.quantile(delta[idx].mean(axis=1),[.025,.975]);results.append({'fatigue_rate_s_inv':rate,'d2_power_mae_W':float(errors.mean()),'persistence_power_mae_W':float(baselines.mean()),'d2_power_bias_W':float(np.mean(bias)),'paired_advantage_W':float(delta.mean()),'paired_bootstrap_95_W':ci.tolist(),'d2_work_mae_J':float(np.mean(work_errors)),'persistence_work_mae_J':float(np.mean(base_work_errors)),'mean_d2_work_J':float(np.mean(d2_work)),'mean_recorded_work_J':float(np.mean(observed_work)),'max_energy_balance_abs_error_J':max(balances),'decision':'D2_advantage' if ci[0]>0 else 'persistence_advantage' if ci[1]<0 else 'uncertain'})
result={'experiment_id':'EXP-0102','classification':'EXPLORATORY_REUSED_COHORT_SUBMAXIMAL_DEMAND_PROXY','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'D2_MCLAUGHLIN_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(rec/'engine.py'),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'participants':len(eligible),'excluded_count':excluded,'intervals_compared':44,'time_label_assumption':'numeric labels treated as interval ends','scenarios':results,'limits':['previously viewed cohort','first-minute recorded power used as proxy for unobserved exact prescribed demand','submaximal constant-load task; D2 estimates conditional capacity','no thermal feedback or individualized aerobic parameters','not CPE45 or physiological validation of whole architecture']}
(H/'D2_MCLAUGHLIN_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
