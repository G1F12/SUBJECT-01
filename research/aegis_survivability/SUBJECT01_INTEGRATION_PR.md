# SUBJECT-01 Integration Pull Request Specification
**Target Repository:** `D:\SUBJECT-01`  
**Integration Path:** `research/aegis_survivability/`  
**Source Branch:** `research/cycle-4b-external-validation` (`D:\AEGIS-01`)  
**Target Branch:** `main` (via clean, isolated packaging)  
**Status:** Ready for Review / Non-Destructive Isolated Package  

---

## 1. Description of Changes

This Pull Request provides the complete, independently validated **AEGIS-01 Survivability & Biological Architecture Research Package** for isolated inclusion within the SUBJECT-01 repository under `research/aegis_survivability/`.

### What This PR Includes:
1. **14 Computational Simulation Models (`aegis/`):**
   - Covering tissue puncture/cutting mechanics, multilayer acoustic wave attenuation, neural latency, ballistic energy transfer (BABT), hemodynamic stability, oncogenic cell division limits, biomaterials comparative mechanics, multi-scale tissue regeneration, CPE45 thermoregulatory integration, Pareto optimization, biological materials evidence matrices, functional multi-axis regeneration, and three-tier architectural categorization.
   - Fully audited in Cycle 4B: First-law thermodynamic energy balance verified ($\Delta \dot{E} < 10^{-12}\text{ W}$), Atkins draw slicing formula parameterized for knife wedge vs razor scalpel geometry, and clinical VML/PEG parameters rigorously tagged.
2. **Independent External Validation Engine (`aegis/external_validation.py`):**
   - Evaluates three independent empirical validation tracks (Dziki 2016 human VML IPD, Wang/Chen/Silver biological materials mechanical coupons, ISO 7933:2023 Predicted Heat Strain thermoregulatory benchmarks).
   - Generates canonical `data/results/independent_validation_matrix.json`.
3. **Comprehensive Automated Test Suite (`tests/`):**
   - 108 unit and integration tests passing in $1.57\text{ seconds}$ ($100\%$ pass rate).
   - Includes regression tests for external validation, cross-repo registry zero-collision checks, and physical conservation laws.
4. **Synchronized Research Registries (`registry/`):**
   - 7 canonical registries (`hypotheses.json`, `experiments.json`, `findings.json`, `negative_results.json`, `decisions.json`, `issues.json`, `sources.json`) with **strictly zero ID collisions** against SUBJECT-01.
5. **Scientific Reports & Invalidation Registers:**
   - Formal retraction log (`INVALIDATED_CLAIMS.md`), Cycle 4B master report, numerical audit, and external validation dossiers.

---

## 2. Non-Destructive Packaging Protocol

To ensure that active development work in `D:\SUBJECT-01` (specifically the uncommitted changes on branch `fix/ci-failure-and-real-data-pipeline-repair`) is **never touched, overwritten, or clobbered**:
- **Isolation Boundary:** All files are strictly contained within `D:\SUBJECT-01\research\aegis_survivability\`.
- **Zero Host Mutation:** No root configuration files (`pyproject.toml`, `.github/workflows`, root tests, or core packages in `SUBJECT-01`) are modified.
- **Independent Execution:** The package contains its own test runner and dependencies, executable directly via:
  ```bash
  pytest research/aegis_survivability/tests/
  python research/aegis_survivability/aegis/run_all.py
  ```

---

## 3. Pre-Merge Verification Checklist

- [x] **Zero Cross-Repo ID Collisions:** Verified via `tests/test_cross_repo_registry.py` (0 collisions across all 7 registries).
- [x] **Zero Broken Cross-References:** All findings, negative results, and hypotheses resolve to valid IDs.
- [x] **108/108 Tests Passing:** Executed with pytest 9.2.0 on Python 3.12.
- [x] **First Law Energy Conservation:** $\Delta \dot{E} < 10^{-12}\text{ W}$ verified across all thermal regimes.
- [x] **Invalidated Claims Formally Retracted:** `INV-0015` (Dziki 78.4% volume fill) and `INV-0016` (Atkins 0.20 multiplier) documented in `INVALIDATED_CLAIMS.md`.
- [x] **Git Bundle Generated:** `AEGIS_CYCLE4B.bundle` prepared for canonical git import.
- [x] **Isolated Working Tree Protected:** No git reset, checkout, or overwrite executed outside `research/aegis_survivability/`.

---

## 4. Verification Instructions for SUBJECT-01 Reviewers

To independently verify the integration package within `D:\SUBJECT-01`:

```bash
# 1. Run the isolated test suite
cd D:\SUBJECT-01
pytest research/aegis_survivability/tests/

# 2. Run the external validation engine
python research/aegis_survivability/aegis/external_validation.py

# 3. Verify master pipeline execution
python research/aegis_survivability/aegis/run_all.py

# 4. Confirm zero working tree modifications to host SUBJECT-01 files
git status --porcelain
# (Ensure only research/aegis_survivability/ files are staged)
```
