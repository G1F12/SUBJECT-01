"""Software verification only; synthetic invariants are not human validation."""
import copy,hashlib,json,math,unittest
import numpy as np
import model,dataset,validation

class DynamicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.s,cls.trace,cls.episodes=model.simulate()
    def test_reserve_bounds(self):
        for r in self.trace:
            self.assertTrue(0<=r['fast_J']<=8000);self.assertTrue(0<=r['slow_J']<=22000)
    def test_energy_each_step(self):
        for r in self.trace:
            self.assertAlmostEqual(r['oxidative_J']+30000-r['fast_J']-r['slow_J'],r['external_J']+r['heat_generated_J'],places=6)
    def test_heat_each_step(self):
        for r in self.trace:self.assertAlmostEqual(r['stored_heat_J'],r['heat_generated_J']-r['heat_lost_J'],places=6)
    def test_kinetic_each_step(self):
        for r in self.trace:self.assertAlmostEqual(r['external_J'],.5*75*r['speed_m_s']**2+r['drag_J']+r['braking_J'],places=6)
    def test_physical_force(self):
        p=model.integrated.load();friction=p['friction_coefficient']*75*9.80665
        for r in self.trace:
            self.assertLessEqual(r['force_N'],r['force_cap_N']+1e-6);self.assertLessEqual(r['force_N'],friction+1e-6)
    def test_speed_bound(self):self.assertLessEqual(max(r['speed_m_s'] for r in self.trace),model.integrated.load()['sprint_v0_m_s'])
    def test_oxygen_cap(self):
        cap=model.integrated.energy(model.integrated.load())['aerobic_W']
        self.assertLessEqual(max(r['oxygen_W'] for r in self.trace),cap+1e-7)
    def test_recovery_rate(self):
        d=model.load()['dynamic'];prev_fast=8000;prev_slow=22000
        for r in self.trace:
            h=r['time_s']-r['interval_start_s']
            self.assertLessEqual(r['fast_J']-prev_fast,(8000-prev_fast)*(1-math.exp(-h/d['fast_recovery_tau_s']))+1e-7)
            self.assertLessEqual(r['slow_J']-prev_slow,(22000-prev_slow)*(1-math.exp(-h/d['slow_recovery_tau_s']))+1e-7)
            prev_fast=r['fast_J'];prev_slow=r['slow_J']
    def test_zero_energy_no_output(self):
        p=model.integrated.load();q=p['metabolic_intercept_W']/((p['arterial_content']-p['venous_content'])*p['oxygen_energy_J_m3'])
        s,_,_=model.simulate(overrides={'fast_capacity_J':0,'slow_capacity_J':0,'slow_component_max_W':0},integrated_overrides={'cardiac_output_m3_s':q},keep_trace=False)
        self.assertLess(s['external_J'],1e-6)
    def test_zero_reserves_no_creation(self):
        s,tr,_=model.simulate(overrides={'fast_capacity_J':0,'slow_capacity_J':0})
        self.assertEqual(s['fast_J']+s['slow_J'],0);self.assertLess(abs(s['energy_residual_J']),1e-5)
    def test_allocation_no_oxidative_free_recharge(self):
        d=model.load()['dynamic'];self.assertEqual(model.allocate(0,0,0,0,d,1),(0,0,0,0))
    def test_recharge_energy_bound(self):
        d=model.load()['dynamic'];f,s,r,w=model.allocate(100,0,0,0,d,1)
        self.assertLessEqual(r,100*d['recharge_efficiency']);self.assertEqual(w,0)
    def test_unpaid_work_raises(self):
        with self.assertRaises(ArithmeticError):model.allocate(0,100,0,0,model.load()['dynamic'],1)
    def test_reproducibility(self):
        s,tr,ep=model.simulate();self.assertEqual(s,self.s);self.assertEqual(tr,self.trace);self.assertEqual(ep,self.episodes)
    def test_convergence(self):
        fine,_,_=model.simulate(dt=.0625,keep_trace=False);half,_,_=model.simulate(dt=.125,keep_trace=False)
        self.assertLess(abs(self.s['external_J']/fine['external_J']-1),.005)
        self.assertLess(abs(self.s['body_delta_K']-fine['body_delta_K']),.02)
        self.assertLess(abs(half['external_J']-fine['external_J']),abs(self.s['external_J']-fine['external_J']))
    def test_protocol_exact(self):
        for name in model.load()['protocols']:
            eps=model.protocol(model.load(),name);self.assertEqual(eps[-1]['end_s'],2700)
            self.assertTrue(all(a['end_s']==b['start_s'] for a,b in zip(eps,eps[1:])))
    def test_invalid_dt(self):
        for dt in [0,-1,2,float('nan')]:
            with self.assertRaises(ValueError):model.simulate(dt=dt)
    def test_invalid_parameters(self):
        for over in [{'fast_capacity_J':-1},{'recharge_efficiency':1.1},{'oxygen_tau_s':0},{'fatigue_rate_s_inv':float('nan')},{'bad':1}]:
            with self.assertRaises(ValueError):model.simulate(overrides=over)
    def test_no_invented_neural_data(self):
        for key in ['reaction','accuracy','coordination','tissue_damage']:self.assertIsNone(self.s[key])
        self.assertEqual(self.s['target_achievement'],'not_assessed');self.assertEqual(self.s['intervention_status'],'NO_GO')
    def test_no_instant_recovery(self):
        recovery=[e for e in self.episodes if e['kind']=='recovery']
        self.assertTrue(all(e['fast_end_J']<8000 for e in recovery));self.assertTrue(all(e['fatigue_end']>0 for e in recovery))
    def test_source_immutable(self):
        p=model.BASE/'data/pone.0276314.s001.xlsx';d=json.loads((p.parent/'dataset_provenance.json').read_text('utf8'))
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),d['sha256']);self.assertEqual(d['version'],1)
    def test_missing_observations(self):
        rows=dataset.observations();self.assertEqual(len(rows),440);self.assertEqual(sum(r['mean_power_W'] is None for r in rows),26)
        data,excluded=validation.prepare(rows);self.assertEqual(excluded[0]['participant'],18);self.assertTrue(all(r['mean_power_W'] is not None for r in data))
    def test_participant_disjoint(self):
        data,_=validation.prepare(dataset.observations());a={r['participant'] for r in data if r['split']=='fit'};b={r['participant'] for r in data if r['split']=='validation'}
        self.assertFalse(a&b);self.assertEqual((len(a),len(b)),(11,10));self.assertTrue(all(r['condition']=='Thermoneutral' for r in data))
    def test_bridge(self):
        b=model.measurement_bridge(self.trace,self.episodes)
        self.assertIsNone(b['coordination']);self.assertFalse(any('error' in k for k in b));self.assertGreater(b['work_net_J'],0)
    def test_no_mutation_inputs(self):
        c=model.load();original=copy.deepcopy(c);model.simulate(c,keep_trace=False);self.assertEqual(c,original)
    def test_fatigue_bound(self):
        self.assertTrue(all(.2<=r['available_contractile_fraction']<=1 for r in self.trace))

if __name__=='__main__':unittest.main(verbosity=2)
