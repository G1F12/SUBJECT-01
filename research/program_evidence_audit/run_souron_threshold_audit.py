"""EXP-0107: post-hoc decomposition of D2 threshold crossing."""
import hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]; p=Path(sys.argv[1])
source=hashlib.sha256(p.read_bytes()).hexdigest(); assert source=='978540bca4ad10a8c4dcda2389a57d4c41b800df78338dcd73085299418b75cc'
w=load_workbook(p,read_only=True,data_only=True); info={r[2]:r[9] for r in list(w["Participants' info"].values)[4:] if r[2] is not None}
rows=[r for r in list(w['Time to exh'].values)[2:] if r[3] is not None]; assert len(rows)==18 and len({r[3] for r in rows})==18
ppos=[float(info[r[3]]) for r in rows]; assert all(x>0 for x in ppos)
eng=ROOT/'research/recovery_2026_11_04/engine.py'; assert text_sha256(eng)=='1711bde73191d16544b585adc3f357a9022c58494bb708209aa61f305068688b'
spec=importlib.util.spec_from_file_location('audit_d2',eng); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
old=json.loads((H/'SOURON_ENDURANCE_RESULTS.json').read_text(encoding='utf-8')); output={}; eps=1e-6; max_balance=0.; max_excess=0.
for dt in (1.,.5):
 for rate in (0.,.001,.003):
  times=[]; reduced=limited=both=neither=0; excesses=[]
  for ppo in ppos:
   d0=.8*ppo; cfg=mod.defaults();cfg.update(demand_W=d0,fatigue_rate_s_inv=rate)
   _,summary,trace=mod.cycle(rest_s=0,effort_s=2700,repetitions=1,dt=dt,mode='corrected',overrides={'demand_W':d0,'fatigue_rate_s_inv':rate},trace=True)
   max_balance=max(max_balance,abs(summary['energy_residual_J'])); fatigue=np.array([0.]+[x['fatigue'] for x in trace[:-1]]); power=np.array([x['output_W'] for x in trace]);demand=d0*np.maximum(cfg['fatigue_floor'],1.-fatigue)
   max_excess=max(max_excess,float(np.max(power-demand))); assert np.all(power<=demand+eps)
   run=0; idx=None; length=round(5/dt)
   for i in range(round(60/dt),len(power)):
    run=run+1 if power[i]<.95*d0 else 0
    if run>=length:idx=i-length+1;break
   if idx is None:times.append(2700.);continue
   times.append(idx*dt);r=bool(demand[idx]<.95*d0);l=bool(power[idx]<demand[idx]-eps);reduced+=r;limited+=l;both+=r and l;neither+=not(r or l);excesses.append(float((demand[idx]-power[idx])/d0))
  prev=old['scenarios'][f'dt{dt}_rate{rate}']; assert abs(np.mean(times)-prev['diagnostic_failure_time_mean_s'])<1e-9
  censored=sum(t==2700 for t in times);assert censored==prev['right_censored_at_2700']
  output[f'dt{dt}_rate{rate}']={'events':18-censored,'censored':censored,'mean_event_or_censor_s':float(np.mean(times)),'internal_demand_below_threshold':reduced,'energy_limited_at_event':limited,'both_flags':both,'neither_flags':neither,'normalized_shortfall_range': [min(excesses),max(excesses)] if excesses else None}
assert max_balance<.01
res={'experiment_id':'EXP-0107','classification':'POST_HOC_MECHANISTIC_AUDIT','source_sha256_bytes':source,'prior_result_sha256_lf':text_sha256(H/'SOURON_ENDURANCE_RESULTS.json'),'protocol_sha256_lf':text_sha256(H/'SOURON_THRESHOLD_AUDIT_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(eng),'participants':18,'epsilon_W':eps,'max_power_minus_internal_demand_W':max_excess,'max_energy_balance_error_J':max_balance,'scenarios':output,'limits':['previously viewed cohort and results','first step of diagnostic window only; flags may coexist','not a physiological endpoint or an estimate of real capacity','no whole-architecture or CPE45 validation']}
(H/'SOURON_THRESHOLD_AUDIT_RESULTS.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8');print(json.dumps(res,indent=2))
