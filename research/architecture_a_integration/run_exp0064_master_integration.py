#!/usr/bin/env python3
"""
EXP-0064: Master Integration & Canonical Specification of Architecture A
across Single-Joint, Closed-Chain (EXP-0061), Enthesis Viscoelastic/Heterochrony (EXP-0062),
and Multi-Compartment Pennes Bioheat Constraints (EXP-0063).

Synthesizes all computational stages of PLAN.md and MASTER_ROADMAP.md and enforces
every hard scientific invariant of SUBJECT-01.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FUN_VAL_JSON = ROOT / "research/functional_mechanics_validation/RESULTS.json"
EXP61_JSON = ROOT / "research/exp0061_multijoint_legpress/RESULTS.json"
EXP62_JSON = ROOT / "research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json"
EXP63_JSON = ROOT / "research/exp0063_pennes_bioheat_cpe45/RESULTS.json"
CPE45_SPEC_JSON = ROOT / "research/targets/CPE45.json"
OUT_DIR = ROOT / "research/architecture_a_integration"


def build_canonical_specification_md(res: dict) -> str:
    p1 = res["pillar_summaries"]["pillar_1_contractile_and_closed_chain"]
    p2 = res["pillar_summaries"]["pillar_2_enthesis_viscoelastic_and_heterochrony"]
    p3 = res["pillar_summaries"]["pillar_3_pennes_bioheat_cpe45"]
    mat = res["master_decision_matrix"]

    return f"""# Каноническая спецификация Архитектуры А (SUBJECT-01 Architecture A Canonical Specification)

