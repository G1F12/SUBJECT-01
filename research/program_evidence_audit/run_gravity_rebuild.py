"""EXP-0090: rebuild the gravity-dependent programme in an isolated workspace."""
import contextlib,hashlib,io,json,tempfile
from pathlib import Path
from run_audit import load_runner,text_sha256
H=Path(__file__).resolve().parent;ROOT=H.parents[1]; chain_src=ROOT/'research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py'; source=chain_src.read_text(encoding='utf-8'); expected='f01ec4c94f013e738d284428100659e0fe68281283310d796a222b42c55d5bfe';assert text_sha256(chain_src)==expected
inputs=[chain_src,chain_src.parent/'RESULTS.json',ROOT/'research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json',ROOT/'research/exp0063_pennes_bioheat_cpe45/RESULTS.json',ROOT/'research/functional_mechanics_validation/RESULTS.json',ROOT/'research/targets/CPE45.json',H/'GRAVITY_AUDIT_RESULTS.json',H/'CHAIN_TENDON_RESULTS.json',H/'INTEGRATED_SCENARIO_RESULTS.json',H/'COUPLED_ENERGY_THERMAL_RESULTS.json',ROOT/'research/recovery_2026_11_04/engine.py',ROOT/'research/cpe45_2026_11_04/model.py',ROOT/'research/cpe45_2026_11_04/config.json',ROOT/'research/integrated_2026_11_01/model.py',ROOT/'research/integrated_2026_11_01/parameters.json',ROOT/'research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py']
input_hashes={p.relative_to(ROOT).as_posix():text_sha256(p) for p in inputs}
old='        tau_g[0] = -(dV_dphi1 + dV_dphi2)';new='        tau_g[0] = -dV_dphi1';assert source.count(old)==1;fixed=source.replace(old,new)
def original_chain(code):
 ctx={'__name__':'rebuild_chain','__file__':str(chain_src)};exec(compile(code,str(chain_src),'exec'),ctx);return ctx['solve_closed_chain_3dof_model']()
archived=json.loads((chain_src.parent/'RESULTS.json').read_text(encoding='utf-8')); baseline=original_chain(source); corrected=original_chain(fixed);assert baseline==archived['part_c_closed_chain_3dof_model']
expected_rows=json.loads((H/'GRAVITY_AUDIT_RESULTS.json').read_text(encoding='utf-8'))['scenarios']
for p,label in [(100,'flexed_100deg_int'),(140,'extended_140deg_int')]:
 for v in ('baseline','strategy_2_coordinated_chain'):
  row=next(x for x in expected_rows if x['pose_deg']==p and x['gravity']=='corrected' and x['variant']==v);assert corrected['scenarios'][v]['postures'][label]['compatible_lp_solution']['bilateral_footplate_force_N']==row['force_N']
chain_all=dict(archived);chain_all['part_c_closed_chain_3dof_model']=corrected;chain_all['revision']='EXP-0090 gravity-only corrected; historical other sections unchanged'
# Each adapted legacy script is run using its original __file__; output and inputs are redirected.
def execute(name,replacements,external):
 path=H/name; src=path.read_text(encoding='utf-8')
 for old_text,new_text in replacements:
  assert src.count(old_text)==1,(name,old_text,src.count(old_text));src=src.replace(old_text,new_text)
 ctx={'__name__':'isolated_'+path.stem,'__file__':str(path),**external}
 with contextlib.redirect_stdout(io.StringIO()):exec(compile(src,str(path),'exec'),ctx)
 return ctx['result']
