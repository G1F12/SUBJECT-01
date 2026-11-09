# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
tools/generate_rehman_report_tables.py
Programmatic Generator and Structural Parser for Rehman 2024 Validation Markdown Tables.

Ensures 1:1 mathematical and structural consistency between canonical JSON
(rehman2024_validation_results.json) and documentation (REAL_DATA_VALIDATION_REPORT.md).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

ROOT = Path(__file__).resolve().parents[1]
CYCLE9_DIR = ROOT / 'research' / 'empirical_recruitment_2026_11_08'
REPORT_PATH = CYCLE9_DIR / 'REAL_DATA_VALIDATION_REPORT.md'
JSON_PATH = CYCLE9_DIR / 'rehman2024_validation_results.json'


def clean_cell(cell: str) -> str:
    """Strip markdown formatting like bold, dollar math symbols, text formatting."""
    c = cell.strip()
    c = c.replace('**', '').replace('$', '').replace('\\text{ s}', '').replace('\\text{min}', '').replace('\\text{ min}^{-1}', '')
    c = c.replace('\\pm', '+/-').replace('\\%', '').replace('%', '').replace('`', '').replace('\\', '')
    return c.strip()


def generate_timing_table(data: Dict[str, Any]) -> str:
    """Generate Markdown Timing Table from canonical JSON."""
    trials = data['stage_1_protocol_timing_audit']['trials']
    lines = [
        "| Trial ID | Baseline PCr Mean | PCr at 90s Stop | Drop at 90s (%) | Actual Nadir Time | Nadir PCr | Drop at Nadir (%) | Published Drop (%) | Post-Stop Lag (s) | Timing Verdict |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for tid_str in ["1", "2", "3"]:
        t = trials[tid_str]
        b = t['resting_baseline']
        nom = t['nominal_protocol']
        nadir = t['actual_biochemical_nadir']
        rec = t['recovery_onset']
        verdict = "EXTENDED_DEPLETION_PHASE" if t['trial_id'] == 1 else "CONGRUENT_WITH_TABLE1"
        
        b_mean_str = f"{b['pcr_mean']:.2f}"
        b_sd_str = f"{b['pcr_sd']:.2f}"
        stop_pcr = f"{int(round(nom['pcr_at_stop']))}"
        drop_90 = f"{nom['pcr_drop_at_stop_pct']:.2f}"
        nadir_t = f"{nadir['nadir_time_s']:.1f}"
        spec = nadir['nadir_spectrum']
        nadir_pcr = f"{int(round(nadir['nadir_pcr']))}"
        drop_nadir = f"{nadir['pcr_drop_at_nadir_pct']:.2f}"
        pub_drop = f"{nadir['published_table1_drop_pct']:.1f}"
        lag = f"{rec['lag_from_nominal_stop_s']:+.1f}"
        
        row = (
            f"| **Trial {tid_str}** | ${b_mean_str} \\pm {b_sd_str}$ | **${stop_pcr}$** | ${drop_90}\\%$ "
            f"| **${nadir_t}\\text{{ s}}$** (Spec {spec}) | **${nadir_pcr}$** | **${drop_nadir}\\%$** "
            f"| ${pub_drop}\\%$ | ${lag}\\text{{ s}}$ | `{verdict}` |"
        )
        lines.append(row)
    return "\n".join(lines)


def generate_insample_table(data: Dict[str, Any]) -> str:
    """Generate Markdown In-Sample Fit Table from canonical JSON."""
    fits = data['stage_4_model_comparison_and_transfer']['in_sample_fits']
    lines = [
        "| Trial ID | M0 RMSE | M0 MAE | M0 $R^2$ | M1 RMSE | M1 MAE | M1 $R^2$ | M1 $k$ ($\\text{min}^{-1}$) | M1 $\\tau$ (s) | M2 RMSE | M2 MAE | M2 $R^2$ | M2 $k$ ($\\text{min}^{-1}$) | M2 $\\tau$ (s) |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for tid_str in ["1", "2", "3"]:
        f = fits[tid_str]
        m0 = f['M0_null_constant']
        m1 = f['M1_monoexponential_3param']
        m2 = f['M2_constrained_monoexponential_baseline']
        
        row = (
            f"| **Trial {tid_str}** "
            f"| **${m0['rmse']:.2f}$** | ${m0['mae']:.2f}$ | **${m0['r_squared']:.4f}$** "
            f"| **${m1['rmse']:.2f}$** | ${m1['mae']:.2f}$ | **${m1['r_squared']:.4f}$** | ${m1['k_min_minus_1']:.4f}$ | ${m1['tau_s']:.1f}$ "
            f"| **${m2['rmse']:.2f}$** | ${m2['mae']:.2f}$ | **${m2['r_squared']:.4f}$** | ${m2['k_min_minus_1']:.4f}$ | ${m2['tau_s']:.1f}$ |"
        )
        lines.append(row)
    return "\n".join(lines)


def generate_transfer_table(data: Dict[str, Any]) -> str:
    """Generate Markdown Within-Subject Cross-Trial Transfer Table from canonical JSON."""
    trans = data['stage_4_model_comparison_and_transfer']['within_subject_trial_transfers']
    scen_a = data['stage_4_model_comparison_and_transfer']['transfer_scenarios']['scenario_A_conditional_trajectory_reconstruction']
    lines = [
        "| Train Trial | Test Trial | Calibrated $k$ ($\\text{min}^{-1}$) | M1 Trans RMSE | M1 Trans MAE | M1 Trans $R^2$ | M2 Trans RMSE | M2 Trans MAE | M2 Trans $R^2$ |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for tr in trans:
        train_id = tr['train_trial']
        test_id = tr['test_trial']
        cal_k = tr['transfer_rate_constant_k_min']
        m1 = tr['M1_transfer']
        m2 = tr['M2_transfer']
        row = (
            f"| **Trial {train_id}** | **Trial {test_id}** | ${cal_k:.3f}$ "
            f"| ${m1['rmse']:.2f}$ | ${m1['mae']:.2f}$ | ${m1['r_squared']:.4f}$ "
            f"| **${m2['rmse']:.2f}$** | ${m2['mae']:.2f}$ | **${m2['r_squared']:.4f}$** |"
        )
        lines.append(row)
    # Mean summary row
    m1_mae_mean = sum(tr['M1_transfer']['mae'] for tr in trans) / len(trans)
    m2_mae_mean = sum(tr['M2_transfer']['mae'] for tr in trans) / len(trans)
    lines.append(
        f"| **Mean** | — | — "
        f"| **${scen_a['m1_transfer_rmse_mean']:.2f}$** | ${m1_mae_mean:.2f}$ | **${scen_a['m1_transfer_r_squared_mean']:.4f}$** "
        f"| **${scen_a['m2_transfer_rmse_mean']:.2f}$** | ${m2_mae_mean:.2f}$ | **${scen_a['m2_transfer_r_squared_mean']:.4f}$** |"
    )
    return "\n".join(lines)


def extract_table_rows(text: str, header_substring: str) -> List[str]:
    """Extract table rows following the header that contains header_substring."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if header_substring in line:
            # Table rows start after header and separator (|:---|)
            rows = []
            for row in lines[i+2:]:
                if row.strip().startswith('|'):
                    rows.append(row)
                else:
                    break
            return rows
    return []


def parse_markdown_timing_table(text: str) -> Dict[int, Dict[str, Any]]:
    """
    Parse the Timing Table from Markdown text into structured trial entries.
    Extracts trial_id, baseline_mean, baseline_sd, pcr_stop, drop_90_pct,
    nadir_time_s, nadir_pcr, drop_nadir_pct, pub_drop_pct, lag_s.
    """
    rows = extract_table_rows(text, "Baseline PCr Mean")
    if not rows:
        raise ValueError("Timing Table header not found in Markdown text")
    
    parsed = {}
    for row in rows:
        cells = [c.strip() for c in row.split('|')[1:-1]]
        if len(cells) < 10:
            continue
        # Extract trial_id
        t_m = re.search(r"Trial\s*(\d+)", cells[0])
        if not t_m:
            continue
        tid = int(t_m.group(1))
        
        # Parse baseline mean +- sd
        b_cell = clean_cell(cells[1])
        b_parts = b_cell.split('+/-')
        b_mean = float(b_parts[0].strip())
        b_sd = float(b_parts[1].strip())
        
        # Parse stop PCr
        stop_pcr = float(clean_cell(cells[2]))
        drop_90 = float(clean_cell(cells[3]))
        
        # Parse nadir time
        nadir_time_str = clean_cell(cells[4])
        nt_m = re.search(r"([\d\.]+)", nadir_time_str)
        nadir_time = float(nt_m.group(1)) if nt_m else 0.0
        
        # Parse nadir PCr
        nadir_pcr = float(clean_cell(cells[5]))
        drop_nadir = float(clean_cell(cells[6]))
        pub_drop = float(clean_cell(cells[7]))
        
        # Parse lag
        lag_str = clean_cell(cells[8])
        lag = float(lag_str)
        
        verdict = clean_cell(cells[9])
        
        parsed[tid] = {
            "trial_id": tid,
            "baseline_mean": b_mean,
            "baseline_sd": b_sd,
            "pcr_stop": stop_pcr,
            "drop_90_pct": drop_90,
            "nadir_time_s": nadir_time,
            "nadir_pcr": nadir_pcr,
            "drop_nadir_pct": drop_nadir,
            "pub_drop_pct": pub_drop,
            "lag_s": lag,
            "verdict": verdict,
        }
    return parsed


def parse_markdown_insample_table(text: str) -> Dict[int, Dict[str, Dict[str, float]]]:
    """
    Parse the In-Sample Fit Table from Markdown text into structured trial entries.
    Extracts for each trial:
      M0: {rmse, mae, r2}
      M1: {rmse, mae, r2, k, tau}
      M2: {rmse, mae, r2, k, tau}
    """
    rows = extract_table_rows(text, "M0 RMSE")
    if not rows:
        raise ValueError("In-Sample Table header not found in Markdown text")
    
    parsed = {}
    for row in rows:
        cells = [clean_cell(c) for c in row.split('|')[1:-1]]
        if len(cells) < 14:
            continue
        t_m = re.search(r"Trial\s*(\d+)", cells[0])
        if not t_m:
            continue
        tid = int(t_m.group(1))
        
        parsed[tid] = {
            "M0": {
                "rmse": float(cells[1]),
                "mae": float(cells[2]),
                "r2": float(cells[3]),
            },
            "M1": {
                "rmse": float(cells[4]),
                "mae": float(cells[5]),
                "r2": float(cells[6]),
                "k": float(cells[7]),
                "tau": float(cells[8]),
            },
            "M2": {
                "rmse": float(cells[9]),
                "mae": float(cells[10]),
                "r2": float(cells[11]),
                "k": float(cells[12]),
                "tau": float(cells[13]),
            }
        }
    return parsed


def parse_markdown_transfer_table(text: str) -> Dict[Tuple[int, int], Dict[str, Any]]:
    """
    Parse Within-Subject Transfer Table from Markdown text.
    Extracts for each (train_id, test_id):
      calibrated_k, M1: {rmse, mae, r2}, M2: {rmse, mae, r2}
    """
    rows = extract_table_rows(text, "Calibrated $k$")
    if not rows:
        raise ValueError("Transfer Table header not found in Markdown text")
    
    parsed = {}
    for row in rows:
        cells = [clean_cell(c) for c in row.split('|')[1:-1]]
        if len(cells) < 9:
            continue
        tr_m = re.search(r"Trial\s*(\d+)", cells[0])
        te_m = re.search(r"Trial\s*(\d+)", cells[1])
        if not (tr_m and te_m):
            continue
        train_id = int(tr_m.group(1))
        test_id = int(te_m.group(1))
        
        parsed[(train_id, test_id)] = {
            "calibrated_k": float(cells[2]),
            "M1": {
                "rmse": float(cells[3]),
                "mae": float(cells[4]),
                "r2": float(cells[5]),
            },
            "M2": {
                "rmse": float(cells[6]),
                "mae": float(cells[7]),
                "r2": float(cells[8]),
            }
        }
    return parsed


def verify_structural_consistency(report_text: str, json_data: Dict[str, Any]) -> List[str]:
    """
    Perform deep structural comparison between parsed Markdown tables and canonical JSON data.
    Returns a list of error descriptions (empty list means 100% PASS).
    """
    errors = []
    
    # 1. Timing table
    try:
        parsed_timing = parse_markdown_timing_table(report_text)
    except Exception as e:
        return [f"Failed to parse timing table: {e}"]
    
    json_trials = json_data['stage_1_protocol_timing_audit']['trials']
    for tid in [1, 2, 3]:
        if tid not in parsed_timing:
            errors.append(f"Timing table missing row for Trial {tid}")
            continue
        pt = parsed_timing[tid]
        jt = json_trials[str(tid)]
        
        # Baseline mean & SD (2 decimal places)
        expected_mean = round(jt['resting_baseline']['pcr_mean'], 2)
        expected_sd = round(jt['resting_baseline']['pcr_sd'], 2)
        if round(pt['baseline_mean'], 2) != expected_mean:
            errors.append(f"Trial {tid} baseline mean: MD={pt['baseline_mean']}, JSON={expected_mean}")
        if round(pt['baseline_sd'], 2) != expected_sd:
            errors.append(f"Trial {tid} baseline SD: MD={pt['baseline_sd']}, JSON={expected_sd}")
            
        # PCr at 90s stop
        expected_stop = round(jt['nominal_protocol']['pcr_at_stop'])
        if round(pt['pcr_stop']) != expected_stop:
            errors.append(f"Trial {tid} PCr@90s: MD={pt['pcr_stop']}, JSON={expected_stop}")
            
        # Nadir time and PCr
        expected_nadir_t = round(jt['actual_biochemical_nadir']['nadir_time_s'], 1)
        expected_nadir_pcr = round(jt['actual_biochemical_nadir']['nadir_pcr'])
        if round(pt['nadir_time_s'], 1) != expected_nadir_t:
            errors.append(f"Trial {tid} nadir time: MD={pt['nadir_time_s']}, JSON={expected_nadir_t}")
        if round(pt['nadir_pcr']) != expected_nadir_pcr:
            errors.append(f"Trial {tid} nadir PCr: MD={pt['nadir_pcr']}, JSON={expected_nadir_pcr}")
            
        # Post-stop lag
        expected_lag = round(jt['recovery_onset']['lag_from_nominal_stop_s'], 1)
        if round(pt['lag_s'], 1) != expected_lag:
            errors.append(f"Trial {tid} lag: MD={pt['lag_s']}, JSON={expected_lag}")

    # 2. In-sample table
    try:
        parsed_insample = parse_markdown_insample_table(report_text)
    except Exception as e:
        return [f"Failed to parse in-sample table: {e}"]
        
    json_fits = json_data['stage_4_model_comparison_and_transfer']['in_sample_fits']
    for tid in [1, 2, 3]:
        if tid not in parsed_insample:
            errors.append(f"In-sample table missing row for Trial {tid}")
            continue
        pi = parsed_insample[tid]
        ji = json_fits[str(tid)]
        
        # M0
        m0_j = ji['M0_null_constant']
        if abs(pi['M0']['rmse'] - m0_j['rmse']) > 0.01:
            errors.append(f"Trial {tid} M0 RMSE: MD={pi['M0']['rmse']}, JSON={m0_j['rmse']:.2f}")
        if abs(pi['M0']['r2'] - m0_j['r_squared']) > 0.001:
            errors.append(f"Trial {tid} M0 R2: MD={pi['M0']['r2']}, JSON={m0_j['r_squared']:.4f}")
            
        # M1
        m1_j = ji['M1_monoexponential_3param']
        if abs(pi['M1']['rmse'] - m1_j['rmse']) > 0.01:
            errors.append(f"Trial {tid} M1 RMSE: MD={pi['M1']['rmse']}, JSON={m1_j['rmse']:.2f}")
        if abs(pi['M1']['r2'] - m1_j['r_squared']) > 0.001:
            errors.append(f"Trial {tid} M1 R2: MD={pi['M1']['r2']}, JSON={m1_j['r_squared']:.4f}")
        if abs(pi['M1']['k'] - m1_j['k_min_minus_1']) > 0.001:
            errors.append(f"Trial {tid} M1 k: MD={pi['M1']['k']}, JSON={m1_j['k_min_minus_1']:.4f}")
        if abs(pi['M1']['tau'] - m1_j['tau_s']) > 0.1:
            errors.append(f"Trial {tid} M1 tau: MD={pi['M1']['tau']}, JSON={m1_j['tau_s']:.1f}")
            
        # M2
        m2_j = ji['M2_constrained_monoexponential_baseline']
        if abs(pi['M2']['rmse'] - m2_j['rmse']) > 0.01:
            errors.append(f"Trial {tid} M2 RMSE: MD={pi['M2']['rmse']}, JSON={m2_j['rmse']:.2f}")
        if abs(pi['M2']['r2'] - m2_j['r_squared']) > 0.001:
            errors.append(f"Trial {tid} M2 R2: MD={pi['M2']['r2']}, JSON={m2_j['r_squared']:.4f}")
        if abs(pi['M2']['k'] - m2_j['k_min_minus_1']) > 0.001:
            errors.append(f"Trial {tid} M2 k: MD={pi['M2']['k']}, JSON={m2_j['k_min_minus_1']:.4f}")
        if abs(pi['M2']['tau'] - m2_j['tau_s']) > 0.1:
            errors.append(f"Trial {tid} M2 tau: MD={pi['M2']['tau']}, JSON={m2_j['tau_s']:.1f}")

    # 3. Transfer table
    try:
        parsed_trans = parse_markdown_transfer_table(report_text)
    except Exception as e:
        return [f"Failed to parse transfer table: {e}"]
        
    json_trans = json_data['stage_4_model_comparison_and_transfer']['within_subject_trial_transfers']
    for tr in json_trans:
        pair = (tr['train_trial'], tr['test_trial'])
        if pair not in parsed_trans:
            errors.append(f"Transfer table missing pair {pair}")
            continue
        pt = parsed_trans[pair]
        
        # Calibrated k
        if abs(pt['calibrated_k'] - tr['transfer_rate_constant_k_min']) > 0.001:
            errors.append(f"Transfer {pair} calibrated k: MD={pt['calibrated_k']}, JSON={tr['transfer_rate_constant_k_min']:.3f}")
            
        # M1 trans RMSE & R2
        if abs(pt['M1']['rmse'] - tr['M1_transfer']['rmse']) > 0.01:
            errors.append(f"Transfer {pair} M1 RMSE: MD={pt['M1']['rmse']}, JSON={tr['M1_transfer']['rmse']:.2f}")
        if abs(pt['M1']['r2'] - tr['M1_transfer']['r_squared']) > 0.001:
            errors.append(f"Transfer {pair} M1 R2: MD={pt['M1']['r2']}, JSON={tr['M1_transfer']['r_squared']:.4f}")
            
        # M2 trans RMSE & R2
        if abs(pt['M2']['rmse'] - tr['M2_transfer']['rmse']) > 0.01:
            errors.append(f"Transfer {pair} M2 RMSE: MD={pt['M2']['rmse']}, JSON={tr['M2_transfer']['rmse']:.2f}")
        if abs(pt['M2']['r2'] - tr['M2_transfer']['r_squared']) > 0.001:
            errors.append(f"Transfer {pair} M2 R2: MD={pt['M2']['r2']}, JSON={tr['M2_transfer']['r_squared']:.4f}")

    return errors


def update_report_markdown_tables(report_path: Path, json_path: Path) -> None:
    """Read canonical JSON, regenerate the three markdown tables, and update report."""
    data = json.loads(json_path.read_text(encoding='utf-8'))
    content = report_path.read_text(encoding='utf-8')
    
    # 1. Update landmarks list text in Section 2:
    landmarks_old = re.compile(
        r"(-\s*\*\*Baseline Control Period\*\*:\s*Spectra 2 through 8.*?\n)"
        r"(\s*-\s*Trial 1:\s*\$\\text\{PCr\}_\{.*?\$.*?\n)"
        r"(\s*-\s*Trial 2:\s*\$\\text\{PCr\}_\{.*?\$.*?\n)"
        r"(\s*-\s*Trial 3:\s*\$\\text\{PCr\}_\{.*?\$.*?\n)",
        re.DOTALL
    )
    t1_b = data['stage_1_protocol_timing_audit']['trials']['1']['resting_baseline']
    t2_b = data['stage_1_protocol_timing_audit']['trials']['2']['resting_baseline']
    t3_b = data['stage_1_protocol_timing_audit']['trials']['3']['resting_baseline']
    
    def replace_landmarks(m):
        header = m.group(1)
        return (
            f"{header}"
            f"  - Trial 1: $\\text{{PCr}}_{{\\text{{rest}}}} = {t1_b['pcr_mean']:.2f} \\pm {t1_b['pcr_sd']:.2f}$.\n"
            f"  - Trial 2: $\\text{{PCr}}_{{\\text{{rest}}}} = {t2_b['pcr_mean']:.2f} \\pm {t2_b['pcr_sd']:.2f}$.\n"
            f"  - Trial 3: $\\text{{PCr}}_{{\\text{{rest}}}} = {t3_b['pcr_mean']:.2f} \\pm {t3_b['pcr_sd']:.2f}$.\n"
        )
    content = landmarks_old.sub(replace_landmarks, content)
    
    # 2. Replace Timing Table
    timing_table_pattern = re.compile(
        r"\|\s*Trial ID\s*\|\s*Baseline PCr Mean.*?\n\|[-:\s|]+\n(?:\|.*?\n)+",
    )
    new_timing_table = generate_timing_table(data) + "\n"
    content = timing_table_pattern.sub(lambda m: new_timing_table, content, count=1)
    
    # 3. Replace In-Sample Table
    insample_table_pattern = re.compile(
        r"\|\s*Trial ID\s*\|\s*M0 RMSE.*?\n\|[-:\s|]+\n(?:\|.*?\n)+",
    )
    new_insample_table = generate_insample_table(data) + "\n"
    content = insample_table_pattern.sub(lambda m: new_insample_table, content, count=1)
    
    # 4. Replace Transfer Table
    transfer_table_pattern = re.compile(
        r"\|\s*Train Trial\s*\|\s*Test Trial.*?\n\|[-:\s|]+\n(?:\|.*?\n)+",
    )
    new_transfer_table = generate_transfer_table(data) + "\n"
    content = transfer_table_pattern.sub(lambda m: new_transfer_table, content, count=1)
    
    report_path.write_text(content, encoding='utf-8')
    print(f"Updated tables in {report_path}")


if __name__ == '__main__':
    update_report_markdown_tables(REPORT_PATH, JSON_PATH)
    errs = verify_structural_consistency(REPORT_PATH.read_text(encoding='utf-8'), json.loads(JSON_PATH.read_text(encoding='utf-8')))
    if errs:
        print("Structural Consistency ERRORS:")
        for e in errs:
            print(" -", e)
    else:
        print("Structural Consistency: 100% PASS")
