"""Только синтетическая верификация измерительного кода; не валидация человека."""
import copy
import dataclasses
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.cpe45 import Sample, Episode, Trial, analyze, profile

ROOT=Path(__file__).resolve().parents[1]

def synthetic():
    samples=[Sample(t,100.,200.,2.,0.,.01,.02) for t in range(0,2701,30)]
    episodes=[Episode(0,30,'effort','fixed_load'),Episode(30,2670,'recovery','rest'),Episode(2670,2700,'effort','fixed_load')]
    return dict(samples=samples,episodes=episodes,early_end_s=30,late_start_s=2670,max_gap_s=30)

class CPE45Tests(unittest.TestCase):
    def test_constant_work_and_duration(self):
        d=analyze(**synthetic())
        self.assertEqual(d['duration_s'],2700)
        self.assertEqual(d['total']['work_net_J'],270000)
        self.assertEqual(d['total']['path_length_m'],5400)
        self.assertEqual(d['episodes'][0]['work_net_J'],3000)
        self.assertEqual(d['target_achievement'],'not_assessed')
        self.assertFalse(d['physiological_validation'])
        self.assertEqual(d['post45']['status'],'not_measured')
    def test_irregular_timestamps_weighted_integral(self):
        s=[Sample(t,p,1,1,0,0,0) for t,p in [(0,0),(1,2),(4,8)]]
        d=profile(s,0,4)
        self.assertEqual(d['work_net_J'],16)
        self.assertEqual(d['mean_power_W'],4)
    def test_signed_work_crossing(self):
        s=[Sample(t,p,1,1,0,0,0) for t,p in [(0,-100),(2,100)]]
        d=profile(s,0,2)
        self.assertEqual(d['work_net_J'],0)
        self.assertEqual(d['work_positive_J'],50)
        self.assertEqual(d['work_negative_J'],-50)
    def test_interpolated_episode_boundaries(self):
        s=[Sample(t,p,1,1,0,0,0) for t,p in [(0,0),(4,8)]]
        self.assertEqual(profile(s,1,3)['work_net_J'],8)
        with self.assertRaises(ValueError):profile(s,-1,3)
    def test_nonmonotonic_duplicate_and_invalid_times(self):
        for time in [0,-1,float('nan'),float('inf'),None,True]:
            data=synthetic();data['samples'][1]=dataclasses.replace(data['samples'][1],time_s=time)
            with self.subTest(time=time),self.assertRaises(ValueError):analyze(**data)
    def test_incomplete_or_extended_duration(self):
        for samples in [synthetic()['samples'][:-1],synthetic()['samples'][1:],synthetic()['samples']+[Sample(2730,100,200,2,0,.01,.02)],[]]:
            data=synthetic();data['samples']=samples
            with self.assertRaises(ValueError):analyze(**data)
    def test_missing_nan_and_inf_not_imputed(self):
        for key in ['power_W','force_N','speed_m_s','acceleration_m_s2','coordination_error_m','maneuver_error_m']:
            for val in [None,float('nan'),float('inf'),True,'100']:
                data=synthetic();data['samples'][3]=dataclasses.replace(data['samples'][3],**{key:val})
                with self.subTest(key=key,val=val),self.assertRaises(ValueError):analyze(**data)
        with self.assertRaises(TypeError):Sample(time_s=0,power_W=100)
        data=synthetic();data['samples']=[dataclasses.replace(x,power_W=1e308) for x in data['samples']]
        with self.assertRaises(ValueError):analyze(**data)
    def test_gaps_require_explicit_protocol_limit(self):
        data=synthetic();data['samples'].pop(2)
        with self.assertRaises(ValueError):analyze(**data)
        data['max_gap_s']=60;self.assertEqual(analyze(**data)['total']['work_net_J'],270000)
    def test_episodes_must_partition_and_alternate_types_exist(self):
        for eps in [[Episode(0,2700,'effort','a')], [Episode(0,20,'effort','a'),Episode(21,2700,'recovery','r')],
                    [Episode(0,40,'effort','a'),Episode(30,2700,'recovery','r')],
                    [Episode(0,30,'effort',''),Episode(30,2700,'recovery','r')],[]]:
            data=synthetic();data['episodes']=eps
            with self.assertRaises(ValueError):analyze(**data)
    def test_windows_require_early_and_late_effort(self):
        for key,value in [('early_end_s',0),('late_start_s',2700),('early_end_s',2690),('late_start_s',float('nan')),('max_gap_s',0)]:
            data=synthetic();data[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):analyze(**data)
        data=synthetic();data['early_end_s']=15
        with self.assertRaises(ValueError):analyze(**data)
    def test_no_comparison_across_unmatched_tasks(self):
        data=synthetic();data['episodes'][-1]=Episode(2670,2700,'effort','different_load')
        d=analyze(**data)
        self.assertEqual(d['early_late'],{})
        self.assertEqual(d['unmatched_task_ids'],['different_load','fixed_load'])
    def test_decline_and_improvement_not_clipped(self):
        for value,ratio,drop in [(80,.8,.2),(120,1.2,-.2)]:
            data=synthetic()
            data['samples']=[dataclasses.replace(x,power_W=value) if x.time_s>=2670 else x for x in data['samples']]
            c=analyze(**data)['early_late']['fixed_load']['metrics']['mean_power_W']
            self.assertAlmostEqual(c['late_over_early'],ratio);self.assertAlmostEqual(c['relative_drop'],drop)
    def test_zero_baseline_undefined_ratio(self):
        data=synthetic();data['samples']=[dataclasses.replace(x,power_W=0) for x in data['samples']]
        self.assertIsNone(analyze(**data)['early_late']['fixed_load']['metrics']['mean_power_W']['late_over_early'])
    def test_unequal_episode_work_not_compared(self):
        data=synthetic();data['episodes'][-2]=Episode(30,2640,'recovery','rest');data['episodes'][-1]=Episode(2640,2700,'effort','fixed_load');data['late_start_s']=2640
        self.assertIsNone(analyze(**data)['early_late']['fixed_load']['work_per_episode_late_over_early'])
    def test_reaction_accuracy_includes_omissions(self):
        data=synthetic();data['trials']=[Trial(1,'fixed_load',.2,True),Trial(2,'fixed_load',None,False,True),Trial(2671,'fixed_load',.3,True),Trial(2672,'fixed_load',.1,False)]
        d=analyze(**data);c=d['early_late']['fixed_load']
        self.assertEqual(d['reaction']['accuracy'],.5);self.assertEqual(d['reaction']['omissions'],1)
        self.assertEqual(c['reaction_early']['mean_correct_latency_s'],.2)
        self.assertAlmostEqual(c['correct_latency_late_over_early'],1.5)
        self.assertEqual(c['accuracy_change'],0)
    def test_invalid_trials(self):
        for trials in [[Trial(1,'a',None,True)], [Trial(1,'a',.1,True,True)], [Trial(1,'a',-.1,True)],
                       [Trial(1,'a',.1,1)], [Trial(1,'a',.1,True),Trial(1,'a',.1,True)], [Trial(2800,'a',.1,True)]]:
            data=synthetic();data['trials']=trials
            with self.assertRaises(ValueError):analyze(**data)
    def test_recovery_is_observed_not_fitted_time_constant(self):
        d=analyze(**synthetic());r=d['observed_recovery'][0]
        self.assertEqual(r['recovery_duration_s'],2640)
        self.assertEqual(r['next_over_previous_power'],1)
        self.assertIsNone(r['restored_fraction_to_early'])
    def test_separate_post45_and_reference(self):
        data=synthetic();data.update(post_samples=[Sample(t,80,160,1.6,0,.02,.04) for t in [2701,2711]],post_task_id='fixed_load')
        d=analyze(**data);p=d['post45']
        self.assertEqual(d['total']['work_net_J'],270000)  # post не входит в main work
        self.assertEqual(p['metrics']['work_net_J'],800)
        self.assertEqual(p['comparison_to_early']['mean_power_W']['late_over_early'],.8)
        data['post_samples']=[data['samples'][-1]]
        with self.assertRaises(ValueError):analyze(**data)
    def test_single_post_observation_no_fabricated_duration(self):
        data=synthetic();data.update(post_samples=[Sample(2701,80,160,1.6,0,.02,.04)],post_task_id='fixed_load')
        p=analyze(**data)['post45'];self.assertEqual(p['metrics']['duration_s'],0);self.assertEqual(p['metrics']['work_net_J'],0)
    def test_force_speed_errors_and_acceleration(self):
        d=analyze(**synthetic());m=d['early_late']['fixed_load']['metrics']
        self.assertEqual(m['mean_force_N']['early'],200)
        self.assertEqual(m['peak_speed_m_s']['early'],2)
        self.assertEqual(m['mean_coordination_error_m']['early'],.01)
        self.assertEqual(d['total']['peak_acceleration_m_s2'],0)
    def test_cli_reproducibility_and_nonmutation(self):
        data=synthetic();before=copy.deepcopy(data);one=analyze(**data);two=analyze(**data)
        self.assertEqual(one,two);self.assertEqual(before,data)
        payload={**data,'samples':[dataclasses.asdict(x) for x in data['samples']], 'episodes':[dataclasses.asdict(x) for x in data['episodes']]}
        payload['protocol']={k:payload.pop(k) for k in ['early_end_s','late_start_s','max_gap_s']}
        with tempfile.TemporaryDirectory() as td:
            input_path=Path(td)/'input.json';output_path=Path(td)/'output.json'
            input_path.write_text(json.dumps(payload),encoding='utf8')
            subprocess.run([sys.executable,str(ROOT/'tools/cpe45.py'),'--input',str(input_path),'--output',str(output_path)],check=True)
            self.assertEqual(json.loads(output_path.read_text('utf8')),one)
    def test_all_omitted_and_boundary_trials(self):
        data=synthetic();data['trials']=[Trial(30,'fixed_load',None,False,True),Trial(2700,'fixed_load',None,False,True)]
        d=analyze(**data)
        self.assertIsNone(d['reaction']['mean_response_latency_s'])
        self.assertEqual(d['reaction']['accuracy'],0)
        self.assertEqual(d['episodes'][0]['reaction']['trials'],0)
        self.assertEqual(d['episodes'][1]['reaction']['trials'],1)
        self.assertEqual(d['episodes'][2]['reaction']['trials'],1)
    def test_quantitative_recovery_fraction(self):
        data=synthetic()
        data['samples']=[dataclasses.replace(x,power_W=60 if 300<=x.time_s<=330 else (80 if x.time_s>=2670 else 100)) for x in data['samples']]
        data['episodes']=[Episode(0,30,'effort','fixed_load'),Episode(30,300,'recovery','rest'),Episode(300,330,'effort','fixed_load'),Episode(330,2670,'recovery','rest'),Episode(2670,2700,'effort','fixed_load')]
        r=analyze(**data)['observed_recovery'][-1]
        self.assertEqual(r['restored_fraction_to_early'],.5)
        self.assertEqual(r['power_change_W'],20)
    def test_invalid_post_data_and_negative_magnitudes(self):
        for key in ['force_N','speed_m_s','coordination_error_m','maneuver_error_m']:
            data=synthetic();data['samples'][1]=dataclasses.replace(data['samples'][1],**{key:-1})
            with self.assertRaises(ValueError):analyze(**data)
        data=synthetic();data.update(post_samples=[],post_task_id='fixed_load')
        with self.assertRaises(ValueError):analyze(**data)
        data=synthetic();data['post_task_id']='fixed_load'
        with self.assertRaises(ValueError):analyze(**data)
    def test_registered_target_and_preserved_history(self):
        goal=json.loads((ROOT/'research/targets/CPE45.json').read_text('utf8'))
        self.assertEqual(goal['target_id'],'TARGET-CPE45');self.assertEqual(goal['duration_s'],2700)
        self.assertIsNone(goal['success_thresholds']);self.assertEqual(goal['biological_interventions'],'NO_GO')
        self.assertEqual(goal['historical_experiments_cpe45_status'],'not_assessed')
        decisions=json.loads((ROOT/'registry/decisions.json').read_text('utf8'));issues=json.loads((ROOT/'registry/issues.json').read_text('utf8'))
        self.assertEqual(sum(x['id']=='DEC-0007' for x in decisions),1)
        self.assertEqual(next(x for x in issues if x['id']=='ISS-0011')['status'],'open')

if __name__=='__main__':unittest.main()
