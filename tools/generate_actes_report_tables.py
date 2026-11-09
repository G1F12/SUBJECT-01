#!/usr/bin/env python3
"""
tools/generate_actes_report_tables.py

Programmatically generates and structurally verifies the 18-participant
validation table in CPET_VALIDATION_REPORT.md from canonical actes_validation_results.json.
Guarantees permanent 1:1 mathematical alignment without manual copy-paste errors.

Governing Standard: Evidence Gate V2.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
CYCLE10_DIR = ROOT / "research" / "cpet_cycloergometer_2026_11_09"
REPORT_MD = CYCLE10_DIR / "CPET_VALIDATION_REPORT.md"
RESULTS_JSON = CYCLE10_DIR / "actes_validation_results.json"


def clean_cell(cell: str) -> str:
    """Clean markdown cell formatting (remove asterisks, dollar signs, bold, math)."""
    c = cell.strip()
    c = c.replace("**", "").replace("*", "")
    c = c.replace("$", "").replace("\\", "")
    c = c.replace(",", "")
    return c.strip()


def generate_actes_18_participant_table(data: Dict[str, Any]) -> str:
    """Generate Markdown LOSO Summary Table for all 18 participants directly from canonical JSON."""
    loso = data["loso_cross_validation"]
    folds = loso["folds"]

    lines = [
        "| Subject ID | Sport | Body Mass (kg) | $P_{\\text{max}}$ (W) | $\\dot{V}\\text{O}_{2,\\text{max}}$ (L/min) | Records ($N$) | M0 RMSE | M0 $R^2$ | M1 RMSE | M1 $R^2$ | M2 Pop RMSE | M2 Pop $R^2$ | M2 Allometric RMSE | M2 Allometric $R^2$ |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for f in folds:
        sid = f["test_subject_id"]
        sport = f["sport"]
        w = f["weight_kg"]
        p_max = f["p_max_w"]
        v_max = f["vo2_max_l_min"]
        n_rec = f["n_records"]

        m0 = f["M0_null"]
        m1 = f["M1_empirical_linear"]
        m2_pop = f["M2_dynamic_pop"]
        m2_allo = f["M2_dynamic_allometric"]

        row = (
            f"| **Subj {sid:02d}** | {sport} | {w:.1f} | {p_max:.1f} | {v_max:.3f} | {n_rec:,} "
            f"| ${m0['rmse']:.3f}$ | ${m0['r_squared']:.4f}$ "
            f"| ${m1['rmse']:.3f}$ | ${m1['r_squared']:.4f}$ "
            f"| ${m2_pop['rmse']:.3f}$ | ${m2_pop['r_squared']:.4f}$ "
            f"| **${m2_allo['rmse']:.3f}$** | **${m2_allo['r_squared']:.4f}$** |"
        )
        lines.append(row)

    # Summary Mean and SD rows
    m0_s = loso["M0_null_summary"]
    m1_s = loso["M1_empirical_linear_summary"]
    m2_pop_s = loso["M2_dynamic_pop_summary"]
    m2_allo_s = loso["M2_dynamic_allometric_summary"]

    mean_w = sum(f["weight_kg"] for f in folds) / len(folds)
    mean_p = sum(f["p_max_w"] for f in folds) / len(folds)
    mean_v = sum(f["vo2_max_l_min"] for f in folds) / len(folds)
    mean_rec = round(sum(f["n_records"] for f in folds) / len(folds))

    lines.append(
        f"| **MEAN** | — | **{mean_w:.1f}** | **{mean_p:.1f}** | **{mean_v:.3f}** | **{mean_rec:,}** "
        f"| **${m0_s['rmse_mean']:.3f}$** | **${m0_s['r_squared_mean']:.4f}$** "
        f"| **${m1_s['rmse_mean']:.3f}$** | **${m1_s['r_squared_mean']:.4f}$** "
        f"| **${m2_pop_s['rmse_mean']:.3f}$** | **${m2_pop_s['r_squared_mean']:.4f}$** "
        f"| **${m2_allo_s['rmse_mean']:.3f}$** | **${m2_allo_s['r_squared_mean']:.4f}$** |"
    )

    sd_w = float(json.loads(json.dumps((sum((f["weight_kg"] - mean_w)**2 for f in folds) / len(folds))**0.5)))
    sd_p = float(json.loads(json.dumps((sum((f["p_max_w"] - mean_p)**2 for f in folds) / len(folds))**0.5)))
    sd_v = float(json.loads(json.dumps((sum((f["vo2_max_l_min"] - mean_v)**2 for f in folds) / len(folds))**0.5)))
    sd_rec = round((sum((f["n_records"] - mean_rec)**2 for f in folds) / len(folds))**0.5)

    lines.append(
        f"| **SD** | — | ${sd_w:.1f}$ | ${sd_p:.1f}$ | ${sd_v:.3f}$ | ${sd_rec}$ "
        f"| ${m0_s['rmse_sd']:.3f}$ | ${m0_s['r_squared_sd']:.4f}$ "
        f"| ${m1_s['rmse_sd']:.3f}$ | ${m1_s['r_squared_sd']:.4f}$ "
        f"| ${m2_pop_s['rmse_sd']:.3f}$ | ${m2_pop_s['r_squared_sd']:.4f}$ "
        f"| **${m2_allo_s['rmse_sd']:.3f}$** | **${m2_allo_s['r_squared_sd']:.4f}$** |"
    )

    return "\n".join(lines)


def parse_actes_markdown_table(text: str) -> Dict[int, Dict[str, Any]]:
    """
    Parse the 18-participant LOSO table from Markdown text into a structured dictionary.
    Keys: participant ID (1..18).
    Values: {sport, weight, p_max, vo2_max, n_records, M0, M1, M2_pop, M2_allometric}.
    """
    lines = text.splitlines()
    table_rows = []
    in_table = False

    for i, line in enumerate(lines):
        if "M0 RMSE" in line and "M2 Allometric" in line:
            # Header found; skip header and separator
            for row in lines[i + 2:]:
                srow = row.strip()
                if srow.startswith("|"):
                    table_rows.append(srow)
                else:
                    break
            break

    if not table_rows:
        raise ValueError("LOSO Summary Table not found in Markdown text")

    parsed = {}
    for r in table_rows:
        cells = [clean_cell(c) for c in r.split("|")[1:-1]]
        if len(cells) < 14:
            continue
        sid_match = re.search(r"Subj\s*(\d+)", cells[0])
        if not sid_match:
            continue
        sid = int(sid_match.group(1))

        parsed[sid] = {
            "subject_id": sid,
            "sport": cells[1],
            "weight_kg": float(cells[2]),
            "p_max_w": float(cells[3]),
            "vo2_max_l_min": float(cells[4]),
            "n_records": int(cells[5]),
            "M0": {
                "rmse": float(cells[6]),
                "r_squared": float(cells[7]),
            },
            "M1": {
                "rmse": float(cells[8]),
                "r_squared": float(cells[9]),
            },
            "M2_pop": {
                "rmse": float(cells[10]),
                "r_squared": float(cells[11]),
            },
            "M2_allometric": {
                "rmse": float(cells[12]),
                "r_squared": float(cells[13]),
            },
        }

    return parsed


def verify_actes_structural_consistency(report_text: str, json_data: Dict[str, Any], tol: float = 0.001) -> List[str]:
    """
    Deep structural comparison of all 72 cells (18 participants x 4 models x 2 metrics)
    between parsed Markdown table and canonical JSON.
    Returns list of error descriptions. Empty list = 100% PASS.
    """
    errors = []
    try:
        parsed_table = parse_actes_markdown_table(report_text)
    except Exception as e:
        return [f"Failed to parse ACTES table: {e}"]

    if len(parsed_table) != 18:
        errors.append(f"Expected 18 participants in table, got {len(parsed_table)}")

    folds = {f["test_subject_id"]: f for f in json_data["loso_cross_validation"]["folds"]}

    for sid in range(1, 19):
        if sid not in parsed_table:
            errors.append(f"Missing Subject {sid} in Markdown table")
            continue
        if sid not in folds:
            errors.append(f"Missing Subject {sid} in canonical JSON folds")
            continue

        p_row = parsed_table[sid]
        j_row = folds[sid]

        # Verify demographic / protocol anchors
        if abs(p_row["weight_kg"] - j_row["weight_kg"]) > 0.05:
            errors.append(f"Subj {sid} weight mismatch: MD={p_row['weight_kg']}, JSON={j_row['weight_kg']}")
        if abs(p_row["p_max_w"] - j_row["p_max_w"]) > 0.05:
            errors.append(f"Subj {sid} P_max mismatch: MD={p_row['p_max_w']}, JSON={j_row['p_max_w']}")
        if abs(p_row["vo2_max_l_min"] - j_row["vo2_max_l_min"]) > 0.005:
            errors.append(f"Subj {sid} VO2_max mismatch: MD={p_row['vo2_max_l_min']}, JSON={j_row['vo2_max_l_min']}")
        if p_row["n_records"] != j_row["n_records"]:
            errors.append(f"Subj {sid} N_records mismatch: MD={p_row['n_records']}, JSON={j_row['n_records']}")

        # Verify models across all 4 regimes
        models_to_check = [
            ("M0", "M0_null"),
            ("M1", "M1_empirical_linear"),
            ("M2_pop", "M2_dynamic_pop"),
            ("M2_allometric", "M2_dynamic_allometric"),
        ]

        for md_name, json_name in models_to_check:
            md_rmse = p_row[md_name]["rmse"]
            json_rmse = j_row[json_name]["rmse"]
            if abs(md_rmse - json_rmse) > tol:
                errors.append(f"Subj {sid} {md_name} RMSE: MD={md_rmse:.3f}, JSON={json_rmse:.3f}")

            md_r2 = p_row[md_name]["r_squared"]
            json_r2 = j_row[json_name]["r_squared"]
            if abs(md_r2 - json_r2) > tol:
                errors.append(f"Subj {sid} {md_name} R2: MD={md_r2:.4f}, JSON={json_r2:.4f}")

    return errors


def update_actes_report_markdown(report_path: Path, json_path: Path) -> None:
    """Read canonical JSON, regenerate the 18-participant table, and update CPET_VALIDATION_REPORT.md."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    content = report_path.read_text(encoding="utf-8")

    new_table = generate_actes_18_participant_table(data)

    table_pattern = re.compile(
        r"(\| Subject ID \| Sport \| Body Mass \(kg\) \|.*?\n"
        r"\|:---:.*?\n"
        r"(?:\| .*?\n)+)",
        re.MULTILINE,
    )

    if not table_pattern.search(content):
        raise ValueError("Could not find LOSO Summary Table pattern in CPET_VALIDATION_REPORT.md")

    updated_content = table_pattern.sub(lambda m: new_table + "\n", content, count=1)
    report_path.write_text(updated_content, encoding="utf-8")
    print(f"Successfully updated {report_path} with 100% canonical JSON values.")


if __name__ == "__main__":
    update_actes_report_markdown(REPORT_MD, RESULTS_JSON)
    # Verify immediately
    rep_text = REPORT_MD.read_text(encoding="utf-8")
    js_data = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    errs = verify_actes_structural_consistency(rep_text, js_data)
    if errs:
        print(f"FAILED verification with {len(errs)} errors:\n" + "\n".join(errs[:10]))
    else:
        print("VERIFICATION SUCCESS: All 72 subject x model cells match canonical JSON perfectly!")
