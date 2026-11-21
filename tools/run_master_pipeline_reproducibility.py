#!/usr/bin/env python3
"""Master pipeline reproducibility runner for SUBJECT-01.

Executes and verifies the full end-to-end evidence and validation pipeline:
1. Repository registry and data provenance validation (tools/validate_repository.py)
2. Foundation model isolated execution and CSV dataset reproduction (tools/reproduce_foundation.py)
3. Open data Link 1 verification: Force -> Motion -> Tissue limits (EXP-0129)
4. Open data Link 2 verification: Work done -> Residual force -> Recovery (EXP-0130)
5. Open data Link 3 verification: ADAPT25, speed, motor control, CPE45 (EXP-0131)
6. Architecture A master evidence synthesis & report generation (EXP-0132)
7. Full pytest test suite across all suites
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_stage(name: str, cmd: list, cwd: Path = ROOT) -> tuple[bool, float, str]:
    print(f"\n{'='*70}\n[STAGE] {name}\nCommand: {' '.join(str(c) for c in cmd)}\n{'='*70}")
    t0 = time.time()
    env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)
    dt = time.time() - t0
    
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
        
    success = (proc.returncode == 0)
    status_str = "PASS" if success else f"FAIL (exit {proc.returncode})"
    print(f"--> {name}: {status_str} in {dt:.2f}s")
    return success, dt, proc.stderr if not success else ""


def main():
    print(f"Starting SUBJECT-01 Master Pipeline Reproducibility Suite...")
    print(f"Repository Root: {ROOT}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version.split()[0]} on {sys.platform}")

    stages = [
        ("1. Validate Repository & Checksums", [sys.executable, "tools/validate_repository.py"]),
        ("2. Foundation Model Reproduction", [sys.executable, "tools/reproduce_foundation.py"]),
        ("3. Link 1 Open Data Audit (EXP-0129)", [
            sys.executable, "research/program_evidence_audit/run_open_data_link1_force_tissue.py"
        ]),
        ("4. Link 2 Open Data Audit (EXP-0130)", [
            sys.executable, "research/program_evidence_audit/run_open_data_link2_work_recovery.py"
        ]),
        ("5. Link 3 Open Data Audit (EXP-0131)", [
            sys.executable, "research/program_evidence_audit/run_open_data_link3_adapt25_cpe45.py"
        ]),
        ("6. Decisive Work-to-Force Test (EXP-0133)", [
            sys.executable, "research/program_evidence_audit/run_work_force_decisive_test.py"
        ]),
        ("7. Architecture A Master Synthesis (EXP-0132)", [
            sys.executable, "research/architecture_a_integration/run_architecture_a_evidence_synthesis.py"
        ]),
        ("8. Full Pytest Test Suite", [sys.executable, "-m", "pytest", "tests/"]),
    ]

    summary = []
    overall_success = True

    for name, cmd in stages:
        ok, dt, err = run_stage(name, cmd)
        summary.append((name, ok, dt, err))
        if not ok:
            overall_success = False
            print(f"\n[CRITICAL] Stage '{name}' failed! Stopping pipeline.")
            break

    print(f"\n{'='*70}\nMASTER PIPELINE REPRODUCIBILITY SUMMARY\n{'='*70}")
    for name, ok, dt, err in summary:
        status_tag = "[PASS]" if ok else "[FAIL]"
        print(f"{status_tag:8} {name:<45} ({dt:.2f}s)")
        if not ok and err:
            print(f"         Error detail: {err.strip()[:200]}")

    if overall_success:
        print(f"\nALL {len(summary)} PIPELINE STAGES PASSED SUCCESSFULLY (Bit-for-Bit & Schema Verified).")
        sys.exit(0)
    else:
        print(f"\nPIPELINE FAILED AT ONE OR MORE STAGES.")
        sys.exit(1)


if __name__ == "__main__":
    main()
