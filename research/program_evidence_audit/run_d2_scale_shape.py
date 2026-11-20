"""EXP-0104: distinguish energy-ledger scale and empirical relative shape."""
import csv,hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];rec=ROOT/'research/recovery_2026_11_04';sys.path.insert(0,str(rec));engine=rec/'engine.py';assert text_sha256(engine)=='1711bde73191d16544b585adc3f357a9022c58494bb708209aa61f305068688b';spec=importlib.util.spec_from_file_location('d2_scale_shape',engine);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
from dataset import power_rows
power=ROOT/'tmp/recovery_raw/Power_rawdata.xlsx';assert hashlib.sha256(power.read_bytes()).hexdigest()=='b5cb03007190a63dae6a118a7a604cd906273f93febf42957a2e7799df16da20'
group=defaultdict(dict)
for r in power_rows(split='all',unlock=True):group[(r['participant'],r['rest_s'])][r['repetition']]=r['power_W']
j=[(str(person),float(rest),v[1],v[10]) for (person,rest),v in sorted(group.items()) if all(k in v and v[k]>0 for k in (1,10))]
ch=ROOT/'research/cpe45_2026_11_04/results/observations.csv';assert text_sha256(ch)=='542b2ff096f6e245ae185c9323a91259b9172f26d64d2c2b71354237d651e8eb';group=defaultdict(dict)
with ch.open(encoding='utf-8',newline='') as f:
 for r in csv.DictReader(f):
  if r['condition']=='Thermoneutral' and r['mean_power_W']:group[r['participant']][int(r['repetition'])]=float(r['mean_power_W'])
c=[(str(person),90.,v[1],v[10]) for person,v in sorted(group.items(),key=lambda x:int(x[0])) if all(k in v and v[k]>0 for k in (1,10))]
assert len(c)==21 and len(j)==63 and len({r[0] for r in j})==21
rng=np.random.default_rng(20261120);out={}; maxbalance=0.
for dt in (1.,.5):
 for rate in (0.,.003):
  for cohort,records in (('chmura',c),('jutlah',j)):
   people=defaultdict(list)
   for person,rest,first,last in records:
    bouts,s,_=mod.cycle(rest_s=rest,effort_s=6.,repetitions=10,dt=dt,mode='corrected',overrides={'demand_W':first,'fatigue_rate_s_inv':rate});maxbalance=max(maxbalance,abs(s['energy_residual_J']));assert abs(s['energy_residual_J'])<.01 and len(bouts)==10 and bouts[0]>0
    raw=float(bouts[-1]);scaled=float(first*bouts[-1]/bouts[0]);baseline=first;actual=last
    people[person].append([abs(raw-actual),abs(scaled-actual),abs(baseline-actual),raw-actual,scaled-actual,baseline-actual,abs(float(bouts[0])-first),abs(float(bouts[-1]/bouts[0]-actual/first))*100])
   a=np.array([np.mean(people[p],axis=0) for p in sorted(people)]);idx=np.random.default_rng(20261120).integers(0,len(a),(10000,len(a)))
   def delta(i,j):
    d=a[:,i]-a[:,j];return {'mean':float(d.mean()),'ci95':np.quantile(d[idx].mean(axis=1),[.025,.975]).tolist()}
   out[f'{cohort}_dt{dt}_rate{rate}']={'participants':len(a),'conditions':len(records),'mae_raw_W':float(a[:,0].mean()),'mae_scaled_W':float(a[:,1].mean()),'mae_persistence_W':float(a[:,2].mean()),'bias_raw_W':float(a[:,3].mean()),'bias_scaled_W':float(a[:,4].mean()),'bias_persistence_W':float(a[:,5].mean()),'first_bout_raw_mae_W':float(a[:,6].mean()),'relative_shape_mae_pp':float(a[:,7].mean()),'raw_minus_scaled':delta(0,1),'persistence_minus_scaled':delta(2,1)}
result={'experiment_id':'EXP-0104','classification':'RETROSPECTIVE_SCALE_SHAPE_DIAGNOSTIC','protocol_sha256_lf':text_sha256(H/'D2_SCALE_SHAPE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(engine),'dataset_loader_sha256_lf':text_sha256(rec/'dataset.py'),'power_xlsx_sha256_bytes':hashlib.sha256(power.read_bytes()).hexdigest(),'chmura_csv_sha256_lf':text_sha256(ch),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'max_balance_abs_error_J':maxbalance,'scenarios':out,'limitations':['both cohorts already viewed; no independent prospective validation','first observed sprint is input, not validated first-bout prediction','posthoc output scaling cannot preserve the D2 energy ledger','Jutlah active unloaded rest approximated as zero external power','no direct force tissue CPE45 or architecture outcome']}
(H/'D2_SCALE_SHAPE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
