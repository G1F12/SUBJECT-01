"""Restricted real-data systemic cost validation; not sprint power validation."""
import json,hashlib,math,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from acquire import BASE,save,digest
import dataset
sys.path.insert(0,str(BASE.parent/'recovery_2026_11_04'))
import engine
LABELS=['constant','affine','quadratic','baseline_slope','historical_D2_equilibrium']

def rows(split='development',unlock=False):
    if split!='development' and not unlock:raise ValueError('test gate')
    x=json.loads((BASE/f'{split}_stage_audit.json').read_text('utf8'))
    bas={r['participant']:r['cost_W'] for r in x['baseline']}
    return [dict(r,baseline_W=bas.get(r['participant'])) for r in x['stages'] if r['primary_eligible']]

def weights(rs):
    ids=[r['participant'] for r in rs];return np.array([1/ids.count(s) for s in ids])
def design(rs,degree):
    p=np.array([r['power_W']/100 for r in rs]);return np.column_stack([p**k for k in range(degree+1)])
def fit(rs):
    y=np.array([r['cost_W'] for r in rs]);w=np.sqrt(weights(rs));out={}
    for label,d in [('constant',0),('affine',1),('quadratic',2)]:
        x=design(rs,d);beta=np.linalg.lstsq(x*w[:,None],y*w,rcond=None)[0];out[label]=beta.tolist()
    if all(r['baseline_W'] is not None for r in rs):
        p=np.array([r['power_W'] for r in rs]);b=np.array([r['baseline_W'] for r in rs])
        out['baseline_slope']=[float(np.sum(w*w*p*(y-b))/np.sum(w*w*p*p))]
    else:out['baseline_slope']=None
    q=engine.defaults();out['historical_D2_equilibrium']=[q['maintenance_W'],1/q['eta']]
    return out

def predict(rs,label,params):
    if label=='historical_D2_equilibrium':return np.array([params[0]+params[1]*r['power_W'] for r in rs])
    if label=='baseline_slope':return np.array([r['baseline_W']+params[0]*r['power_W'] for r in rs])
    return design(rs,len(params)-1)@params

def metrics(rs,pred):
    e=np.array(pred)-[r['cost_W'] for r in rs];w=weights(rs);w=w/w.sum()
    return dict(n=len(rs),participants=len({r['participant'] for r in rs}),RMSE_W=float(np.sqrt(np.sum(w*e*e))),MAE_W=float(np.sum(w*abs(e))),bias_W=float(np.sum(w*e)))
def codehashes():return {n:digest((BASE/n).read_bytes()) for n in ['dataset.py','models.py']}

def build_lock():
    target=BASE/'model_lock.json'
    if target.exists():raise ValueError('immutable model lock exists; no overwrite')
    rs=rows();params=fit(rs);cv=[]
    eligible=['constant','affine','quadratic','baseline_slope']
    for sid in sorted({r['participant'] for r in rs}):
        train=[r for r in rs if r['participant']!=sid];held=[r for r in rs if r['participant']==sid];local=fit(train)
        for label in LABELS:
            if local[label] is None:continue
            pp=predict(held,label,local[label]);cv.extend(dict(model=label,participant=sid,power_W=r['power_W'],cost_W=r['cost_W'],predicted_W=float(p)) for r,p in zip(held,pp))
    scores=[]
    for label in LABELS:
        r=[v for v in cv if v['model']==label]
        if r:scores.append(dict(model=label,**metrics(r,[v['predicted_W'] for v in r])))
    # Quadratic is admissible only if nonnegative throughout predeclared load range.
    probe=np.column_stack([np.ones(201),np.linspace(0,2,201),np.linspace(0,2,201)**2])
    if min(probe@params['quadratic'])<0:eligible.remove('quadratic')
    if params['baseline_slope'] is None:eligible.remove('baseline_slope')
    selected=min((r for r in scores if r['model'] in eligible),key=lambda r:r['RMSE_W'])['model']
    lock=dict(preregistration_commit='0446eaadcecb7c4ebea3613d20527a6d3fd94897',base_commit='a4d3a04ab8ef0fc056815989f4b775cf9773f3ca',
      code_sha256=codehashes(),development_snapshot_sha256=digest((BASE/'development_stage_audit.json').read_bytes()),
      source_retrieval_sha256=digest((BASE/'cpet_retrieval.json').read_bytes()),parameters=params,selected_model=selected,
      development_ids=sorted({r['participant'] for r in rs}),test_ids=[i for i in dataset.ids() if i%5==0],LOPO_scores=scores,
      endpoint='systemic costW from measuredVO2/VCO2, given prescribed cycleW; NOT independently predicted mechanicalpower',
      reduced_model_status='absolute systemiccost NOT DEFINED by9Dquotient without independent measurement layer; no fake eta1 conversion',
      test_status='NOT_OPENED',metrics='participant-balancedRMSE primary;MAE,bias,calibration;2000pairedparticipantbootstrap seed20261106',
      NO_GO=True,CPE45='NOT EXTERNALLY VALIDATED')
    save(target,lock);save(BASE/'results/development_cv.json',scores)
    print(json.dumps(dict(selected=selected,parameters=params,CV=scores),indent=2))
    return lock