(ROOT/'tmp').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='gravity_rebuild_',dir=ROOT/'tmp') as tmp:
 tmp=Path(tmp);chain_path=tmp/'corrected61.json';chain_path.write_text(json.dumps(chain_all,indent=2)+'\n',encoding='utf-8'); tendon_path=tmp/'corrected69.json'; integrated_path=tmp/'corrected77.json'; interface_path=tmp/'corrected78.json'; reopt_path=tmp/'corrected79.json'; coupling_path=tmp/'corrected85.json'; sensitivity_path=tmp/'corrected68.json'
 tendon=execute('run_chain_tendon.py',[( 'chain_path = ROOT / "research/exp0061_multijoint_legpress/RESULTS.json"','chain_path = _chain_path'),('(HERE/"CHAIN_TENDON_RESULTS.json").write_text','_output.write_text')],{'_chain_path':chain_path,'_output':tendon_path})
 assert len(tendon['cases'])==48; tendon['inputs_sha256_lf']={'corrected_chain':text_sha256(chain_path),'original_tendon62':text_sha256(ROOT/'research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json'),'original_protocol':text_sha256(H/'CHAIN_TENDON_PROTOCOL.md')};tendon['experiment_id']='EXP-0090_tendon_rebuild';tendon_path.write_text(json.dumps(tendon,indent=2)+'\n',encoding='utf-8')
 oldcases=json.loads((H/'CHAIN_TENDON_RESULTS.json').read_text(encoding='utf-8'))['cases']; keys=('posture','scenario','csa_multiplier','uts_multiplier','rate_N_s');assert len({tuple(x[k] for k in keys) for x in oldcases})==48;assert {tuple(x[k] for k in keys) for x in oldcases}=={tuple(x[k] for k in keys) for x in tendon['cases']}
 integrated=execute('run_integrated_scenario.py',[( 'chain_path=HERE/"CHAIN_TENDON_RESULTS.json"','chain_path=_tendon_path'),('(HERE/"INTEGRATED_SCENARIO_RESULTS.json").write_text','_output.write_text')],{'_tendon_path':tendon_path,'_output':integrated_path})
 interface=execute('run_tendon_interface.py',[( 'original=HERE/"CHAIN_TENDON_RESULTS.json"','original=_tendon_path'),('(HERE/"TENDON_INTERFACE_RESULTS.json").write_text','_output.write_text')],{'_tendon_path':tendon_path,'_output':interface_path});assert len(interface['cases'])==24
 reopt=execute('run_chain_reopt.py',[( 'source=source_path.read_text(encoding="utf-8")','source=_fixed_source'),('(HERE/"CHAIN_TENDON_RESULTS.json")','_tendon_path'),('(HERE/"TENDON_INTERFACE_RESULTS.json")','_interface_path'),('(HERE/"CHAIN_REOPT_RESULTS.json").write_text','_output.write_text')],{'_fixed_source':fixed,'_tendon_path':tendon_path,'_interface_path':interface_path,'_output':reopt_path});assert len(reopt['cases'])==10
 sensitivity=execute('run_chain_sensitivity.py',[( 'source = source_path.read_text(encoding="utf-8")','source = _fixed_source'),('archive = json.loads((source_path.parent / "RESULTS.json").read_text(encoding="utf-8"))','archive = _chain'),('(HERE / "CHAIN_SENSITIVITY_RESULTS.json").write_text','_output.write_text')],{'_fixed_source':fixed,'_chain':chain_all,'_output':sensitivity_path});assert sum(len(v) for v in sensitivity['results'].values())==23
 coupling=execute('run_coupled_energy_thermal.py',[("text_sha256(H/'CHAIN_TENDON_RESULTS.json')",'text_sha256(_tendon_path)'),( "(H/'CHAIN_TENDON_RESULTS.json')",'_tendon_path'),("(H/'COUPLED_ENERGY_THERMAL_RESULTS.json').write_text",'_output.write_text')],{'_tendon_path':tendon_path,'_output':coupling_path});assert len(coupling['runs'])==6 and all(abs(x['energy_residual_J'])<.01 and x['coupled_thermal_residual_J']<.01 for x in coupling['runs'])
 master=load_runner(64);master.EXP61_JSON=chain_path;master.OUT_DIR=tmp/'master';
 with contextlib.redirect_stdout(io.StringIO()):master.main()
 summary64=json.loads((master.OUT_DIR/'RESULTS.json').read_text(encoding='utf-8'));assert summary64['invariants']['TARGET_CPE45']=='NOT EXTERNALLY VALIDATED'
 historic85=json.loads((H/'COUPLED_ENERGY_THERMAL_RESULTS.json').read_text(encoding='utf-8')); assert all(a['actual_work_J']==b['actual_work_J'] and a['heat_J']==b['heat_J'] and a['conditional_thermal_peak_C']==b['conditional_thermal_peak_C'] for a,b in zip(historic85['runs'],coupling['runs']))
 historic77=json.loads((H/'INTEGRATED_SCENARIO_RESULTS.json').read_text(encoding='utf-8'));assert all(a['work_J']==b['work_J'] and a['peak_core_C']==b['peak_core_C'] for a,b in zip(historic77['scenarios'],integrated['scenarios']))
 gate_changes=sum(a['joint_gate_pass']!=b['joint_gate_pass'] for a,b in zip(oldcases,tendon['cases'])); outputs={'chain':corrected,'tendon_cases':tendon['cases'],'sensitivity_68':sensitivity['results'],'interface_77':integrated['scenarios'],'interface_78':interface['cases'],'reoptimization_79':reopt['cases'],'coupled_85':coupling['runs'],'aggregator_64_pillars':summary64['pillar_summaries']}
 assert input_hashes=={p.relative_to(ROOT).as_posix():text_sha256(p) for p in inputs}
 result={'input_hashes_sha256_lf':input_hashes,'experiment_id':'EXP-0090','classification':'GRAVITY_ONLY_REBUILD_MODEL_NOT_VALIDATED','protocol_sha256_lf':text_sha256(H/'GRAVITY_REBUILD_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'source_chain_sha256_lf':text_sha256(chain_src),'corrected_source_sha256_lf':hashlib.sha256(fixed.replace('\r\n','\n').encode('utf-8')).hexdigest(),'dependency_hashes':{p.name:text_sha256(p) for p in [H/'run_chain_tendon.py',H/'run_integrated_scenario.py',H/'run_tendon_interface.py',H/'run_chain_reopt.py',H/'run_chain_sensitivity.py',H/'run_coupled_energy_thermal.py',ROOT/'research/architecture_a_integration/run_exp0064_master_integration.py']},'checks':{'archive_chain_reproduced':True,'gravity89_matched':True,'tendon_cases':48,'tendon_gate_changes':gate_changes,'sensitivity_cases':23,'interface_cases':24,'reoptimization_cases':10,'coupled_energy_heat_invariant_to_chain':True,'fixed_work_thermal_invariant_to_chain':True,'legacy_master_rules_not_adopted':True},'outputs':outputs,'unassessed':['hip_trunk_geometry','individual_tendon_strain','dynamic_force_power','motor_accuracy','post45','independent_joint_outcomes','whole_architecture']}
 (H/'GRAVITY_REBUILD_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['checks'],indent=2))
