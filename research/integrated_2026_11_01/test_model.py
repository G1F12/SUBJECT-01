"""Независимые физические инварианты и проверки регрессий (stdlib unittest)."""
import unittest,math,json,csv,hashlib
from pathlib import Path
import numpy as np
import model
BASE=Path(__file__).resolve().parent
def read_csv(path):
    with path.open(encoding='utf8',newline='') as fp:return list(csv.DictReader(fp))

class Physics(unittest.TestCase):
    def setUp(self):self.p=model.load()
    def test_dimensions(self):
        # M,L,T,K; проверяются размерности уравнений, значения в коде строго SI.
        kg=(1,0,0,0);m=(0,1,0,0);s=(0,0,1,0);K=(0,0,0,1)
        def mul(*dims):return tuple(sum(x) for x in zip(*dims))
        def pow(d,n):return tuple(x*n for x in d)
        N=(1,1,-2,0);Pa=(1,-1,-2,0);J=(1,2,-2,0);W=(1,2,-3,0)
        self.assertEqual(mul(Pa,pow(m,2)),N)
        self.assertEqual(mul(N,m),J)
        self.assertEqual(mul(N,m,pow(s,-1)),W)
        self.assertEqual(mul(kg,pow(m,-3),pow(m,2),pow(m,3),pow(s,-3)),W)
        self.assertEqual(mul(J,pow(kg,-1),pow(K,-1),kg,K,pow(s,-1)),W)
        self.assertEqual(mul(pow(m,3),pow(s,-1),J,pow(m,-3)),W)
        self.assertEqual(mul(W,pow(m,-2),pow(K,-4),pow(m,2),pow(K,4)),W)
    def test_invalid_inputs(self):
        for key,value in [('delta_efficiency',1.01),('cardiac_output_m3_s',-1),('air_K',-1),('relative_humidity',1.1),('pcsa_m2',float('nan')),('sensory_s',float('inf'))]:
            with self.subTest(key=key),self.assertRaises(ValueError):model.evaluate(dict(self.p,**{key:value}))
        with self.assertRaises(ValueError):model.evaluate(dict(self.p,venous_content=.25))
    def test_fick_bound(self):
        for cv in [0,.03,.1,.203]:
            p=dict(self.p,venous_content=cv);e=model.energy(p)
            self.assertGreaterEqual(e['vo2_m3_s'],0)
            self.assertLessEqual(e['vo2_m3_s'],p['cardiac_output_m3_s']*p['arterial_content'])
        p=dict(self.p,venous_content=self.p['arterial_content']);self.assertEqual(model.energy(p)['oxygen_mechanical_W'],0)
    def test_static_force_and_tendon_plateau(self):
        f,_,cap=model.muscle(self.p)
        fs=[model.muscle(dict(self.p,specific_tension_Pa=self.p['specific_tension_Pa']*g))[0] for g in [1,1.5,2]]
        self.assertEqual(fs,[cap]*3)
        self.assertLessEqual(f,self.p['bone_load_cap_N'])
    def test_force_velocity_and_length(self):
        force=[model.muscle(self.p,v)[0] for v in [0,.1,.4,.8,1.]]
        self.assertTrue(all(a>=b for a,b in zip(force,force[1:])))
        self.assertEqual(force[-1],0)
        center=model.muscle(self.p)[1]
        for l in [.7,1.3]:self.assertLess(model.muscle(dict(self.p,normalized_length=l))[1],center)
    def test_transmission_power(self):
        ratio=self.p['moment_arm_m']/self.p['external_lever_m']*self.p['geometry_projection']
        for v in [.5,3,6]:
            fiber_force=model.muscle(self.p,ratio*v)[0]
            self.assertLessEqual(model.horizontal_force(self.p,v)*v,self.p['parallel_groups']*fiber_force*ratio*v+1e-8)
    def test_contact_and_drag(self):
        mass=self.p['body_mass_kg']
        for v in [0,2,8,12]:self.assertLessEqual(model.horizontal_force(self.p,v),self.p['friction_coefficient']*mass*9.80665)
        self.assertAlmostEqual(model.drag(self.p,4)/model.drag(self.p,2),4)
    def test_energy_and_thermal_balance(self):
        for t,rh in [(298.15,.5),(308.15,.8),(313.15,1.)]:
            p=dict(self.p,air_K=t,radiant_K=t,relative_humidity=rh);e=model.evaluate(p);power=e['sustainable_external_W']
            metabolic=e['maintenance_W']+power/p['delta_efficiency'];heat=metabolic-power
            self.assertAlmostEqual(heat,e['heat_loss_W']+e['stored_heat_J']/p['duration_s'])
            self.assertLessEqual(metabolic,e['aerobic_W']+1e-8)
            if power>0:self.assertLessEqual(e['delta_temperature_K'],p['allowed_delta_K']+1e-8)
    def test_evaporation_bounds(self):
        p=dict(self.p,air_K=self.p['skin_K'],radiant_K=self.p['skin_K'],relative_humidity=1.)
        self.assertAlmostEqual(model.heat_loss(p)[2],0)
        self.assertAlmostEqual(model.heat_loss(p)[1],0)
        for factor in [0,1,2]:
            pp=dict(self.p,evaporated_water_kg_s=self.p['evaporated_water_kg_s']*factor)
            self.assertLessEqual(model.heat_loss(pp)[2],pp['evaporated_water_kg_s']*pp['latent_J_kg'])
    def test_monotonic_oxygen_cooling(self):
        for key in ['cardiac_output_m3_s','evaporated_water_kg_s','tendon_area_m2']:
            vals=[model.evaluate(dict(self.p,**{key:self.p[key]*g})) for g in [.8,1,1.2]]
            metric='force_N' if key=='tendon_area_m2' else 'sustainable_external_W'
            self.assertTrue(all(a[metric]<=b[metric]+1e-8 for a,b in zip(vals,vals[1:])))
    def test_added_mass_coupling(self):
        p=dict(self.p,added_contractile_kg=2.,support_mass_kg=1.)
        a,b=model.evaluate(self.p),model.evaluate(p)
        self.assertAlmostEqual(b['mass_kg']-a['mass_kg'],3)
        self.assertAlmostEqual(b['maintenance_W']-a['maintenance_W'],9)
        self.assertGreater(model.muscle(p)[1],model.muscle(self.p)[1])
    def test_sprint_energy_reserve_and_timestep(self):
        with self.assertRaises(ValueError):model.sprint(self.p,dt=0)
        e,_=model.sprint(self.p);f,_=model.sprint(self.p,dt=.005)
        self.assertGreaterEqual(e['reserve_remaining_J'],0)
        self.assertAlmostEqual(e['maintenance_deficit_J'],0)
        self.assertAlmostEqual(e['aerobic_used_J']+e['reserve_used_J'],e['heat_generated_J']+e['mechanical_work_J'],places=6)
        self.assertLessEqual(e['reserve_used_J'],self.p['anaerobic_reserve_J']+1e-6)
        self.assertAlmostEqual(e['metabolic_work_J']+model.energy(self.p)['maintenance_W']*6,e['heat_generated_J']+e['mechanical_work_J'],places=6)
        self.assertLess(abs(e['distance_m']-f['distance_m'])/f['distance_m'],.01)
        no_reserve=dict(self.p,anaerobic_reserve_J=0.)
        a,_=model.sprint(no_reserve);self.assertLessEqual(a['speed_m_s'],e['speed_m_s'])
        self.assertLessEqual(a['reserve_used_J'],1e-5)
    def test_prediction_tradeoff(self):
        a=model.evaluate(self.p);b=model.evaluate(dict(self.p,prediction_horizon_s=.08))
        self.assertLess(b['effective_latency_s'],a['effective_latency_s'])
        self.assertGreater(b['prediction_error_m'],a['prediction_error_m'])
    def test_all_results_finite(self):
        for name in ['scenarios.csv','uncertainty.csv','local_sensitivity.csv','global_sensitivity.csv','validation.csv']:
            with (BASE/'results'/name).open(encoding='utf8') as f:
                for row in csv.DictReader(f):
                    for v in row.values():
                        try:self.assertTrue(math.isfinite(float(v)))
                        except ValueError:pass
    def test_uncertainty_not_degenerate(self):
        d=json.loads((BASE/'results/summary.json').read_text('utf8'))
        for mode in ['population','mean_estimation','epistemic']:
            q=d['uncertainty_p05_p50_p95'][mode]['sustainable_external_W'];self.assertGreater(q[2],q[0])
        # Не требуем отклика выхода на параметр за активным bottleneck.
        self.assertEqual(model.evaluate(self.p)['bottleneck'],'тепло')
    def test_calibration_fit_wiring(self):
        rows=read_csv(BASE/'calibration.csv')
        self.assertEqual(len(rows),43)
        for row in rows:
            self.assertGreater(int(row['n']),0)
            self.assertTrue(math.isfinite(float(row['value'])))
            self.assertGreaterEqual(float(row['spread']),0)
        gross=[r for r in rows if r['parameter']=='gross_efficiency' and r['role']=='calibration']
        x=np.array([float(r['group'].split('_')[-1][:-1]) for r in gross])
        y=x/np.array([float(r['value']) for r in gross])
        a,b=np.polyfit(x,y,1)
        self.assertAlmostEqual(self.p['delta_efficiency'],1/a)
        self.assertAlmostEqual(self.p['metabolic_intercept_W'],b)
    def test_architecture_matrix_matches_outputs(self):
        matrix=read_csv(BASE/'architecture_matrix.csv')
        scenarios=read_csv(BASE/'results/scenarios.csv')
        self.assertEqual(len(matrix),6)
        for row in matrix:
            match=next(r for r in scenarios if r['architecture']==row['architecture'] and r['climate']=='temperate')
            for k in ['mass_kg','peak_horizontal_W','sustainable_external_W','effective_latency_s','prediction_error_m']:
                self.assertAlmostEqual(float(row[k]),float(match[k]))
    def test_infeasible_heat_budget_is_explicit(self):
        p=dict(self.p,air_K=313.15,radiant_K=313.15,relative_humidity=1.)
        self.assertFalse(model.evaluate(p)['steady_feasible'])
    def test_manifest(self):
        data=json.loads((BASE/'manifest.json').read_text('utf8'))
        for name,digest in data.items():self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),digest,name)

if __name__=='__main__':unittest.main(verbosity=2)
