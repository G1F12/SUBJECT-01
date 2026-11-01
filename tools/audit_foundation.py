#!/usr/bin/env python3
"""Independent dimensional/conservation audit of existing Foundation CSV outputs.

Read only. The conditional CaO2 limit is NOT an empirical human universal.
No numpy/matplotlib needed. Exit nonzero on arithmetic inconsistency.
"""
from pathlib import Path
import csv, math, json
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research' / 'foundation_2026_11_01'

def table(name):
    with (BASE/name).open(newline='', encoding='utf8') as fp:
        return [{k: (float(v) if k not in ('scenario','caveat','tendon_bottleneck') else v)
                 for k,v in row.items()} for row in csv.DictReader(fp)]

def near(a,b,atol=0.011):
    if not math.isclose(a,b,rel_tol=1e-9,abs_tol=atol):
        raise AssertionError(f'mismatch {a} != {b}')

count=0
for x in table('muscle_force.csv'):
    near(x['muscle_force_N'],x['specific_tension_N_cm2']*x['illustrative_PCSA_cm2']); count+=1
for x in table('tendon_bottleneck.csv'):
    target=min(1+x['muscle_potential_gain_pct']/100,x['tendon_capacity_to_baseline_ratio'])
    near(x['realizable_force_gain_pct'],(target-1)*100); count+=1
    assert x['tendon_bottleneck'] == str(1+x['muscle_potential_gain_pct']/100 > x['tendon_capacity_to_baseline_ratio']+1e-12)
for x in table('sprint_energy.csv'):
    m,v,t=x['mass_kg'],x['target_speed_m_s'],2.0
    drag=.5*1.2*.5*v**3
    near(x['kinetic_energy_J'],.5*m*v*v)
    near(x['drag_power_at_speed_W'],drag)
    near(x['minimum_avg_external_power_during_2s_accel_W'],.5*m*v*v/t+drag/4)
    near(x['minimum_peak_external_power_at_end_of_2s_accel_W'],m*v*v/t+drag)
    count+=1
for x in table('heat_budget.csv'):
    p,e=x['external_mechanical_power_W'],x['illustrative_efficiency']
    store=75*3500*.5/600
    near(x['max_mean_heat_storage_W_for_0_5K_in_10min'],store)
    near(x['metabolic_power_W'],p/e)
    near(x['heat_generation_W'],p/e-p)
    near(x['minimum_mean_heat_loss_W_for_0_5K_budget'],max(0,p/e-p-store))
    count+=1
bad=[]; extreme=[]
for x in table('oxygen_fick.csv'):
    target=x['target_VO2_L_min']; q=x['cardiac_output_needed_if_extraction_constant_L_min']; extract=x['extraction_needed_if_cardiac_output_constant_L_L']
    near(x['baseline_VO2_L_min'],25*.15)
    near(target,3.75*(1+x['VO2_requested_gain_pct']/100))
    near(target,q*.15)
    near(target,25*extract)
    if extract > .2 + 1e-10:bad.append(int(x['VO2_requested_gain_pct']))
    if extract >= .195 - 1e-10:extreme.append(int(x['VO2_requested_gain_pct']))
    count+=1
for x in table('reaction_budget.csv'):
    total=sum(x[k] for k in ['sensory_detection_ms','central_processing_ms','neural_delivery_ms','motor_execution_ms'])
    near(total,x['total_latency_ms']);near(x['moving_object_distance_at_10m_s_m'],.01*total);count+=1
for x in table('diffusion_grid.csv'):
    spacing=math.sqrt(2)*x['max_distance_to_perfused_vessel_um']/1000
    near(spacing,x['max_square_grid_spacing_mm'],atol=0.0001)
    near(x['idealized_vascular_tracks_per_cm2'],(10/spacing)**2,atol=1)
    count+=1
assert bad==[50,100],bad
assert extreme==[30,50,100],extreme
assert count == 45, count
report={
 'audit':'2026-11-01 independently reconstructed CSV formulas',
 'rows_checked':count,'arithmetics':'PASS',
 'conditional_CaO2_L_per_L':.2,
 'fick_extraction_only_unphysical_gain_pct':bad,
 'fick_extraction_only_near_or_beyond_bound_gain_pct':extreme,
 'caveats':['CaO2 is an explicit assumed comparator, not a hard universal value',
            'Original synthetic parameter sweeps not calibrated to human physiology',
            'Cannot interpret arithmetic PASS as efficacy or safe enhancement']
}
expected_path = ROOT / 'audits' / '2026-11-01_model_results.json'
expected = json.loads(expected_path.read_text('utf-8'))
assert report == expected, 'Audited results differ from locked expectations'
print(json.dumps(report,indent=2))
