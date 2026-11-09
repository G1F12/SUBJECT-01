# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
SUBJECT-01 — Rehman et al. 2024 Actual XLSX Acquisition & Processing Pipeline
DOI: 10.5061/dryad.08kprr59v / PMC11617988
Target file: 2024_829_Ergometer_Dryad_Raw_V3.xlsx

Official metadata from Dryad REST API & PMC11617988:
- Size: 18,136 bytes
- SHA256: ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf
- Subjects: N=1 human participant (untrained healthy male volunteer, right quadriceps)
- Repeated trials: 3 distinct experimental trials
- Sampling: 75 spectra per trial, 6-second temporal resolution (0.1 min per spectrum)
- Sheet name: 2024_829_DiB_Raw (18 columns in 3 blocks of 6: 1.*, 2.*, 3.*)
- Measurements: PCr signal amplitude, PCr chemical shift (δppm), Pi signal amplitude, Pi chemical shift (δppm)
- Published Table 1 metrics:
  * Trial 1: PCr drop = 31.6%, k = 1.43 min^-1 (tau = 41.96 s), pH control = 6.97, end_ex = 6.98, end_rec = 6.92
  * Trial 2: PCr drop = 25.2%, k = 1.62 min^-1 (tau = 37.04 s), pH control = 7.02, end_ex = 7.02, end_rec = 7.00
  * Trial 3: PCr drop = 24.8%, k = 1.53 min^-1 (tau = 39.22 s), pH control = 7.01, end_ex = 7.03, end_rec = 6.99
  * Mean +/- SD: PCr drop = 27.2 +/- 3.8%, k = 1.53 +/- 0.10 min^-1 (tau = 39.4 s)

Architectural Invariants & Evidence Gate V2:
1. When real raw XLSX is absent, returns PENDING_RAW_DATA without false success claims.
2. When candidate file is present, verifies exact byte SHA256 (ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf).
3. Inspects real structure of sheets and columns, handling '1.', '2.', '3.' prefixes and greek delta 'δ'.
4. Verifies timestamps (6.0 s) and measurement units; converts minutes to seconds correctly.
5. Verifies monotonic spectra ordering and uniform sampling intervals.
6. Rejects chemical shifts (δppm) passed erroneously as signal amplitudes.
7. Requires inorganic phosphate (Pi) measurements; rejects incomplete tables missing Pi.
8. Calculates intracellular pH strictly from Pi and PCr chemical shifts (PMC11617988 Fig. 7 formula).
   NEVER substitutes an artificial constant (e.g. 7.0). If shifts are missing, preserves pH=null.
