"""Regression checks for the consolidated interpretation and numeric replay."""
import unittest
from functools import partial

from research.consolidation import reproduce_evidence as evidence


class TestConsolidationEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = evidence.read_json(evidence.HERE / "evidence_results.json")

    def test_active_only_and_mixed_protocols_are_distinct(self):
        bird = self.snapshot["bird"]
        active = bird["active_only"]
        mixed = bird["all"]
        self.assertEqual(mixed["observations"] - active["observations"], 1382)
        self.assertEqual(active["subjects"], 6)
        models = active["models"]
        bridge = models["M_Bridge_CoActivation"]
        baseline = models["M1_sEMG"]
        self.assertLess(bridge["mean_fold_r2"], 0)
        self.assertGreater(bridge["pooled_r2"], 0)
        self.assertLess(bridge["mean_fold_r2"], baseline["mean_fold_r2"])
        self.assertGreater(bridge["pooled_rmse"], baseline["pooled_rmse"])

    def test_bird_replay_matches_snapshot_when_raw_input_available(self):
        config = evidence.read_json(evidence.ROOT / "research/cycle13_decision_experiment/config.json")
        if not (evidence.ROOT / config["dataset"]["file_path"]).is_file():
            self.skipTest("Original Dryad dynamic knee array is unavailable")
        evidence.verify(self.snapshot["bird"], evidence.bird_evidence())

    def test_fixed_gamma_bridge_is_a_rescaling_of_m4(self):
        from research.cycle13_decision_experiment.functional_force_bridge import (
            FunctionalForceBridge,
        )

        bridge = FunctionalForceBridge()
        if not (evidence.ROOT / bridge.raw_data_path).is_file():
            self.skipTest("Original Dryad dynamic knee array is unavailable")
        bridge.compute_multi_muscle_torque = partial(
            bridge.compute_multi_muscle_torque, antagonist_gamma_slope=0.0
        )
        for condition in ("all", "active_only"):
            with self.subTest(condition=condition):
                models = bridge.evaluate_loso_cross_validation(condition)["models_summary"]
                evidence.verify(models["M4_Hill_Composite"], models["M_Bridge_CoActivation"])

    def test_evidence_snapshot_rejects_mismatch(self):
        with self.assertRaisesRegex(ValueError, r"results\.NEG-0042\.usable"):
            evidence.verify(
                {"NEG-0042": {"usable": 66}},
                {"NEG-0042": {"usable": 68}},
            )

    def test_consolidation_preserves_evidence_boundaries(self):
        registry = evidence.ROOT / "registry"
        hypotheses = {row["id"]: row for row in evidence.read_json(registry / "hypotheses.json")}
        experiments = {row["id"]: row for row in evidence.read_json(registry / "experiments.json")}
        self.assertEqual(hypotheses["HYP-0009"]["status"], "unverified")
        self.assertEqual(hypotheses["HYP-0009"]["evidence_status"], "MODEL_ONLY")
        self.assertEqual(hypotheses["HYP-0010"]["status"], "unverified")
        self.assertEqual(experiments["EXP-0046"]["external_validation"], "same_cohort_leave_one_subject_out_only")
        self.assertEqual(experiments["EXP-0047"]["external_validation"], "none_new")
