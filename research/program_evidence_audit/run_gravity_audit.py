"""EXP-0089: independently differentiate chain potential and rerun LP."""
import json,math
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]; source_path=ROOT/'research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py'; src=source_path.read_text(encoding='utf-8');old='        tau_g[0] = -(dV_dphi1 + dV_dphi2)';new='        tau_g[0] = -dV_dphi1';assert src.count(old)==1
stress_path=H/'run_chain_tendon.py';stress_code=stress_path.read_text(encoding='utf-8').split('chain = json.loads')[0];st={'__name__':'gravity_tendon','__file__':str(stress_path)};exec(compile(stress_code,str(stress_path),'exec'),st);local_stress=st['local_stress']
def evaluate(code):
 ctx={'__name__':'gravity_chain','__file__':str(source_path)};exec(compile(code,str(source_path),'exec'),ctx);return ctx,ctx['solve_closed_chain_3dof_model']()['scenarios']
def theta110(code):
 a='"theta_knee_flex_deg": 80.0, "theta_hip_flex_deg": 78.0';b='"theta_knee_flex_deg": 70.0, "theta_hip_flex_deg": 78.0';assert code.count(a)==1;return code.replace(a,b)
checks=[];mass=75.;L1=.245*1.78;L2=.246*1.78;mt=.1*mass;ms=.0465*mass;mf=.0145*mass;g=9.81
for knee in (80.,70.,40.):
 k=math.radians(knee);d=math.sqrt(L1**2+L2**2+2*L1*L2*math.cos(k)); beta=math.acos(np.clip((L1**2+d**2-L2**2)/(2*L1*d),-1,1));p1=math.radians(4)+beta;p2=p1-k
 def V(a,b):return g*(mt*.433*L1*math.sin(a)+ms*(L1*math.sin(a)+.433*L2*math.sin(b))+mf*(L1*math.sin(a)+L2*math.sin(b)))
 A=g*(mt*.433*L1*math.cos(p1)+ms*(L1*math.cos(p1)+.433*L2*math.cos(p2))+mf*(L1*math.cos(p1)+L2*math.cos(p2)));B=g*(ms*.433*L2*math.cos(p2)+mf*L2*math.cos(p2))
 for h in (1e-3,1e-5,1e-6):
  hip=(V(p1-h,p2-h)-V(p1+h,p2+h))/(2*h); knee_fd=(V(p1,p2+h)-V(p1,p2-h))/(2*h)
  checks.append({'internal_knee_deg':180-knee,'step_rad':h,'hip_finite_difference_Nm':hip,'hip_original_Nm':-(A+B),'hip_corrected_Nm':-A,'knee_finite_difference_Nm':knee_fd,'knee_original_Nm':B})
  if h==1e-5:assert abs(hip+A)<1e-6 and abs(hip+A+B)>1e-3 and abs(knee_fd-B)<1e-6
runs={}
for label,code in [('original',src),('corrected',src.replace(old,new)),('original110',theta110(src)),('corrected110',theta110(src.replace(old,new)))]:runs[label]=evaluate(code)
rows=[]
for pose,label in [('100','flexed_100deg_int'),('140','extended_140deg_int'),('110','flexed_100deg_int')]:
 for model in ('original','corrected'):
  key=model+'110' if pose=='110' else model; ctx,sc=runs[key]
  for variant in ('baseline','strategy_2_coordinated_chain'):
   p=sc[variant]['postures'][label]; sol=p['compatible_lp_solution']; arm=ctx['patellar_moment_arm_m'](p['theta_knee_flex_deg']); tendon=sol['quadriceps_knee_torque_Nm']/arm; sf=95*1.08/local_stress(tendon,104*1.15,20000,1.1204)
   row={'pose_deg':int(pose),'gravity':model,'variant':variant,'force_N':sol['bilateral_footplate_force_N'],'quad_torque_Nm':sol['quadriceps_knee_torque_Nm'],'tendon_sf_proxy':sf}
   if variant!='baseline':row['force_gain_pct']=p['comparison_to_baseline']['bilateral_footplate_force_gain_pct'];row['joint_gate']=row['force_gain_pct']>=20 and sf>=1.5
   rows.append(row)
result={'experiment_id':'EXP-0089','classification':'ARITHMETIC_AUDIT_AND_MODEL_ONLY_RECOMPUTATION','protocol_sha256_lf':text_sha256(H/'GRAVITY_AUDIT_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'chain_source_sha256_lf':text_sha256(source_path),'tendon_source_sha256_lf':text_sha256(stress_path),'derivative_checks':checks,'scenarios':rows,'whole_architecture':'NOT_ASSESSED'}
(H/'GRAVITY_AUDIT_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