9. Dynamically detects exercise nadir (minimum PCr during exercise window); does not assume point 7.
10. Fits monoexponential recovery kinetics on real observations with 95% confidence intervals.
11. Compares calculated rate constants with published k = 1.43, 1.62, 1.53 min^-1 and logs discrepancies.
12. With N=1, evaluates intra-subject technical test-retest repeatability (CV%) but strictly prohibits cross-subject LOSO.
13. Generates canonical derived JSON artifact (rehman2024_extracted_timeseries.json) while keeping raw binary in .gitignore.
"""

from pathlib import Path
import hashlib
import json
import math
import re
import sys
import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[1]
CYCLE9_DIR = ROOT / 'research' / 'empirical_recruitment_2026_11_08'
sys.path.insert(0, str(ROOT / 'tools'))

from rehman_ooxml import read_xlsx_sheets

EXPECTED_FILENAME = "2024_829_Ergometer_Dryad_Raw_V3.xlsx"
EXPECTED_SHA256 = "ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf"
EXPECTED_SIZE_BYTES = 18136

PUBLISHED_TABLE1_METRICS = {
    1: {"pcr_drop_pct": 31.6, "k_min_minus_1": 1.43, "tau_s": 41.96, "ph_ctrl": 6.97, "ph_end_ex": 6.98, "ph_end_rec": 6.92},
    2: {"pcr_drop_pct": 25.2, "k_min_minus_1": 1.62, "tau_s": 37.04, "ph_ctrl": 7.02, "ph_end_ex": 7.02, "ph_end_rec": 7.00},
    3: {"pcr_drop_pct": 24.8, "k_min_minus_1": 1.53, "tau_s": 39.22, "ph_ctrl": 7.01, "ph_end_ex": 7.03, "ph_end_rec": 6.99},
    "mean_sd": {"pcr_drop_pct": 27.2, "pcr_drop_sd": 3.8, "k_min_minus_1": 1.53, "k_sd": 0.10, "tau_s": 39.41}
}

SEARCH_PATHS = [
    CYCLE9_DIR / EXPECTED_FILENAME,
    ROOT / EXPECTED_FILENAME,
    Path.home() / 'Downloads' / EXPECTED_FILENAME
]

class RehmanProcessingError(Exception):
    """Base exception for Rehman XLSX processing errors."""
    pass

class FileMissingError(RehmanProcessingError):
    pass

class Sha256MismatchError(RehmanProcessingError):
    pass

class EmptyWorkbookError(RehmanProcessingError):
    pass

class MissingTrialSheetError(RehmanProcessingError):
    pass

class CorruptedColumnError(RehmanProcessingError):
    pass

class IncompleteTrialDataError(RehmanProcessingError):
    pass

class LosoProhibitedError(RehmanProcessingError):
    pass


def compute_bytes_sha256(filepath: Path) -> str:
    """Compute cryptographic SHA256 digest directly from file bytes."""
    return hashlib.sha256(filepath.read_bytes()).hexdigest()


def find_rehman_xlsx() -> Path | None:
    """Search for the original Rehman XLSX file in candidate directories."""
    for p in SEARCH_PATHS:
        if p.is_file():
            return p
    return None


def calculate_ph_from_chemical_shifts(pi_ppm: float | None, pcr_ppm: float | None) -> float | None:
    """
    Calculate intracellular pH from Pi and PCr chemical shifts using Henderson-Hasselbalch equation
    as published in Rehman et al. 2024 (PMC11617988 Fig. 7 formula):
    delta_o = delta_Pi - delta_PCr
    pH = 6.75 + log10((delta_o - 3.290) / (5.805 - delta_o))
    """
    if pi_ppm is None or pcr_ppm is None:
        return None
    try:
        delta_o = float(pi_ppm) - float(pcr_ppm)
        numerator = delta_o - 3.290
        denominator = 5.805 - delta_o
        if denominator <= 0 or numerator <= 0:
            return None
        val = numerator / denominator
        return float(6.75 + math.log10(val))
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def validate_cross_subject_loso_applicability(n_subjects: int) -> None:
    """
    Strictly prohibit cross-subject leave-one-subject-out (LOSO) on N=1 cohort.
    Raises LosoProhibitedError if n_subjects <= 1.
    """
    if n_subjects <= 1:
        raise LosoProhibitedError(
            f"Cannot perform cross-subject LOSO validation on N={n_subjects} participants. "
            "Rehman et al. 2024 dataset contains only N=1 biological subject (3 repeated trials). "
            "Single-subject data supports intra-subject technical test-retest repeatability only."
        )


def monoexponential_recovery_curve(t, pcr_end, delta_pcr, k_sec):
    """
    Standard monoexponential recovery function:
    PCr(t) = pcr_end + delta_pcr * (1 - exp(-k * t))
    where t >= 0 is elapsed recovery time in seconds.
    """
    return pcr_end + delta_pcr * (1.0 - np.exp(-k_sec * t))


def fit_monoexponential_kinetics(time_recovery_s: np.ndarray, pcr_recovery: np.ndarray) -> dict:
    """
    Fit monoexponential recovery kinetics to observations with 95% confidence intervals.
    """
    if len(time_recovery_s) < 5:
        raise IncompleteTrialDataError(f"Insufficient recovery points for fitting: {len(time_recovery_s)}")
        
    t_rel = time_recovery_s - time_recovery_s[0]
    pcr_min = float(np.min(pcr_recovery))
    pcr_max = float(np.max(pcr_recovery))
    delta_init = max(pcr_max - pcr_min, 1e-4)
    k_init = 1.5 / 60.0 # ~0.025 s^-1
    
    p0 = [pcr_min, delta_init, k_init]
    bounds = (
        [0.0, 0.0, 0.001],           # k >= 0.06 min^-1 (tau <= 1000 s)
        [pcr_max * 2.0, pcr_max * 3.0, 0.2] # k <= 12 min^-1 (tau >= 5 s)
    )
    
    try:
        popt, pcov = curve_fit(monoexponential_recovery_curve, t_rel, pcr_recovery, p0=p0, bounds=bounds, maxfev=5000)
    except Exception as exc:
        raise RehmanProcessingError(f"Curve fitting failed: {exc}")
        
    pcr_end_fit, delta_pcr_fit, k_sec_fit = popt
    k_min_fit = k_sec_fit * 60.0
    tau_sec_fit = 1.0 / k_sec_fit if k_sec_fit > 0 else None
    
    # 95% confidence intervals from covariance diagonal
    if pcov is not None and np.all(np.isfinite(pcov)):
        perr = np.sqrt(np.diag(pcov))
        ci_95_k_min = float(1.96 * perr[2] * 60.0)
    else:
        ci_95_k_min = None
        
    fitted_vals = monoexponential_recovery_curve(t_rel, *popt)
    residuals = pcr_recovery - fitted_vals
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((pcr_recovery - np.mean(pcr_recovery)) ** 2))
    r_squared = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    mae = float(np.mean(np.abs(residuals)))
    
    return {
        "pcr_end_fitted": float(pcr_end_fit),
        "delta_pcr_fitted": float(delta_pcr_fit),
        "k_sec_minus_1": float(k_sec_fit),
        "k_min_minus_1": float(k_min_fit),
        "k_min_minus_1_ci95": ci_95_k_min,
        "tau_recovery_s": float(tau_sec_fit) if tau_sec_fit else None,
        "fit_r_squared": r_squared,
        "fit_rmse": rmse,
        "fit_mae": mae,
        "number_of_recovery_points": len(time_recovery_s)
    }


def _classify_column(header_cell: str | None) -> tuple[int | None, str | None]:
    """
    Classify a header cell into (trial_id, role).
    Roles: 'spectra', 'time', 'pcr_amp', 'pcr_ppm', 'pi_amp', 'pi_ppm', 'ph'
    Handles:
      - '1.Spectra ', '1.Time, min', '1.PCr δppm', '1. PCr signal amplitude', '1. Pi δppm', '1. Pi signal amplitude'
      - 'Trial 1 Time', 't1_pcr', etc.
    """
    if header_cell is None:
        return None, None
        
    s = str(header_cell).strip().lower()
    s = s.replace('\u03b4', 'delta').replace('\u2212', '-')
    s = re.sub(r'\s+', ' ', s)
    
    # Check trial prefix
    m = re.match(r'^([1-3])\.\s*(.*)$', s)
    if not m:
        m = re.match(r'^(?:trial\s*|t)([1-3])[:_\s-]*(.*)$', s)
        
    if not m:
        # No trial prefix in header
        return None, _classify_role_without_prefix(s)
        
    tid = int(m.group(1))
    rest = m.group(2).strip()
    role = _classify_role_without_prefix(rest)
    return tid, role


def _classify_role_without_prefix(text: str) -> str | None:
    """Classify role of header substring without prefix."""
    t = text.lower()
    if 'spectra' in t or 'spectrum' in t:
        return 'spectra'
    if 'time' in t or t.startswith('min') or t == 's' or t == 'sec':
        return 'time'
    if 'pcr' in t:
        if 'ppm' in t or 'delta' in t or 'shift' in t:
            return 'pcr_ppm'
        return 'pcr_amp'
    if 'pi' in t:
        if 'ppm' in t or 'delta' in t or 'shift' in t:
            return 'pi_ppm'
        return 'pi_amp'
    if 'ph' in t:
        return 'ph'
    return None


def _validate_time_and_spectra(time_s: np.ndarray, spectra: np.ndarray | None, trial_id: int):
    """Validate time step resolution (6s), uniformity, monotonicity, and spectra order."""
    if len(time_s) < 2:
        return
        
    diffs = np.diff(time_s)
    if np.any(diffs <= 0):
        raise IncompleteTrialDataError(f"Trial {trial_id} time sequence is non-monotonic.")
        
    median_dt = float(np.median(diffs))
    if abs(median_dt - 6.0) > 0.5:
        raise IncompleteTrialDataError(
            f"Trial {trial_id} sampling resolution {median_dt:.2f} s differs from expected 6.0 s."
        )
        
    if np.any(np.abs(diffs - median_dt) > 1.0):
        raise IncompleteTrialDataError(
            f"Trial {trial_id} has non-uniform time sampling intervals: deltas={diffs.tolist()[:10]}"
        )
        
    if spectra is not None and len(spectra) > 1:
        spec_diffs = np.diff(spectra)
        if np.any(spec_diffs <= 0):
            raise IncompleteTrialDataError(
                f"Trial {trial_id} spectra sequence is non-monotonic: {spectra.tolist()[:10]}"
            )


def _validate_amplitudes(pcr_amp: np.ndarray, pi_amp: np.ndarray, trial_id: int):
    """Validate that PCr and Pi amplitudes are positive signal intensities, not chemical shift ppm."""
    if np.all(pcr_amp <= 0) or np.mean(pcr_amp) < 10.0:
        raise CorruptedColumnError(
            f"Trial {trial_id}: PCr amplitude values appear to be chemical shifts or invalid signals "
            f"(mean={np.mean(pcr_amp):.2f}). PCr amplitude must be positive resonance peak intensity, not chemical shift ppm."
        )
    if np.all(pi_amp <= 0) or np.mean(pi_amp) < 1.0:
        raise CorruptedColumnError(
            f"Trial {trial_id}: Pi amplitude values appear to be invalid signals (mean={np.mean(pi_amp):.2f})."
        )


def _parse_rows_table(rows: list[list], sheet_name: str, trial_id: int) -> dict:
    """Parse rows from a table representation of a worksheet (Strategy 1: 1 sheet per trial)."""
    if not rows or len(rows) < 2:
        raise EmptyWorkbookError(f"Worksheet {sheet_name} for trial {trial_id} has insufficient data rows.")
        
    header = [str(c).strip() if c is not None else '' for c in rows[0]]
    
    col_t = None
    col_pcr_amp = None
    col_pcr_ppm = None
    col_pi_amp = None
    col_pi_ppm = None
    col_ph = None
    col_spec = None
    
    for idx, h in enumerate(header):
        role = _classify_role_without_prefix(h)
        if role == 'time' and col_t is None: col_t = idx
        elif role == 'pcr_amp' and col_pcr_amp is None: col_pcr_amp = idx
        elif role == 'pcr_ppm' and col_pcr_ppm is None: col_pcr_ppm = idx
        elif role == 'pi_amp' and col_pi_amp is None: col_pi_amp = idx
        elif role == 'pi_ppm' and col_pi_ppm is None: col_pi_ppm = idx
        elif role == 'ph' and col_ph is None: col_ph = idx
        elif role == 'spectra' and col_spec is None: col_spec = idx
        
    if col_t is None or col_pcr_amp is None:
        raise CorruptedColumnError(f"Cannot identify Time and PCr columns in sheet {sheet_name}. Headers: {header}")
        
    if col_pi_amp is None:
        raise CorruptedColumnError(f"Missing inorganic phosphate (Pi) column in sheet {sheet_name}. Headers: {header}")
        
    time_list = []
    pcr_list = []
    pi_list = []
    pcr_ppm_list = []
    pi_ppm_list = []
    ph_list = []
    spec_list = []
    
    for r_idx, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        if col_t >= len(row) or col_pcr_amp >= len(row) or row[col_t] is None or row[col_pcr_amp] is None:
            continue
        try:
            val_t = float(row[col_t])
            val_pcr = float(row[col_pcr_amp])
            val_pi = float(row[col_pi_amp]) if (col_pi_amp < len(row) and row[col_pi_amp] is not None) else None
            val_pcr_ppm = float(row[col_pcr_ppm]) if (col_pcr_ppm is not None and col_pcr_ppm < len(row) and row[col_pcr_ppm] is not None) else None
            val_pi_ppm = float(row[col_pi_ppm]) if (col_pi_ppm is not None and col_pi_ppm < len(row) and row[col_pi_ppm] is not None) else None
            val_ph = float(row[col_ph]) if (col_ph is not None and col_ph < len(row) and row[col_ph] is not None) else None
            val_spec = int(row[col_spec]) if (col_spec is not None and col_spec < len(row) and row[col_spec] is not None) else len(time_list) + 1
        except (ValueError, TypeError) as exc:
            raise CorruptedColumnError(f"Row {r_idx} in sheet {sheet_name} has corrupted numeric value: {exc}")
            
        time_list.append(val_t)
        pcr_list.append(val_pcr)
        pi_list.append(val_pi if val_pi is not None else 0.0)
        pcr_ppm_list.append(val_pcr_ppm)
        pi_ppm_list.append(val_pi_ppm)
        ph_list.append(val_ph)
        spec_list.append(val_spec)
        
    if len(time_list) < 20:
        raise IncompleteTrialDataError(f"Trial {trial_id} contains only {len(time_list)} points; expected at least 20 points.")
        
    t_raw = np.array(time_list, dtype=float)
    h_time_str = str(header[col_t]).lower()
    if 'min' in h_time_str or (np.max(t_raw) < 20.0 and 's' not in h_time_str):
        time_s = t_raw * 60.0
    else:
        time_s = t_raw
        
    pcr_arr = np.array(pcr_list, dtype=float)
    pi_arr = np.array(pi_list, dtype=float)
    spec_arr = np.array(spec_list, dtype=int) if spec_list else None
    
    _validate_time_and_spectra(time_s, spec_arr, trial_id)
    _validate_amplitudes(pcr_arr, pi_arr, trial_id)
    
    # pH calculation
    has_explicit_ph = any(v is not None for v in ph_list)
    has_shifts = any(p is not None for p in pcr_ppm_list) and any(p is not None for p in pi_ppm_list)
    
    if has_explicit_ph:
        final_ph = ph_list
        ph_status = "RECORDED_IN_SOURCE"
    elif has_shifts:
        final_ph = [calculate_ph_from_chemical_shifts(pi, pc) for pc, pi in zip(pcr_ppm_list, pi_ppm_list)]
        ph_status = "DERIVED_FROM_CHEMICAL_SHIFTS"
    else:
        final_ph = [None] * len(pcr_arr)
        ph_status = "NOT_DERIVED_FROM_AVAILABLE_SIGNALS"
        
    return {
        "time_s": time_s,
        "pcr": pcr_arr,
        "pi": pi_arr,
        "pcr_ppm": np.array(pcr_ppm_list, dtype=float) if has_shifts else None,
        "pi_ppm": np.array(pi_ppm_list, dtype=float) if has_shifts else None,
        "ph": final_ph,
        "ph_status": ph_status,
        "spectra": spec_arr
    }


def _parse_single_table_multi_trial(rows: list[list], sheet_name: str) -> dict:
    """
    Parse single sheet with 3 trials side by side (Strategy 2, e.g. sheet '2024_829_DiB_Raw').
    Recognizes prefixes '1.', '2.', '3.' with arbitrary spacing, case, and greek delta 'δ'.
    """
    if not rows or len(rows) < 2:
        raise EmptyWorkbookError(f"Worksheet {sheet_name} has insufficient data.")
        
    header = rows[0]
    
    # Map columns per trial
    col_map: dict[int, dict[str, int]] = {1: {}, 2: {}, 3: {}}
    for idx, h in enumerate(header):
        tid, role = _classify_column(h)
        if tid in col_map and role is not None:
            col_map[tid][role] = idx
            
    trials = {}
    for tid in [1, 2, 3]:
        cols = col_map[tid]
        c_t = cols.get('time')
        c_pcr_amp = cols.get('pcr_amp')
        c_pi_amp = cols.get('pi_amp')
        c_pcr_ppm = cols.get('pcr_ppm')
        c_pi_ppm = cols.get('pi_ppm')
        c_spec = cols.get('spectra')
        c_ph = cols.get('ph')
        
        if c_t is None or c_pcr_amp is None:
            continue
            
        if c_pi_amp is None:
            raise CorruptedColumnError(f"Trial {tid} in sheet {sheet_name} is missing Pi signal amplitude column.")
            
        t_list, pcr_list, pi_list, pcr_ppm_list, pi_ppm_list, spec_list, ph_list = [], [], [], [], [], [], []
        
        for r_idx, r in enumerate(rows[1:], start=2):
            if c_t >= len(r) or c_pcr_amp >= len(r):
                continue
            # If time or PCr is None (e.g. spectrum 1 pre-scan marker), skip data row
            if r[c_t] is None or r[c_pcr_amp] is None:
                continue
                
            try:
                val_t = float(r[c_t])
                val_pcr = float(r[c_pcr_amp])
                val_pi = float(r[c_pi_amp]) if (c_pi_amp < len(r) and r[c_pi_amp] is not None) else None
                val_pcr_ppm = float(r[c_pcr_ppm]) if (c_pcr_ppm is not None and c_pcr_ppm < len(r) and r[c_pcr_ppm] is not None) else None
                val_pi_ppm = float(r[c_pi_ppm]) if (c_pi_ppm is not None and c_pi_ppm < len(r) and r[c_pi_ppm] is not None) else None
                val_spec = int(r[c_spec]) if (c_spec is not None and c_spec < len(r) and r[c_spec] is not None) else len(t_list) + 1
                val_ph = float(r[c_ph]) if (c_ph is not None and c_ph < len(r) and r[c_ph] is not None) else None
            except (ValueError, TypeError) as exc:
                raise CorruptedColumnError(f"Trial {tid} row {r_idx} in sheet {sheet_name} has invalid numeric value: {exc}")
                
            t_list.append(val_t)
            pcr_list.append(val_pcr)
            pi_list.append(val_pi if val_pi is not None else 0.0)
            pcr_ppm_list.append(val_pcr_ppm)
            pi_ppm_list.append(val_pi_ppm)
            spec_list.append(val_spec)
            ph_list.append(val_ph)
            
        if len(t_list) < 20:
            raise IncompleteTrialDataError(f"Trial {tid} contains only {len(t_list)} valid data points; expected >= 20.")
            
        t_raw = np.array(t_list, dtype=float)
        h_time_str = str(header[c_t]).lower()
        if 'min' in h_time_str or (np.max(t_raw) < 20.0 and 's' not in h_time_str):
            time_s = t_raw * 60.0
        else:
            time_s = t_raw
            
        pcr_arr = np.array(pcr_list, dtype=float)
        pi_arr = np.array(pi_list, dtype=float)
        spec_arr = np.array(spec_list, dtype=int) if spec_list else None
        
        _validate_time_and_spectra(time_s, spec_arr, tid)
        _validate_amplitudes(pcr_arr, pi_arr, tid)
        
        # pH derivation
        has_explicit_ph = any(v is not None for v in ph_list)
        has_shifts = any(p is not None for p in pcr_ppm_list) and any(p is not None for p in pi_ppm_list)
        
        if has_explicit_ph:
            final_ph = ph_list
            ph_status = "RECORDED_IN_SOURCE"
        elif has_shifts:
            final_ph = [calculate_ph_from_chemical_shifts(pi, pc) for pc, pi in zip(pcr_ppm_list, pi_ppm_list)]
            ph_status = "DERIVED_FROM_CHEMICAL_SHIFTS"
        else:
            final_ph = [None] * len(pcr_arr)
            ph_status = "NOT_DERIVED_FROM_AVAILABLE_SIGNALS"
            
        trials[tid] = {
            "time_s": time_s,
            "pcr": pcr_arr,
            "pi": pi_arr,
            "pcr_ppm": np.array(pcr_ppm_list, dtype=float) if has_shifts else None,
            "pi_ppm": np.array(pi_ppm_list, dtype=float) if has_shifts else None,
            "ph": final_ph,
            "ph_status": ph_status,
            "spectra": spec_arr
        }
        
    if len(trials) < 3:
        raise MissingTrialSheetError(
            f"Could not extract 3 distinct trial column groups from sheet {sheet_name}. Found: {list(trials.keys())}"
        )
        
    return trials


def inspect_and_extract_sheets_dict(sheets_dict: dict[str, list[list]], source_label="ORIGINAL_XLSX") -> dict:
    """
    Inspect dictionary of sheet tables {sheet_name: rows}, validate sheets and columns,
    extract PCr and Pi time-series per trial, and perform kinetic fits.
    """
    if not sheets_dict:
        raise EmptyWorkbookError("Excel workbook contains no sheets.")
        
    sheet_names = list(sheets_dict.keys())
    trials_data = {}
    
    # Strategy 1: Multi-sheet workbook where each sheet is a Trial (e.g. Trial 1, Trial 2, Trial 3)
    trial_sheets = [s for s in sheet_names if 'trial' in s.lower() or 't1' in s.lower() or 't2' in s.lower() or 't3' in s.lower()]
    
    if len(trial_sheets) >= 3:
        for idx, sname in enumerate(trial_sheets[:3], start=1):
            rows = sheets_dict[sname]
            extracted = _parse_rows_table(rows, sheet_name=sname, trial_id=idx)
            trials_data[idx] = extracted
    else:
        # Strategy 2: Single sheet with trial columns (e.g. '2024_829_DiB_Raw')
        first_sheet = sheet_names[0]
        rows = sheets_dict[first_sheet]
        trials_data = _parse_single_table_multi_trial(rows, sheet_name=first_sheet)
        
    if len(trials_data) < 3:
        raise IncompleteTrialDataError(f"Found {len(trials_data)} trials; expected exactly 3 experimental trials.")
        
    # Process kinetics for all 3 trials
    trial_results = []
    k_vals = []
    tau_vals = []
    drop_vals = []
    
    for trial_id in sorted(trials_data.keys()):
        t_data = trials_data[trial_id]
        time_s = t_data["time_s"]
        pcr = t_data["pcr"]
        pi = t_data["pi"]
        pcr_ppm = t_data["pcr_ppm"]
        pi_ppm = t_data["pi_ppm"]
        ph = t_data["ph"]
        ph_status = t_data["ph_status"]
        spectra = t_data["spectra"]
        
        # Dynamically determine exercise nadir (minimum PCr during exercise window t <= 200 s)
        ex_window_idx = np.where(time_s <= 200.0)[0]
        if len(ex_window_idx) == 0:
            ex_window_idx = np.arange(min(30, len(pcr)))
            
        nadir_idx = ex_window_idx[int(np.argmin(pcr[ex_window_idx]))]
        
        # Determine resting baseline PCr from pre-exercise period (first 2-8 points before drop)
        n_ctrl = max(1, min(7, nadir_idx))
        pcr_rest = float(np.mean(pcr[:n_ctrl]))
        pcr_end_ex = float(pcr[nadir_idx])
        pcr_drop_pct = float(max(0.0, (pcr_rest - pcr_end_ex) / pcr_rest * 100.0)) if pcr_rest > 0 else 0.0
        
        # Recovery phase: from nadir onward
        time_rec = time_s[nadir_idx:]
        pcr_rec = pcr[nadir_idx:]
        
        fit_res = fit_monoexponential_kinetics(time_rec, pcr_rec)
        
        # Compare with published Table 1 rate constants
        pub_ref = PUBLISHED_TABLE1_METRICS.get(trial_id, {})
        pub_k = pub_ref.get("k_min_minus_1")
        discrepancy_k = float(abs(fit_res["k_min_minus_1"] - pub_k)) if pub_k is not None else None
        discrepancy_k_pct = float(discrepancy_k / pub_k * 100.0) if (discrepancy_k is not None and pub_k) else None
        pub_drop = pub_ref.get("pcr_drop_pct")
        discrepancy_drop_pct = float(abs(pcr_drop_pct - pub_drop)) if pub_drop is not None else None
        
        # pH summary
        if all(v is None for v in ph):
            ph_ctrl = None
            ph_end_ex = None
            ph_end_rec = None
        else:
            ctrl_phs = [v for v in ph[:n_ctrl] if v is not None]
            ph_ctrl = float(np.mean(ctrl_phs)) if ctrl_phs else None
            ph_end_ex = float(ph[nadir_idx]) if ph[nadir_idx] is not None else None
            ph_end_rec = float(ph[-1]) if ph[-1] is not None else None
            
        t_summary = {
            "trial_id": trial_id,
            "observation_id": f"REHMAN_2024_DRYAD_RAW_TRIAL_{trial_id}",
            "number_of_spectra": len(time_s),
            "temporal_resolution_s": 6.0,
            "nadir_index": int(nadir_idx),
            "nadir_time_s": float(time_s[nadir_idx]),
            "nadir_spectrum": int(spectra[nadir_idx]) if spectra is not None else None,
            "pcr_rest_baseline": pcr_rest,
            "pcr_end_exercise": pcr_end_ex,
            "pcr_depletion_fraction": pcr_drop_pct / 100.0,
            "pcr_drop_pct": pcr_drop_pct,
            "ph_status": ph_status,
            "ph_control": ph_ctrl,
            "ph_end_exercise": ph_end_ex,
            "ph_end_recovery": ph_end_rec,
            "kinetic_fit": fit_res,
            "published_table1_comparison": {
                "published_k_min_minus_1": pub_k,
                "calculated_k_min_minus_1": fit_res["k_min_minus_1"],
                "discrepancy_k_min_minus_1": discrepancy_k,
                "discrepancy_k_pct": discrepancy_k_pct,
                "published_pcr_drop_pct": pub_drop,
                "calculated_pcr_drop_pct": pcr_drop_pct,
                "discrepancy_pcr_drop_pct": discrepancy_drop_pct,
                "published_tau_s": pub_ref.get("tau_s"),
                "calculated_tau_s": fit_res["tau_recovery_s"],
                "published_ph_ctrl": pub_ref.get("ph_ctrl"),
                "calculated_ph_ctrl": ph_ctrl,
                "published_ph_end_ex": pub_ref.get("ph_end_ex"),
                "calculated_ph_end_ex": ph_end_ex,
                "published_ph_end_rec": pub_ref.get("ph_end_rec"),
                "calculated_ph_end_rec": ph_end_rec
            },
            "time_series": {
                "spectra": [int(x) for x in spectra] if spectra is not None else None,
                "time_s": time_s.tolist(),
                "pcr_raw_amplitude": pcr.tolist(),
                "pi_raw_amplitude": pi.tolist(),
                "pcr_shift_ppm": pcr_ppm.tolist() if pcr_ppm is not None else None,
                "pi_shift_ppm": pi_ppm.tolist() if pi_ppm is not None else None,
                "ph_profile": ph if isinstance(ph, list) else ph.tolist()
            }
        }
        trial_results.append(t_summary)
        k_vals.append(fit_res["k_min_minus_1"])
        if fit_res["tau_recovery_s"]:
            tau_vals.append(fit_res["tau_recovery_s"])
        drop_vals.append(pcr_drop_pct)
        
    # Technical repeatability statistics across 3 trials
    k_mean = float(np.mean(k_vals))
    k_sd = float(np.std(k_vals, ddof=1)) if len(k_vals) > 1 else 0.0
    k_cv_pct = float(k_sd / k_mean * 100.0) if k_mean > 0 else 0.0
    
    tau_mean = float(np.mean(tau_vals)) if tau_vals else None
    tau_sd = float(np.std(tau_vals, ddof=1)) if len(tau_vals) > 1 else 0.0
    
    drop_mean = float(np.mean(drop_vals))
    drop_sd = float(np.std(drop_vals, ddof=1)) if len(drop_vals) > 1 else 0.0
    
    return {
        "n_biological_participants": 1,
        "n_operators": 1,
        "n_trials": 3,
        "n_records": len(trial_results),
        "total_spectra_extracted": sum(t["number_of_spectra"] for t in trial_results),
        "repeatability_analysis": {
            "type": "INTRA_SUBJECT_TECHNICAL_TEST_RETEST_REPEATABILITY",
            "k_mean_min_minus_1": k_mean,
            "k_sd_min_minus_1": k_sd,
            "k_cv_pct": k_cv_pct,
            "tau_mean_s": tau_mean,
            "tau_sd_s": tau_sd,
            "pcr_drop_mean_pct": drop_mean,
            "pcr_drop_sd_pct": drop_sd,
            "evaluation": "Technical reproducibility across 3 trials on N=1 human participant demonstrates scanner/protocol precision; does NOT constitute independent cross-subject biological validation."
        },
        "trials": trial_results,
        "cross_subject_loso_policy": {
            "permitted": False,
            "reason": "Single participant (N=1). Cross-subject Leave-One-Subject-Out (LOSO) validation is mathematically and epistemically prohibited."
        }
    }


def execute_pipeline(filepath: Path | None = None, allow_synthetic_fixture: bool = False) -> dict:
    """
    Main execution pipeline:
    - If real XLSX is absent: returns PENDING_RAW_DATA without false pass.
    - If candidate file present: verifies SHA256, parses, fits, and outputs derived data.
    """
    if filepath is None:
        filepath = find_rehman_xlsx()
        
    if filepath is None or not filepath.is_file():
        return {
            "status": "PENDING_RAW_DATA",
            "available": False,
            "verdict": "REAL_DATA_PENDING_OWNER_ASSISTED_ACQUISITION",
            "programmatic_blocker": {
                "web_stream_status": "HTTP 403 Forbidden / AWS WAF Anubis BotStopper Proof-of-Work Challenge",
                "rest_api_download_status": "HTTP 401 Unauthorized (OAuth Bearer token required)",
                "security_boundary": "Automated bypass of bot protection, solving CAPTCHA/PoW, or spoofing credentials is strictly prohibited."
            },
            "target_file_spec": {
                "filename": EXPECTED_FILENAME,
                "expected_sha256": EXPECTED_SHA256,
                "expected_size_bytes": EXPECTED_SIZE_BYTES,
                "n_biological_participants": 1,
                "n_trials": 3,
                "n_spectra_per_trial": 75,
                "temporal_resolution_s": 6.0
            },
            "owner_assisted_workflow": {
                "step_1": "Open browser to: https://datadryad.org/stash/dataset/doi:10.5061/dryad.08kprr59v",
                "step_2": f"Download '{EXPECTED_FILENAME}' (approx. 18.14 KB)",
                "step_3": f"Save into project at: {CYCLE9_DIR / EXPECTED_FILENAME} (or project root, or Downloads)",
                "step_4": "Run 'python tools/process_rehman_xlsx.py' to automatically verify byte SHA256 and process real data."
            }
        }
        
    # File is present: verify byte SHA256
    raw_bytes = filepath.read_bytes()
    computed_sha = hashlib.sha256(raw_bytes).hexdigest()
    
    if not allow_synthetic_fixture and computed_sha != EXPECTED_SHA256:
        raise Sha256MismatchError(f"SHA256 mismatch for {filepath}: got '{computed_sha}', expected '{EXPECTED_SHA256}'")
        
    sheets_dict = read_xlsx_sheets(filepath)
    extracted = inspect_and_extract_sheets_dict(sheets_dict, source_label="REAL_DRYAD_RAW_V3" if not allow_synthetic_fixture else "SYNTHETIC_TEST_FIXTURE")
    
    if not allow_synthetic_fixture:
        out_json = CYCLE9_DIR / "rehman2024_extracted_timeseries.json"
        payload = {
            "status": "PROCESSED_PRIMARY_RAW_XLSX",
            "provenance_type": "DERIVED_EXTRACTION_JSON",
            "source_raw_file": EXPECTED_FILENAME,
            "source_raw_sha256": EXPECTED_SHA256,
            "source_raw_size_bytes": EXPECTED_SIZE_BYTES,
            "extraction_results": extracted
        }
        out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8', newline='\n')
        
        return {
            "status": "PROCESSED_PRIMARY_RAW_XLSX",
            "available": True,
            "raw_file": str(filepath.relative_to(ROOT) if filepath.is_relative_to(ROOT) else filepath),
            "raw_sha256": computed_sha,
            "derived_json_path": str(out_json.relative_to(ROOT)),
            "extracted_metrics": extracted
        }
    else:
        return {
            "status": "SYNTHETIC_FIXTURE_PARSED_FOR_UNIT_TEST",
            "provenance_type": "SYNTHETIC_FIXTURE_PARSER_TEST_ONLY",
            "available": True,
            "extracted_metrics": extracted
        }


if __name__ == '__main__':
    report = execute_pipeline()
    print("\n--- REHMAN 2024 RAW XLSX PIPELINE REPORT ---")
    print(f"Status: {report['status']}")
    if report.get('available'):
        metrics = report['extracted_metrics']
        rep = metrics['repeatability_analysis']
        print(f"Total spectra extracted: {metrics['total_spectra_extracted']} across {metrics['n_trials']} trials")
        print(f"Repeatability k_mean: {rep['k_mean_min_minus_1']:.3f} +/- {rep['k_sd_min_minus_1']:.3f} min^-1 (CV: {rep['k_cv_pct']:.2f}%)")
        print(f"Repeatability tau_mean: {rep['tau_mean_s']:.2f} +/- {rep['tau_sd_s']:.2f} s")
        for t in metrics['trials']:
            kf = t['kinetic_fit']
            pub = t['published_table1_comparison']
            print(f"Trial {t['trial_id']}: nadir spec {t['nadir_spectrum']} (t={t['nadir_time_s']}s) | drop={t['pcr_drop_pct']:.2f}% (pub: {pub['published_pcr_drop_pct']}%) | k={kf['k_min_minus_1']:.3f} min^-1 (pub: {pub['published_k_min_minus_1']}, diff: {pub['discrepancy_k_pct']:.2f}%) | R2={kf['fit_r_squared']:.4f}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
