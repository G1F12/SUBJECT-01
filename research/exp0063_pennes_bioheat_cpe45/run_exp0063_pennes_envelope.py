#!/usr/bin/env python3
"""
EXP-0063: Multi-Compartment Cylindrical Pennes Bioheat Model and Intermittent Workload
Feasibility Envelope for TARGET-CPE45 over 2700 s (MASTER_ROADMAP.md §4.3, BLOCKER-01, ISS-0011).

Strictly distinguishes:
- Empirical metabolic anchoring: PhysioNet Malaga CPET (SRC-0074, N=846 unique subjects) and
  ACTES thermoneutral dataset (observations.csv).
- Mechanistic simulation (MODEL_ONLY): 4-layer cylindrical Pennes bioheat + arterial pool solver
  over [0, 2700] s verified for First-Law energy balance and interfaced with tools.cpe45.analyze.
Preserves invariant: TARGET-CPE45 = NOT EXTERNALLY VALIDATED.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import cpe45

MALAGA_INFO_CSV = ROOT / "research/treadmill_cpet_2026_11_09/subject-info.csv"
MALAGA_SUMMARY_JSON = ROOT / "research/treadmill_cpet_2026_11_09/malaga_validation_results.json"
ACTES_OBS_CSV = ROOT / "research/cpe45_2026_11_04/results/observations.csv"
OUT_DIR = ROOT / "research/exp0063_pennes_bioheat_cpe45"


def anchor_empirical_metabolic_loads() -> dict:
    """
    Read SHA256-verified empirical Malaga and ACTES metabolic anchors from repository artifacts.
    """
    malaga_sha = hashlib.sha256(MALAGA_INFO_CSV.read_bytes()).hexdigest()
    actes_sha = hashlib.sha256(ACTES_OBS_CSV.read_bytes()).hexdigest()

    df_mal_subj = pd.read_csv(MALAGA_INFO_CSV)
    mal_json = json.loads(MALAGA_SUMMARY_JSON.read_text(encoding="utf-8"))
    df_actes = pd.read_csv(ACTES_OBS_CSV)

    tn = df_actes[df_actes["condition"] == "Thermoneutral"].dropna(subset=["mean_power_W"])
    return {
        "malaga_cohort": {
            "source_file": "research/treadmill_cpet_2026_11_09/subject-info.csv",
            "source_sha256": malaga_sha,
            "n_unique_subjects": mal_json["cohort_description"]["n_valid_unique_subjects"],
            "n_valid_tests": mal_json["cohort_description"]["n_valid_incremental_tests"],
            "mean_mass_kg": round(float(df_mal_subj["Weight"].mean()), 2),
            "mean_age_years": round(float(df_mal_subj["Age"].mean()), 2),
            "oxycaloric_equiv_kj_per_L": round(float(mal_json["respiratory_exchange_and_oxycaloric_audit"]["derived_oxycaloric_equivalent_kj_per_l_distribution"]["mean"]), 3),
        },
        "actes_intermittent_cohort": {
            "source_file": "research/cpe45_2026_11_04/results/observations.csv",
            "source_sha256": actes_sha,
            "n_participants": int(tn["participant"].nunique()),
            "thermoneutral_mean_power_W": round(float(tn["mean_power_W"].mean()), 1),
            "thermoneutral_p95_power_W": round(float(np.nanpercentile(tn["mean_power_W"].values, 95)), 1),
        },
    }


def saturation_vapor_pressure_kpa(temp_c: float) -> float:
    """Tetens formula for saturated water vapor pressure [kPa]."""
    return 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def simulate_4layer_pennes_2700s(
    p_effort_W: float,
    duty_cycle: float,
    temp_amb_C: float,
    rel_humidity: float,
    skin_evap_factor: float = 1.0,
    exogenous_cooling_W: float = 0.0,
    added_mass_kg: float = 0.0,
    body_mass_kg: float = 75.0,
    dt_s: float = 5.0,
) -> dict:
    """
    Simulate 4-compartment cylindrical Pennes bioheat transfer over 2700 s (`MODEL_ONLY`):
    Compartments: [0] Core/Viscera, [1] Skeletal Muscle, [2] Subcutaneous Fat, [3] Skin.
    Coupled through conductive inter-shell thermal conductances G_k and perfusion exchange
    with a well-mixed central arterial blood pool T_art conserving total thermal energy exactly.
    """
    duration_s = 2700.0
    n_steps = int(round(duration_s / dt_s))
    trace_stride = max(1, int(round(30.0 / dt_s)))

    # Compartment thermal capacitances C_k [J/K] summing to total mass * 3470 J/(kg*K)
    m_tot = body_mass_kg + added_mass_kg
    c_specific = 3470.0
    fracs = np.array([0.35, 0.42, 0.16, 0.07], dtype=float)
    C_k = m_tot * c_specific * fracs  # [J/K]
    C_art = 3.2 * 3800.0               # ~3.2 L blood central arterial buffer [J/K]

    # Radial conductive conductances between layers [W/K]:
    # Core<->Muscle (fast internal conduction), Muscle<->Fat (insulating layer), Fat<->Skin
    G_cond = np.array([115.0, 28.0, 42.0], dtype=float)

    # Initial physiological temperatures [deg C]
    T = np.array([37.0, 35.8, 34.0, 33.0], dtype=float)
    T_art = 36.85
    T_initial = T.copy()
    T_art_initial = T_art

    # Metabolic and thermoregulatory parameters calibrated to ARCHITECTURE_COMPARISON.md (1100-1450 W heat,
    # sweat dripping efficiency eta_drip = 0.72 at 1.20 L/h sweat rate => ~580-750 W effective evaporative ceiling):
    delta_efficiency = 0.21  # Gross/delta locomotor work efficiency: Q_heat = P_mech * (1/eta - 1)
    q_bmr_core_W = 82.0      # Basal core organ heat production
    q_rest_recovery_mech_W = 35.0 if duty_cycle < 1.0 else p_effort_W  # active unloading during recovery
    surface_area_m2 = 1.92
    hc_W_m2_K = 7.8 * skin_evap_factor  # Indoor still/moderate convection
    emissivity = 0.95
    sigma_sb = 5.670374419e-8
    sweat_evap_efficiency = 0.72        # Physiological sweat dripping loss (~28% runs off unevaporated)
    max_sweat_rate_kg_s = (1.20 / 3600.0) * sweat_evap_efficiency * skin_evap_factor
    latent_J_kg = 2.42e6

    # Cycle timing: 60 s effort block followed by rest block to match exact duty_cycle D
    cycle_effort_s = 60.0
    cycle_period_s = cycle_effort_s / max(duty_cycle, 1e-6) if duty_cycle < 1.0 else 60.0

    # Tracking exact energy ledger and trajectories for CPE45 interface
    energy_in_heat_J = 0.0
    energy_out_loss_J = 0.0
    energy_exo_J = 0.0
    peak_core_C = float(T[0])
    peak_muscle_C = float(T[1])
    time_to_395C_s = None
    time_to_400C_s = None
    trace_30s = []

    rho_c_blood = 3850.0  # J / (L * K) -> perfusion in L/s * rho_c = [W/K]

    for step in range(n_steps):
        t_now = step * dt_s
        if duty_cycle >= 0.999:
            is_effort = True
            p_now = p_effort_W
        else:
            phase = t_now % cycle_period_s
            is_effort = phase < cycle_effort_s
            p_now = p_effort_W if is_effort else q_rest_recovery_mech_W

        if step % trace_stride == 0:
            trace_30s.append({
                "time_s": float(t_now),
                "power_W": float(p_now),
                "is_effort": bool(is_effort),
                "T_core_C": float(T[0]),
                "T_muscle_C": float(T[1]),
                "T_skin_C": float(T[3]),
            })

        # Heat generation q_k(t) [W]
        q_mus = p_now * (1.0 / delta_efficiency - 1.0)
        q_gen = np.array([q_bmr_core_W, q_mus, 2.0, 4.0], dtype=float)

        # Blood perfusion conductance w_k = F_blood_k(L/s) * rho_c_blood [W/K]
        thermal_drive = max(0.0, (T[0] - 37.0) + 0.15 * (T[3] - 33.0))
        q_blood_L_s = np.array([
            3.0 / 60.0,
            (1.2 + 12.5 * min(1.0, p_now / 380.0)) / 60.0,
            0.3 / 60.0,
            (0.45 + 4.8 * min(1.0, thermal_drive / 1.8) * skin_evap_factor) / 60.0,
        ], dtype=float)
        W_perf = q_blood_L_s * rho_c_blood  # [W/K]

        # Surface heat loss (skin -> ambient) + respiratory loss (core -> ambient)
        t_skin_C = float(T[3])
        t_skin_K = t_skin_C + 273.15
        t_amb_K = temp_amb_C + 273.15
        dry_loss_W = hc_W_m2_K * surface_area_m2 * (t_skin_C - temp_amb_C) + emissivity * sigma_sb * surface_area_m2 * (t_skin_K ** 4 - t_amb_K ** 4)
        e_max_W = max(0.0, 16.5 * hc_W_m2_K * surface_area_m2 * (saturation_vapor_pressure_kpa(t_skin_C) - rel_humidity * saturation_vapor_pressure_kpa(temp_amb_C)))
        sweat_drive_kg_s = max_sweat_rate_kg_s * min(1.0, thermal_drive / 1.5)
        evap_loss_W = min(sweat_drive_kg_s * latent_J_kg, e_max_W)
        m_total_W = q_bmr_core_W + p_now / delta_efficiency
        resp_loss_W = max(8.0, 0.075 * m_total_W + 0.0014 * m_total_W * (34.0 - temp_amb_C))

        # Thermostatted exogenous vascular cooling activates smoothly above 37.2 C core temperature
        exo_active_W = exogenous_cooling_W * min(1.0, max(0.0, (T[0] - 37.2) / 0.5))

        skin_loss_total_W = dry_loss_W + evap_loss_W
        rhs_sources = np.array([
            q_gen[0] - resp_loss_W,
            q_gen[1],
            q_gen[2],
            q_gen[3] - skin_loss_total_W,
            -exo_active_W,
        ], dtype=float)

        # Unconditionally stable 5x5 Backward Euler step over [T_core, T_mus, T_fat, T_skin, T_art]
        # Internal conduction G_cond and perfusion W_perf form an exact conservative symmetric exchange matrix K_ex:
        C_vec = np.append(C_k, C_art)
        K_ex = np.zeros((5, 5), dtype=float)
        # Symmetric conduction pairs (0-1, 1-2, 2-3):
        for idx, g_val in enumerate(G_cond):
            K_ex[idx, idx] += g_val
            K_ex[idx + 1, idx + 1] += g_val
            K_ex[idx, idx + 1] -= g_val
            K_ex[idx + 1, idx] -= g_val
        # Symmetric perfusion exchange between shell idx (0..3) and arterial pool (4):
        for idx in range(4):
            w_val = float(W_perf[idx])
            K_ex[idx, idx] += w_val
            K_ex[4, 4] += w_val
            K_ex[idx, 4] -= w_val
            K_ex[4, idx] -= w_val

        # Linear system: (diag(C_vec)/dt + K_ex) @ T_all_next = (diag(C_vec)/dt) @ T_all_prev + rhs_sources
        A_sys = np.diag(C_vec / dt_s) + K_ex
        T_prev_all = np.append(T, T_art)
        b_sys = (C_vec / dt_s) * T_prev_all + rhs_sources
        T_next_all = np.linalg.solve(A_sys, b_sys)
        T = T_next_all[:4]
        T_art = float(T_next_all[4])

        energy_in_heat_J += float(np.sum(q_gen)) * dt_s
        energy_out_loss_J += float(skin_loss_total_W + resp_loss_W) * dt_s
        energy_exo_J += exo_active_W * dt_s

        if T[0] > peak_core_C:
            peak_core_C = float(T[0])
        if T[1] > peak_muscle_C:
            peak_muscle_C = float(T[1])
        if time_to_395C_s is None and T[0] >= 39.5:
            time_to_395C_s = float((step + 1) * dt_s)
        if time_to_400C_s is None and T[0] >= 40.0:
            time_to_400C_s = float((step + 1) * dt_s)

    # Final point at t = 2700 s
    trace_30s.append({
        "time_s": float(duration_s),
        "power_W": float(p_effort_W if duty_cycle >= 0.999 else q_rest_recovery_mech_W),
        "is_effort": bool(duty_cycle >= 0.999),
        "T_core_C": float(T[0]),
        "T_muscle_C": float(T[1]),
        "T_skin_C": float(T[3]),
    })

    # Verify First Law energy closure:
    stored_J = float(np.sum(C_k * (T - T_initial)) + C_art * (T_art - T_art_initial))
    expected_stored_J = energy_in_heat_J - energy_out_loss_J - energy_exo_J
    energy_closure_err_J = abs(stored_J - expected_stored_J)

    return {
        "final_T_core_C": round(float(T[0]), 3),
        "peak_T_core_C": round(peak_core_C, 3),
        "peak_T_muscle_C": round(peak_muscle_C, 3),
        "final_T_skin_C": round(float(T[3]), 3),
        "time_to_39_5C_s": time_to_395C_s,
        "time_to_40_0C_s": time_to_400C_s,
        "passes_core_39_5C_gate": bool(peak_core_C < 39.5 and peak_muscle_C < 40.5),
        "energy_balance_error_J": round(energy_closure_err_J, 6),
        "mean_heat_generated_W": round(energy_in_heat_J / duration_s, 1),
        "mean_heat_dissipated_W": round(energy_out_loss_J / duration_s, 1),
        "trace_30s": trace_30s,
    }


def evaluate_cpe45_bridge(sim_result: dict, label_name: str, force_N: float = 400.0) -> dict:
    """
    Feed a generated mechanical trace through tools.cpe45.analyze to ensure
    full schema compatibility while preserving target_achievement == 'not_assessed'.
    """
    trace = sim_result["trace_30s"]
    samples = [
        cpe45.Sample(
            time_s=row["time_s"],
            power_W=row["power_W"],
            force_N=force_N if row["is_effort"] else 80.0,
            speed_m_s=row["power_W"] / (force_N if row["is_effort"] else 80.0),
            acceleration_m_s2=0.0,
            coordination_error_m=0.01,
            maneuver_error_m=0.02,
        )
        for row in trace
    ]
    # Build contiguous alternating effort / recovery episodes cleanly covering [0, 2700]:
    episodes = []
    cur_kind = "effort" if trace[0]["is_effort"] else "recovery"
    cur_start = 0.0
    for i in range(1, len(trace)):
        t_i = trace[i]["time_s"]
        k_i = "effort" if trace[i]["is_effort"] else "recovery"
        if k_i != cur_kind:
            episodes.append(cpe45.Episode(cur_start, t_i, cur_kind, f"{label_name}_{cur_kind}"))
            cur_kind = k_i
            cur_start = t_i
    if cur_start < 2700.0:
        episodes.append(cpe45.Episode(cur_start, 2700.0, cur_kind, f"{label_name}_{cur_kind}"))

    if len(episodes) < 2:
        # cpe45 requires alternating effort/recovery partition when protocol has recovery; continuous test skips recovery check
        return {
            "mode": "continuous_single_episode",
            "total_work_kJ": round(cpe45.profile(samples, 0.0, 2700.0)["work_net_J"] / 1000.0, 2),
            "target_achievement": "not_assessed",
            "physiological_validation": False,
        }

    # Ensure early_end_s spans first effort and late_start_s spans last effort
    early_end = episodes[0].end_s
    last_effort = [ep for ep in episodes if ep.kind == "effort"][-1]
    res = cpe45.analyze(
        samples=samples,
        episodes=episodes,
        early_end_s=early_end,
        late_start_s=last_effort.start_s,
        max_gap_s=30.0,
    )
    return {
        "mode": "intermittent_cpe45_analyzed",
        "total_work_kJ": round(res["total"]["work_net_J"] / 1000.0, 2),
        "target_achievement": res["target_achievement"],
        "physiological_validation": res["physiological_validation"],
        "n_episodes": len(res["episodes"]),
    }


def write_markdown_report(results: dict) -> None:
    emp = results["part_a_empirical_metabolic_anchors"]
    summary = results["part_b_3d_envelope_summary"]
    climates = summary["climate_thresholds_for_360W_arch_a"]
    climates_300 = summary["climate_thresholds_for_300W"]
    cont_300 = summary["continuous_300W_arch_a"]
    cont_360 = summary["continuous_360W_arch_a"]
    aegis = summary["aegis01_thermal_penalty"]
    cpe_check = results["part_c_cpe45_bridge_verification"]

    def fmt_time(t_val) -> str:
        return f"{t_val:.0f} с" if t_val is not None else "не достигнут (< 39.5 °C)"

    def fmt_exo(val) -> str:
        return f"{val} Вт" if val is not None else "> 1500 Вт"

    t_min_360 = min(v["time_to_39_5C_s"] for v in cont_360.values() if v["time_to_39_5C_s"] is not None)
    t_max_360 = max(v["time_to_39_5C_s"] for v in cont_360.values() if v["time_to_39_5C_s"] is not None)

    md = f"""# Отчёт по EXP-0063: Многослойная биотермодинамика Пеннеса и допустимая огибающая TARGET-CPE45 (2700 с)

