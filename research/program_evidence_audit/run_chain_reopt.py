"""Re-optimize the static chain with a consistent quadriceps moment arm."""
import json
from pathlib import Path
from run_audit import text_sha256

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source_path=ROOT/"research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py"
source=source_path.read_text(encoding="utf-8")
fragment="r_vec[1] = patellar_moment_arm_m(th_k_deg)"
assert source.count(fragment)==1
stress_path=HERE/"run_chain_tendon.py"
stress_code=stress_path.read_text(encoding="utf-8").split("chain = json.loads")[0]
stress_context={"__name__":"tendon_stress","__file__":str(stress_path)}
exec(compile(stress_code,str(stress_path),"exec"),stress_context)
local_stress=stress_context["local_stress"]
archived=json.loads((HERE/"CHAIN_TENDON_RESULTS.json").read_text(encoding="utf-8"))["cases"]
sensitivity=json.loads((HERE/"TENDON_INTERFACE_RESULTS.json").read_text(encoding="utf-8"))["cases"]
outputs=[]
for multiplier in (0.8,0.9,1.0,1.1,1.2):
    revised=source.replace(fragment,f"r_vec[1] = {multiplier} * patellar_moment_arm_m(th_k_deg)")
    context={"__name__":"reoptimized_chain","__file__":str(source_path)}
    exec(compile(revised,str(source_path),"exec"),context)
    scenarios=context["solve_closed_chain_3dof_model"]()["scenarios"]
    for pose in ("flexed_100deg_int","extended_140deg_int"):
        current=scenarios["strategy_2_coordinated_chain"]["postures"][pose]
        solution=current["compatible_lp_solution"]
        gain=current["comparison_to_baseline"]["bilateral_footplate_force_gain_pct"]
        arm=multiplier*context["patellar_moment_arm_m"](current["theta_knee_flex_deg"])
        force=solution["quadriceps_knee_torque_Nm"]/arm
        sf=95*1.08/local_stress(force,104*1.15,20000,1.1204)
        post=next(x for x in sensitivity if x["posture"]==pose and x["csa_multiplier"]==1.15 and x["uts_multiplier"]==1.08 and x["rate_N_s"]==20000)
        if multiplier==1:
            old=next(x for x in archived if x["posture"]==pose and x["scenario"]=="strategy_2_coordinated_chain" and x["csa_multiplier"]==1.15 and x["uts_multiplier"]==1.08 and x["rate_N_s"]==20000)
            assert abs(sf-old["local_sf"])<0.001 and solution["bilateral_footplate_force_N"]==old["plate_force_bilateral_N"]
        outputs.append({"pose":pose,"arm_multiplier":multiplier,"force_N":solution["bilateral_footplate_force_N"],"gain_pct":gain,"quadriceps_moment_Nm":solution["quadriceps_knee_torque_Nm"],"tendon_proxy_force_N":force,"reoptimized_SF":sf,"fixed_torque_SF":post["sf_by_arm_multiplier"][str(multiplier)],"joint_gate":gain>=20 and sf>=1.5})
result={"experiment_id":"EXP-0079","classification":"MODEL_ONLY_STATIC_REOPTIMIZATION","protocol_sha256_lf":text_sha256(HERE/"CHAIN_REOPT_PROTOCOL.md"),"runner_sha256_lf":text_sha256(Path(__file__)),"chain_source_sha256_lf":text_sha256(source_path),"tendon_source_sha256_lf":text_sha256(stress_path),"cases":outputs}
(HERE/"CHAIN_REOPT_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
for row in outputs: print(row["pose"],row["arm_multiplier"],row["gain_pct"],round(row["reoptimized_SF"],3),row["joint_gate"])
