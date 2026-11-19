"""Join existing static chain, tendon proxy and prescribed thermal profile."""
import json
from pathlib import Path
from run_audit import load_runner, text_sha256

HERE = Path(__file__).resolve().parent
chain_path=HERE/"CHAIN_TENDON_RESULTS.json"
records=json.loads(chain_path.read_text(encoding="utf-8"))["cases"]
solver=load_runner(63)
duration_s=2700
duty=0.60
effort_power_W=360
recovery_power_W=35
step_s=5
period_s=60/duty
powers=[effort_power_W if (t % period_s)<60 else recovery_power_W for t in range(0,duration_s,step_s)]
work_J=sum(p*step_s for p in powers)
assert work_J==27*(60*effort_power_W+40*recovery_power_W)
thermal=solver.simulate_4layer_pennes_2700s(effort_power_W,duty,20,0.5,body_mass_kg=75,dt_s=step_s)
assert thermal["energy_balance_error_J"]<0.001
scenarios=[]
for posture in ("flexed_100deg_int","extended_140deg_int"):
    for variant in ("baseline","strategy_2_coordinated_chain"):
        matches=[r for r in records if r["posture"]==posture and r["scenario"]==variant and r["csa_multiplier"]==1.15 and r["uts_multiplier"]==1.08 and r["rate_N_s"]==20000]
        assert len(matches)==1
        row=matches[0]
        force=row["plate_force_bilateral_N"]
        outcomes={
            "force_gain_target": "PASS_MODEL" if row["force_goal_pass"] else "FAIL_MODEL",
            "tendon_margin_SF15": "PASS_MODEL" if row["conditional_tissue_gate_pass"] else "FAIL_MODEL",
            "thermal_model_gate": "PASS_MODEL" if thermal["passes_core_39_5C_gate"] else "FAIL_MODEL",
            "fatigue_and_power_retention":"NOT_ASSESSED",
            "motor_accuracy_and_reaction":"NOT_ASSESSED",
            "post45_and_recovery":"NOT_ASSESSED",
        }
        scenarios.append({
            "posture":posture,"variant":variant,
            "force_N":force,"force_gain_pct":row["plate_gain_pct"],
            "nominal_velocity_for_360W_m_s":effort_power_W/force,
            "tendon_force_proxy_N":row["equivalent_tendon_force_N"],
            "tendon_local_sf":row["local_sf"],
            "work_J":work_J,"peak_core_C":thermal["peak_T_core_C"],
            "outcomes":outcomes,"whole_architecture":"NOT_ASSESSED",
        })
result={
    "experiment_id":"EXP-0077","classification":"CONDITIONAL_INTERFACE_DEMONSTRATION",
    "protocol_sha256_lf":text_sha256(HERE/"INTEGRATED_SCENARIO_PROTOCOL.md"),
    "chain_tendon_sha256_lf":text_sha256(chain_path),
    "thermal_solver_sha256_lf":text_sha256(HERE.parent/"exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py"),
    "mass_kg":75,"height_m":1.78,"duty":duty,"effort_W":effort_power_W,
    "recovery_W":recovery_power_W,"duration_s":duration_s,
    "unmet_channels":["dynamic_fatigue","motor_accuracy","response_latency","post45","recovery"],
    "scenarios":scenarios,
}
(HERE/"INTEGRATED_SCENARIO_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
