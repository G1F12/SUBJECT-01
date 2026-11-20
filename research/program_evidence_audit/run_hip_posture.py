"""EXP-0088: audit hip argument and exploratory knee-angle transfer."""
import ast,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1];path=Path(sys.argv[1]);digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest=='8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe'
source_path=ROOT/'research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py';source=source_path.read_text(encoding='utf-8');tree=ast.parse(source);functions=[x for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name=='posture_kinematics'];assert len(functions)==1
hip_reads=[x for x in ast.walk(functions[0]) if isinstance(x,ast.Name) and x.id=='theta_hip_flex_deg' and isinstance(x.ctx,ast.Load)]
def compute(code):
 ctx={'__name__':'hip_posture_check','__file__':str(source_path)};exec(compile(code,str(source_path),'exec'),ctx);return ctx['solve_closed_chain_3dof_model']()
original=compute(source); hip_invariance={}
for hip in (40.,78.,110.):
 s=source
 for old in ('"theta_hip_flex_deg": 78.0','"theta_hip_flex_deg": 48.0'):
  assert s.count(old)==1;s=s.replace(old,f'"theta_hip_flex_deg": {hip}')
 altered=compute(s); hip_invariance[str(hip)]={'all_scenario_outputs_equal':altered['scenarios']==original['scenarios']}
assert all(x['all_scenario_outputs_equal'] for x in hip_invariance.values())
old='"theta_knee_flex_deg": 80.0, "theta_hip_flex_deg": 78.0';assert source.count(old)==1
p110=compute(source.replace(old,'"theta_knee_flex_deg": 70.0, "theta_hip_flex_deg": 78.0'))
base100=original['scenarios']['baseline']['postures']['flexed_100deg_int']['compatible_lp_solution']['bilateral_footplate_force_N'];base110=p110['scenarios']['baseline']['postures']['flexed_100deg_int']['compatible_lp_solution']['bilateral_footplate_force_N'];enh=p110['scenarios']['strategy_2_coordinated_chain']['postures']['flexed_100deg_int'];enh110=enh['compatible_lp_solution']['bilateral_footplate_force_N'];gain=enh['comparison_to_baseline']['bilateral_footplate_force_gain_pct'];assert base100==2601.1
sheet=load_workbook(path,read_only=True,data_only=True)['Mechanical+EMG'];rows=list(sheet.values);assert rows[1][2]=="PF'" and rows[1][7]=="RFDmax'";people={};person=None
for row in rows[2:]:
 if row[0] is not None:person=str(row[0]).strip()
 if row[1] is not None:
  assert person and row[1] not in people.setdefault(person,{})
  people[person][row[1]]=(row[2],row[7])
valid=[]
for person,d in sorted(people.items()):
 try:
  a,ar=d['W0'];b,br=d['POS']
  if not all(isinstance(v,(float,int)) and math.isfinite(v) and v>0 for v in (a,b,ar,br)):raise ValueError('invalid')
  valid.append(float(a))
 except (KeyError,ValueError):pass
x=np.array(valid);n=len(x);assert n==11;predictions={'knee100':np.full(n,base100),'knee110':np.full(n,base110),'loso_mean':(x.sum()-x)/(n-1)};errors={k:np.abs(v-x) for k,v in predictions.items()};idx=np.random.default_rng(20261120).integers(0,n,(10000,n));contrasts={}
for k in ('knee100','loso_mean'):
 diff=errors[k]-errors['knee110'];contrasts[k]={'mean_mae_delta_N':float(diff.mean()),'ci95_N':np.quantile(diff[idx].mean(axis=1),[.025,.975]).tolist()}
output={'experiment_id':'EXP-0088','classification':'EXPLORATORY_REUSED_DATA_AND_MODEL_AUDIT','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'HIP_POSTURE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'chain_source_sha256_lf':text_sha256(source_path),'hip_parameter_ast_read_count':len(hip_reads),'hip_variation':hip_invariance,'participants':n,'baseline100_force_N':base100,'baseline110_force_N':base110,'strategy2_110_force_N':enh110,'strategy2_110_gain_pct':gain,'metrics':{k:{'mae_N':float(v.mean()),'bias_N':float(np.mean(predictions[k]-x))} for k,v in errors.items()},'paired_comparator_minus_110':contrasts,'conditional_superiority_both':all(contrasts[k]['ci95_N'][0]>0 for k in contrasts),'whole_architecture':'NOT_ASSESSED'}
(H/'HIP_POSTURE_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8');print(json.dumps(output,indent=2))
