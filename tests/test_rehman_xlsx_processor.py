# -*- coding: utf-8 -*-
"""
Tests for Rehman 2024 Actual XLSX Processor (Evidence Gate V2 & Negative Test Battery).
Verifies:
1. Status PENDING_RAW_DATA when raw file is absent.
2. Negative test: SHA256 mismatch rejection.
3. Negative test: Empty workbook rejection.
4. Negative test: Missing/wrong trial sheet rejection.
5. Negative test: Corrupted column / non-numeric data rejection.
6. Negative test: Incomplete trial points rejection.
7. Synthetic fixture parsing with monoexponential kinetics and confidence intervals.
8. Strict prohibition of cross-subject LOSO on N=1 participant.
9. Prohibition of claiming PROCESSED_PRIMARY_RAW_XLSX for synthetic test fixtures.
"""

import unittest
import tempfile
import json
from pathlib import Path
import numpy as np

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from rehman_ooxml import create_test_xlsx, read_xlsx_sheets
from process_rehman_xlsx import (
    execute_pipeline,
    inspect_and_extract_sheets_dict,
    fit_monoexponential_kinetics,
    RehmanProcessingError,
    Sha256MismatchError,
    EmptyWorkbookError,
    MissingTrialSheetError,
    CorruptedColumnError,
    IncompleteTrialDataError,
    EXPECTED_SHA256,
    PUBLISHED_TABLE1_METRICS
)