def load_lock():
    x=json.loads((BASE/'model_lock.json').read_text('utf8'))
    assert x['code_sha256']==codehashes(),'locked code changed'
    assert x['development_snapshot_sha256']==digest((BASE/'development_stage_audit.json').read_bytes())
    assert x['source_retrieval_sha256']==digest((BASE/'cpet_retrieval.json').read_bytes())
    return x

def evaluate():
    lock=load_lock();rs=rows('test',True)
    assert not set(lock['development_ids'])&{r['participant'] for r in rs}
    scores=[];people=[];predictions=[];rng=np.random.default_rng(20261106)
    ids=sorted({r['participant'] for r in rs});draws=rng.choice(ids,(2000,len(ids)));allpred={}
    for label in LABELS:
        if lock['parameters'][label] is None:continue
        pred=predict(rs,label,lock['parameters'][label]);allpred[label]=pred;score=dict(model=label,**metrics(rs,pred))
        y=np.array([r['cost_W'] for r in rs]);w=np.sqrt(weights(rs));x=np.column_stack([np.ones(len(pred)),pred])
        a,b=np.linalg.lstsq(x*w[:,None],y*w,rcond=None)[0];score.update(calibration_intercept_W=float(a),calibration_slope=float(b));scores.append(score)
        for sid in ids:
            ix=[i for i,r in enumerate(rs) if r['participant']==sid];people.append(dict(model=label,participant=sid,**metrics([rs[i] for i in ix],pred[ix])))
        predictions.extend(dict(model=label,participant=r['participant'],stage=r['stage'],observed_cost_W=r['cost_W'],given_power_W=r['power_W'],predicted_cost_W=float(p)) for r,p in zip(rs,pred))
    boot=[];subject_mse={label:np.array([np.mean([(pred[i]-rs[i]['cost_W'])**2 for i in range(len(rs)) if rs[i]['participant']==sid]) for sid in ids]) for label,pred in allpred.items()}
    di=np.searchsorted(ids,draws)
    for label,mse in subject_mse.items():
        rmse=np.sqrt(mse[di].mean(axis=1));diff=rmse-np.sqrt(subject_mse['constant'][di].mean(axis=1));hist=rmse-np.sqrt(subject_mse['historical_D2_equilibrium'][di].mean(axis=1))
        boot.append(dict(model=label,RMSE_95_W=np.quantile(rmse,[.025,.975]).tolist(),paired_minus_constant_95_W=np.quantile(diff,[.025,.975]).tolist(),paired_minus_historical_95_W=np.quantile(hist,[.025,.975]).tolist()))
    chosen=next(r for r in boot if r['model']==lock['selected_model'])
    passed=chosen['paired_minus_constant_95_W'][1]<0 and chosen['paired_minus_historical_95_W'][1]<0
    out=dict(scores=scores,participant_errors=people,predictions=predictions,bootstrap=boot,selected_before_test=lock['selected_model'],test_ids=ids,
      limited_systemic_cost_validation_passed=bool(passed),mechanical_power_validation='NOT DONE',CPE45_validation='NOT DONE',
      lock_sha256=digest((BASE/'model_lock.json').read_bytes()),NO_GO=True,scope=lock['endpoint'])
    save(BASE/'results/independent_test.json',out)
    print(json.dumps(dict(scores=scores,bootstrap=boot,limited_systemic_cost_validation_passed=passed),indent=2))
    return out

if __name__=='__main__':
    (BASE/'results').mkdir(exist_ok=True)
    if '--lock' in sys.argv:build_lock()
    elif '--test' in sys.argv:
        if (BASE/'results/independent_test.json').exists():raise ValueError('test already evaluated; use numerical replay checker, never retune')
        dataset.export('test',True);evaluate()
