"""Measurement, physics, leakage and identifiability regression controls."""
import unittest,json,math,hashlib,tempfile,io
from pathlib import Path
from unittest.mock import patch
import numpy as np
import dataset,models,analysis
from acquire import BASE,RangeFile

class CalibrationTests(unittest.TestCase):
    def test_source_snapshot_integrity(self):
        m=json.loads((BASE/'manifest.json').read_text('utf8'))
        for name in ['development_stage_audit.json','test_stage_audit.json','development_kinetic_inputs.json','cpet_retrieval.json','weee_retrieval.json']:
            self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),m[name])
    def test_gas_cost_units(self):
        self.assertAlmostEqual((3.9+1.1*.8)*4184/60,333.32533333333333)
    def test_no_fabricated_local_channels(self):
        x=json.loads((BASE/'development_stage_audit.json').read_text())
        self.assertTrue(all(r['PCr'] is None and r['local_ATP_flux'] is None for r in x['stages']))
    def test_native_gate_before_IO(self):
        with self.assertRaises(ValueError):dataset.native(10)
        with self.assertRaises(ValueError):dataset.collect('test')
    def test_group_split(self):
        a={r['participant'] for r in models.rows()};b={r['participant'] for r in models.rows('test',True)}
        self.assertFalse(a&b);self.assertTrue(all(i%5 for i in a));self.assertTrue(all(i%5==0 for i in b))
    def test_locked_models_unchanged(self):self.assertEqual(models.load_lock()['code_sha256'],models.codehashes())
    def test_no_lock_overwrite(self):
        before=(BASE/'model_lock.json').read_bytes()
        with self.assertRaises(ValueError):models.build_lock()
        self.assertEqual(before,(BASE/'model_lock.json').read_bytes())
    def test_test_outcomes_do_not_change_training(self):
        expected=models.fit(models.rows())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'development_stage_audit.json').write_bytes((BASE/'development_stage_audit.json').read_bytes())
            fake=json.loads((BASE/'test_stage_audit.json').read_text())
            for r in fake['stages']:r['cost_W']=1e12
            (p/'test_stage_audit.json').write_text(json.dumps(fake))
            with patch.object(models,'BASE',p):actual=models.fit(models.rows())
        self.assertEqual(expected,actual)
    def test_prescribed_load_not_independent_power_output(self):
        lock=models.load_lock();self.assertIn('NOT independently predicted',lock['endpoint']);self.assertIn('NOT DEFINED',lock['reduced_model_status'])
    def test_constant_calibration_rank_one(self):
        p=np.full(56,457.);self.assertEqual(np.linalg.matrix_rank(np.column_stack([np.ones(56),p])),1)
    def test_time_conversion(self):self.assertEqual(dataset.second('0:06:30'),390)
    def test_missing_optional_channel_stays_missing(self):self.assertIsNone(dataset.finite_or_none(''))
    def test_gap_not_interpolated(self):
        rows=[dict(time_s=t,vo2_L_min=1.,vco2_L_min=.8,power_W=None,cadence_rpm=None) for t in [0,2,4,50,52,54]]
        self.assertIsNone(dataset.window(rows,0,60))
    def test_linear_integral_convergence(self):
        def integral(step):
            x=np.arange(0,60+step/2,step);return float(np.trapezoid(100+2*x,x))
        self.assertAlmostEqual(integral(1),integral(.5));self.assertAlmostEqual(integral(.5),integral(.25));self.assertAlmostEqual(integral(1),9600.)
    def test_exact_synthetic_parameter_recovery(self):
        # SOFTWARECONTROL on real workload design; these outcomes neverenter snapshots.
        rs=[dict(r,cost_W=130+3.5*r['power_W']) for r in models.rows()]
        a,b=models.fit(rs)['affine'];self.assertAlmostEqual(a,130,places=8);self.assertAlmostEqual(b,350,places=8)
    def test_pulmonary_synthetic_recovery(self):
        t=np.arange(0,221,5.);y=.4+.8*(1-np.exp(-np.maximum(0,t-25)/30))
        f=analysis.kinetics(dict(participant=-1,time_s=t.tolist(),vo2_L_min=y.tolist(),onset_s=20,origin='SYNTHETIC SOFTWARECONTROL'))
        self.assertAlmostEqual(f['tau_s'],30,places=3)
    def test_flat_pulmonary_profile_not_identified(self):
        t=np.arange(0,221,5.)
        f=analysis.kinetics(dict(participant=-1,time_s=t.tolist(),vo2_L_min=[.5]*len(t),onset_s=20,origin='SYNTHETIC SOFTWARECONTROL'))
        self.assertFalse(f['finite_profile']);self.assertEqual(f['status'],'UNIDENTIFIABLE')
    def test_unknown_gain_offset_rank_deficiency(self):
        x=json.loads((BASE/'results/falsification.json').read_text());self.assertEqual(x['realdesign_gain_offset_rank'],2)
        self.assertLess(x['gain_null_residual'],1e-8);self.assertEqual(x['offset_null_residual'],0)
    def test_offset_changes_intercept_not_efficiency(self):
        rs=models.rows();a=models.fit(rs)['affine'];b=models.fit(analysis.perturb(rs,bO=.1))['affine']
        self.assertAlmostEqual(a[1],b[1]);self.assertAlmostEqual(b[0]-a[0],27.196)
    def test_other_cohort_not_fused(self):
        x=json.loads((BASE/'weee_oxygen_summary.json').read_text());self.assertTrue(all(r['cohort']=='WEEE' for r in x['rows']))
        self.assertTrue(all(r['VCO2']=='NOT OBSERVED' for r in x['rows']))
    def test_RER_bound_order(self):
        x=json.loads((BASE/'weee_oxygen_summary.json').read_text());self.assertTrue(all(r['conditional_cost_W_RER07_to1'][0]<=r['conditional_cost_W_RER07_to1'][1] for r in x['rows'] if r['conditional_cost_W_RER07_to1']))
    def test_primary_endpoints_and_winner_fixed(self):
        x=json.loads((BASE/'results/independent_test.json').read_text());self.assertEqual(x['selected_before_test'],models.load_lock()['selected_model']);self.assertEqual({r['n'] for r in x['scores']},{56})
    def test_status_separates_cost_validation_from_CPE45(self):
        x=json.loads((BASE/'results/independent_test.json').read_text());self.assertEqual(x['mechanical_power_validation'],'NOT DONE');self.assertTrue(x['NO_GO'])
    def test_reduced_energy_and_paid_recovery(self):
        import sys
        sys.path.insert(0,str(BASE.parent/'observability_2026_11_04'));import audit
        q=audit.nominal();d=dict(audit.DESIGNS[2],demand_W=100,effort_s=6,rest_s=30,repetitions=3)
        a,s=audit.trace(q,d);b,t=audit.reduced_trace(audit.quotient(q),d)
        np.testing.assert_allclose(a[:,1],b[:,1],atol=1e-7)
        self.assertLess(abs(s['energy_residual_J']),1e-6);self.assertLess(abs(t['energy_residual_J']),1e-6)
        self.assertTrue(np.all((a[:,3]>=0)&(a[:,3]<=1)))
    def test_range_request_never_accepts_full_archive(self):
        class Response:
            status=200;headers={}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,*args):raise AssertionError('must rejectfullarchive before reading')
        with patch('urllib.request.urlopen',return_value=Response()):
            with self.assertRaises(ValueError):RangeFile('https://example.invalid/source',6_500_000_000).read(10)

if __name__=='__main__':unittest.main(verbosity=2)