**Идентификатор:** `EXP-0064` · **Статус программы:** завершение вычислительного и протокольного плана [PLAN.md](file:///D:/SUBJECT-01/PLAN.md) и [MASTER_ROADMAP.md](file:///D:/SUBJECT-01/MASTER_ROADMAP.md)  
**Категория зрелости:** Смешанная триада (`EVIDENCE-BASED` якоря + `MODEL_ONLY / CONDITIONAL POTENTIAL` системный синтез + `DATA_BLOCKED` для внешнего двустороннего жима и 2700-с CPE45)

---

## 1. Инварианты безопасности и эпистемологические границы

1. `TARGET-CPE45 = NOT EXTERNALLY VALIDATED` (подтверждено инвариантом [CPE45.json](file:///D:/SUBJECT-01/research/targets/CPE45.json): `historical_experiments_cpe45_status = "not_assessed"`, `success_thresholds = null`).
2. `BIOLOGICAL INTERVENTIONS = NO_GO` (любые генетические, фармакологические или хирургические вмешательства на человеке запрещены).
3. `STRENGTH +20% = THEORETICALLY_FEASIBLE_WITH_COORDINATED_TENDON_ADAPTATION` (**не валидирована in vivo**).
4. `EXP-0061 (Bilateral Isometric Leg Press Cohort Transfer) = DATA_BLOCKED` (0 из 6 кандидатов прошли гейты допуска; парный бутстрэп выполнен на односуставном референсе `DPValid` со сменой протокола `PROTOCOL_SHIFT_SINGLE_JOINT_REFERENCE`).

---

## 2. Столп 1: Сократительный профиль и многосуставная замкнутая цепь (`EXP-0059`, `EXP-0061`)

- **Калибровка удельного напряжения (`DPValid`, $N = 20$):** $\\sigma = {p1['dpvalid_specific_tension_n_cm2']:.2f} \\pm {p1['dpvalid_specific_tension_sd_n_cm2']:.2f}\\text{{ Н/см}}^2$ ($95\\%$ MC-интервал $[17.58, 44.98]\\text{{ Н/см}}^2$, [`NEG-0058`](file:///D:/SUBJECT-01/registry/negative_results.json#L469-L475)).
- **Односуставный референсный бенчмарк (`DPValid`, парный кластерный бутстрэп $B = 10\\,000$):** модель PCSA `M2` даёт $\\Delta R^2_{{\\text{{pooled}}}} = {p1['dpvalid_m2_vs_f0_cond_delta_r2']:+.4f}$ ($95\\%$ ДИ `[{p1['dpvalid_m2_vs_f0_cond_ci95'][0]:+.4f}, {p1['dpvalid_m2_vs_f0_cond_ci95'][1]:+.4f}]`) относительно простой антропометрии `Baseline F0` и `{p1['dpvalid_m2_vs_m1_cond_delta_r2']:+.4f}` (`[{p1['dpvalid_m2_vs_m1_cond_ci95'][0]:+.4f}, {p1['dpvalid_m2_vs_m1_cond_ci95'][1]:+.4f}]`) относительно `M1` — оба попадают в **`Outcome 3: INCONCLUSIVE`** при $\\Delta_{{\\min}} = 0.08$.
- **Стратегия 2 Архитектуры А (односуставный оптимум, $V = \\text{{const}}$):** $\\Delta\\theta = +2.0^\\circ$ ($14^\\circ \\to 16^\\circ$), $\\Delta\\sigma = +8\\%$, $\\Delta\\tilde{{v}}_{{\\max}} = +12\\%$, $\\Delta\\text{{CSA}} = +15\\%$, $\\Delta\\text{{UTS}} = +8\\% \\implies$ момент **$+{p1['strategy2_torque_gain_pct']:.1f}\\%$**, $v_{{\\max}}$ **{p1['strategy2_vmax_change_pct']:+.1f}%**, мощность **$+{p1['strategy2_power_gain_pct']:.1f}\\%$**.
- **Многосуставная 3-DOF замкнутая цепь жима (`EXP-0061`, `MODEL_ONLY`):**
  * Наивное $a_i \\equiv 0.95$ несовместно (точечная невязка `{p1['naive_point_contact_residual_Nm']:.1f}` Н·м, выход $x_{{\\text{{COP}}}} = +{p1['naive_x_cop_m']:.4f}$ м за границу $+0.16$ м).
  * Изолированный рост квадрицепса $+20\\%$ передаётся на платформу с потерями: $+{p1['quad_only_20_legpress_gain_100deg_pct']:.2f}\\%$ ($\\eta_{{\\text{{chain}}}} = {p1['quad_only_20_eta_chain_100deg']:.3f}$ при $100^\\circ$ колена).
  * Согласованная перестройка цепи (Стратегия 2 по разгибателям бедра, колена и голеностопа) обеспечивает **$+{p1['strategy2_chain_legpress_gain_100deg_pct']:.2f}\\%$** силы на упоре ($\\eta_{{\\text{{chain}}}} = {p1['strategy2_chain_eta_chain_100deg']:.3f}$), а с реципрокным торможением антагонистов ($-25\\%$) — **$+{p1['strategy2_synergy_legpress_gain_100deg_pct']:.2f}\\%$**.

---

## 3. Столп 2: Вязкоупругий предел энтезиса ($dF/dt$) и гетерохрония (`EXP-0060`, `EXP-0062`)

- **Закон сохранения циклического ресурса (`FND-0063`):** $(1 + \\Delta_{{\\text{{CSA}}}}) (1 + \\Delta_{{\\text{{UTS}}}}) \\ge \\lambda_F$. Для $\\lambda_F = 1.20$ адаптация Case 2C ($+15\\%$ CSA, $+10\\%$ UTS) снижает $\\sigma_{{\\text{{nom}}}}$ до `40.13` МПа и даёт $1.678\\times$ расчётного ресурса при одноосном циклическом нагружении.
- **Многослойная вязкоупругая модель сдвига ($dF/dt = 20\\,000\\text{{ Н/с}}$, калибровка по Bogaerts $N = 10$):**
  * Глубокий слой перегружен относительно поверхностного (коэффициент смещения `{p2['bogaerts_deep_sup_ratio']:.3f}`, коэффициент напряжения $k_{{\\text{{deep}}}} = {p2['k_deep']:.3f}$).
  * На уровне $4800\\text{{ Н}}$ ($+20\\%$ от базы `EXP-0060`): без адаптации $\\sigma_{{\\text{{vM,peak}}}} = {p2['s1_4800N_20kNs_vm_MPa']:.2f}$ МПа ($SF_{{\\text{{local}}}} = {p2['s1_4800N_20kNs_sf_local']:.2f}$); Case 2C восстанавливает $SF_{{\\text{{local}}}} = {p2['s2_4800N_20kNs_sf_local']:.2f} \\ge 1.50$.
  * На уровне пикового баллистического 100% MVC ($7661\\text{{ Н}}$): без адаптации $\\sigma_{{\\text{{vM,peak}}}} = {p2['mvc_7661N_20kNs_vm_MPa']:.2f}$ МПа **превышает порог текучести коллагена $85\\text{{ МПа}}$** ($SF_{{\\text{{local}}}} = {p2['mvc_7661N_20kNs_sf_local']:.2f}$); Case 2C снижает $\\sigma_{{\\text{{vM,peak}}}}$ до `{p2['mvc_case2c_7661N_20kNs_vm_MPa']:.2f}` МПа ($< 85$ МПа, но $SF_{{\\text{{local}}}} = {p2['mvc_case2c_7661N_20kNs_sf_local']:.2f} < 1.50$), указывая на необходимость ограничения взрывных 100% MVC баллистических фронтов либо $\\Delta\\text{{CSA}} > 20\\%$ на энтезисе.
- **Гетерохрония ремоделирования (`BLOCKER-03`):** несогласованное форсирование `TARGET-ADAPT25` ($\\tau_m = 12$ дн. против $\\tau_t = 90$ дн.) вызывает пик усталостного риска **`{p2['h1_peak_damage_ratio']:.2f}x`** на {p2['h1_peak_week']:.1f}-й неделе; синхронизированная прогрессия по сухожилию (H2) удерживает риск на `{p2['h2_peak_damage_ratio']:.2f}x`.

---

## 4. Столп 3: 4-слойная биотермодинамика Пеннеса и огибающая CPE45 (`EXP-0063`)

- **Эмпирические якоря:** Malaga CPET (`N = {p3['malaga_n_subjects']}` уникальных субъектов, c_ox = `21.374` кДж/л O2) и ACTES (`N = {p3['actes_n_subjects']}`). Максимальная невязка баланса энергии модели за 2700 с: `{p3['max_energy_error_J']:.2e}` Дж.
- **Непрерывная высоковыходная нагрузка ($360\\text{{ Вт}}$, $+20\\%$ от $300\\text{{ Вт}}$, $D = 1.00$):** во всех исследованных климатах $\\ge 20^\\circ\\text{{C}}$ температура ядра превышает $39.5^\\circ\\text{{C}}$ (`{p3['cont_360W_temperate_peak_C']:.2f} °C` за `{p3['cont_360W_temperate_t395_s']:.0f}` с в умеренном климате и `{p3['cont_360W_hot_humid_peak_C']:.2f} °C` за `{p3['cont_360W_hot_humid_t395_s']:.0f}` с в жарком влажном); при умеренной нагрузке $300\\text{{ Вт}}$ перегрев наступает во всех тёплых и жарких климатах ($28\\text{{–}}35^\\circ\\text{{C}}$).
- **Допустимая прерывистая огибающая (`D_max` для $T_{{\\text{{core}}}} < 39.5^\\circ\\text{{C}}$ на 2700 с при $360\\text{{ Вт}}$):**
  * Умеренный климат (`20°C, 50% RH`): $D \\le {p3['d_max_temperate_360W']:.2f}$ (с `AEGIS-01` падает до $D \\le {p3['d_max_aegis01_360W']:.2f}$, потеря `{p3['aegis01_loss_360W_pct']:+.1f}%`);
  * Тёплый (`28°C, 60% RH`): $D \\le {p3['d_max_warm_360W']:.2f}$;
  * Жаркий сухой (`35°C, 30% RH`): $D \\le {p3['d_max_hot_dry_360W']:.2f}$;
  * Жаркий влажный (`32°C, 80% RH`): $D \\le {p3['d_max_hot_humid_360W']:.2f}$ (для непрерывной работы $360\\text{{ Вт}}$ требуется внешний сосудистый теплосъём `{p3['exo_cool_hot_humid_cont_360W_W']} Вт`).

---

## 5. Итоговая матрица решений программы SUBJECT-01 (`DEC-0026`)

| Направление / Цель | Итоговый статус | Категория зрелости | Обоснование и граничное условие |
|---|---|---|---|
| **TARGET-FORCE20 (Architecture A)** | **`{mat['TARGET-FORCE20']['status']}`** | `{mat['TARGET-FORCE20']['maturity']}` | {mat['TARGET-FORCE20']['rationale']} |
| **EXP-0061 (Bilateral Leg Press External Test)** | **`{mat['EXP-0061_LegPress']['status']}`** | `{mat['EXP-0061_LegPress']['maturity']}` | {mat['EXP-0061_LegPress']['rationale']} |
| **TARGET-ADAPT25 (+25% Speed)** | **`{mat['TARGET-ADAPT25']['status']}`** | `{mat['TARGET-ADAPT25']['maturity']}` | {mat['TARGET-ADAPT25']['rationale']} |
| **TARGET-CPE45 (2700 s Endurance)** | **`{mat['TARGET-CPE45']['status']}`** | `{mat['TARGET-CPE45']['maturity']}` | {mat['TARGET-CPE45']['rationale']} |
| **AEGIS-01 Integration (PR #9)** | **`{mat['AEGIS-01']['status']}`** | `{mat['AEGIS-01']['maturity']}` | {mat['AEGIS-01']['rationale']} |
| **Architecture B (Bioengineered Muscle)** | **`{mat['Architecture_B']['status']}`** | `NO_GO` | {mat['Architecture_B']['rationale']} |
| **Architecture C (Internal Biohybrid)** | **`{mat['Architecture_C']['status']}`** | `HOLD / BREAKTHROUGH_DEPENDENT` | {mat['Architecture_C']['rationale']} |
| **Biological Human Interventions** | **`{mat['Biological_Interventions']['status']}`** | `HARD_INVARIANT_NO_GO` | {mat['Biological_Interventions']['rationale']} |
| **MTJCore Programme** | **`{mat['MTJCore']['status']}`** | `COMPLETED / HOLD_PENDING_NEW_EVIDENCE` | {mat['MTJCore']['rationale']} |
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fv = json.loads(FUN_VAL_JSON.read_text(encoding="utf-8"))
    e61 = json.loads(EXP61_JSON.read_text(encoding="utf-8"))
    e62 = json.loads(EXP62_JSON.read_text(encoding="utf-8"))
    e63 = json.loads(EXP63_JSON.read_text(encoding="utf-8"))
    cpe_spec = json.loads(CPE45_SPEC_JSON.read_text(encoding="utf-8"))

    # Hard runtime invariant assertions
    assert cpe_spec["historical_experiments_cpe45_status"] == "not_assessed", "CPE45 historical status invariant violated!"
    assert cpe_spec["success_thresholds"] is None, "CPE45 success_thresholds invariant violated!"
    assert e63["part_c_cpe45_bridge_verification"]["target_achievement"] == "not_assessed", "CPE45 bridge target_achievement must stay not_assessed!"
    assert e63["part_c_cpe45_bridge_verification"]["physiological_validation"] is False

    def find_rate(case_key: str, rate: int = 20000) -> dict:
        for r in e62["part_b_viscoelastic_enthesis_rates"]["rate_sweep_results"][case_key]:
            if r["dF_dt_N_s"] == rate:
                return r
        raise KeyError(f"{case_key}/{rate}")

    b_cond = e61["part_b_dpvalid_reference_benchmark"]["paired_cluster_bootstrap_condition_level"]
    sc_chain = e61["part_c_closed_chain_3dof_model"]["scenarios"]
    s2_int = fv["integrated_model"]["deterministic_scenarios"]["strategy_2_coordinated_biological_enhancement"]
    s1_4800 = find_rate("s1_unadapted_plus20_4800N", 20000)
    s2_4800 = find_rate("s2_case2c_adapted_plus20_4800N", 20000)
    m1_7661 = find_rate("mvc_unadapted_plus20_7661N", 20000)
    m2_7661 = find_rate("mvc_adapted_case2c_7661N", 20000)

    cont300 = e63["part_b_3d_envelope_summary"]["continuous_300W_arch_a"]
    cont360 = e63["part_b_3d_envelope_summary"]["continuous_360W_arch_a"]
    clim_th300 = e63["part_b_3d_envelope_summary"]["climate_thresholds_for_300W"]
    clim_th360 = e63["part_b_3d_envelope_summary"]["climate_thresholds_for_360W_arch_a"]
    aegis = e63["part_b_3d_envelope_summary"]["aegis01_thermal_penalty"]

    pillar_summaries = {
        "pillar_1_contractile_and_closed_chain": {
            "dpvalid_specific_tension_n_cm2": fv["muscle_audit"]["specific_tension_evaluations"]["corrected_convA_single_cosine"]["mean_n_cm2"],
            "dpvalid_specific_tension_sd_n_cm2": fv["muscle_audit"]["specific_tension_evaluations"]["corrected_convA_single_cosine"]["std_n_cm2"],
            "dpvalid_m2_vs_f0_cond_delta_r2": b_cond["M2_vs_Baseline_F0"]["delta_r2_pooled_point"],
            "dpvalid_m2_vs_f0_cond_ci95": b_cond["M2_vs_Baseline_F0"]["ci95_cluster_bootstrap"],
            "dpvalid_m2_vs_m1_cond_delta_r2": b_cond["M2_vs_M1_anthro_age"]["delta_r2_pooled_point"],
            "dpvalid_m2_vs_m1_cond_ci95": b_cond["M2_vs_M1_anthro_age"]["ci95_cluster_bootstrap"],
            "strategy2_torque_gain_pct": s2_int["torque_gain_pct"],
            "strategy2_vmax_change_pct": s2_int["absolute_vmax_change_pct"],
            "strategy2_power_gain_pct": s2_int["peak_power_change_pct"],
            "naive_point_contact_residual_Nm": sc_chain["baseline"]["postures"]["flexed_100deg_int"]["naive_uncoordinated_diagnostics"]["point_contact_overdetermination_residual_Nm"],
            "naive_x_cop_m": sc_chain["baseline"]["postures"]["flexed_100deg_int"]["naive_uncoordinated_diagnostics"]["naive_x_cop_m"],
            "quad_only_20_legpress_gain_100deg_pct": sc_chain["quad_only_plus20"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["bilateral_footplate_force_gain_pct"],
            "quad_only_20_eta_chain_100deg": sc_chain["quad_only_plus20"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["closed_chain_transfer_ratio_eta"],
            "strategy2_chain_legpress_gain_100deg_pct": sc_chain["strategy_2_coordinated_chain"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["bilateral_footplate_force_gain_pct"],
            "strategy2_chain_eta_chain_100deg": sc_chain["strategy_2_coordinated_chain"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["closed_chain_transfer_ratio_eta"],
            "strategy2_synergy_legpress_gain_100deg_pct": sc_chain["strategy_2_plus_reciprocal_inhibition"]["postures"]["flexed_100deg_int"]["comparison_to_baseline"]["bilateral_footplate_force_gain_pct"],
        },
        "pillar_2_enthesis_viscoelastic_and_heterochrony": {
            "bogaerts_deep_sup_ratio": e62["part_a_bogaerts_calibration"]["deep_to_superficial_ratio"],
            "k_deep": e62["part_a_bogaerts_calibration"]["calibrated_layer_stress_multipliers"]["deep_k"],
            "s1_4800N_20kNs_vm_MPa": s1_4800["peak_von_mises_stress_MPa"],
            "s1_4800N_20kNs_sf_local": s1_4800["local_enthesis_safety_factor"],
            "s2_4800N_20kNs_vm_MPa": s2_4800["peak_von_mises_stress_MPa"],
            "s2_4800N_20kNs_sf_local": s2_4800["local_enthesis_safety_factor"],
            "mvc_7661N_20kNs_vm_MPa": m1_7661["peak_von_mises_stress_MPa"],
            "mvc_7661N_20kNs_sf_local": m1_7661["local_enthesis_safety_factor"],
            "mvc_case2c_7661N_20kNs_vm_MPa": m2_7661["peak_von_mises_stress_MPa"],
            "mvc_case2c_7661N_20kNs_sf_local": m2_7661["local_enthesis_safety_factor"],
            "h1_peak_damage_ratio": e62["part_c_remodeling_heterochrony_ode"]["regimes"]["H1_uncoordinated_target_adapt25_12d"]["peak_daily_damage_acceleration_ratio"],
            "h1_peak_week": e62["part_c_remodeling_heterochrony_ode"]["regimes"]["H1_uncoordinated_target_adapt25_12d"]["peak_hazard_week"],
            "h2_peak_damage_ratio": e62["part_c_remodeling_heterochrony_ode"]["regimes"]["H2_tendon_paced_synchronized"]["peak_daily_damage_acceleration_ratio"],
        },
        "pillar_3_pennes_bioheat_cpe45": {
            "malaga_n_subjects": e63["part_a_empirical_metabolic_anchors"]["malaga_cohort"]["n_unique_subjects"],
            "actes_n_subjects": e63["part_a_empirical_metabolic_anchors"]["actes_intermittent_cohort"]["n_participants"],
            "max_energy_error_J": e63["part_b_3d_envelope_summary"]["max_energy_closure_error_J"],
            "cont_300W_warm_peak_C": cont300["warm_28C_60RH"]["peak_T_core_C"],
            "cont_360W_temperate_peak_C": cont360["temperate_20C_50RH"]["peak_T_core_C"],
            "cont_360W_temperate_t395_s": cont360["temperate_20C_50RH"]["time_to_39_5C_s"],
            "cont_360W_hot_humid_peak_C": cont360["hot_humid_32C_80RH"]["peak_T_core_C"],
            "cont_360W_hot_humid_t395_s": cont360["hot_humid_32C_80RH"]["time_to_39_5C_s"],
            "d_max_temperate_300W": clim_th300["temperate_20C_50RH"]["max_safe_duty_cycle_300W"],
            "d_max_warm_300W": clim_th300["warm_28C_60RH"]["max_safe_duty_cycle_300W"],
            "d_max_temperate_360W": clim_th360["temperate_20C_50RH"]["max_safe_duty_cycle_360W"],
            "d_max_warm_360W": clim_th360["warm_28C_60RH"]["max_safe_duty_cycle_360W"],
            "d_max_hot_dry_360W": clim_th360["hot_dry_35C_30RH"]["max_safe_duty_cycle_360W"],
            "d_max_hot_humid_360W": clim_th360["hot_humid_32C_80RH"]["max_safe_duty_cycle_360W"],
            "d_max_aegis01_360W": aegis["temperate_360W_aegis01_max_D"],
            "aegis01_loss_360W_pct": aegis["duty_cycle_360W_loss_pct"],
            "exo_cool_hot_humid_cont_360W_W": clim_th360["hot_humid_32C_80RH"]["required_exo_cooling_W_at_cont_360W"],
        },
    }

    decision_matrix = {
        "TARGET-FORCE20": {
            "status": "CONDITIONAL_POTENTIAL_MODEL_FEASIBLE_NOT_VALIDATED_IN_VIVO",
            "maturity": "CONDITIONAL POTENTIAL",
            "rationale": f"Closed-chain Strategy 2 reaches +{pillar_summaries['pillar_1_contractile_and_closed_chain']['strategy2_chain_legpress_gain_100deg_pct']:.2f}% bilateral force with Case 2C SF_local={s2_4800['local_enthesis_safety_factor']:.2f} at 4800 N; extreme ballistic 100% MVC (7661 N) drops local enthesis SF to {m2_7661['local_enthesis_safety_factor']:.2f} < 1.50 without extra CSA or dF/dt cap.",
        },
        "EXP-0061_LegPress": {
            "status": "DATA_BLOCKED",
            "maturity": "EVIDENCE_GATE_BLOCKED",
            "rationale": "0/6 audited datasets pass open bilateral isometric leg press requirements; DPValid single-joint reference yields Outcome 3 INCONCLUSIVE (N=20).",
        },
        "TARGET-ADAPT25": {
            "status": "HOLD_RATE_LIMITED_BY_COLLAGEN_SYNTHESIS",
            "maturity": "CONDITIONAL POTENTIAL",
            "rationale": f"Uncoordinated +25% adaptation accelerates transient tendon damage {pillar_summaries['pillar_2_enthesis_viscoelastic_and_heterochrony']['h1_peak_damage_ratio']:.2f}x around week {pillar_summaries['pillar_2_enthesis_viscoelastic_and_heterochrony']['h1_peak_week']:.1f}; risk eliminated ({pillar_summaries['pillar_2_enthesis_viscoelastic_and_heterochrony']['h2_peak_damage_ratio']:.2f}x) only under tendon-paced progression H2.",
        },
        "TARGET-CPE45": {
            "status": "NOT_EXTERNALLY_VALIDATED_CONDITIONAL_HOLD",
            "maturity": "MODEL_ONLY_INTERMITTENT_ENVELOPE",
            "rationale": f"Continuous 360 W breaches 39.5 C in all tested climates (temperate 20 C in {cont360['temperate_20C_50RH']['time_to_39_5C_s']:.0f} s, hot-humid 32 C in {cont360['hot_humid_32C_80RH']['time_to_39_5C_s']:.0f} s); safe over 2700 s only via intermittent pacing (D <= {clim_th360['temperate_20C_50RH']['max_safe_duty_cycle_360W']:.2f} at 20 C, D <= {clim_th360['hot_humid_32C_80RH']['max_safe_duty_cycle_360W']:.2f} at 32 C/80%RH) or active external cooling.",
        },
        "AEGIS-01": {
            "status": "CONDITIONAL_HOLD",
            "maturity": "HOLD",
            "rationale": f"Skin barrier (-35% evaporative conductance, +2 kg) reduces temperate safe duty cycle by {abs(aegis['duty_cycle_300W_loss_pct']):.1f}% at 300 W and {abs(aegis['duty_cycle_360W_loss_pct']):.1f}% at 360 W, compounding BLOCKER-01.",
        },
        "Architecture_B": {
            "status": "DISQUALIFIED_NO_GO",
            "maturity": "NO_GO",
            "rationale": "Preserved from DEC-0021 (compartment syndrome, microvascular ischemia, periosteal avulsion).",
        },
        "Architecture_C": {
            "status": "HOLD_BREAKTHROUGH_DEPENDENT",
            "maturity": "BREAKTHROUGH-DEPENDENT",
            "rationale": "Preserved from DEC-0021 (internal heat rejection and reflex latency incompatibilities).",
        },
        "Biological_Interventions": {
            "status": "NO_GO",
            "maturity": "HARD_INVARIANT",
            "rationale": "Hard program invariant strictly enforced.",
        },
        "MTJCore": {
            "status": "COMPLETED_HOLD_PENDING_NEW_EVIDENCE",
            "maturity": "COMPLETED_STANDALONE_BIOINFORMATICS",
            "rationale": "Preserved from DEC-0023 (manuscript v1.0.3-commsbio-submission prepared, awaiting independent non-Oxford/non-Copenhagen cohort).",
        },
    }

    results = {
        "experiment_id": "EXP-0064",
        "title": "Master Architecture A Integration and Canonical Specification Across Closed-Chain, Enthesis, and Thermal Constraints",
        "invariants": {
            "TARGET_CPE45": "NOT EXTERNALLY VALIDATED",
            "BIOLOGICAL_INTERVENTIONS": "NO_GO",
            "STRENGTH_PLUS20": "THEORETICALLY_FEASIBLE_WITH_COORDINATED_TENDON_ADAPTATION",
        },
        "pillar_summaries": pillar_summaries,
        "master_decision_matrix": decision_matrix,
    }

    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    md_text = build_canonical_specification_md(results)
    (OUT_DIR / "ARCHITECTURE_A_CANONICAL_SPECIFICATION.md").write_text(md_text, encoding="utf-8")
    print("EXP-0064 master integration complete.")


if __name__ == "__main__":
    main()
