#!/usr/bin/env python3
"""
Verification unit tests for the completed PLAN.md & MASTER_ROADMAP.md suite:
EXP-0061, EXP-0062, EXP-0063, EXP-0064, DEC-0026, and hard program invariants.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/exp0061_multijoint_legpress"))
sys.path.insert(0, str(ROOT / "research/exp0062_enthesis_viscoelastic_hazard"))
sys.path.insert(0, str(ROOT / "research/exp0063_pennes_bioheat_cpe45"))

import run_exp0061_protocol_and_chain as exp61
import run_exp0062_enthesis_and_heterochrony as exp62
import run_exp0063_pennes_envelope as exp63


class TestMasterRoadmapCompletion(unittest.TestCase):
    def test_required_artifacts_and_reports_exist(self):
        required = [
            ROOT / "PLAN.md",
            ROOT / "MASTER_ROADMAP.md",
            ROOT / "research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py",
            ROOT / "research/exp0061_multijoint_legpress/RESULTS.json",
            ROOT / "research/exp0061_multijoint_legpress/EXPERIMENT_REPORT_RU.md",
            ROOT / "research/exp0062_enthesis_viscoelastic_hazard/run_exp0062_enthesis_and_heterochrony.py",
            ROOT / "research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json",
            ROOT / "research/exp0062_enthesis_viscoelastic_hazard/EXPERIMENT_REPORT_RU.md",
            ROOT / "research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py",
            ROOT / "research/exp0063_pennes_bioheat_cpe45/RESULTS.json",
            ROOT / "research/exp0063_pennes_bioheat_cpe45/EXPERIMENT_REPORT_RU.md",
            ROOT / "research/architecture_a_integration/run_exp0064_master_integration.py",
            ROOT / "research/architecture_a_integration/RESULTS.json",
            ROOT / "research/architecture_a_integration/ARCHITECTURE_A_CANONICAL_SPECIFICATION.md",
        ]
        for path in required:
            self.assertTrue(path.is_file(), f"Missing deliverable artifact: {path}")

    def test_exp0061_cohort_gate_and_closed_chain_invariants(self):
        res = json.loads((ROOT / "research/exp0061_multijoint_legpress/RESULTS.json").read_text(encoding="utf-8"))
        gate = res["part_a_cohort_gate_audit"]
        self.assertEqual(gate["n_candidates_audited"], 6)
        self.assertEqual(gate["n_admitted"], 0)
        self.assertEqual(gate["primary_outcome_bilateral_leg_press"], "Outcome 4: DATA_BLOCKED")

        dpv = res["part_b_dpvalid_reference_benchmark"]
        self.assertEqual(dpv["status"], "PROTOCOL_SHIFT_SINGLE_JOINT_REFERENCE")
        self.assertLess(dpv["convention_A_vs_B_max_sigma_diff_n_cm2"], 1e-12)
        boot_f0 = dpv["paired_cluster_bootstrap_condition_level"]["M2_vs_Baseline_F0"]
        self.assertEqual(boot_f0["n_subject_clusters"], 20)
        self.assertEqual(boot_f0["n_bootstrap_replicates"], 10000)

        chain = res["part_c_closed_chain_3dof_model"]["scenarios"]
        base_100 = chain["baseline"]["postures"]["flexed_100deg_int"]
        self.assertAlmostEqual(base_100["det_J_ankle_numeric"], base_100["det_J_ankle_analytic"], places=5)
        self.assertEqual(base_100["rank_J_foot_T"], 2)
        self.assertFalse(base_100["naive_uncoordinated_diagnostics"]["naive_cop_within_foot_bounds"])
        self.assertGreater(chain["strategy_2_coordinated_chain"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["bilateral_footplate_force_gain_pct"], 20.0)
        # Isolated quad augmentation cannot transfer 1:1 without chain adaptation
        self.assertLess(chain["quad_only_plus20"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["closed_chain_transfer_ratio_eta"], 0.85)

    def test_exp0062_enthesis_and_heterochrony_bounds(self):
        res = json.loads((ROOT / "research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(res["part_a_bogaerts_calibration"]["deep_to_superficial_ratio"], 1.2315, places=3)
        rates = res["part_b_viscoelastic_enthesis_rates"]["rate_sweep_results"]
        s1_20k = [r for r in rates["s1_unadapted_plus20_4800N"] if r["dF_dt_N_s"] == 20000][0]
        s2_20k = [r for r in rates["s2_case2c_adapted_plus20_4800N"] if r["dF_dt_N_s"] == 20000][0]
        m1_20k = [r for r in rates["mvc_unadapted_plus20_7661N"] if r["dF_dt_N_s"] == 20000][0]
        self.assertGreater(s1_20k["peak_von_mises_stress_MPa"], s1_20k["nominal_proximal_stress_MPa"])
        self.assertGreaterEqual(s2_20k["local_enthesis_safety_factor"], 1.50)
        self.assertTrue(m1_20k["exceeds_85MPa_collagen_threshold"])

        regimes = res["part_c_remodeling_heterochrony_ode"]["regimes"]
        self.assertGreater(regimes["H1_uncoordinated_target_adapt25_12d"]["peak_daily_damage_acceleration_ratio"], 2.0)
        self.assertLessEqual(regimes["H2_tendon_paced_synchronized"]["peak_daily_damage_acceleration_ratio"], 1.05)

    def test_exp0063_energy_conservation_and_cpe45_invariants(self):
        # Directly verify First Law closure on fresh solver run + saved results
        sim = exp63.simulate_4layer_pennes_2700s(360.0, 0.50, 20.0, 0.50, dt_s=5.0)
        self.assertLess(sim["energy_balance_error_J"], 1e-4)

        res = json.loads((ROOT / "research/exp0063_pennes_bioheat_cpe45/RESULTS.json").read_text(encoding="utf-8"))
        self.assertEqual(res["invariant_status"], "TARGET-CPE45 = NOT EXTERNALLY VALIDATED")
        self.assertLess(res["part_b_3d_envelope_summary"]["max_energy_closure_error_J"], 1e-4)
        self.assertEqual(res["part_c_cpe45_bridge_verification"]["target_achievement"], "not_assessed")
        self.assertFalse(res["part_c_cpe45_bridge_verification"]["physiological_validation"])
        aegis = res["part_b_3d_envelope_summary"]["aegis01_thermal_penalty"]
        self.assertLess(aegis["temperate_360W_aegis01_max_D"], aegis["temperate_360W_native_max_D"])

    def test_exp0064_and_program_invariants(self):
        res64 = json.loads((ROOT / "research/architecture_a_integration/RESULTS.json").read_text(encoding="utf-8"))
        self.assertEqual(res64["invariants"]["TARGET_CPE45"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(res64["invariants"]["BIOLOGICAL_INTERVENTIONS"], "NO_GO")
        self.assertEqual(res64["master_decision_matrix"]["EXP-0061_LegPress"]["status"], "DATA_BLOCKED")
        self.assertEqual(res64["master_decision_matrix"]["Architecture_B"]["status"], "DISQUALIFIED_NO_GO")

        cpe_spec = json.loads((ROOT / "research/targets/CPE45.json").read_text(encoding="utf-8"))
        self.assertEqual(cpe_spec["historical_experiments_cpe45_status"], "not_assessed")
        self.assertIsNone(cpe_spec["success_thresholds"])


if __name__ == "__main__":
    unittest.main()
