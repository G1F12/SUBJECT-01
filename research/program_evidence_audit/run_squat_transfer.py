"""Participant-held-out squat moment prediction, see EXP-0081 protocol."""
import hashlib, json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
from run_audit import text_sha256
HERE=Path(__file__).resolve().parent
root=Path(sys.argv[1]); manifest=json.loads((HERE/'SQUAT_DATA_MANIFEST.json').read_text(encoding='utf-8'))
for record in manifest['files']:
    assert hashlib.sha256((root/record['path']).read_bytes()).hexdigest()==record['sha256']
subjects=sorted({x['path'].split('/')[0] for x in manifest['files']})
series={}; exclusions=[]
for person in subjects:
    for load in (0,25):
        paths=sorted({str(Path(r['path']).parent).replace('\\','/') for r in manifest['files'] if r['path'].startswith(person+'/') and re.search(fr'_({load})lbs/',r['path'])})
        if not paths:
            exclusions.append(f'{person} {load}: missing directory'); continue
        folder=paths[0]; basename=folder.split('/')[-1]; prefix=f'{person}_{basename}'
        def read(suffix): return pd.read_csv(root/folder/f'{prefix}_{suffix}.csv')
        try:
            a,v,m,f=(read(x) for x in ('angle','velocity','moment_filt','activity_flag'))
            if not all(len(x)==len(a) and np.allclose(x['time'],a['time'],atol=1e-8,rtol=0) for x in (v,m,f)):
                raise ValueError('time mismatch')
            z=np.column_stack((a['knee_angle_r'],v['knee_velocity_r'],m['knee_angle_r_moment']))[::10]
            active=np.asarray(f['right'])[::10]==1
            z=z[active & np.isfinite(z).all(axis=1)]
            if len(z)<10: raise ValueError('fewer than 10 eligible rows')
            series[(person,load)]=z
        except (OSError,KeyError,ValueError) as e: exclusions.append(f'{person} {load}: {e}')
people=[p for p in subjects if (p,0) in series and (p,25) in series]
assert len(people)>=5
predictions={0:[],25:[]}
for p in people:
    train=[series[(q,0)] for q in people if q!=p]
    x=np.concatenate(train); weights=np.concatenate([np.full(len(z),1/len(z)) for z in train])
    def fit(d):
        w=np.sqrt(weights); return np.linalg.lstsq(d*w[:,None],x[:,2]*w,rcond=None)[0]
    models=[fit(np.ones((len(x),1))), fit(np.column_stack((np.ones(len(x)),x[:,0]))), fit(np.column_stack((np.ones(len(x)),x[:,:2])))]
    for load in (0,25):
        z=series[(p,load)]; n=len(z)
        inputs=[np.ones((n,1)),np.column_stack((np.ones(n),z[:,0])),np.column_stack((np.ones(n),z[:,:2]))]
        residuals=np.column_stack([a@b-z[:,2] for a,b in zip(inputs,models)])
        predictions[load].append((np.abs(residuals).mean(axis=0),residuals.mean(axis=0),n))
def summarize(rows):
    a=np.array([r[0] for r in rows]); b=np.array([r[1] for r in rows]); delta=a[:,1]-a[:,2]
    rng=np.random.default_rng(20261120); idx=rng.integers(0,len(delta),(10000,len(delta)))
    return {'participants':len(rows),'eligible_downsampled_frames':sum(r[2] for r in rows),
            'mae_constant_angle_dynamic_source_units':a.mean(axis=0).tolist(),'bias_constant_angle_dynamic_source_units':b.mean(axis=0).tolist(),
            'paired_gain_angle_minus_dynamic_source_units':delta.mean(),'paired_bootstrap_ci95_source_units':np.quantile(delta[idx].mean(axis=1),[.025,.975]).tolist()}
result={'experiment_id':'EXP-0081','classification':'EXPLORATORY_INVERSE_DYNAMICS','source_archive_md5_publisher_only':manifest['archive_md5_publisher_only'],
        'manifest_sha256_lf':text_sha256(HERE/'SQUAT_DATA_MANIFEST.json'),'protocol_sha256_lf':text_sha256(HERE/'SQUAT_TRANSFER_PROTOCOL.md'),
        'runner_sha256_lf':text_sha256(Path(__file__)),'retrieval_sha256_lf':text_sha256(HERE/'retrieve_squat_data.py'),
        'moment_units_status':'UNRESOLVED_source_table_Nm_plot_code_Nm_per_kg','participants_eligible':len(people),'exclusions':exclusions,'held_out_0lbs':summarize(predictions[0]),'held_out_25lbs':summarize(predictions[25])}
(HERE/'SQUAT_TRANSFER_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
