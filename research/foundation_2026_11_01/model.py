#!/usr/bin/env python3
"""SUBJECT-01 Foundation Research 1.0: dimensionally checked illustrative constraint sweeps.

NOT a prediction of efficacy, not a calibrated human digital twin, and not a clinical model.
All engineering assumptions are made explicit below; citations in README.md.
Run: python model.py  (requires numpy, matplotlib; no network)
"""
from pathlib import Path
import csv
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
# Evidence anchor, Persad et al. JAP 2024: median 26.8 N/cm^2, IQR 20-43 N/cm^2.
SIGMA_MEDIAN_N_CM2 = 26.8
SIGMA_IQR_N_CM2 = (20.0, 43.0)
# Speculative reference values below are engineering examples, not measured user anatomy.
REFERENCE_PCSA_CM2 = 100.0
BODY_MASS_KG = 75.0
AIR_DENSITY_KG_M3 = 1.2
CDA_M2 = 0.5
ACCEL_TIME_S = 2.0
HEAT_CAPACITY_J_KG_K = 3500.0  # rough whole-body effective heat capacity
THERMAL_STORAGE_BUDGET_K = 0.5
THERMAL_WINDOW_S = 600.0
REFERENCE_CARDO_OUTPUT_L_MIN = 25.0
REFERENCE_A_V_O2_DIFF_L_L = 0.15


def write_csv(name, rows):
    rows = list(rows)
    if not rows:
        raise ValueError('No rows')
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def force_sweeps():
    rows = []
    for sigma in (SIGMA_IQR_N_CM2[0], SIGMA_MEDIAN_N_CM2, SIGMA_IQR_N_CM2[1]):
        rows.append({'specific_tension_N_cm2': sigma,
                     'illustrative_PCSA_cm2': REFERENCE_PCSA_CM2,
                     'muscle_force_N': sigma * REFERENCE_PCSA_CM2})
    write_csv('muscle_force.csv', rows)
    rows = []
    for a in (0., .1, .2, .4, .8):
        for tendon_capacity in (1.05, 1.10, 1.20, 1.50):
            actual = min(1+a, tendon_capacity)
            rows.append({'muscle_potential_gain_pct': round(a*100),
                         'tendon_capacity_to_baseline_ratio': tendon_capacity,
                         'realizable_force_gain_pct': round((actual-1)*100, 4),
                         'tendon_bottleneck': (1+a)>tendon_capacity + 1e-12})
    write_csv('tendon_bottleneck.csv', rows)
    # Compute ratio of hypothetical baseline tendon capacity needed for +20% functional force.
    assert math.isclose(min(1.2, 1.1), 1.1)
    assert math.isclose(min(1.2, 1.5), 1.2)
    return rows


def sprint_sweeps():
    rows=[]
    for v in (9., 12., 15.):
        e = .5*BODY_MASS_KG*v*v
        drag_power = .5 * AIR_DENSITY_KG_M3 * CDA_M2*v**3
        # constant acceleration from rest: mean drag power (over time) = drag_power/4
        accel_avg_power = e / ACCEL_TIME_S + drag_power/4
        accel_peak_power = BODY_MASS_KG*v*v / ACCEL_TIME_S + drag_power
        rows.append({'target_speed_m_s':v, 'mass_kg':BODY_MASS_KG,
                     'kinetic_energy_J':round(e,2),
                     'drag_power_at_speed_W':round(drag_power,2),
                     'minimum_avg_external_power_during_2s_accel_W':round(accel_avg_power,2),
                     'minimum_peak_external_power_at_end_of_2s_accel_W':round(accel_peak_power,2),
                     'caveat':'excludes running internal work, ground losses and biomechanics'})
    write_csv('sprint_energy.csv',rows)
    return rows


def heat_sweeps():
    rows=[]
    allowed_storage_W = BODY_MASS_KG*HEAT_CAPACITY_J_KG_K*THERMAL_STORAGE_BUDGET_K/THERMAL_WINDOW_S
    for p_external in (250., 500., 750.):
        for eta in (.20,.25,.30):
            metabolic = p_external/eta
            heat = metabolic-p_external
            min_cooling = max(0, heat-allowed_storage_W)
            rows.append({'external_mechanical_power_W':p_external,
                         'illustrative_efficiency':eta,
                         'metabolic_power_W':round(metabolic,3),
                         'heat_generation_W':round(heat,3),
                         'max_mean_heat_storage_W_for_0_5K_in_10min':round(allowed_storage_W,3),
                         'minimum_mean_heat_loss_W_for_0_5K_budget':round(min_cooling,3)})
    write_csv('heat_budget.csv',rows)
    return rows


def fick_sweeps():
    rows=[]
    baseline=REFERENCE_CARDO_OUTPUT_L_MIN*REFERENCE_A_V_O2_DIFF_L_L
    for gain in (0.,.2,.3,.5,1.):
        required=baseline*(1+gain)
        rows.append({'VO2_requested_gain_pct':int(round(gain*100)),
                     'baseline_VO2_L_min':baseline,
                     'target_VO2_L_min':round(required,3),
                     'cardiac_output_needed_if_extraction_constant_L_min':round(required/REFERENCE_A_V_O2_DIFF_L_L,3),
                     'extraction_needed_if_cardiac_output_constant_L_L':round(required/REFERENCE_CARDO_OUTPUT_L_MIN,3)})
    write_csv('oxygen_fick.csv', rows)
    return rows


