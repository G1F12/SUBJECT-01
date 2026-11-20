import json,math
import numpy as np
from pathlib import Path
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]
source=ROOT/'research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py'; src=source.read_text(encoding='utf-8')
assert text_sha256(source)=='f01ec4c94f013e738d284428100659e0fe68281283310d796a222b42c55d5bfe'
old='        tau_g[0] = -(dV_dphi1 + dV_dphi2)'; new='        tau_g[0] = -dV_dphi1'; assert src.count(old)==1
assert src.count('mu_friction = 0.80')==1
stress_path=H/'run_chain_tendon.py'; st={'__name__':'friction_tendon','__file__':str(stress_path)}; exec(compile(stress_path.read_text(encoding='utf-8').split('chain = json.loads')[0],str(stress_path),'exec'),st)
residuals=[]
reference=json.loads((H/'GRAVITY_AUDIT_RESULTS.json').read_text(encoding='utf-8'))['scenarios']; rows=[]; errors=[]
for mu in (0.,.1,.2,.4,.6,.8):
 for knee in (100,110,140):
  code=src.replace(old,new).replace('mu_friction = 0.80',f'mu_friction = {mu}')
  # Diagnostic-only guard: at mu=0 utilization is undefined; LP constraints remain unchanged.
  diagnostic='round(abs(F_t_opt) / (mu_friction * F_n_opt), 3)'
  assert code.count(diagnostic)==1
  code=code.replace(diagnostic, '(round(abs(F_t_opt) / (mu_friction * F_n_opt), 3) if mu_friction > 0 else None)')
  if knee==110:
   a='"theta_knee_flex_deg": 80.0, "theta_hip_flex_deg": 78.0'; b='"theta_knee_flex_deg": 70.0, "theta_hip_flex_deg": 78.0'; assert code.count(a)==1; code=code.replace(a,b)
  ctx={'__name__':'friction_chain','__file__':str(source)}; exec(compile(code,str(source),'exec'),ctx)
  original_linprog=ctx['linprog']
  def audited_linprog(c, **kw):
   result=original_linprog(c,**kw)
   if result.success:
    eq=float(np.max(np.abs(kw['A_eq']@result.x-kw['b_eq'])))
    ub=float(max(0.,np.max(kw['A_ub']@result.x-kw['b_ub'])))
    bound=max([max(0., (lo-x) if lo is not None else 0., (x-hi) if hi is not None else 0.) for x,(lo,hi) in zip(result.x,kw['bounds'])])
    assert max(eq,ub,bound)<1e-6
    residuals.append({'mu':mu,'knee_deg':knee,'max_equality_abs':eq,'max_inequality_violation':ub,'max_bound_violation':bound})
   return result
  ctx['linprog']=audited_linprog
  try: scenarios=ctx['solve_closed_chain_3dof_model']()['scenarios']
  except (RuntimeError,ZeroDivisionError) as exc: errors.append({'mu':mu,'knee_deg':knee,'error':str(exc)}); continue
  label='extended_140deg_int' if knee==140 else 'flexed_100deg_int'
  for variant in ('baseline','strategy_2_coordinated_chain'):
   p=scenarios[variant]['postures'][label]; sol=p['compatible_lp_solution']; force=sol['bilateral_footplate_force_N']; torque=sol['quadriceps_knee_torque_Nm']; tendon=torque/ctx['patellar_moment_arm_m'](p['theta_knee_flex_deg']); sf=95*1.08/st['local_stress'](tendon,104*1.15,20000,1.1204)
   n=sol['single_limb_normal_force_N']; t=sol['single_limb_shear_force_N']; r={'mu':mu,'internal_knee_deg':knee,'variant':variant,'force_N':force,'normal_N_rounded':n,'shear_N_rounded':t,'friction_utilization_rounded':sol['friction_utilization'],'quad_torque_Nm':torque,'tendon_sf_proxy':sf}
   if variant!='baseline': r.update({'gain_pct':p['comparison_to_baseline']['bilateral_footplate_force_gain_pct'],'model_joint_gate':p['comparison_to_baseline']['bilateral_footplate_force_gain_pct']>=20 and sf>=1.5})
   if mu==.8:
    ref=next(x for x in reference if x['pose_deg']==knee and x['gravity']=='corrected' and x['variant']==variant); assert abs(force-ref['force_N'])<1e-8 and abs(sf-ref['tendon_sf_proxy'])<1e-8
   rows.append(r)
result={'experiment_id':'EXP-0093','classification':'MODEL_ONLY_FRICTION_SENSITIVITY','protocol_sha256_lf':text_sha256(H/'FRICTION_SENSITIVITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'chain_source_sha256_lf':text_sha256(source),'tendon_source_sha256_lf':text_sha256(stress_path),'scenarios':rows,'lp_checks':residuals,'solver_or_implementation_errors':errors,'limitations':['coefficient grid diagnostic, not measured','rounded legacy output limits exact active-set inference','static proxy not actual tissue safety','hip/trunk geometry unresolved','no human functional effect or whole architecture assessment']}
(H/'FRICTION_SENSITIVITY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