class TestRehmanXlsxProcessor(unittest.TestCase):

    def test_01_pending_status_when_raw_file_absent(self):
        """When target raw XLSX is absent, returns PENDING_RAW_DATA without false pass."""
        non_existent = ROOT / "non_existent_rehman_raw_file.xlsx"
        res = execute_pipeline(non_existent)
        self.assertEqual(res["status"], "PENDING_RAW_DATA")
        self.assertFalse(res["available"])
        self.assertIn("programmatic_blocker", res)
        self.assertIn("owner_assisted_workflow", res)

    def test_02_negative_sha256_mismatch(self):
        """Candidate file with non-matching SHA256 must be rejected with Sha256MismatchError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp.write(b"NOT_THE_REAL_DRYAD_RAW_XLSX_BYTES")
            tmp_path = Path(tmp.name)
            
        try:
            with self.assertRaises(Sha256MismatchError):
                execute_pipeline(tmp_path, allow_synthetic_fixture=False)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_03_negative_empty_workbook(self):
        """Empty workbook with no data rows must raise EmptyWorkbookError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            create_test_xlsx(tmp_path, {"EmptySheet": []})
            with self.assertRaises(EmptyWorkbookError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_EMPTY")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_04_negative_missing_trial_sheets(self):
        """Workbook with non-trial sheets and no identifiable columns must raise MissingTrialSheetError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            data = {"RandomMetadata": [["Note", "Value"], ["Subject", "None"]]}
            create_test_xlsx(tmp_path, data)
            with self.assertRaises((MissingTrialSheetError, EmptyWorkbookError)):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_WRONG_SHEET")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_05_negative_corrupted_columns(self):
        """Worksheet with non-numeric text in numeric data rows must raise CorruptedColumnError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            rows = [["Time (s)", "PCr", "Pi", "pH"]]
            for t in range(0, 120, 6):
                rows.append([t, "CORRUPTED_NON_NUMERIC_TEXT", 5.0, 7.0])
            create_test_xlsx(tmp_path, {"Trial 1": rows, "Trial 2": rows, "Trial 3": rows})
            with self.assertRaises(CorruptedColumnError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_CORRUPTED")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_06_negative_incomplete_trials(self):
        """Worksheet with fewer than required points must raise IncompleteTrialDataError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            # Only 5 points (less than required ~70)
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi", "pH"]]
                for i in range(5):
                    rows.append([i * 6.0, 100.0, 5.0, 7.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(IncompleteTrialDataError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_INCOMPLETE")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_07_synthetic_fixture_parser_success(self):
        """
        Explicitly labeled synthetic test fixture is correctly parsed:
        - 3 trials extracted
        - monoexponential recovery kinetics fitted with confidence intervals
        - comparison with published rate constants logged
        - technical repeatability evaluated
        - cross-subject LOSO strictly prohibited
        """
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            # Create 3 trials matching paper dynamics
            # 75 spectra at 6s resolution: 0 to 444s
            # 0..42s = exercise (drop 25-30%), 42..402s = recovery (exponential rise)
            time_s = np.arange(0, 75 * 6, 6) # 75 points
            k_rates_min = [1.43, 1.62, 1.53]
            sheets_data = {}
            
            for tid, k_pub in enumerate(k_rates_min, start=1):
                rows = [["Time (s)", "PCr", "Pi", "pH"]]
                k_sec = k_pub / 60.0
                pcr_rest = 100.0
                pcr_drop = 27.0
                pcr_end = pcr_rest - pcr_drop
                
                for t in time_s:
                    if t <= 42.0:
                        pcr_val = pcr_rest - (pcr_drop * (t / 42.0))
                        ph_val = 7.00 + 0.02 * (t / 42.0)
                    else:
                        t_rec = t - 42.0
                        pcr_val = pcr_end + pcr_drop * (1.0 - np.exp(-k_sec * t_rec))
                        ph_val = 7.02 - 0.03 * (1.0 - np.exp(-k_sec * t_rec))
                    pi_val = 120.0 - pcr_val
                    rows.append([float(t), float(pcr_val), float(pi_val), float(ph_val)])
                sheets_data[f"Trial {tid}"] = rows
                
            create_test_xlsx(tmp_path, sheets_data)
            
            res = execute_pipeline(tmp_path, allow_synthetic_fixture=True)
            self.assertEqual(res["status"], "SYNTHETIC_FIXTURE_PARSED_FOR_UNIT_TEST")
            self.assertEqual(res["provenance_type"], "SYNTHETIC_FIXTURE_PARSER_TEST_ONLY")
            
            metrics = res["extracted_metrics"]
            self.assertEqual(metrics["n_biological_participants"], 1)
            self.assertEqual(metrics["n_trials"], 3)
            self.assertEqual(metrics["total_spectra_extracted"], 225)
            
            # Check trials
            for t_dict in metrics["trials"]:
                fit = t_dict["kinetic_fit"]
                self.assertIsNotNone(fit["k_min_minus_1"])
                self.assertIsNotNone(fit["tau_recovery_s"])
                self.assertGreater(fit["fit_r_squared"], 0.95)
                # Check 95% CI is computed
                self.assertIsNotNone(fit["k_min_minus_1_ci95"])
                # Check comparison
                comp = t_dict["published_table1_comparison"]
                self.assertIsNotNone(comp["published_k_min_minus_1"])
                self.assertLess(comp["discrepancy_k_min_minus_1"], 0.2)
                
            # Check technical repeatability
            rep = metrics["repeatability_analysis"]
            self.assertEqual(rep["type"], "INTRA_SUBJECT_TECHNICAL_TEST_RETEST_REPEATABILITY")
            self.assertGreater(rep["k_mean_min_minus_1"], 1.3)
            self.assertLess(rep["k_mean_min_minus_1"], 1.7)
            
            # Check LOSO policy
            loso = metrics["cross_subject_loso_policy"]
            self.assertFalse(loso["permitted"])
            self.assertIn("prohibited", loso["reason"].lower())
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_08_synthetic_fixture_never_claims_production_success(self):
        """Synthetic fixture processing must NEVER return PROCESSED_PRIMARY_RAW_XLSX."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi", "pH"]]
                for i in range(25):
                    rows.append([i * 6.0, 100.0, 5.0, 7.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            
            res = execute_pipeline(tmp_path, allow_synthetic_fixture=True)
            self.assertNotEqual(res["status"], "PROCESSED_PRIMARY_RAW_XLSX")
            self.assertEqual(res["provenance_type"], "SYNTHETIC_FIXTURE_PARSER_TEST_ONLY")
        finally:
            tmp_path.unlink(missing_ok=True)

if __name__ == '__main__':
    unittest.main()
