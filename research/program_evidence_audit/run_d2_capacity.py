"""EXP-0103: retrospective D2 demand/capacity model sensitivity."""
import hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];path=Path(sys.argv[1]);source_data_sha=hashlib.sha256(path.read_bytes()).hexdigest();assert source_data_sha=='499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531'
loader=H/'run_d2_mclaughlin.py';pre=loader.read_text(encoding='utf-8').split("rec=ROOT/'research/recovery_2026_11_04'")[0];assert 'assert len(eligible)==23' in pre
args=sys.argv;sys.argv=[str(loader),str(path)]; ctx={'__name__':'capacity_input','__file__':str(loader)};exec(compile(pre,str(loader),'exec'),ctx);sys.argv=args;eligible=ctx['eligible']
rec=ROOT/'research/recovery_2026_11_04';sys.path.insert(0,str(rec));engine_path=rec/'engine.py';source=engine_path.read_text(encoding='utf-8');assert text_sha256(engine_path)=='1711bde73191d16544b585adc3f357a9022c58494bb708209aa61f305068688b'
spec=importlib.util.spec_from_file_location('d2_base_exp0103',engine_path);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
a="                demand=q['demand_W']*max(q['fatigue_floor'],1-fatigue) if effort else 0."; b="                demand=q['demand_W'] if effort else 0.";c="                external=min(demand*h,(aerobic+fb+sb)*q['eta'])";d="                external=min(demand*h,(aerobic+fb+sb)*q['eta'], q['capacity_W']*max(q['fatigue_floor'],1-fatigue)*h if effort else 0.)";assert source.count(a)==source.count(c)==1;patched=source.replace(a,b).replace(c,d);capctx={'__name__':'d2_capacity_exp0103','__file__':str(engine_path)};exec(compile(patched,str(engine_path),'exec'),capctx);candidate=capctx['cycle']
from dataset import power_rows
power_path=ROOT/'tmp/recovery_raw/Power_rawdata.xlsx';assert hashlib.sha256(power_path.read_bytes()).hexdigest()=='b5cb03007190a63dae6a118a7a604cd906273f93febf42957a2e7799df16da20'
groups=defaultdict(dict)
for row in power_rows(split='all',unlock=True):groups[(row['participant'],row['rest_s'])][row['repetition']]=row['power_W']
jutlah=[(person,rest,v[1],v[10]) for (person,rest),v in sorted(groups.items()) if all(x in v and v[x]>0 for x in (1,10))];assert len({r[0] for r in jutlah})==21 and len(jutlah)==63

def run(fn,dt,rate,demand,capacity,effort,rest,repetitions,trace=False):
 params={'demand_W':float(demand),'fatigue_rate_s_inv':rate}
 if fn is candidate:params['capacity_W']=float(capacity)
 bouts,summary,series=fn(rest_s=rest,effort_s=effort,repetitions=repetitions,dt=dt,mode='corrected',overrides=params,trace=trace);assert abs(summary['energy_residual_J'])<.01
 return bouts,summary,series

def summarize(pairs,seed=20261120):
 a=np.array(pairs,float);diff=a[:,0]-a[:,1];idx=np.random.default_rng(seed).integers(0,len(a),(10000,len(a)));return {'participants':len(a),'old_mae':float(a[:,0].mean()),'candidate_mae':float(a[:,1].mean()),'persistence_mae':float(a[:,2].mean()),'old_minus_candidate_mae':float(diff.mean()),'paired_bootstrap_95':np.quantile(diff[idx].mean(axis=1),[.025,.975]).tolist(),'persistence_minus_candidate_mae':float((a[:,2]-a[:,1]).mean()),'persistence_minus_candidate_bootstrap_95':np.quantile((a[:,2]-a[:,1])[idx].mean(axis=1),[.025,.975]).tolist()}
results={};balmax=0.
for dt in (1.,.5):
 for rate in (0.,.003):
  pairs=[];workpairs=[]
  for initial,sequence in eligible:
   output=[]
   for fn in (base.cycle,candidate):
    _,summary,tr=run(fn,dt,rate,initial,initial/.6,2700.,0.,1,True);balmax=max(balmax,abs(summary['energy_residual_J']));x=np.array([x['output_W'] for x in tr]).reshape(45,round(60/dt)).mean(axis=1)[1:];output.append(x)
   obs=np.array(sequence,float);persist=np.full(44,initial)
   pairs.append([float(abs(x-obs).mean()) for x in (*output,persist)]);workpairs.append([float(abs((x-obs).sum()*60)) for x in (*output,persist)])
   if rate==0:assert np.max(abs(output[0]-output[1]))<1e-10
  results[f'mclaughlin_dt{dt}_rate{rate}']={'power_W':summarize(pairs),'work_J':summarize(workpairs)}
 for rate in (.003,):
  grouped=defaultdict(list);bias=defaultdict(list)
  for person,rest,first,last in jutlah:
   preds=[]
   for fn in (base.cycle,candidate):
    bouts,summary,_=run(fn,dt,rate,first,first,6.,float(rest),10);balmax=max(balmax,abs(summary['energy_residual_J']));assert len(bouts)==10;preds.append(float(bouts[-1]))
   vals=[*preds,first];grouped[person].append([abs(x-last) for x in vals]);bias[person].append([x-last for x in vals])
  pairs=[np.mean(grouped[p],axis=0) for p in sorted(grouped)]; biases=np.array([np.mean(bias[p],axis=0) for p in sorted(bias)]).mean(axis=0)
  results[f'jutlah_dt{dt}_rate{rate}']={'power10_W':summarize(pairs),'bias_old_candidate_persistence_W':biases.tolist(),'conditions':len(jutlah)}
result={'experiment_id':'EXP-0103','classification':'RETROSPECTIVE_CANDIDATE_NOT_VALIDATED','protocol_sha256_lf':text_sha256(H/'D2_CAPACITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'d2_engine_sha256_lf':text_sha256(engine_path),'d2_candidate_text_sha256_lf':hashlib.sha256(patched.replace('\r\n','\n').encode('utf-8')).hexdigest(),'mclaughlin_loader_sha256_lf':text_sha256(loader),'mclaughlin_source_sha256_bytes':source_data_sha,'jutlah_source_sha256_bytes':hashlib.sha256(power_path.read_bytes()).hexdigest(),'dataset_loader_sha256_lf':text_sha256(rec/'dataset.py'),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'max_energy_balance_abs_error_J':balmax,'scenarios':results,'limits':['both cohorts previously viewed; no independent validation','McLaughlin first minute proxies demand and first-minute/0.6 is only hypothetical capacity','Jutlah active unloaded recovery approximated by zero external power','aerobic maximum is not measured maximal instantaneous capability','thermal feedback force tissue post45 and CPE45 remain unassessed']}
(H/'D2_CAPACITY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
