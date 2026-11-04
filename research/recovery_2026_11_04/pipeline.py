"""Development and explicitly gated test. Run --lock before --test; never tune on test."""
from pathlib import Path
import argparse,csv,hashlib,json,math
import numpy as np
import dataset,engine
BASE=Path(__file__).resolve().parent
SEED=20261104
LABELS=['constant','linear','monoexponential','D1_existing','D2_corrected','empirical_recovery','D4_hybrid_conditional']
ELIGIBLE=LABELS[:-1]  # D4 imports an effective output tau, not an identified PCr tau.

def save_json(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def save_csv(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader()
        for r in rows:w.writerow({k:format(v,'.12g') if isinstance(v,(float,np.floating)) else v for k,v in r.items()})
def scoring_rows(split='development',unlock=False):return [r for r in dataset.power_rows(split,unlock) if r['repetition']>1]

def fit(rows):
    """Fit only observable output-shape coefficients; no simultaneous latent physiological fit."""
    y=np.array([r['ratio'] for r in rows]);n=np.array([r['repetition']-1 for r in rows]);rest=np.array([r['rest_s'] for r in rows])
    slope=float(np.dot(n,y-1)/np.dot(n,n))
    options=[]
    for tau in [1.,2.,3.,5.,10.]:
        x=1-np.exp(-n/tau);amp=float(np.clip(np.dot(x,y-1)/np.dot(x,x),-.6,.6));err=np.mean((1+amp*x-y)**2)
        options.append((err,amp,tau))
    _,amp,tau=min(options)
    recover=[]
    for depletion in np.linspace(0,.6,61):
        for tau_s in np.geomspace(1,600,91):
            shape=np.array([engine.recovery_shape(float(depletion),float(tau_s),r) for r in [12,18,24]])
            pred=shape[np.searchsorted([12,18,24],rest),n]
            recover.append((float(np.mean((pred-y)**2)),float(depletion),float(tau_s)))
    _,depletion,tau_s=min(recover)
    params={label:{} for label in LABELS}
    params['linear']={'slope':slope};params['monoexponential']={'amplitude':amp,'tau_reps':tau}
    params['empirical_recovery']={'depletion':depletion,'tau_s':tau_s}
    params['D4_hybrid_conditional']={'tau_s':tau_s,'interpretation':'effective output recovery imported as conditional stress-test, not identified PCr kinetics'}
    return params,recover

def predictions(rows,label,params):
    cache={};result=[]
    for r in rows:
        key=(r['rest_s'],r['reference_W'])
        if key not in cache:cache[key]=engine.shape(label,params,r['rest_s'],r['reference_W'])
        pred=float(cache[key][r['repetition']-1])*r['reference_W']
        result.append(dict(participant=r['participant'],rest_s=r['rest_s'],repetition=r['repetition'],predicted_W=pred,residual_W=pred-r['power_W'],observed_W=r['power_W'],predicted_ratio=pred/r['reference_W'],reference_W=r['reference_W']))
    return result

def metric(rows):
    e=np.array([r['residual_W'] for r in rows]);p=np.array([r['predicted_W'] for r in rows]);y=np.array([r['observed_W'] for r in rows])
    intercept,slope=np.linalg.lstsq(np.column_stack([np.ones(len(p)),p]),y,rcond=None)[0] if np.std(p)>1e-10 else (float(y.mean()),0.)
    return dict(n=len(e),MAE_W=float(np.mean(abs(e))),RMSE_W=float(np.sqrt(np.mean(e**2))),bias_W=float(e.mean()),calibration_intercept_W=float(intercept),calibration_slope=float(slope))

def input_digest(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def code_hashes():return {name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in ['engine.py','dataset.py','pipeline.py']}

def build_lock():
    rows=scoring_rows();ids=sorted({r['participant'] for r in rows});cv=[];scores=[]
    params,profile=fit(rows)
    for held in ids:
        train=[r for r in rows if r['participant']!=held];val=[r for r in rows if r['participant']==held]
        local,_=fit(train)
        for label in LABELS:
            pp=predictions(val,label,local[label]);cv.extend(dict(model=label,**r) for r in pp)
    for label in LABELS:
        selected=[r for r in cv if r['model']==label]
        scores.append(dict(model=label,**metric(selected)))
    selected=min((r for r in scores if r['model'] in ELIGIBLE),key=lambda r:r['RMSE_W'])['model']
    lock=dict(preregistration_commit='9f25664',source_commit='c7a7c9caa7f619f64c88b9e0430a6b1f83148807',seed=SEED,development_ids=ids,test_ids=[3,6,9,12,15,18,21],training_observations=len(rows),training_sha256=input_digest(rows),source_metadata_sha256=hashlib.sha256((BASE/'osf_provenance.json').read_bytes()).hexdigest(),code_hashes=code_hashes(),models=params,selected_model=selected,selection='grouped leave-one-participant-out RMSE among preregistered eligible models',D4_status='diagnostic only; effective output tau is not physical PCr tau',grouped_cv_scores=scores,test_status='NOT_OPENED',CPE45_status='not_assessed',intervention_status='NO_GO')
    if (BASE/'model_lock.json').exists():raise ValueError('lock already exists; do not overwrite after test')
    save_json(BASE/'model_lock.json',lock)
    out=BASE/'results';out.mkdir(exist_ok=True)
    save_csv(out/'development_cv.csv',scores)
    # No source outcome cells republished where source redistribution licence is absent.
    save_csv(out/'development_cv_predictions.csv',[{k:r[k] for k in ['model','participant','rest_s','repetition','predicted_W','predicted_ratio']} for r in cv])
    best=min(x[0] for x in profile);tau_profile=[]
    sigma2=best  # explicit homoscedastic normalized-error working assumption
    for tau in sorted({x[2] for x in profile}):
        options=[x for x in profile if x[2]==tau];loss,dep,_=min(options)
        tau_profile.append(dict(tau_s=tau,depletion=dep,MSE_ratio=loss,delta_profile_chi2=(loss-best)*len(rows)/max(sigma2,1e-20)))
    save_csv(out/'recovery_profile.csv',tau_profile)
    save_json(out/'data_audit.json',dataset.development_audit())
    print(json.dumps(dict(selected_model=selected,models=params,CV=scores),indent=2))

def load_lock():
    lock=json.loads((BASE/'model_lock.json').read_text('utf8'))
    assert lock['code_hashes']==code_hashes(),'code moved after lock'
    assert lock['training_sha256']==input_digest(scoring_rows()),'training inputs changed'
    assert lock['source_metadata_sha256']==hashlib.sha256((BASE/'osf_provenance.json').read_bytes()).hexdigest()
    return lock

def evaluate_test(out=None):
    lock=load_lock();rows=scoring_rows('test',True)
    assert not set(lock['development_ids'])&{r['participant'] for r in rows}
    out=out or BASE/'results';out.mkdir(exist_ok=True)
    scores=[];by_subject=[];by_protocol=[];public_predictions=[];all_predictions={};recovery=[]
    for label in LABELS:
        pred=predictions(rows,label,lock['models'][label]);all_predictions[label]=pred
        scores.append(dict(model=label,**metric(pred)))
        public_predictions.extend(dict(model=label,**{k:r[k] for k in ['participant','rest_s','repetition','predicted_W','predicted_ratio']}) for r in pred)
        for sid in sorted({r['participant'] for r in pred}):by_subject.append(dict(model=label,participant=sid,**metric([r for r in pred if r['participant']==sid])))
        for rest in [12,18,24]:by_protocol.append(dict(model=label,rest_s=rest,**metric([r for r in pred if r['rest_s']==rest])))
        delta=[]
        for sid in sorted({r['participant'] for r in pred}):
            for rest in [12,18,24]:
                pp=sorted([r for r in pred if r['participant']==sid and r['rest_s']==rest],key=lambda x:x['repetition'])
                delta.extend((b['predicted_W']-a['predicted_W'])-(b['observed_W']-a['observed_W']) for a,b in zip(pp,pp[1:]) if b['repetition']==a['repetition']+1)
        recovery.append(dict(model=label,n=len(delta),MAE_delta_power_W=float(np.mean(np.abs(delta))),RMSE_delta_power_W=float(np.sqrt(np.mean(np.array(delta)**2))),interpretation='between-consecutive-effort change, not measured PCr recovery'))
    ids=lock['test_ids'];rng=np.random.default_rng(SEED);draws=rng.choice(ids,(2000,len(ids)));boot=[]
    baseline=all_predictions['constant']
    for label in LABELS:
        pred=all_predictions[label];rmses=[];diff=[]
        for sample in draws:
            e=[r['residual_W'] for sid in sample for r in pred if r['participant']==sid]
            b=[r['residual_W'] for sid in sample for r in baseline if r['participant']==sid]
            rmse=float(np.sqrt(np.mean(np.array(e)**2)));rmses.append(rmse);diff.append(rmse-float(np.sqrt(np.mean(np.array(b)**2))))
        boot.append(dict(model=label,RMSE_p025_W=float(np.quantile(rmses,.025)),RMSE_p975_W=float(np.quantile(rmses,.975)),paired_RMSE_minus_constant_p025_W=float(np.quantile(diff,.025)),paired_RMSE_minus_constant_p975_W=float(np.quantile(diff,.975)),resamples=2000,participants=len(ids)))
    save_csv(out/'test_scores.csv',scores);save_csv(out/'test_participants.csv',by_subject);save_csv(out/'test_protocols.csv',by_protocol);save_csv(out/'test_predictions.csv',public_predictions);save_csv(out/'test_bootstrap.csv',boot);save_csv(out/'test_recovery_changes.csv',recovery)
    result=dict(selected_model_before_test=lock['selected_model'],test_ids=ids,test_observations=len(rows),scores=scores,bootstrap=boot,status='new independent cohort, locked participant test for power endpoint only; CPE45 NOT EXTERNALLY VALIDATED',source='OSF db3sk; no PCr and no continuous VO2',model_lock_sha256=hashlib.sha256((BASE/'model_lock.json').read_bytes()).hexdigest(),raw_data_policy='unlicensed raw omitted; public retrieval recipe + SHA256; predictions/statistics are our derived research outputs')
    save_json(out/'test_summary.json',result)
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--test',action='store_true');args=p.parse_args()
    if args.lock:build_lock()
    elif args.test:evaluate_test()
    else:p.error('--lock or --test required')
