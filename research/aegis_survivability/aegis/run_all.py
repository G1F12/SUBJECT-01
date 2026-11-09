#!/usr/bin/env python3
"""AEGIS-01 — Master Simulation Runner (Cycle 2A).

Executes all 11 computational models, generates structured machine-readable JSON
results in data/results/, and outputs consolidated summary CSVs.
"""

from pathlib import Path
import json
import csv
import sys
from typing import Dict, Any

# Ensure aegis is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from aegis import (
    model_01_tissue_mechanics,
    model_02_multilayer_protection,
    model_03_reaction_movement,
    model_04_energy_transfer,
    model_05_hemodynamic_stability,
    model_06_regeneration_dynamics,
    model_07_integrated_architecture,
    model_08_materials_comparison,
    model_09_multiscale_regeneration,
    model_10_cpe45_integration,
    model_11_architecture_pareto,
    model_12_biological_materials,
    model_13_functional_regeneration,
    model_14_architecture_categories,
)

RESULTS_DIR = ROOT / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_all() -> Dict[str, Any]:
    print("=" * 75)
    print("AEGIS-01 MASTER COMPUTATIONAL PIPELINE EXECUTION (CYCLE 2A)")
    print("=" * 75)

    # 1. Model 01
    print("[1/11] Running MODEL-01: Tissue Mechanics & Puncture/Cut...")
    res_m1 = model_01_tissue_mechanics.run_benchmark_scenarios()
    (RESULTS_DIR / "model_01_tissue_mechanics.json").write_text(json.dumps(res_m1, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Model 02
    print("[2/11] Running MODEL-02: Multilayer Protection & Wave Attenuation...")
    res_m2 = model_02_multilayer_protection.run_benchmark_scenarios()
    (RESULTS_DIR / "model_02_multilayer_protection.json").write_text(json.dumps(res_m2, indent=2, ensure_ascii=False), encoding="utf-8")

    # 3. Model 03
    print("[3/11] Running MODEL-03: Neural Latency & Dodge Horizon...")
    res_m3 = model_03_reaction_movement.run_benchmark_scenarios()
    (RESULTS_DIR / "model_03_reaction_movement.json").write_text(json.dumps(res_m3, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4. Model 04
    print("[4/11] Running MODEL-04: Ballistic Energy Transfer & BABT...")
    res_m4 = model_04_energy_transfer.run_benchmark_scenarios()
    (RESULTS_DIR / "model_04_energy_transfer.json").write_text(json.dumps(res_m4, indent=2, ensure_ascii=False), encoding="utf-8")

    # 5. Model 05
    print("[5/11] Running MODEL-05: Hemodynamic Stability & Hemorrhage...")
    res_m5 = model_05_hemodynamic_stability.run_benchmark_scenarios()
    (RESULTS_DIR / "model_05_hemodynamic_stability.json").write_text(json.dumps(res_m5, indent=2, ensure_ascii=False), encoding="utf-8")

    # 6. Model 06
    print("[6/11] Running MODEL-06: Regeneration Dynamics & Oncogenic Limits...")
    res_m6 = model_06_regeneration_dynamics.run_benchmark_scenarios()
    (RESULTS_DIR / "model_06_regeneration_dynamics.json").write_text(json.dumps(res_m6, indent=2, ensure_ascii=False), encoding="utf-8")

    # 7. Model 07
    print("[7/11] Running MODEL-07: Integrated Architecture Trade-offs...")
    res_m7 = model_07_integrated_architecture.run_benchmark_scenarios()
    (RESULTS_DIR / "model_07_integrated_architecture.json").write_text(json.dumps(res_m7, indent=2, ensure_ascii=False), encoding="utf-8")

    # 8. Model 08
    print("[8/11] Running MODEL-08: Comparative Biomaterials Mechanics (Systems A-E)...")
    res_m8 = model_08_materials_comparison.run_comparative_materials_benchmark()
    (RESULTS_DIR / "model_08_materials_comparison.json").write_text(json.dumps(res_m8, indent=2, ensure_ascii=False), encoding="utf-8")

    # 9. Model 09
    print("[9/11] Running MODEL-09: Multi-Scale Regeneration Across 6 Phases...")
    res_m9 = model_09_multiscale_regeneration.run_regeneration_benchmark_suite()
    (RESULTS_DIR / "model_09_multiscale_regeneration.json").write_text(json.dumps(res_m9, indent=2, ensure_ascii=False), encoding="utf-8")

    # 10. Model 10
    print("[10/11] Running MODEL-10: SUBJECT-01 CPE45 2700s Integration...")
    res_m10 = model_10_cpe45_integration.run_cpe45_comprehensive_matrix()
    (RESULTS_DIR / "model_10_cpe45_integration.json").write_text(json.dumps(res_m10, indent=2, ensure_ascii=False), encoding="utf-8")

    # 11. Model 11
    print("[11/14] Running MODEL-11: Multi-Criteria Architecture Comparison & Pareto Optimization...")
    res_m11 = model_11_architecture_pareto.compute_pareto_dominance()
    (RESULTS_DIR / "model_11_architecture_pareto.json").write_text(json.dumps(res_m11, indent=2, ensure_ascii=False), encoding="utf-8")

    # 12. Model 12
    print("[12/14] Running MODEL-12: Biological & Biohybrid Materials Evidence Matrix...")
    res_m12 = model_12_biological_materials.compare_material_archetypes()
    (RESULTS_DIR / "model_12_biological_materials.json").write_text(json.dumps(res_m12, indent=2, ensure_ascii=False), encoding="utf-8")

    # 13. Model 13
    print("[13/14] Running MODEL-13: Functional Multi-Axis Regeneration & Tissue Preservation...")
    res_m13 = model_13_functional_regeneration.run_comprehensive_regeneration_benchmark()
    (RESULTS_DIR / "model_13_functional_regeneration.json").write_text(json.dumps(res_m13, indent=2, ensure_ascii=False), encoding="utf-8")

    # 14. Model 14
    print("[14/14] Running MODEL-14: Three-Tier Categorization & SUBJECT-01 Compatibility...")
    res_m14 = model_14_architecture_categories.run_cross_category_evaluation()
    (RESULTS_DIR / "model_14_architecture_categories.json").write_text(json.dumps(res_m14, indent=2, ensure_ascii=False), encoding="utf-8")

    # Consolidated CSV summary
    summary_csv_path = RESULTS_DIR / "summary_metrics.csv"
    with summary_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Architecture",
            "Total_Mass_kg",
            "Armor_Mass_kg",
            "Resting_Metabolic_W",
            "Max_Sprint_Speed_m_s",
            "Sprint_Pct_Baseline",
            "Hyperthermia_Limit_min",
            "Cut_Puncture_Score",
            "Ballistic_Score",
            "Mobility_Score",
            "Thermal_Score",
            "Hemostasis_Score",
            "Regeneration_Score",
            "Overall_Survivability_Index",
        ])
        for a in res_m7["architectures"]:
            writer.writerow([
                a["architecture_name"],
                a["total_mass_kg"],
                a["armor_mass_kg"],
                a["resting_metabolic_rate_w"],
                a["max_sprint_velocity_m_s"],
                a["sprint_speed_pct_baseline"],
                a["hyperthermia_limit_minutes"],
                a["scores"]["cut_puncture_score"],
                a["scores"]["ballistic_protection_score"],
                a["scores"]["mobility_score"],
                a["scores"]["thermal_sustainability_score"],
                a["scores"]["hemostasis_score"],
                a["scores"]["regeneration_score"],
                a["scores"]["overall_survivability_index"],
            ])

    # Pareto & CPE45 Summary CSV
    pareto_csv_path = RESULTS_DIR / "pareto_summary.csv"
    with pareto_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Arch_ID",
            "Name",
            "Total_Mass_kg",
            "Puncture_Depth_300N_mm",
            "Cutting_Resistance_N",
            "Sprint_Vmax_m_s",
            "CPE45_Work_Net_kJ",
            "Free_Sweat_Skin_Pct",
            "Heat_Dissipation_W",
            "Skin_Closure_Days",
            "Return_90pct_Days",
            "Epistemic_Uncertainty",
            "On_Pareto_Frontier",
        ])
        for aid, a in res_m11["architectures"].items():
            writer.writerow([
                aid,
                a["name"],
                a["total_mass_kg"],
                a["puncture_depth_300N_mm"],
                a["slicing_resistance_N"],
                a["sprint_vmax_m_s"],
                a["cpe45_work_net_kJ"],
                a["free_sweating_skin_pct"],
                a["heat_dissipation_capacity_W"],
                a["skin_cut_closure_days"],
                a["functional_return_90pct_days"],
                a["epistemic_uncertainty_score"],
                aid in res_m11["pareto_frontier"],
            ])

    print(f"\n[SUCCESS] All 14 models executed successfully.")
    print(f"Results stored in: {RESULTS_DIR}")
    print(f"Summary CSVs: {summary_csv_path.name}, {pareto_csv_path.name}")
    return {
        "status": "ALL_MODELS_COMPLETED_PASS",
        "results_directory": str(RESULTS_DIR),
        "models_count": 14,
        "pareto_frontier": res_m11["pareto_frontier"],
    }


if __name__ == "__main__":
    run_all()
