"""Locked participant-disjoint short cycling endpoint test, not CPE45 validation."""
import math
import numpy as np
import model,dataset

def cycling_shape(rate,dt=.5):
    """Same reserve allocator; cycling demand replaces uncalibrated running mechanics.

    Fixed nominal 1000 W demand; normalized to first simulated sprint, no participant
    parameters estimated. Peripheral fatigue rate alone selected on fit participants.
    No thermal/reaction prediction validated by this isolated endpoint.
    """
    d=model.load()['dynamic'];d=dict(d,fatigue_rate_s_inv=rate)
    p=model.integrated.load();eta=p['delta_efficiency'];maintenance=p['metabolic_intercept_W']
    cap=model.integrated.energy(p)['aerobic_W'];oxygen=maintenance
    fast=d['fast_capacity_J'];slow=d['slow_capacity_J'];fatigue=0.;work=[]
    for rep in range(10):
        total=0.
        for effort,seconds in [(True,6),(False,90)]:
            for _ in range(round(seconds/dt)):
                demand=1000*max(d['fatigue_floor'],1-fatigue) if effort else 0.
                recovery=(d['fast_capacity_J']-fast)/d['fast_recovery_tau_s']+(d['slow_capacity_J']-slow)/d['slow_recovery_tau_s']
                target=min(cap,maintenance+demand/eta+recovery/d['recharge_efficiency'])
                oxygen=model.approach(oxygen,target,dt,d['oxygen_tau_s'])
                aerobic=max(0.,oxygen-maintenance)*dt
                reserve=fast*(1-math.exp(-dt/d['fast_discharge_tau_s']))+slow*(1-math.exp(-dt/d['slow_discharge_tau_s']))
                output=min(demand,(aerobic+reserve)*eta/dt)
                fast,slow,_,_=model.allocate(aerobic,output/eta*dt,fast,slow,d,dt)
                fatigue=model.approach(fatigue,rate*(output/500)*d['fatigue_recovery_tau_s'],dt,d['fatigue_recovery_tau_s'])
                if effort:total+=output*dt
        work.append(total/6)
    return np.array(work)/work[0]

def prepare(rows):
    out=[];excluded=[]
    for subject in sorted({r['participant'] for r in rows if r['split']!='excluded_unresolved_pairing'}):
        group=[r for r in rows if r['participant']==subject and r['split']!='excluded_unresolved_pairing']
        first=next(r['mean_power_W'] for r in group if r['repetition']==1)
        if first is None or first<=0:
            excluded.append(dict(participant=subject,reason='first sprint missing; no imputation'));continue
        for row in group:
            if row['repetition']==1 or row['mean_power_W'] is None:continue
            out.append(dict(row,reference_power_W=first,ratio=row['mean_power_W']/first))
    return out,excluded

def evaluate():
    raw=dataset.observations();data,excluded=prepare(raw)
    fit=[r for r in data if r['split']=='fit'];hold=[r for r in data if r['split']=='validation']
    loss=lambda shape:np.mean([(shape[r['repetition']-1]-r['ratio'])**2 for r in fit])
    xs=np.arange(10)
    # One signed empirical slope allows measured potentiation; not forced to decline.
    slopes=np.linspace(-.1,.1,401)
    slope=min(slopes,key=lambda b:loss(1+b*xs))
    # Monoexponential bounded restoration/decrement endpoint, not mechanistic PCr fit.
    candidates=[(a,tau) for a in np.linspace(-.6,.6,61) for tau in [1,2,3,5,10]]
    amp,tau=min(candidates,key=lambda at:loss(1+at[0]*(1-np.exp(-xs/at[1]))))
    rates=[0,.0001,.0003,.001,.003,.01]
    shapes={rate:cycling_shape(rate) for rate in rates};rate=min(rates,key=lambda r:loss(shapes[r]))
    models={'constant':np.ones(10),'monoexponential':1+amp*(1-np.exp(-xs/tau)),'empirical_linear':1+slope*xs,'coupled_energy_peripheral':shapes[rate]}
    predictions=[];scores=[];participants=[]
    for label,shape in models.items():
        for split,items in [('fit',fit),('validation',hold)]:
            for r in items:
                pred=float(shape[r['repetition']-1])*r['reference_power_W']
                predictions.append(dict(model=label,**r,predicted_W=pred,residual_W=pred-r['mean_power_W']))
            selected=[x for x in predictions if x['model']==label and x['split']==split]
            errors=np.array([x['residual_W'] for x in selected])
            scores.append(dict(model=label,split=split,n=len(errors),participants=len({r['participant'] for r in items}),MAE_W=float(np.mean(abs(errors))),RMSE_W=float(np.sqrt(np.mean(errors**2))),bias_W=float(np.mean(errors))))
            for subject in sorted({r['participant'] for r in items}):
                e=np.array([x['residual_W'] for x in selected if x['participant']==subject])
                participants.append(dict(model=label,split=split,participant=subject,n=len(e),MAE_W=float(np.mean(abs(e))),RMSE_W=float(np.sqrt(np.mean(e**2))),bias_W=float(np.mean(e))))
    rng=np.random.default_rng(20261104);bootstrap=[]
    for label in models:
        selected=[x for x in predictions if x['model']==label and x['split']=='validation'];ids=sorted({x['participant'] for x in selected})
        estimates=[]
        for _ in range(1000):
            sample=rng.choice(ids,len(ids));e=[x['residual_W'] for sub in sample for x in selected if x['participant']==sub]
            estimates.append(np.sqrt(np.mean(np.array(e)**2)))
        bootstrap.append(dict(model=label,RMSE_cluster_p025_W=float(np.quantile(estimates,.025)),RMSE_cluster_p975_W=float(np.quantile(estimates,.975)),interpretation='participant cluster resampling, conditional on baseline sprint; not external population CI'))
    # PCr aggregate diagnostic: fit tau on 90 s, test 360 s in SAME cohort, not independent.
    initial=.197;at90=.650;at360=.855;tau_pcr=-90/math.log((1-at90)/(1-initial));pred=1-(1-initial)*math.exp(-360/tau_pcr)
    diagnostic=dict(source='SRC-0032',fit_time_s=90,test_time_s=360,same_cohort=True,tau_s=tau_pcr,predicted_fraction=pred,observed_fraction=at360,residual_percentage_points=100*(pred-at360),interpretation='aggregate temporal holdout; rejects universal monoexponential recovery, no independent validation')
    metadata=dict(fit_ids=sorted({x['participant'] for x in fit}),validation_ids=sorted({x['participant'] for x in hold}),excluded=excluded,excluded_climate_rows=22,raw_rows=44,raw_mean_power_cells=440,missing_mean_power_cells=sum(r['mean_power_W'] is None for r in raw),selected_parameters=dict(empirical_slope_per_rep=float(slope),monoexponential_amplitude=float(amp),monoexponential_tau_repetitions=tau,coupled_fatigue_rate_s_inv=rate),pc_r_diagnostic=diagnostic,bootstrap=bootstrap,status='limited participant-disjoint endpoint test; integrated CPE45 not_empirically_validated',baseline_conditioning='first observed sprint in validation is an input; repetitions 2..10 predicted; no future sprint used for fit')
    return raw,predictions,scores,participants,metadata