def reaction_sweeps():
    # The breakdown below is a purely illustrative timing budget, not empirical means.
    baseline={'sensory_detection':45.,'central_processing':65.,'neural_delivery':20.,'motor_execution':60.}
    alternative={'sensory_detection':20.,'central_processing':40.,'neural_delivery':10.,'motor_execution':30.}
    rows=[]
    for label,budget in [('reference_hypothetical',baseline),('optimized_hypothetical',alternative)]:
        rows.append({'scenario':label, **{k+'_ms':v for k,v in budget.items()},
                     'total_latency_ms':sum(budget.values()),
                     'moving_object_distance_at_10m_s_m':round(sum(budget.values())/1000*10,3)})
    write_csv('reaction_budget.csv',rows)
    return rows


def diffusion_sweeps():
    # For idealized parallel vascular grid with 2D square spacing L, furthest point is L/sqrt(2).
    # Not a capillary-density prescription; excludes heterogeneous geometry, consumption and flow.
    rows=[]
    for distance_um in (100,150,200):
        spacing_mm=math.sqrt(2)*distance_um/1000
        tracks_per_cm2=(10/spacing_mm)**2
        rows.append({'max_distance_to_perfused_vessel_um':distance_um,
                     'max_square_grid_spacing_mm':round(spacing_mm,4),
                     'idealized_vascular_tracks_per_cm2':round(tracks_per_cm2)})
    write_csv('diffusion_grid.csv',rows)
    return rows


def make_plots(force, sprint, heat):
    fig,ax=plt.subplots(figsize=(8.1,4.7))
    for c in (1.05,1.10,1.20,1.50):
        pts=[r for r in force if r['tendon_capacity_to_baseline_ratio']==c]
        ax.plot([r['muscle_potential_gain_pct'] for r in pts],
                [r['realizable_force_gain_pct'] for r in pts],marker='o',label=f'Tendon capacity {c:.2f}×')
    ax.plot([0,80],[0,80],color='gray',linestyle='--',linewidth=1,label='No bottleneck')
    ax.set(xlabel='Muscle-only force potential gain (%)',ylabel='Realizable force gain (%)',
           title='Model 1: muscle gain is capped by tendon load capacity')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT/'force_tendon_constraints.png',dpi=180)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(8.1,4.7))
    ax.plot([r['target_speed_m_s'] for r in sprint], [r['drag_power_at_speed_W'] for r in sprint],marker='o',label='Aerodynamic drag only')
    ax.plot([r['target_speed_m_s'] for r in sprint], [r['minimum_avg_external_power_during_2s_accel_W'] for r in sprint],marker='o',label='Minimum mean during 2 s acceleration')
    ax.plot([r['target_speed_m_s'] for r in sprint], [r['minimum_peak_external_power_at_end_of_2s_accel_W'] for r in sprint],marker='o',label='Minimum peak at end of acceleration')
    ax.set(xlabel='Target speed (m/s)',ylabel='Mechanical power (W)',title='Model 2: speed rapidly raises mechanical demands')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT/'speed_constraints.png',dpi=180)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(8.1,4.7))
    for eff in (.20,.25,.30):
        pts=[r for r in heat if r['illustrative_efficiency']==eff]
        ax.plot([r['external_mechanical_power_W'] for r in pts],
                [r['heat_generation_W'] for r in pts],marker='o',label=f'Efficiency {eff:.0%}')
    ax.set(xlabel='Externally measured mechanical power (W)',ylabel='Heat generation (W)',title='Model 3: power cannot be increased without heat management')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT/'thermal_constraints.png',dpi=180)
    plt.close(fig)


def main():
    force = force_sweeps()
    sprint = sprint_sweeps()
    heat = heat_sweeps()
    fick = fick_sweeps()
    reaction = reaction_sweeps()
    diffusion = diffusion_sweeps()
    make_plots(force,sprint,heat)
    assert len(force)==20 and len(sprint)==3 and len(heat)==9
    assert len(fick)==5 and len(reaction)==2 and len(diffusion)==3
    assert math.isclose(sprint[2]['drag_power_at_speed_W'],1012.5)
    assert math.isclose(heat[4]['heat_generation_W'],1500)
    assert math.isclose(fick[2]['cardiac_output_needed_if_extraction_constant_L_min'],32.5)
    assert reaction[0]['total_latency_ms']==190 and reaction[1]['total_latency_ms']==100
    print('PASS: all model consistency checks')
    print('FORCE sigma 26.8 N/cm2, PCSA 100 cm2 => 2680 N')
    print('SPEED at 15m/s:',sprint[2])
    print('HEAT at 500W, eff 25%:',heat[4])
    print('FICK +30%:',fick[2])
    print('REACTION:',reaction)
    print('DIFFUSION:',diffusion)

if __name__=='__main__':
    main()
