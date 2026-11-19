"""Join static LP torque to the existing conditional tendon stress equation."""
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
chain_path = ROOT / "research/exp0061_multijoint_legpress/RESULTS.json"
tendon_path = ROOT / "research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json"

def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()

def local_stress(force, csa, rate, deep):
    dynamic = 1 + 0.24 * rate * 0.18 * (1 - math.exp(-force / rate / 0.18)) / force
    axial = force / csa * deep * (1 + 0.55 * (dynamic - 1))
    shear_ratio = 0.195 * dynamic ** 0.35
    return axial * math.sqrt(1 + 3 * shear_ratio ** 2)

chain = json.loads(chain_path.read_text(encoding="utf-8"))["part_c_closed_chain_3dof_model"]["scenarios"]
tendon = json.loads(tendon_path.read_text(encoding="utf-8"))
deep = tendon["part_a_bogaerts_calibration"]["calibrated_layer_stress_multipliers"]["deep_k"]
reference = next(x for x in tendon["part_b_viscoelastic_enthesis_rates"]["rate_sweep_results"]["s1_unadapted_plus20_4800N"] if x["dF_dt_N_s"] == 20000)
assert abs(local_stress(4800, 104, 20000, deep) - reference["peak_von_mises_stress_MPa"]) < 0.02
rows = []
for posture, scenario, csa_factor, uts_factor, rate in itertools.product(
    ("flexed_100deg_int", "extended_140deg_int"),
    ("baseline", "strategy_2_coordinated_chain"),
    (1.0, 1.15), (1.0, 1.08, 1.10), (2000, 20000)
):
    record = chain[scenario]["postures"][posture]
    sol = record["compatible_lp_solution"]
    flex = record["theta_knee_flex_deg"]
    moment_arm = 0.043 + 0.00018 * flex - 0.0000015 * flex ** 2
    force = sol["quadriceps_knee_torque_Nm"] / moment_arm
    csa = 104 * csa_factor
    stress = local_stress(force, csa, rate, deep)
    sf = 95 * uts_factor / stress
    gain = record.get("comparison_to_baseline", {}).get("bilateral_footplate_force_gain_pct", 0)
    rows.append({
        "posture": posture, "scenario": scenario,
        "plate_force_bilateral_N": sol["bilateral_footplate_force_N"],
        "quadriceps_moment_Nm_single_limb": sol["quadriceps_knee_torque_Nm"],
        "equivalent_tendon_force_N": round(force, 2),
        "moment_arm_m": round(moment_arm, 6),
        "csa_multiplier": csa_factor, "uts_multiplier": uts_factor,
        "rate_N_s": rate, "nominal_stress_MPa": round(force/csa, 3),
        "local_stress_MPa": round(stress, 3), "local_sf": round(sf, 4),
        "plate_gain_pct": gain, "force_goal_pass": gain >= 20,
        "conditional_tissue_gate_pass": sf >= 1.5,
        "joint_gate_pass": gain >= 20 and sf >= 1.5,
    })
result = {
    "experiment_id": "EXP-0069",
    "classification": "MODEL_ONLY_STATIC_CHAIN_WITH_CONDITIONAL_TENDON_PROXY",
    "inputs_sha256_lf": {str(p.relative_to(ROOT)): digest(p) for p in [chain_path, tendon_path, HERE/"CHAIN_TENDON_PROTOCOL.md"]},
    "verification_4800N_stress_MPa": round(local_stress(4800, 104, 20000, deep), 4),
    "tendon_reference_stress_MPa": reference["peak_von_mises_stress_MPa"],
    "cases": rows,
}
(HERE/"CHAIN_TENDON_RESULTS.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
for p in ("flexed_100deg_int", "extended_140deg_int"):
    group = [r for r in rows if r["posture"] == p and r["scenario"] == "strategy_2_coordinated_chain"]
    print(p, "force", group[0]["equivalent_tendon_force_N"], "SF", min(r["local_sf"] for r in group), max(r["local_sf"] for r in group), "joint", sum(r["joint_gate_pass"] for r in group), "/", len(group))
