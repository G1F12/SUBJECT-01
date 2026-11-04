"""Verification and leakage controls, not human efficacy tests."""
import copy,json,math,sys,unittest
from unittest.mock import patch
import numpy as np
import engine,dataset,pipeline,diagnostics

class RecoveryTests(unittest.TestCase):
    def test_old_shape_unchanged(self):
        sys.path.insert(0,str(engine.OLD));import validation as original_validation
        expected=original_validation.cycling_shape(0)
        actual=engine.cycle(overrides={'fatigue_rate_s_inv':0})[0]
        np.testing.assert_allclose(actual/actual[0],expected,rtol=1e-12,atol=1e-12)
    def test_instrumented_legacy_parity(self):
        np.testing.assert_allclose(diagnostics.legacy_counterfactual(),engine.cycle(overrides={'fatigue_rate_s_inv':0})[0],rtol=1e-12)
    def test_historical_RMSE(self):
        p=diagnostics.legacy_counterfactual();self.assertAlmostEqual(diagnostics.old_metrics(p/p[0])['RMSE_W'],378.5437701,places=5)
    def test_energy_ledger_each_step(self):
        for mode in ['legacy','corrected']:
            _,s,tr=engine.cycle(mode=mode,trace=True)
            self.assertLess(abs(s['energy_residual_J']),1e-5)
            for r in tr:self.assertLess(abs(r['energy_residual_J']),1e-5)
    def test_reserve_bounds(self):
        _,_,tr=engine.cycle(rest_s=12,mode='corrected',trace=True)
        self.assertTrue(all(0<=r['fast_J']<=8000 and 0<=r['slow_J']<=22000 for r in tr))
    def test_no_energy_no_output(self):
        p,s,_=engine.cycle(mode='corrected',overrides={'fast_capacity_J':0,'slow_capacity_J':0,'oxygen_cap_W':0,'maintenance_W':0,'fatigue_rate_s_inv':0})
        self.assertEqual(float(sum(p)),0);self.assertEqual(s['recharged_J'],0)
    def test_recharge_not_free(self):
        _,s,_=engine.cycle(mode='corrected',overrides={'initial_fraction':0,'oxygen_cap_W':0,'maintenance_W':0})
        self.assertEqual(s['fast_J']+s['slow_J'],0);self.assertEqual(s['external_J'],0)
    def test_recharge_paid(self):
        _,s,_=engine.cycle(mode='corrected',overrides={'initial_fraction':0})
        self.assertLessEqual(s['recharged_J']/engine.defaults()['recharge_efficiency'],s['oxidative_J']+1e-6)
    def test_release_power_bound(self):
        q=engine.defaults();_,_,tr=engine.cycle(mode='corrected',trace=True)
        for r in tr:self.assertLessEqual(r['output_W'],min(q['demand_W'],q['eta']*(q['oxygen_cap_W']+q['fast_power_cap_W']+q['slow_power_cap_W']))+1e-6)
    def test_corrected_convergence(self):
        a=engine.cycle(mode='corrected',dt=.5)[0];b=engine.cycle(mode='corrected',dt=.25)[0];c=engine.cycle(mode='corrected',dt=.125)[0]
        self.assertLess(np.max(abs(b-c)),np.max(abs(a-c)));self.assertLess(np.max(abs(a-c)),2)
    def test_2700_stability(self):
        _,s,_=engine.cycle(mode='corrected',rest_s=12,repetitions=150,dt=.25)
        self.assertEqual(s['time_s'],2700);self.assertLess(abs(s['energy_residual_J']),1e-4)
    def test_exact_nondivisible_events(self):
        _,s,_=engine.cycle(mode='corrected',rest_s=12.1,effort_s=6.2,repetitions=3,dt=.37)
        self.assertAlmostEqual(s['time_s'],54.9,places=9)
    def test_invalid_parameters(self):
        for over in [{'eta':0},{'eta':1.1},{'initial_fraction':-1},{'fast_capacity_J':-1},{'oxygen_tau_s':float('nan')},{'fast_recovery_tau_s':0}]:
            with self.assertRaises(ValueError):engine.cycle(overrides=over)
    def test_reproducible(self):
        a=engine.cycle(mode='corrected',trace=True);b=engine.cycle(mode='corrected',trace=True)
        np.testing.assert_array_equal(a[0],b[0]);self.assertEqual(a[1:],b[1:])
    def test_group_split_no_leakage(self):
        dev=dataset.power_rows();test=dataset.power_rows('test',True)
        self.assertEqual(len(dev),420);self.assertEqual(len(test),210)
        self.assertFalse({r['participant'] for r in dev}&{r['participant'] for r in test})
        for sid in {r['participant'] for r in dev}:self.assertEqual({r['rest_s'] for r in dev if r['participant']==sid},{12,18,24})
    def test_test_gate(self):
        with self.assertRaises(ValueError):dataset.power_rows('test')
        with self.assertRaises(ValueError):dataset.power_rows('all')
    def test_locked_model_unchanged(self):
        lock=pipeline.load_lock();self.assertEqual(lock['selected_model'],'constant');self.assertEqual(lock['training_observations'],378)
    def test_training_digest_ignores_test_outcomes(self):
        original=dataset.sheets
        def changed(path):
            book=copy.deepcopy(original(path))
            for rows in book.values():
                for _,r in rows:
                    if str(r.get('A','')).startswith('WTR03_'):
                        for c in 'CDEFGHIJK':r[c]='999999'
            return book
        expected=pipeline.input_digest(pipeline.scoring_rows())
        with patch.object(dataset,'sheets',changed):self.assertEqual(pipeline.input_digest(pipeline.scoring_rows()),expected)
    def test_missing_no_imputation(self):
        original=dataset.sheets
        def changed(path):
            book=copy.deepcopy(original(path))
            for _,r in book['Avg_12']:
                if str(r.get('A','')).startswith('WTR01_'):r['C']=None
            return book
        with patch.object(dataset,'sheets',changed):self.assertEqual(len(dataset.power_rows()),419)
    def test_units_work_power(self):self.assertLess(dataset.development_audit()['max_work_minus_6power_J'],1e-8)
    def test_no_PC_r_or_continuous_VO2_claim(self):
        a=dataset.development_audit();self.assertIn('no PCr',a['VO2_scope']);self.assertIn('extrema',a['VO2_scope'])
    def test_exact_scale_nonidentifiability(self):
        d=diagnostics.identifiability();self.assertEqual(d['rank'],7);self.assertLess(d['absolute_eta_metabolic_scale_symmetry_error_W'],1e-7)
    def test_empirical_tau_unidentified_when_depletion_zero(self):
        np.testing.assert_array_equal(engine.recovery_shape(0,1,12),engine.recovery_shape(0,600,12))
    def test_synthetic_parameter_recovery(self):
        r=diagnostics.synthetic_control();self.assertEqual(r['MSE'],0);self.assertEqual(r['recovered_tau_s'],60);self.assertIn('SYNTHETIC',r['origin'])
    def test_same_test_cells(self):
        p=pipeline.load_lock();rows=pipeline.scoring_rows('test',True)
        self.assertEqual({len(pipeline.predictions(rows,label,p['models'][label])) for label in pipeline.LABELS},{189})
    def test_source_hashes(self):
        from fetch_data import verify_cache
        self.assertTrue((verify_cache()/'Power_rawdata.xlsx').exists())

if __name__=='__main__':unittest.main(verbosity=2)
