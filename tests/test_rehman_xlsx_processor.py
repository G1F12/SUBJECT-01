# -*- coding: utf-8 -*-
"""
Tests for Rehman 2024 Actual XLSX Processor (Evidence Gate V2 & Negative Test Battery).
Verifies:
1. Status PENDING_RAW_DATA when raw file is absent.
2. Negative test: SHA256 mismatch rejection.
3. Negative test: Empty workbook rejection.
4. Negative test: Missing/wrong trial sheet rejection.
5. Negative test: Corrupted column / non-numeric data rejection.
6. Negative test: Incomplete trial points rejection (< 20 points).
7. Negative test: Wrong min-to-sec conversion / wrong sampling resolution rejection.
8. Negative test: Chemical shift δppm mistakenly used as amplitude rejection.
9. Negative test: Missing Pi column rejection.
10. Negative test: Non-existent pH must NOT be substituted with fake constant (e.g. 7.0).
11. Negative test: Non-monotonic spectra ordering rejection.
12. Negative test: Non-uniform time sampling intervals rejection.
13. Negative test: Strict prohibition of cross-subject LOSO on N=1 participant.
14. Unit test: Exact real Dryad XLSX headers ('1.Spectra ', '1.Time, min', '1.PCr δppm', '1. PCr signal amplitude', '1. Pi δppm', '1. Pi signal amplitude', etc.).
15. Synthetic fixture parsing with monoexponential kinetics and confidence intervals.
16. Prohibition of claiming PROCESSED_PRIMARY_RAW_XLSX for synthetic test fixtures.
17. Real data end-to-end processing test (if file is present on disk).
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
    validate_cross_subject_loso_applicability,
    calculate_ph_from_chemical_shifts,
    find_rehman_xlsx,
    RehmanProcessingError,
    Sha256MismatchError,
    EmptyWorkbookError,
    MissingTrialSheetError,
    CorruptedColumnError,
    IncompleteTrialDataError,
    LosoProhibitedError,
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
            for t in range(0, 150, 6):
                rows.append([float(t), "CORRUPTED_NON_NUMERIC_TEXT", 5.0, 7.0])
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
            # Only 5 points (less than required 20)
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi", "pH"]]
                for i in range(5):
                    rows.append([float(i * 6.0), 100.0, 5.0, 7.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(IncompleteTrialDataError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_INCOMPLETE")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_07_negative_wrong_min_to_sec_conversion(self):
        """If time step is 0.1 s instead of 6.0 s (e.g. not converted from min), must raise IncompleteTrialDataError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            # Headers explicitly say seconds, but values step by 0.1
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi"]]
                for i in range(25):
                    rows.append([float(i * 0.1), 100.0, 20.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(IncompleteTrialDataError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_WRONG_DT")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_08_negative_pcr_shift_as_amplitude(self):
        """If chemical shifts (e.g. -2.54 ppm) are erroneously supplied as PCr amplitude, must raise CorruptedColumnError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi"]]
                for i in range(25):
                    # Negative ppm values passed as amplitude
                    rows.append([float(i * 6.0), -2.54, 2.26])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(CorruptedColumnError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_SHIFT_AS_AMP")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_09_negative_missing_pi(self):
        """Table missing Pi column must be rejected with CorruptedColumnError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr"]] # Pi missing!
                for i in range(25):
                    rows.append([float(i * 6.0), 100.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(CorruptedColumnError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_MISSING_PI")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_10_negative_nonexistent_ph_no_fake_constant(self):
        """When pH column and shifts are absent, pH must be None and NOT substituted with fake constant (e.g. 7.0)."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi"]] # No pH column and no shift columns
                for i in range(25):
                    rows.append([float(i * 6.0), 100.0, 20.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            sheets = read_xlsx_sheets(tmp_path)
            res = inspect_and_extract_sheets_dict(sheets, source_label="TEST_NO_PH")
            
            for t in res["trials"]:
                self.assertEqual(t["ph_status"], "NOT_DERIVED_FROM_AVAILABLE_SIGNALS")
                self.assertIsNone(t["ph_control"])
                self.assertIsNone(t["ph_end_exercise"])
                self.assertIsNone(t["ph_end_recovery"])
                self.assertTrue(all(v is None for v in t["time_series"]["ph_profile"]))
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_11_negative_wrong_spectra_order(self):
        """Non-monotonic or scrambled spectra order must raise IncompleteTrialDataError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Spectra", "Time (s)", "PCr", "Pi"]]
                for i in range(25):
                    # Inverted spectra order
                    rows.append([25 - i, float(i * 6.0), 100.0, 20.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(IncompleteTrialDataError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_WRONG_SPECTRA")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_12_negative_non_uniform_time_intervals(self):
        """Non-uniform time intervals (e.g. irregular steps) must raise IncompleteTrialDataError."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi"]]
                t_cur = 0.0
                for i in range(25):
                    t_cur += 6.0 if i % 2 == 0 else 18.0 # irregular steps!
                    rows.append([t_cur, 100.0, 20.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            with self.assertRaises(IncompleteTrialDataError):
                sheets = read_xlsx_sheets(tmp_path)
                inspect_and_extract_sheets_dict(sheets, source_label="TEST_NON_UNIFORM_TIME")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_13_prohibit_cross_subject_loso(self):
        """Calling cross-subject LOSO validation on N=1 must raise LosoProhibitedError."""
        with self.assertRaises(LosoProhibitedError):
            validate_cross_subject_loso_applicability(1)
            
        # N=0 should also be rejected
        with self.assertRaises(LosoProhibitedError):
            validate_cross_subject_loso_applicability(0)

    def test_14_exact_real_dryad_headers_parsing(self):
        """
        Verify exact 18-column header block parsing as found in 2024_829_Ergometer_Dryad_Raw_V3.xlsx:
        '1.Spectra ', '1.Time, min', '1.PCr δppm', '1. PCr signal amplitude', '1. Pi δppm', '1. Pi signal amplitude',
        '2. Spectra', '2. Time, min', '2. PCr δppm', '2. PCr signal amplitude', '2. Pi δppm', '2. Pi signal amplitude',
        '3. Spectra', '3. Time, min', '3. PCr δppm', '3. PCr signal amplitude', '3. Pi δppm', '3. Pi signal amplitude'
        """
        exact_headers = [
            '1.Spectra ', '1.Time, min', '1.PCr \u03b4ppm', '1. PCr signal amplitude', '1. Pi \u03b4ppm', '1. Pi signal amplitude',
            '2. Spectra', '2. Time, min', '2. PCr \u03b4ppm', '2. PCr signal amplitude', '2. Pi \u03b4ppm', '2. Pi signal amplitude',
            '3. Spectra', '3. Time, min', '3. PCr \u03b4ppm', '3. PCr signal amplitude', '3. Pi \u03b4ppm', '3. Pi signal amplitude'
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            rows = [exact_headers]
            # Row 1: spectrum 1 has None for signals (as in real file)
            row_1 = [1, 0.1, None, None, None, None, 1, 0.1, None, None, None, None, 1, 0.1, None, None, None, None]
            rows.append(row_1)
            
            # Rows 2..75: 74 spectra (0.2 to 7.5 min)
            for s_idx in range(2, 76):
                t_min = round(s_idx * 0.1, 2)
                row = []
                for tid in [1, 2, 3]:
                    # nadir around 144s (spec 24) or 108s (spec 18)
                    nadir_s = 24 if tid == 1 else 18
                    if s_idx <= 8:
                        pcr = 2000.0
                    elif s_idx <= nadir_s:
                        pcr = 2000.0 - 500.0 * ((s_idx - 8) / (nadir_s - 8))
                    else:
                        t_rec = (s_idx - nadir_s) * 6.0
                        pcr = 1500.0 + 500.0 * (1.0 - np.exp(-0.025 * t_rec))
                    row.extend([s_idx, t_min, -2.54, float(pcr), 2.26, 200.0])
                rows.append(row)
                
            create_test_xlsx(tmp_path, {"2024_829_DiB_Raw": rows})
            sheets = read_xlsx_sheets(tmp_path)
            res = inspect_and_extract_sheets_dict(sheets, source_label="EXACT_HEADER_TEST")
            
            self.assertEqual(res["n_biological_participants"], 1)
            self.assertEqual(res["n_trials"], 3)
            self.assertEqual(res["total_spectra_extracted"], 222) # 74 valid spectra * 3 trials
            
            for t in res["trials"]:
                self.assertEqual(t["ph_status"], "DERIVED_FROM_CHEMICAL_SHIFTS")
                self.assertIsNotNone(t["ph_control"])
                self.assertIsNotNone(t["ph_end_exercise"])
                self.assertGreater(t["ph_control"], 6.5)
                self.assertLess(t["ph_control"], 7.5)
                self.assertGreater(t["kinetic_fit"]["fit_r_squared"], 0.95)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_15_synthetic_fixture_parser_success(self):
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
                self.assertIsNotNone(fit["k_min_minus_1_ci95"])
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

    def test_16_synthetic_fixture_never_claims_production_success(self):
        """Synthetic fixture processing must NEVER return PROCESSED_PRIMARY_RAW_XLSX."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            sheets_data = {}
            for tid in [1, 2, 3]:
                rows = [["Time (s)", "PCr", "Pi", "pH"]]
                for i in range(25):
                    rows.append([float(i * 6.0), 100.0, 5.0, 7.0])
                sheets_data[f"Trial {tid}"] = rows
            create_test_xlsx(tmp_path, sheets_data)
            
            res = execute_pipeline(tmp_path, allow_synthetic_fixture=True)
            self.assertNotEqual(res["status"], "PROCESSED_PRIMARY_RAW_XLSX")
            self.assertEqual(res["provenance_type"], "SYNTHETIC_FIXTURE_PARSER_TEST_ONLY")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_17_real_data_end_to_end_if_present(self):
        """If real 2024_829_Ergometer_Dryad_Raw_V3.xlsx is present, verify full end-to-end extraction."""
        real_file = find_rehman_xlsx()
        if real_file is None:
            self.skipTest("Real Rehman XLSX not found on disk; skipping production end-to-end test.")
            
        res = execute_pipeline(real_file, allow_synthetic_fixture=False)
        self.assertEqual(res["status"], "PROCESSED_PRIMARY_RAW_XLSX")
        self.assertTrue(res["available"])
        
        metrics = res["extracted_metrics"]
        self.assertEqual(metrics["n_biological_participants"], 1)
        self.assertEqual(metrics["n_trials"], 3)
        self.assertEqual(metrics["total_spectra_extracted"], 222)
        
        # Verify k rates match published within 5%
        for t in metrics["trials"]:
            pub_comp = t["published_table1_comparison"]
            self.assertLess(pub_comp["discrepancy_k_pct"], 5.0)
            self.assertGreater(t["kinetic_fit"]["fit_r_squared"], 0.95)
            self.assertEqual(t["ph_status"], "DERIVED_FROM_CHEMICAL_SHIFTS")
            
        # Verify repeatability CV < 10%
        rep = metrics["repeatability_analysis"]
        self.assertLess(rep["k_cv_pct"], 10.0)


if __name__ == '__main__':
    unittest.main()