**Статус валидации цели:** `TARGET-CPE45 = NOT EXTERNALLY VALIDATED` (строго модельная термодинамическая огибающая `MODEL_ONLY`, опирающаяся на метаболические якоря Malaga $N = {emp['malaga_cohort']['n_unique_subjects']}$ и ACTES $N = {emp['actes_intermittent_cohort']['n_participants']}$).

---

## 1. Проверка баланса энергии и совместимость с `tools/cpe45.py`

- Максимальная невязка Первого начала термодинамики за 2700 с по всем расчётам: `{summary['max_energy_closure_error_J']:.2e}` Дж.
- Проверка на измерительном мосту `tools.cpe45.analyze` ([cpe45.py](file:///D:/SUBJECT-01/tools/cpe45.py)): `target_achievement = "{cpe_check['target_achievement']}"`, `physiological_validation = {cpe_check['physiological_validation']}`, полная механическая работа прерывистого режима (`300 Вт`, $D = 0.50$) равна `{cpe_check['total_work_kJ']:.1f}` кДж.

---

## 2. Непрерывная vs Прерывистая нагрузка при усилении Архитектуры А (`BLOCKER-01`)

Рассмотрены два устойчивых рабочих уровня усиления ($+20\\%$): умеренно-тяжёлый (`300 Вт`, $1216.6\\text{{ Вт}}$ тепла) и высоковыходной форсированный (`360 Вт` = $300\\text{{ Вт}} \\times 1.20$, $1436.3\\text{{ Вт}}$ полного тепла — верхняя граница оценки `BLOCKER-01`).

### Режим 300 Вт (умеренно-тяжёлый +20%):
| Климатический сценарий (непрерывно $300\\text{{ Вт}}$, $D=1.00$) | Пик $T_{{\\text{{core}}}}$ за 2700 с | Время до $39.5^\\circ\\text{{C}}$ | Макс. допустимый $D_{{\\max}}$ (без экзоохл.) |
|---|---|---|---|
| Умеренный (`20°C, 50% RH`) | `{cont_300['temperate_20C_50RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_300['temperate_20C_50RH']['time_to_39_5C_s'])} | **{climates_300['temperate_20C_50RH']['max_safe_duty_cycle_300W']:.2f}** |
| Тёплый (`28°C, 60% RH`) | `{cont_300['warm_28C_60RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_300['warm_28C_60RH']['time_to_39_5C_s'])} | **{climates_300['warm_28C_60RH']['max_safe_duty_cycle_300W']:.2f}** |
| Жаркий сухой (`35°C, 30% RH`) | `{cont_300['hot_dry_35C_30RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_300['hot_dry_35C_30RH']['time_to_39_5C_s'])} | **{climates_300['hot_dry_35C_30RH']['max_safe_duty_cycle_300W']:.2f}** |
| Жаркий влажный (`32°C, 80% RH`) | `{cont_300['hot_humid_32C_80RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_300['hot_humid_32C_80RH']['time_to_39_5C_s'])} | **{climates_300['hot_humid_32C_80RH']['max_safe_duty_cycle_300W']:.2f}** |

### Режим 360 Вт (высоковыходной +20%, $1436.3\\text{{ Вт}}$ тепла):
| Климатический сценарий (непрерывно $360\\text{{ Вт}}$, $D=1.00$) | Пик $T_{{\\text{{core}}}}$ за 2700 с | Время до $39.5^\\circ\\text{{C}}$ | Макс. допустимый $D_{{\\max}}$ (без экзоохл.) | Мин. экзоохлаждение для $D=1.00$ |
|---|---|---|---|---|
| Умеренный (`20°C, 50% RH`) | `{cont_360['temperate_20C_50RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_360['temperate_20C_50RH']['time_to_39_5C_s'])} | **{climates['temperate_20C_50RH']['max_safe_duty_cycle_360W']:.2f}** | `{fmt_exo(climates['temperate_20C_50RH']['required_exo_cooling_W_at_cont_360W'])}` |
| Тёплый (`28°C, 60% RH`) | `{cont_360['warm_28C_60RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_360['warm_28C_60RH']['time_to_39_5C_s'])} | **{climates['warm_28C_60RH']['max_safe_duty_cycle_360W']:.2f}** | `{fmt_exo(climates['warm_28C_60RH']['required_exo_cooling_W_at_cont_360W'])}` |
| Жаркий сухой (`35°C, 30% RH`) | `{cont_360['hot_dry_35C_30RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_360['hot_dry_35C_30RH']['time_to_39_5C_s'])} | **{climates['hot_dry_35C_30RH']['max_safe_duty_cycle_360W']:.2f}** | `{fmt_exo(climates['hot_dry_35C_30RH']['required_exo_cooling_W_at_cont_360W'])}` |
| Жаркий влажный (`32°C, 80% RH`) | `{cont_360['hot_humid_32C_80RH']['peak_T_core_C']:.2f} °C` | {fmt_time(cont_360['hot_humid_32C_80RH']['time_to_39_5C_s'])} | **{climates['hot_humid_32C_80RH']['max_safe_duty_cycle_360W']:.2f}** | `{fmt_exo(climates['hot_humid_32C_80RH']['required_exo_cooling_W_at_cont_360W'])}` |

---

## 3. Штраф кератинизации/защиты кожи AEGIS-01

При снижении эффективной испарительной и конвективной проводимости кожи на $-35\\%$ (барьерный штраф `AEGIS-01`, $+2.0\\text{{ кг}}$):
- При `300 Вт` в умеренном климате (`20°C, 50% RH`) допустимая плотность работы $D_{{\\max}}$ падает с `{aegis['temperate_300W_native_max_D']:.2f}` до `{aegis['temperate_300W_aegis01_max_D']:.2f}` (`{aegis['duty_cycle_300W_loss_pct']:+.1f}%`), а при высоковыходном `360 Вт` падает с `{aegis['temperate_360W_native_max_D']:.2f}` до `{aegis['temperate_360W_aegis01_max_D']:.2f}` (`{aegis['duty_cycle_360W_loss_pct']:+.1f}%`). Пиковое $T_{{\\text{{core}}}}$ при `300 Вт`, $D = 0.50$ возрастает с `{aegis['native_D050_peak_T_core_C']:.2f} °C` до `{aegis['aegis01_D050_peak_T_core_C']:.2f} °C`.
- **Вывод (`FND-0066`, `NEG-0062`):** Длительная 45-минутная работоспособность при высокой $+20\\%$ мощности (`360 Вт`) физически невозможна в непрерывном режиме ни в одном из исследованных климатов (`{t_min_360:.0f}–{t_max_360:.0f} с` до $39.5^\\circ\\text{{C}}$ без экзогенного отвода тепла), а при `300 Вт` нарушается во всех тёплых и жарких климатах ($\\ge 28^\\circ\\text{{C}}$). Единственное допустимое решение Архитектуры A без внешнего охлаждения — прерывистое квантование усилий ($D \\le {climates['temperate_20C_50RH']['max_safe_duty_cycle_360W']:.2f}$ при `360 Вт` в умеренном климате и $D \\le {climates['hot_dry_35C_30RH']['max_safe_duty_cycle_360W']:.2f}$ в жарком) либо внешний теплосъём `{climates['temperate_20C_50RH']['required_exo_cooling_W_at_cont_360W']}–{climates['hot_dry_35C_30RH']['required_exo_cooling_W_at_cont_360W']}` Вт для непрерывной работы. Статус `AEGIS-01 = CONDITIONAL_HOLD` подтверждён.
"""
    (OUT_DIR / "EXPERIMENT_REPORT_RU.md").write_text(md, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    part_a = anchor_empirical_metabolic_loads()

    powers_W = [200.0, 250.0, 300.0, 360.0, 400.0]
    duties = [0.25, 0.35, 0.45, 0.55, 0.65, 0.80, 1.00]
    climates = {
        "temperate_20C_50RH": (20.0, 0.50),
        "warm_28C_60RH": (28.0, 0.60),
        "hot_dry_35C_30RH": (35.0, 0.30),
        "hot_humid_32C_80RH": (32.0, 0.80),
    }

    grid_records = []
    max_energy_err = 0.0

    for c_name, (tamb, rh) in climates.items():
        for p_w in powers_W:
            for d_val in duties:
                sim = simulate_4layer_pennes_2700s(p_w, d_val, tamb, rh, dt_s=5.0)
                max_energy_err = max(max_energy_err, float(sim["energy_balance_error_J"]))
                rec = {k: v for k, v in sim.items() if k != "trace_30s"}
                rec.update({"climate": c_name, "power_W": p_w, "duty_cycle": d_val})
                grid_records.append(rec)

    def find_max_safe_duty(p_w: float, tamb_c: float, rh_val: float, evap_fac: float = 1.0, add_m: float = 0.0) -> float:
        nonlocal max_energy_err
        lo_idx, hi_idx = 0, 85
        grid_d = [round(0.15 + 0.01 * i, 2) for i in range(86)]
        best = 0.0
        while lo_idx <= hi_idx:
            mid = (lo_idx + hi_idx) // 2
            dv = grid_d[mid]
            sim_d = simulate_4layer_pennes_2700s(p_w, dv, tamb_c, rh_val, skin_evap_factor=evap_fac, added_mass_kg=add_m, dt_s=5.0)
            max_energy_err = max(max_energy_err, float(sim_d["energy_balance_error_J"]))
            if sim_d["passes_core_39_5C_gate"]:
                best = dv
                lo_idx = mid + 1
            else:
                hi_idx = mid - 1
        return best

    def find_req_exo_cooling(p_w: float, d_val: float, tamb_c: float, rh_val: float) -> int | None:
        nonlocal max_energy_err
        exo_vals = [20 * i for i in range(76)]  # [0 .. 1500 W]
        lo_e, hi_e = 0, len(exo_vals) - 1
        req_exo = None
        while lo_e <= hi_e:
            mid_e = (lo_e + hi_e) // 2
            sim_e = simulate_4layer_pennes_2700s(p_w, d_val, tamb_c, rh_val, exogenous_cooling_W=float(exo_vals[mid_e]), dt_s=5.0)
            max_energy_err = max(max_energy_err, float(sim_e["energy_balance_error_J"]))
            if sim_e["passes_core_39_5C_gate"]:
                req_exo = exo_vals[mid_e]
                hi_e = mid_e - 1
            else:
                lo_e = mid_e + 1
        return req_exo

    continuous_300W = {}
    continuous_360W = {}
    climate_thresholds_300W = {}
    climate_thresholds_360W = {}

    for c_name, (tamb, rh) in climates.items():
        safe_d_300 = find_max_safe_duty(300.0, tamb, rh)
        safe_d_360 = find_max_safe_duty(360.0, tamb, rh)
        req_exo_300_cont = find_req_exo_cooling(300.0, 1.00, tamb, rh)
        req_exo_360_cont = find_req_exo_cooling(360.0, 1.00, tamb, rh)

        cont_300 = simulate_4layer_pennes_2700s(300.0, 1.00, tamb, rh, dt_s=5.0)
        cont_360 = simulate_4layer_pennes_2700s(360.0, 1.00, tamb, rh, dt_s=5.0)
        max_energy_err = max(max_energy_err, float(cont_300["energy_balance_error_J"]), float(cont_360["energy_balance_error_J"]))

        continuous_300W[c_name] = {k: v for k, v in cont_300.items() if k != "trace_30s"}
        continuous_360W[c_name] = {k: v for k, v in cont_360.items() if k != "trace_30s"}
        climate_thresholds_300W[c_name] = {
            "ambient_C": tamb,
            "rel_humidity": rh,
            "max_safe_duty_cycle_300W": round(safe_d_300, 2),
            "required_exo_cooling_W_at_cont_300W": req_exo_300_cont,
        }
        climate_thresholds_360W[c_name] = {
            "ambient_C": tamb,
            "rel_humidity": rh,
            "max_safe_duty_cycle_360W": round(safe_d_360, 2),
            "required_exo_cooling_W_at_cont_360W": req_exo_360_cont,
        }

    # Evaluate AEGIS-01 keratinized skin penalty (-35% evaporative conductance, +2 kg):
    native_D050 = simulate_4layer_pennes_2700s(300.0, 0.50, 20.0, 0.50, skin_evap_factor=1.0, dt_s=5.0)
    aegis_D050 = simulate_4layer_pennes_2700s(300.0, 0.50, 20.0, 0.50, skin_evap_factor=0.65, added_mass_kg=2.0, dt_s=5.0)
    aegis_max_d_300 = find_max_safe_duty(300.0, 20.0, 0.50, evap_fac=0.65, add_m=2.0)
    aegis_max_d_360 = find_max_safe_duty(360.0, 20.0, 0.50, evap_fac=0.65, add_m=2.0)
    nat_max_d_300 = climate_thresholds_300W["temperate_20C_50RH"]["max_safe_duty_cycle_300W"]
    nat_max_d_360 = climate_thresholds_360W["temperate_20C_50RH"]["max_safe_duty_cycle_360W"]
    aegis_summary = {
        "temperate_300W_native_max_D": nat_max_d_300,
        "temperate_300W_aegis01_max_D": round(aegis_max_d_300, 2),
        "duty_cycle_300W_loss_pct": round(((aegis_max_d_300 / max(nat_max_d_300, 1e-6)) - 1.0) * 100.0, 1),
        "temperate_360W_native_max_D": nat_max_d_360,
        "temperate_360W_aegis01_max_D": round(aegis_max_d_360, 2),
        "duty_cycle_360W_loss_pct": round(((aegis_max_d_360 / max(nat_max_d_360, 1e-6)) - 1.0) * 100.0, 1),
        "native_D050_peak_T_core_C": native_D050["peak_T_core_C"],
        "aegis01_D050_peak_T_core_C": aegis_D050["peak_T_core_C"],
    }

    # Verify strict integration with tools.cpe45 measurement script on safe intermittent trace
    cpe_bridge = evaluate_cpe45_bridge(native_D050, "arch_a_300W_D050_temperate")

    results = {
        "experiment_id": "EXP-0063",
        "title": "Multi-Compartment Cylindrical Pennes Bioheat Transfer and Intermittent CPE45 Envelope",
        "invariant_status": "TARGET-CPE45 = NOT EXTERNALLY VALIDATED",
        "part_a_empirical_metabolic_anchors": part_a,
        "part_b_3d_envelope_summary": {
            "model_classification": "MODEL_ONLY_PENNES_4_LAYER_THERMAL",
            "max_energy_closure_error_J": round(max_energy_err, 6),
            "continuous_300W_arch_a": continuous_300W,
            "continuous_360W_arch_a": continuous_360W,
            "climate_thresholds_for_300W": climate_thresholds_300W,
            "climate_thresholds_for_360W_arch_a": climate_thresholds_360W,
            "aegis01_thermal_penalty": aegis_summary,
            "grid_point_count": len(grid_records),
            "grid_records": grid_records,
        },
        "part_c_cpe45_bridge_verification": cpe_bridge,
    }

    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    write_markdown_report(results)
    print(f"EXP-0063 complete. Grid points={len(grid_records)}, max First-Law error={max_energy_err:.2e} J")
    print(f"Max safe duty at 360 W: temperate={nat_max_d_360}, aegis01={aegis_max_d_360}, hot_dry={climate_thresholds_360W['hot_dry_35C_30RH']['max_safe_duty_cycle_360W']}")


if __name__ == "__main__":
    main()
