"""
Unit test suite for EXP-0134 (Open Data Candidate Audit & Transfer Boundary Verification).

Verifies:
- Audit of candidate open datasets for joint mechanical work and residual strength
- Exact empirical recovery kinetics from primary Norbury XLSX (91.01% at 5m, 93.34% at 45m, 99.10% at 24h)
- Verification that accumulated work strictly precedes predicted sprint in Jutlah et al.
- Comparison of work models against multi-factorial sprint+rest baselines (89.83 W vs 91.98 W)
- Status of request-only and blocked candidates (de Poli, Plantarflexion, Kudzia)
- Rejection of direct scalar work-to-force coupling
"""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestOpenDataCandidateAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/program_evidence_audit/OPEN_DATA_CANDIDATE_AUDIT_RESULTS.json"
        cls.report_path = ROOT / "research/program_evidence_audit/OPEN_DATA_CANDIDATE_AUDIT_REPORT.md"
        cls.script_path = ROOT / "research/program_evidence_audit/run_open_data_candidate_audit.py"

        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))

    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertTrue(self.script_path.is_file())

    def test_schema_and_metadata(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0134")
        self.assertIn("FND-0130", self.res["findings"])
        self.assertIn("NEG-0114", self.res["negative_results"])
        self.assertIn("DEC-0033", self.res["decisions"])
        self.assertEqual(self.res["coupling_verdict"], "DIRECT_SCALAR_WORK_TO_FORCE_COUPLING_PERMANENTLY_REJECTED")

    def test_norbury_empirical_recovery_checkpoint(self):
        c = self.res["candidates_evaluated"]
        n = c["SRC-0111_Norbury_2020"]
        self.assertEqual(n["access_status"], "FULLY_OPEN_VERIFIED")
        self.assertEqual(n["cohort_size"], 12)
        self.assertEqual(n["observations"], 24)

        rec = n["exact_empirical_recovery_pct"]
        self.assertAlmostEqual(rec["5m"], 91.01, places=1)
        self.assertAlmostEqual(rec["45m_overall"], 93.34, places=1)
        self.assertAlmostEqual(rec["45m_LL"], 93.01, places=1)
        self.assertAlmostEqual(rec["45m_HL"], 93.67, places=1)
        self.assertAlmostEqual(rec["24h_overall"], 99.10, places=1)
        self.assertAlmostEqual(rec["24h_LL"], 99.35, places=1)
        self.assertAlmostEqual(rec["24h_HL"], 98.85, places=1)
        self.assertAlmostEqual(rec["24h_ratio_of_means"], 99.04, places=1)

        mae = n["loso_mae_45m_N"]
        self.assertAlmostEqual(mae["mean_retention_baseline"], 46.49, places=1)
        self.assertAlmostEqual(mae["volume_linear_model"], 50.86, places=1)
        self.assertAlmostEqual(mae["dmae_N"], -4.38, places=2)

    def test_jutlah_sprint_rest_baseline(self):
        c = self.res["candidates_evaluated"]
        j = c["SRC-0040_Jutlah_2026"]
        self.assertEqual(j["access_status"], "FULLY_OPEN_VERIFIED")
        self.assertEqual(j["cohort_size"], 21)
        self.assertEqual(j["observations"], 567)
        self.assertIn("strictly includes only sprints prior", j["work_accumulation_audit"])

        mae = j["loso_mae_W"]
        self.assertAlmostEqual(mae["sprint_index_baseline"], 89.23, places=1)
        self.assertAlmostEqual(mae["sprint_plus_rest_baseline"], 89.83, places=1)
        self.assertAlmostEqual(mae["cumulative_work_linear_model"], 88.70, places=1)
        self.assertAlmostEqual(mae["work_plus_rest_duration_model"], 89.48, places=1)
        self.assertAlmostEqual(mae["sprint_rest_and_work_model"], 91.98, places=1)

    def test_candidate_statuses(self):
        c = self.res["candidates_evaluated"]
        self.assertEqual(c["SRC-0102_de_Poli_2026"]["access_status"], "REQUEST_ONLY_BLOCKED")
        self.assertEqual(c["SRC-0112_Plantarflexion_Zenodo_15679911"]["access_status"], "DATA_BLOCKED_BY_QUALITY_GATE")
        self.assertEqual(c["SRC-0101_Souron_2024"]["access_status"], "PARTIALLY_OPEN_VARIABLE_BLOCKED")
        self.assertEqual(c["SRC-0104_Kudzia_2024"]["access_status"], "ARCHIVE_EMPTY_BLOCKED")


if __name__ == "__main__":
    unittest.main()
