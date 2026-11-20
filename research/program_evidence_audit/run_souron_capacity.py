"""EXP-0108: retrospective D2-cap threshold sensitivity, no model promotion."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];p=Path(sys.argv[1]);source_sha=hashlib.sha256(p.read_bytes()).hexdigest();assert source_sha=='978540bca4ad10a8c4dcda2389a57d4c41b800df78338dcd73085299418b75cc'
w=load_workbook(p,read_only=True,data_only=True);info={r[2]:r[9] for r in list(w["Participants' info"].values)[4:] if r[2] is not None};rows=[r for r in list(w['Time to exh'].values)[2:] if r[3] is not None];assert len(rows)==18 and len({r[3] for r in rows})==18
z=np.array([[info[r[3]],r[4],r[5]] for r in rows],float);assert np.isfinite(z).all() and (z>0).all();obs=np.minimum(z[:,1:],2700);baseline=(obs[:,0].sum()-obs[:,0])/17;baseline_mae=float(np.abs(baseline[:,None]-obs).mean())
eng=ROOT/'research/recovery_2026_11_04/engine.py'; assert text_sha256(eng)=='1711bde73191d16544b585adc3f357a9022c58494bb708209aa61f305068688b';source=eng.read_text(encoding='utf-8')
a="                demand=q['demand_W']*max(q['fatigue_floor'],1-fatigue) if effort else 0.";b="                demand=q['demand_W'] if effort else 0.";c="                external=min(demand*h,(aerobic+fb+sb)*q['eta'])";d="                external=min(demand*h,(aerobic+fb+sb)*q['eta'], q['capacity_W']*max(q['fatigue_floor'],1-fatigue)*h if effort else 0.)";assert source.count(a)==source.count(c)==1;patched=source.replace(a,b).replace(c,d);patched_sha=hashlib.sha256(patched.replace('\r\n','\n').encode()).hexdigest();prior=json.loads((H/'D2_CAPACITY_RESULTS.json').read_text(encoding='utf-8'));assert patched_sha==prior['d2_candidate_text_sha256_lf']
sys.path.insert(0,str(eng.parent));ctx={'__name__':'souron_d2cap','__file__':str(eng)};exec(compile(patched,str(eng),'exec'),ctx);cycle=ctx['cycle'];defaults=ctx['defaults'];result={};maxbalance=0.
for dt in (1.,.5):
 for rate in (0.,.001,.003):
  for factor in (1.,1.5,2.):
   times=[];works=[];cap_active=other=0
   for ppo,_,_ in z:
    demand=.8*ppo;cap=factor*ppo;_,summary,trace=cycle(rest_s=0,effort_s=2700,repetitions=1,dt=dt,mode='corrected',overrides={'demand_W':float(demand),'capacity_W':float(cap),'fatigue_rate_s_inv':rate},trace=True);maxbalance=max(maxbalance,abs(summary['energy_residual_J']));works.append(summary['external_J']);power=np.array([r['output_W'] for r in trace]);fatigue=np.array([0.]+[r['fatigue'] for r in trace[:-1]]);capacity=cap*np.maximum(defaults()['fatigue_floor'],1-fatigue);assert np.all(power<=capacity+1e-6) and np.all(power<=demand+1e-6)
    n=round(5/dt);run=0;event=None
    for i in range(round(60/dt),len(power)):
     run=run+1 if power[i]<.95*demand else 0
     if run>=n:event=i-n+1;break
    if event is None:times.append(2700.);continue
    times.append(event*dt);cap_active+=bool(abs(power[event]-capacity[event])<=1e-6);other+=bool(power[event]<capacity[event]-1e-6)
   assert cap_active+other==sum(t<2700 for t in times);pred=np.array(times);result[f'dt{dt}_rate{rate}_cap{factor}']={'events':sum(t<2700 for t in times),'censored':sum(t==2700 for t in times),'mean_event_or_censor_s':float(pred.mean()),'mean_work_J':float(np.mean(works)),'truncated_model_mae_s':float(np.abs(pred[:,None]-obs).mean()),'control_lopo_mae_s':baseline_mae,'cap_binding_at_event':cap_active,'strictly_below_cap_at_event':other}
assert maxbalance<.01
r={'experiment_id':'EXP-0108','classification':'POST_HOC_SENSITIVITY_NOT_VALIDATION','source_sha256_bytes':source_sha,'protocol_sha256_lf':text_sha256(H/'SOURON_CAPACITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(eng),'candidate_text_sha256_lf':patched_sha,'previous_candidate_result_sha256_lf':text_sha256(H/'D2_CAPACITY_RESULTS.json'),'prior_cohort_result_sha256_lf':text_sha256(H/'SOURON_ENDURANCE_RESULTS.json'),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'participants':18,'max_energy_balance_abs_error_J':maxbalance,'scenarios':result,'limits':['previously viewed source and outcomes','capacity scenarios are not measured capability or validated range','model threshold differs from voluntary/cadence endpoint','censoring and unmodelled warmup/cognitive conditions','no CPE45 or whole-architecture inference']};(H/'SOURON_CAPACITY_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
