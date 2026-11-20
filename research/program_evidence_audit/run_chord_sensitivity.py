import hashlib, json, math, sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]
source=ROOT/'research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py'; src=source.read_text(encoding='utf-8')
assert text_sha256(source)=='f01ec4c94f013e738d284428100659e0fe68281283310d796a222b42c55d5bfe'
old='        tau_g[0] = -(dV_dphi1 + dV_dphi2)'; new='        tau_g[0] = -dV_dphi1'; assert src.count(old)==1
assert src.count('sled_elev = math.radians(4.0)')==1
stress_path=H/'run_chain_tendon.py'; st={'__name__':'chord_tendon','__file__':str(stress_path)}; exec(compile(stress_path.read_text(encoding='utf-8').split('chain = json.loads')[0],str(stress_path),'exec'),st)
xlsx=Path(sys.argv[1]); digest=hashlib.sha256(xlsx.read_bytes()).hexdigest(); assert digest=='8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe'
sheet=load_workbook(xlsx,read_only=True,data_only=True)['Mechanical+EMG']; raw=list(sheet.values); assert raw[1][2]=="PF'" and raw[1][7]=="RFDmax'"
records={}; person=None
for row in raw[2:]:
 if row[0] is not None: person=str(row[0]).strip()
 if row[1] is not None:
  assert person and row[1] not in records.setdefault(person,{})
  records[person][row[1]]=(row[2],row[7])
valid=[]
for row in records.values():
 try:
  values=(*row['W0'],*row['POS'])
  if all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in values): valid.append(values[0])
 except KeyError: pass
assert len(valid)==11
initial=np.array(valid); loso=(initial.sum()-initial)/(len(initial)-1)
reference=json.loads((H/'GRAVITY_AUDIT_RESULTS.json').read_text(encoding='utf-8'))['scenarios']; rows=[]; errors=[]
for angle in (-6,-1,4,9,14):
 for knee in (100,110,140):
  code=src.replace(old,new).replace('sled_elev = math.radians(4.0)',f'sled_elev = math.radians({angle}.0)')
  if knee==110:
   a='"theta_knee_flex_deg": 80.0, "theta_hip_flex_deg": 78.0'; b='"theta_knee_flex_deg": 70.0, "theta_hip_flex_deg": 78.0'; assert code.count(a)==1; code=code.replace(a,b)
  ctx={'__name__':'chord_chain','__file__':str(source)}; exec(compile(code,str(source),'exec'),ctx)
  try: scenarios=ctx['solve_closed_chain_3dof_model']()['scenarios']
  except RuntimeError as exc: errors.append({'angle_deg':angle,'knee_deg':knee,'error':str(exc)}); continue
  label='extended_140deg_int' if knee==140 else 'flexed_100deg_int'
  for variant in ('baseline','strategy_2_coordinated_chain'):
   p=scenarios[variant]['postures'][label]; sol=p['compatible_lp_solution']; force=sol['bilateral_footplate_force_N']; torque=sol['quadriceps_knee_torque_Nm']; tendon=torque/ctx['patellar_moment_arm_m'](p['theta_knee_flex_deg']); sf=95*1.08/st['local_stress'](tendon,104*1.15,20000,1.1204)
   r={'chord_deg':angle,'internal_knee_deg':knee,'variant':variant,'force_N':force,'quad_torque_Nm':torque,'tendon_sf_proxy':sf}
   if variant!='baseline':
    r['gain_pct']=p['comparison_to_baseline']['bilateral_footplate_force_gain_pct']; r['model_joint_gate']=r['gain_pct']>=20 and sf>=1.5
   if knee==110 and variant=='baseline': r.update({'santos_reused_mae_N':float(np.abs(force-initial).mean()),'santos_reused_bias_N':float((force-initial).mean())})
   if angle==4:
    ref=next(x for x in reference if x['pose_deg']==knee and x['gravity']=='corrected' and x['variant']==variant)
    assert abs(force-ref['force_N'])<1e-8 and abs(sf-ref['tendon_sf_proxy'])<1e-8
   rows.append(r)
result={'experiment_id':'EXP-0092','classification':'MODEL_ONLY_GEOMETRY_SENSITIVITY_REUSED_COHORT','protocol_sha256_lf':text_sha256(H/'CHORD_SENSITIVITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'chain_source_sha256_lf':text_sha256(source),'tendon_source_sha256_lf':text_sha256(stress_path),'source_xlsx_sha256_bytes':digest,'participants':len(initial),'santos_loso_mae_N':float(np.abs(loso-initial).mean()),'scenarios':rows,'solver_errors':errors,'limitations':['fixed diagnostic grid, not a population distribution','chord orientation does not determine torso-relative hip angle','previously viewed cohort, no new validation','tendon SF is a conditional model proxy','whole architecture and real functional effect not assessed']}
(H/'CHORD_SENSITIVITY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
