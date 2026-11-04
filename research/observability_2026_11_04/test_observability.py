"""Physics, exact counterexamples and observation-map controls."""
import unittest,json,hashlib,ast
import numpy as np
import audit

class ObservabilityTests(unittest.TestCase):
    def test_exact_scale_all_protocols(self):
        for d in audit.DESIGNS:
            a,_=audit.trace(audit.nominal(),d);b,_=audit.trace(audit.scale(audit.nominal(),1.2),d)
            np.testing.assert_allclose(a[:,1],b[:,1],atol=1e-7,rtol=1e-10)
            np.testing.assert_allclose(a[:,3],b[:,3],atol=1e-10)
    def test_new_baseline_shift_symmetry(self):
        for d in audit.DESIGNS:
            q=audit.nominal();a,_=audit.trace(q,d)
            q['maintenance_W']+=100;q['oxygen_cap_W']+=100;b,_=audit.trace(q,d)
            np.testing.assert_allclose(a[:,1],b[:,1],atol=1e-7)
            np.testing.assert_allclose(a[:,3:],b[:,3:],atol=1e-7)
            np.testing.assert_allclose(a[:,2]+100,b[:,2],atol=1e-8)
    def test_quotient_has_nine_parameters(self):
        q=audit.nominal();self.assertEqual(len(audit.quotient(q)),9)
        z=audit.quotient(q);zz=audit.quotient(audit.scale(q,1.2))
        for k in z:self.assertAlmostEqual(z[k],zz[k])
    def test_reduced_preserves_power_and_bounds(self):
        for d in audit.DESIGNS:
            q=audit.nominal();a,s=audit.trace(q,d);b,t=audit.reduced_trace(audit.quotient(q),d)
            np.testing.assert_allclose(a[:,1],b[:,1],atol=1e-7)
            np.testing.assert_allclose(a[:,3],b[:,3],atol=1e-9)
            self.assertLess(abs(s['energy_residual_J']),1e-5)
            self.assertLess(abs(t['energy_residual_J']),1e-5)
            self.assertTrue(np.all((b[:,3]>=0)&(b[:,3]<=1)))
    def test_analytic_generator(self):
        q=audit.nominal();_,g=audit.projection();d=audit.DESIGNS[2]
        j=audit.jacobian(q,d,'M1');self.assertLess(np.linalg.norm(j@g)/np.linalg.norm(j),1e-5)
    def test_relative_PCr_cannot_anchor_scale(self):
        q=audit.nominal();d=audit.DESIGNS[2]
        np.testing.assert_allclose(audit.observe(q,d,'M3'),audit.observe(audit.scale(q,1.2),d,'M3'),atol=1e-7)
    def test_absolute_reserve_breaks_scale(self):
        q=audit.nominal();d=audit.DESIGNS[2]
        self.assertGreater(np.linalg.norm(audit.observe(q,d,'M4')-audit.observe(audit.scale(q,1.2),d,'M4')),1)
    def test_known_oxygen_breaks_scale(self):
        q=audit.nominal();d=audit.DESIGNS[2]
        self.assertGreater(np.linalg.norm(audit.observe(q,d,'M2')-audit.observe(audit.scale(q,1.2),d,'M2')),1)
    def test_singular_FIM_not_scored_full_rank(self):
        j=audit.jacobian(audit.nominal(),audit.DESIGNS[2],'M1')
        c=audit.criterion(j,np.eye(11));self.assertIsNone(c['logdet']);self.assertEqual(c['lambda_min'],0)
    def test_add_measurements_adds_information(self):
        q=audit.nominal();d=audit.DESIGNS[2]
        a=audit.jacobian(q,d,'M1');b=audit.jacobian(q,d,'M5')
        self.assertGreater(np.linalg.eigvalsh(b.T@b-a.T@a).min(),-1e-7)
    def test_anchor_only_once(self):
        q=audit.nominal();d=audit.DESIGNS[2]
        self.assertEqual(len(audit.observe(q,d,'M6'))-len(audit.observe(q,d,'M5')),1)
    def test_results_structural_rank_bounds(self):
        x=json.loads((audit.BASE/'results/measurement_sets.json').read_text())
        self.assertEqual(x['combined']['M1']['rank'],9)
        self.assertEqual(x['combined']['M3']['rank'],9)
        self.assertEqual(x['combined']['M4']['rank'],10)
        self.assertEqual(x['combined']['M5']['rank'],11)
    def test_fd_convergence_rejects_spurious_direction(self):
        x=json.loads((audit.BASE/'results/finite_difference.json').read_text())
        self.assertLess(x[-1]['singular_values'][-2],x[0]['singular_values'][-2]/1000)
        self.assertEqual(x[-1]['rank'],9)
    def test_no_human_outcome_dependency(self):
        tree=ast.parse((audit.BASE/'audit.py').read_text())
        imports=[n.name for a in ast.walk(tree) if isinstance(a,ast.Import) for n in a.names]
        self.assertFalse({'pipeline','dataset','diagnostics'}&set(imports))
    def test_prior_locks_preserved(self):
        root=audit.BASE.parent/'recovery_2026_11_04'
        lock=json.loads((root/'model_lock.json').read_text())
        for name,h in lock['code_hashes'].items():self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),h)
    def test_zero_depletion_flat_profile(self):
        np.testing.assert_array_equal(audit.engine.recovery_shape(0,1,12),audit.engine.recovery_shape(0,600,12))
    def test_synthetic_truth_recovered(self):
        x=json.loads((audit.BASE/'results/stress.json').read_text())['synthetic']['cases'][0]
        for f in x['fits']:
            self.assertAlmostEqual(f['depletion'],.18,places=6);self.assertAlmostEqual(f['tau_s'],60,places=4)
        a=dict(log_parameter_error=[.075],nfev=53,prediction_RMSE_W=2.)
        self.assertTrue(audit.recovery_equivalent(a,dict(a,log_parameter_error=[.075044],nfev=49)))
        self.assertFalse(audit.recovery_equivalent(a,dict(a,log_parameter_error=[.076])))
        self.assertFalse(audit.recovery_equivalent(a,dict(a,prediction_RMSE_W=3.)))
    def test_status_no_empirical_promotion(self):
        x=json.loads((audit.BASE/'results/summary.json').read_text())
        self.assertFalse(x['new_external_validation']);self.assertTrue(x['NO_GO'])
    def test_licensed_native_XLS_integrity_and_blank_names(self):
        import xlrd
        p=audit.BASE/'licensed_data/peerj-04-2259-s003.xls'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'3e2030f7f62054ff4fd7085496a279b04a7eba2df1e8d00b95e8fa1c66712d92')
        s=xlrd.open_workbook(p).sheet_by_index(0)
        self.assertTrue(all(s.cell_value(i,1)=='' for i in list(range(3,20))+list(range(25,35))+list(range(40,47))))

if __name__=='__main__':unittest.main(verbosity=2)
