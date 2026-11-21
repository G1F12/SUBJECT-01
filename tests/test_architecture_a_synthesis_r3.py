"""
Unit and regression test suite for Milestone 3 / Requirement R3 & R4
(Architecture A Master System Synthesis, Definitive Evidence Verdicts, and Governance Closure).

Covers:
- System synthesis across Module 1 through Module 5
- System transitions T1 through T5
- Definitive scientific verdicts for TARGET-FORCE20, TARGET-ADAPT25, TARGET-CPE45, and Joint Compatibility
- Decisive measurement pre-registrations
- Program hard invariants and registry integrity (EXP-0132, FND-0128, NEG-0112, DEC-0033)
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestArchitectureASynthesisR3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/architecture_a_integration/ARCHITECTURE_A_EVIDENCE_SYNTHESIS_RESULTS.json"
        cls.report_path = ROOT / "research/architecture_a_integration/ARCHITECTURE_A_EVIDENCE_SYNTHESIS_REPORT.md"
        cls.protocol_path = ROOT / "research/architecture_a_integration/ARCHITECTURE_A_SYNTHESIS_PROTOCOL.md"
        cls.script_path = ROOT / "research/architecture_a_integration/run_architecture_a_evidence_synthesis.py"

        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))
        cls.experiments = {e["id"]: e for e in json.loads((ROOT / "registry/experiments.json").read_text(encoding="utf-8"))}
        cls.findings = {f["id"]: f for f in json.loads((ROOT / "registry/findings.json").read_text(encoding="utf-8"))}
        cls.negative = {n["id"]: n for n in json.loads((ROOT / "registry/negative_results.json").read_text(encoding="utf-8"))}
        cls.decisions = {d["id"]: d for d in json.loads((ROOT / "registry/decisions.json").read_text(encoding="utf-8"))}

    # =========================================================================
    # Artifact Existence & Schema
    # =========================================================================
    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file(), f"Missing {self.results_path}")
        self.assertTrue(self.report_path.is_file(), f"Missing {self.report_path}")
        self.assertTrue(self.protocol_path.is_file(), f"Missing {self.protocol_path}")
        self.assertTrue(self.script_path.is_file(), f"Missing {self.script_path}")

    def test_basic_schema_properties(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0132")
        self.assertIn("FND-0128", self.res["findings"])
        self.assertIn("NEG-0112", self.res["negative_results"])
        self.assertIn("DEC-0033", self.res["decisions"])
        self.assertEqual(len(self.res["modules"]), 5)
        self.assertEqual(len(self.res["system_transitions"]), 5)
        self.assertEqual(len(self.res["decisive_measurements"]), 3)
        self.assertIn("audit_trace_matrix", self.res)
        self.assertIn("unified_consistent_scenario", self.res)

    # =========================================================================
    # Module 1: Closed-Chain Multijoint Biomechanics
    # =========================================================================
    def test_module1_biomechanics_and_angular_sensitivity(self):
        m1 = self.res["modules"]["module_1_closed_chain_biomechanics"]
        outs = m1["measured_outputs"]

        # Bilateral force gains
        self.assertAlmostEqual(outs["strategy2_force_gain_100deg_pct"], 21.64, places=2)
        self.assertAlmostEqual(outs["strategy2_force_gain_100deg_corrected_pct"], 21.93, places=2)
        self.assertAlmostEqual(outs["strategy2_force_gain_140deg_corrected_pct"], 21.77, places=2)
        self.assertAlmostEqual(outs["strategy2_force_gain_with_reciprocal_inhibition_pct"], 21.78, places=2)
        self.assertAlmostEqual(outs["strategy2_transfer_efficiency_eta"], 0.988, places=3)
        self.assertAlmostEqual(outs["quad_isolated_transfer_efficiency_eta"], 0.764, places=3)

        # Angular sensitivity gradient and artifact
        self.assertAlmostEqual(outs["angular_gradient_100_to_110_N_deg"], 40.98, places=1)
        self.assertAlmostEqual(outs["angular_gradient_110_to_140_N_deg"], 27.59, places=1)
        self.assertAlmostEqual(outs["mismatch_artifact_10deg_N"], 409.8, places=1)
        self.assertAlmostEqual(outs["mismatch_artifact_relative_to_baseline_pct"], 16.30, places=1)

        # Santos holdout bias & constant baseline comparison
        self.assertAlmostEqual(outs["santos_holdout_110deg_model_bias_N"], 463.2, places=1)
        self.assertAlmostEqual(outs["santos_holdout_110deg_model_mae_N"], 613.6, places=1)
        self.assertAlmostEqual(outs["santos_holdout_constant_baseline_mae_N"], 458.8, places=1)

        # Variance decomposition repeatability
        self.assertAlmostEqual(outs["detrended_within_subject_repeatability_sd_N"], 309.08, places=1)
        self.assertAlmostEqual(outs["detrended_within_subject_cv_pct"], 10.80, places=1)

    # =========================================================================
    # Module 2: Viscoelastic Tissue Hazard & Tendon Heterochrony
    # =========================================================================
    def test_module2_tissue_hazard_and_heterochrony(self):
        m2 = self.res["modules"]["module_2_tissue_hazard_and_heterochrony"]
        outs = m2["measured_outputs"]

        # Quasi-static loading SF >= 1.50
        self.assertAlmostEqual(outs["quasi_static_4800N_safety_factor"], 2.05, places=2)
        self.assertTrue(outs["quasi_static_safety_gate_passed"])
        self.assertAlmostEqual(outs["nominal_cyclic_fatigue_life_ratio"], 1.678, places=3)

        # Dynamic posture comparison (100° fails vs 140° passes)
        self.assertAlmostEqual(outs["posture_100deg_dynamic_sf"], 1.285, places=2)
        self.assertFalse(outs["posture_100deg_dynamic_safety_gate_passed"])
        self.assertAlmostEqual(outs["posture_140deg_dynamic_sf"], 1.747, places=2)
        self.assertTrue(outs["posture_140deg_dynamic_safety_gate_passed"])

        # Explosive ballistic recruitment (20,000 N/s) failure
        self.assertAlmostEqual(outs["ballistic_20k_deep_to_superficial_shear_ratio"], 1.232, places=2)
        self.assertAlmostEqual(outs["ballistic_mvc_7661N_adapted_sf_local"], 1.31, places=2)
        self.assertFalse(outs["ballistic_safety_gate_passed"])

        # Empirical longitudinal strength gain & reserve sensitivity
        self.assertAlmostEqual(outs["santos_day14_mean_force_gain_pct"], 18.35, places=1)
        self.assertAlmostEqual(outs["simulated_min_sf_under_sf0_1_50"], 1.267, places=2)
        self.assertAlmostEqual(outs["critical_reserve_threshold_sf0"], 1.776, places=3)
        self.assertEqual(outs["days_below_1_50_with_critical_sf0"], 0)
        self.assertAlmostEqual(outs["h2_tendon_paced_hazard_ratio"], 1.00, places=2)

    # =========================================================================
    # Module 3: 4-Component Bioenergetic Transition Interface
    # =========================================================================
    def test_module3_bioenergetic_transition_interface(self):
        m3 = self.res["modules"]["module_3_bioenergetic_transition_interface"]
        outs = m3["measured_outputs"]

        # Norbury crossover workload dissociation
        self.assertAlmostEqual(outs["norbury_volume_difference_pct"], 22.5, places=1)
        self.assertAlmostEqual(outs["norbury_5min_force_retention_LL_pct"], 91.01, places=1)
        self.assertAlmostEqual(outs["norbury_5min_force_retention_HL_pct"], 91.04, places=1)
        self.assertAlmostEqual(outs["norbury_retention_difference_pp"], 0.04, places=2)

        # Paired bootstrap out-of-sample failure of linear volume model
        self.assertAlmostEqual(outs["mean_retention_baseline_mae_N"], 50.61, places=1)
        self.assertAlmostEqual(outs["volume_linear_model_mae_N"], 54.69, places=1)
        self.assertAlmostEqual(outs["paired_dmae_volume_vs_baseline_N"], -4.08, places=2)
        self.assertLess(outs["paired_dmae_ci95_N"][1], 0.0)  # CI upper bound strictly negative

        # de Poli group directional falsification
        self.assertAlmostEqual(outs["depoli_retention_pre_pct"], 71.36, places=1)
        self.assertAlmostEqual(outs["depoli_retention_post_pct"], 75.08, places=1)

        # Recovery timeline
        self.assertAlmostEqual(outs["recovery_kinetics_retention_5min_pct"], 91.0, places=1)
        self.assertAlmostEqual(outs["recovery_kinetics_retention_45min_pct"], 98.3, places=1)
        self.assertAlmostEqual(outs["recovery_kinetics_retention_24h_pct"], 100.1, places=1)

    # =========================================================================
    # Module 4: 4-Layer Pennes Bioheat Solver for 2700 s CPE45
    # =========================================================================
    def test_module4_pennes_bioheat_and_cpe45_envelope(self):
        m4 = self.res["modules"]["module_4_pennes_bioheat_solver"]
        outs = m4["measured_outputs"]

        # McLaughlin empirical validation
        self.assertEqual(outs["mclaughlin_cohort_n"], 23)
        self.assertAlmostEqual(outs["pennes_solver_mae_C"], 0.586, places=2)
        self.assertAlmostEqual(outs["persistence_baseline_mae_C"], 1.275, places=2)
        self.assertAlmostEqual(outs["lumped_capacitance_mae_C"], 1.351, places=2)
        self.assertAlmostEqual(outs["pennes_vs_persistence_paired_dmae_C"], 0.689, places=2)
        self.assertGreater(outs["pennes_vs_persistence_ci95_C"][0], 0.0)

        # Continuous 360 W hyperthermia breach times (< 2700 s)
        breaches = outs["continuous_360W_breach_times_s"]
        self.assertEqual(breaches["Temperate"], 2365)
        self.assertEqual(breaches["Warm"], 1630)
        self.assertEqual(breaches["Hot-Dry"], 1240)
        self.assertEqual(breaches["Hot-Humid"], 1350)

        # Safe intermittent duty cycles
        duty = outs["safe_duty_cycles_D_max"]
        self.assertAlmostEqual(duty["Temperate"], 0.92, places=2)
        self.assertAlmostEqual(duty["Warm"], 0.74, places=2)
        self.assertAlmostEqual(duty["Hot-Dry"], 0.59, places=2)
        self.assertAlmostEqual(duty["Hot-Humid"], 0.65, places=2)

        # Intermittent peak T_core strictly < 39.5 C
        for climate, t_peak in outs["intermittent_peak_tcore_C"].items():
            self.assertLess(t_peak, 39.5, f"Climate {climate} breached 39.5°C with {t_peak}°C")

        # Active cooling and AEGIS-01
        self.assertAlmostEqual(outs["active_cooling_required_hot_humid_W"], 420.0, places=1)
        self.assertAlmostEqual(outs["aegis01_temperate_max_D"], 0.69, places=2)

    # =========================================================================
    # Module 5: Motor Control, Velocity Preservation, and Power
    # =========================================================================
    def test_module5_motor_control_velocity_power(self):
        m5 = self.res["modules"]["module_5_motor_control_velocity_power"]
        outs = m5["measured_outputs"]

        self.assertAlmostEqual(outs["single_joint_torque_gain_pct"], 21.9, places=1)
        self.assertAlmostEqual(outs["vmax_change_pct"], -1.7, places=1)
        self.assertAlmostEqual(outs["peak_power_gain_pct"], 19.8, places=1)
        self.assertAlmostEqual(outs["force_steadiness_cv_pct"], 2.1, places=1)
        self.assertTrue(outs["force_steadiness_threshold_passed"])
        self.assertTrue(outs["cop_within_margins"])
        self.assertLessEqual(outs["cop_displacement_m"], outs["cop_margin_limit_m"])

    # =========================================================================
    # Transitions T1 through T5
    # =========================================================================
    def test_transitions_t1_to_t5(self):
        transitions = {t["transition_id"]: t for t in self.res["system_transitions"]}
        self.assertEqual(set(transitions.keys()), {"T1", "T2", "T3", "T4", "T5"})
        for tid, t in transitions.items():
            self.assertTrue(len(t["input_contract"]) > 0, f"Empty input_contract in {tid}")
            self.assertTrue(len(t["measured_output"]) > 0, f"Empty measured_output in {tid}")
            self.assertTrue(len(t["baseline_comparison"]) > 0, f"Empty baseline_comparison in {tid}")
            self.assertTrue(len(t["uncertainty_bounds"]) > 0, f"Empty uncertainty_bounds in {tid}")
            self.assertTrue(len(t["operational_boundary"]) > 0, f"Empty operational_boundary in {tid}")

    # =========================================================================
    # Definitive Scientific Verdicts
    # =========================================================================
    def test_definitive_verdicts(self):
        v = self.res["definitive_verdicts"]

        # TARGET-FORCE20
        f20 = v["TARGET-FORCE20"]
        self.assertEqual(f20["status"], "CONDITIONALLY_VALIDATED_IN_MODEL_AND_TRANSFER_BOUNDED")
        self.assertEqual(f20["verdict"], "FEASIBLE_UNDER_RIGID_POSTURAL_ALIGNMENT")
        self.assertIn("±2°", f20["operational_boundary"])

        # TARGET-ADAPT25
        a25 = v["TARGET-ADAPT25"]
        self.assertEqual(a25["status"], "EMPIRICALLY_SUPPORTED_WITH_TISSUE_RESERVE_GATE")
        self.assertEqual(a25["verdict"], "EMPIRICALLY_DEMONSTRATED_IN_COHORT_AND_TISSUE_FEASIBLE")
        self.assertIn("1.78", a25["operational_boundary"])

        # TARGET-CPE45
        c45 = v["TARGET-CPE45"]
        self.assertEqual(c45["status"], "VALIDATED_INTERMITTENT_ENVELOPE_CONTINUOUS_360W_UNFEASIBLE")
        self.assertEqual(c45["verdict"], "VALIDATED_UNDER_INTERMITTENT_DUTY_CYCLE_PACING")

        # Joint System Compatibility
        jc = v["JOINT_SYSTEM_COMPATIBILITY"]
        self.assertEqual(jc["status"], "CONDITIONAL_POTENTIAL_WHOLE_SYSTEM_HOLD")
        self.assertEqual(jc["verdict"], "NOT_CONFIRMED_PENDING_DECISIVE_MEASUREMENTS")
        self.assertTrue(jc["definitive_answer"].startswith("NO"))
        self.assertEqual(len(jc["trade_offs_and_bounds"]), 4)

    # =========================================================================
    # Pre-Registered Decisive Measurements
    # =========================================================================
    def test_decisive_measurements(self):
        m = {dm["measurement_id"]: dm for dm in self.res["decisive_measurements"]}
        self.assertEqual(set(m.keys()), {"MEASUREMENT-1", "MEASUREMENT-2", "MEASUREMENT-3"})

        m1 = m["MEASUREMENT-1"]
        self.assertIn("ultrasound", m1["modality"].lower())
        self.assertIn("modulus", m1["parameters"].lower())

        m2 = m["MEASUREMENT-2"]
        self.assertIn("motion capture", m2["modality"].lower())
        self.assertIn("force plates", m2["modality"].lower())

        m3 = m["MEASUREMENT-3"]
        self.assertIn("cpet", m3["title"].lower())
        self.assertIn("mvc", m3["parameters"].lower())

    # =========================================================================
    # Program Hard Invariants
    # =========================================================================
    def test_program_hard_invariants(self):
        inv = self.res["program_invariants"]
        self.assertIn("NO_GO", inv["BIOLOGICAL_HUMAN_INTERVENTIONS"])
        self.assertIn("DISQUALIFIED_NO_GO", inv["ARCHITECTURE_B_BIOENGINEERED_MUSCLE"])
        self.assertIn("HOLD_BREAKTHROUGH_DEPENDENT", inv["ARCHITECTURE_C_INTERNAL_BIOHYBRID"])
        self.assertIn("CONDITIONAL_HOLD", inv["AEGIS_01_SUIT_INTEGRATION"])
        self.assertIn("INDEPENDENT_MANDATORY_REQUIREMENT", inv["TARGET_CPE45_STATUS"])


if __name__ == "__main__":
    unittest.main()
