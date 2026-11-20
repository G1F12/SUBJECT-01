"""EXP-0085: one-way conditional recovery-to-thermal energy coupling."""
import importlib.util,json,sys
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]; rec=ROOT/'research/recovery_2026_11_04'; sys.path.insert(0,str(rec))
spec=importlib.util.spec_from_file_location('subject01_recovery_engine',rec/'engine.py'); engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
thermal_path=ROOT/'research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py'; src=thermal_path.read_text(encoding='utf-8')
needle='        if step % trace_stride == 0:'; assert src.count(needle)==1
src=src.replace(needle,'        p_now = float(power_schedule(t_now))\n'+needle)
needle='        "energy_balance_error_J": round(energy_closure_err_J, 6),'; assert src.count(needle)==1
src=src.replace(needle,'        "injected_heat_J": energy_in_heat_J,\n'+needle)
reference_context={'__name__':'coupled_reference','__file__':str(thermal_path)}; exec(compile(src,str(thermal_path),'exec'),reference_context)
needle='        q_gen = np.array([q_bmr_core_W, q_mus, 2.0, 4.0], dtype=float)'; assert src.count(needle)==1
src=src.replace(needle,'        q_in = float(heat_schedule(t_now))\n        q_core = min(q_bmr_core_W, q_in)\n        q_gen = np.array([q_core, q_in - q_core, 0.0, 0.0], dtype=float)')
needle='        m_total_W = q_bmr_core_W + p_now / delta_efficiency'; assert src.count(needle)==1
src=src.replace(needle,'        m_total_W = float(oxidative_schedule(t_now))')
linked_context={'__name__':'coupled_energy','__file__':str(thermal_path)}; exec(compile(src,str(thermal_path),'exec'),linked_context)
chain=json.loads((H/'CHAIN_TENDON_RESULTS.json').read_text(encoding='utf-8'))['cases']
selected=[]
for pose in ('flexed_100deg_int','extended_140deg_int'):
 for variant in ('baseline','strategy_2_coordinated_chain'):
  rows=[x for x in chain if x['posture']==pose and x['scenario']==variant and x['csa_multiplier']==1.15 and x['uts_multiplier']==1.08 and x['rate_N_s']==20000]
  assert len(rows)==1; selected.append(rows[0])
runs=[]
for dt in (1.,0.5):
 for rate in (0.,0.001,0.003):
  bouts,summary,trace=engine.cycle(rest_s=40,effort_s=60,repetitions=27,dt=dt,mode='corrected',overrides={'demand_W':360.,'fatigue_rate_s_inv':rate},trace=True)
  assert abs(summary['time_s']-2700)<1e-6 and abs(summary['energy_residual_J'])<.01 and len(trace)==round(2700/dt)
  p=np.array([r['output_W'] for r in trace]); f=np.array([r['fatigue'] for r in trace]); q=np.diff(np.r_[0.,[r['heat_J'] for r in trace]])/dt; ox=np.diff(np.r_[0.,[r['oxidative_J'] for r in trace]])/dt
  assert np.min(q)>=0 and np.all((f>=0)&(f<1))
  assert abs(p.sum()*dt-summary['external_J'])<.01 and abs(q.sum()*dt-summary['heat_J'])<.01
  def schedule(array):return lambda t:float(array[min(len(array)-1,int(round(t/dt)))])
  reference_context['power_schedule']=schedule(p); linked_context['power_schedule']=schedule(p); linked_context['heat_schedule']=schedule(q); linked_context['oxidative_schedule']=schedule(ox)
  calc_args=(360.,.6,20.,.5); kw={'body_mass_kg':75.,'dt_s':dt}
  reference=reference_context['simulate_4layer_pennes_2700s'](*calc_args,**kw); linked=linked_context['simulate_4layer_pennes_2700s'](*calc_args,**kw)
  assert reference['energy_balance_error_J']<.01 and linked['energy_balance_error_J']<.01 and abs(linked['injected_heat_J']-summary['heat_J'])<.01
  assumptions=[]
  for r in selected:
   cap=r['plate_force_bilateral_N']*(1-f); vel=np.divide(p,cap,out=np.zeros_like(p),where=cap>0); sf=r['local_sf']/(1-f)
   assumptions.append({'posture':r['posture'],'variant':r['scenario'],'static_force_N':r['plate_force_bilateral_N'],'minimum_assumed_force_N':float(np.min(cap)),'first_assumed_force_N':r['plate_force_bilateral_N'],'last_assumed_force_N':float(cap[-1]),'max_nominal_speed_m_s':float(vel.max()),'minimum_static_tendon_sf_proxy':float(min(r['local_sf'],sf.min())),'force_gain_static_pct':r['plate_gain_pct']})
  runs.append({'dt_s':dt,'assumed_fatigue_rate_s_inv':rate,'required_work_J':583200.,'actual_work_J':summary['external_J'],'work_fraction':summary['external_J']/583200.,'diagnostic_work_gate':summary['external_J']>=.99*583200.,'heat_J':summary['heat_J'],'oxidative_J':summary['oxidative_J'],'energy_residual_J':summary['energy_residual_J'],'first_bout_mean_W':float(bouts[0]),'last_bout_mean_W':float(bouts[-1]),'last_fatigue':float(f[-1]),'max_fatigue':float(f.max()),'conditional_thermal_peak_C':linked['peak_T_core_C'],'conditional_thermal_final_C':linked['final_T_core_C'],'reference_thermal_peak_C':reference['peak_T_core_C'],'reference_heat_J':reference['injected_heat_J'],'coupled_thermal_residual_J':linked['energy_balance_error_J'],'source_heat_integral_delta_J':linked['injected_heat_J']-summary['heat_J'],'mechanical_interfaces':assumptions})
result={'experiment_id':'EXP-0085','classification':'MODEL_ONLY_UNVALIDATED_ONE_WAY_INTERFACE','protocol_sha256_lf':text_sha256(H/'COUPLED_ENERGY_THERMAL_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'engine_sha256_lf':text_sha256(rec/'engine.py'),'legacy_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/model.py'),'legacy_config_sha256_lf':text_sha256(ROOT/'research/cpe45_2026_11_04/config.json'),'integrated_model_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/model.py'),'integrated_parameters_sha256_lf':text_sha256(ROOT/'research/integrated_2026_11_01/parameters.json'),'thermal_sha256_lf':text_sha256(thermal_path),'chain_sha256_lf':text_sha256(H/'CHAIN_TENDON_RESULTS.json'),'unassessed':['real_force_trajectory','tendon_fatigue','thermal_to_power_feedback','accuracy','reaction','post45','recovery','architecture_A_outcome'],'runs':runs}
(H/'COUPLED_ENERGY_THERMAL_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
