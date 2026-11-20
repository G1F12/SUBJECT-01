"""EXP-0094: counterfactual fatigue-to-force sensitivity on the common D2 trace."""
import importlib.util,json,sys
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]; rec=ROOT/'research/recovery_2026_11_04';sys.path.insert(0,str(rec))
spec=importlib.util.spec_from_file_location('subject01_recovery_exp0094',rec/'engine.py'); engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
rebuild_path=H/'GRAVITY_REBUILD_RESULTS.json'; rebuild=json.loads(rebuild_path.read_text(encoding='utf-8'))['outputs']; cases=rebuild['tendon_cases']; rows=[]; traces=[]
for dt in (1.,.5):
 for rate in (0.,.001,.003):
  bouts,summary,trace=engine.cycle(rest_s=40,effort_s=60,repetitions=27,dt=dt,mode='corrected',overrides={'demand_W':360.,'fatigue_rate_s_inv':rate},trace=True)
  f=np.array([x['fatigue'] for x in trace]); assert len(f)==round(2700/dt) and abs(summary['time_s']-2700)<1e-6 and abs(summary['energy_residual_J'])<.01
  reference=next(r for r in rebuild['coupled_85'] if r['dt_s']==dt and r['assumed_fatigue_rate_s_inv']==rate)
  assert abs(reference['actual_work_J']-summary['external_J'])<1e-6 and abs(reference['max_fatigue']-float(f.max()))<1e-12
  traces.append({'dt_s':dt,'fatigue_rate_s_inv':rate,'required_work_J':583200.,'actual_work_J':summary['external_J'],'actual_heat_J':summary['heat_J'],'max_fatigue':float(f.max()),'final_fatigue':float(f[-1]),'energy_residual_J':summary['energy_residual_J']})
  for pose in ('flexed_100deg_int','extended_140deg_int'):
   def pick(variant):
    x=[r for r in cases if r['posture']==pose and r['scenario']==variant and r['csa_multiplier']==1.15 and r['uts_multiplier']==1.08 and r['rate_N_s']==20000];assert len(x)==1;return x[0]
   base=pick('baseline'); strat=pick('strategy_2_coordinated_chain'); B=base['plate_force_bilateral_N'];S=strat['plate_force_bilateral_N'];ratio=S/B
   positive=f[f>0];threshold=None
   if len(positive):
    threshold=float(np.min((1-1.2*(1-positive)/ratio)/positive)); test=ratio*(1-threshold*f)/(1-f);assert abs(float(test.min())-1.2)<1e-12
   for alpha in (.8,1.,1.02,1.05,1.1,1.2):
    factor=1-alpha*f
    if np.any(factor<=0):rows.append({'dt_s':dt,'fatigue_rate_s_inv':rate,'posture':pose,'alpha':alpha,'valid':False,'reason':'nonpositive strategy factor'});continue
    gains=100*(ratio*factor/(1-f)-1); i=int(np.argmin(gains));
    if alpha==1.: assert np.max(np.abs(gains-100*(ratio-1)))<1e-10
    force_gate=bool(gains[i]>=20);tissue_gate=bool(strat['local_sf']>=1.5);work_gate=bool(summary['external_J']>=.99*583200.)
    rows.append({'dt_s':dt,'fatigue_rate_s_inv':rate,'posture':pose,'alpha':alpha,'valid':True,'static_baseline_force_N':B,'static_strategy_force_N':S,'static_strategy_tendon_sf_proxy':strat['local_sf'],'minimum_gain_pct':float(gains[i]),'minimum_gain_time_s':trace[i]['time_s'],'gain_at_end_pct':float(gains[-1]),'strategy_force_at_end_N':float(S*factor[-1]),'alpha_boundary_for_20pct_all_steps':threshold,'force_gate_all_steps':force_gate,'conditional_static_tendon_gate':tissue_gate,'diagnostic_work_gate':work_gate,'joint_diagnostic_gate':force_gate and tissue_gate and work_gate})
result={'experiment_id':'EXP-0094','classification':'MODEL_ONLY_COUNTERFACTUAL_FORCE_INTERFACE','protocol_sha256_lf':text_sha256(H/'DIFFERENTIAL_FATIGUE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'gravity_rebuild_sha256_lf':text_sha256(rebuild_path),'recovery_engine_sha256_lf':text_sha256(rec/'engine.py'),'legacy_model_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'traces_summary':traces,'cases':rows,'limitations':['alpha is an unmeasured counterfactual mapping, not physiological fatigue','same energy trace irrespective of alpha, no force-to-power feedback','work gate is diagnostic and fails; not CPE45 criterion','static tendon proxy omits fatigue damage','time 2700 s follows final rest and is not measured post45','accuracy and recovery not assessed']}
(H/'DIFFERENTIAL_FATIGUE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
