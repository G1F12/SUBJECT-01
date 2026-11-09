#!/usr/bin/env python3
"""
SUBJECT-01 — Unit Tests for Evidence Gate V2
Enforces strict provenance validation, cryptographic byte SHA256 checks,
negative testing battery, and epistemic boundaries.
"""

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from verify_data_provenance import (
    audit_dataset_provenance_records,
    audit_registry_experiments,
    audit_validation_scripts,
    audit_structured_experiment_results,
    audit_strict_json_rfc8259,
    audit_negative_tests
)

class TestEvidenceGateV2(unittest.TestCase):
    
    def test_positive_dataset_provenance(self):
        """Verify empirical dataset records satisfy Evidence Gate V2."""
        problems = audit_dataset_provenance_records()
        self.assertEqual(problems, [], f"Dataset provenance violations: {problems}")
        
    def test_positive_registry_experiments(self):
        """Verify registry experiments statuses align with empirical vs synthetic reality."""
        problems = audit_registry_experiments()
        self.assertEqual(problems, [], f"Registry experiment violations: {problems}")
        
    def test_positive_validation_scripts(self):
        """Verify validation scripts contain no fake empirical ground truths."""
        problems = audit_validation_scripts()
        self.assertEqual(problems, [], f"Validation script violations: {problems}")
        
    def test_positive_structured_results(self):
        """Verify cross-cycle structured experiment results and CPE45 energy bounds."""
        problems = audit_structured_experiment_results()
        self.assertEqual(problems, [], f"Structured results violations: {problems}")

    def test_positive_strict_json(self):
        """Verify repository JSON files strictly adhere to RFC 8259 (no Infinity/NaN)."""
        problems = audit_strict_json_rfc8259()
        self.assertEqual(problems, [], f"Strict JSON RFC 8259 violations: {problems}")
        
    def test_negative_battery_wrong_sha256(self):
        """Negative test: Intentionally wrong SHA256 must be detected."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('wrong_sha256_caught', False))
        
    def test_negative_battery_missing_file(self):
        """Negative test: Missing source_file must be detected."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('missing_file_caught', False))
        
    def test_negative_battery_dummy_hash(self):
        """Negative test: Dummy 'N/A' hash on file must be detected."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('forbidden_dummy_hash_caught', False))
        
    def test_negative_battery_synthetic_empirical_claim(self):
        """Negative test: Synthetic data claiming EXTERNALLY_VALIDATED must be blocked."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('synthetic_empirical_claim_caught', False))
        
    def test_negative_battery_conflated_participants(self):
        """Negative test: Equating raters with independent biological subjects must be blocked."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('conflated_participants_caught', False))

    def test_negative_battery_tampered_published_table_sha(self):
        """Negative test: Tampered SHA256 on PUBLISHED_TABLE_DATA must be detected."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('tampered_published_table_sha_caught', False))

    def test_negative_battery_strict_json(self):
        """Negative test: Non-standard token Infinity in JSON must be detected."""
        neg_results = audit_negative_tests()
        self.assertTrue(neg_results.get('strict_json_inf_caught', False))

if __name__ == '__main__':
    unittest.main()
