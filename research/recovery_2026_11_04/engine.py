"""Competing endpoint models and auditable SI energy dynamics. No efficacy claim."""
from pathlib import Path
import sys,math,importlib.util
import numpy as np
BASE=Path(__file__).resolve().parent
OLD=BASE.parent/'cpe45_2026_11_04'
spec=importlib.util.spec_from_file_location('cpe45_legacy_model',OLD/'model.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def defaults():
    p=legacy.integrated.load();d=legacy.load()['dynamic']
    return dict(d,eta=p['delta_efficiency'],maintenance_W=p['metabolic_intercept_W'],oxygen_cap_W=legacy.integrated.energy(p)['aerobic_W'],demand_W=1000.,initial_fraction=1.,fast_power_cap_W=d['fast_capacity_J']/d['fast_discharge_tau_s'],slow_power_cap_W=d['slow_capacity_J']/d['slow_discharge_tau_s'])

def cycle(rest_s=90.,effort_s=6.,repetitions=10,dt=.5,mode='legacy',overrides=None,trace=False):
    """D2 separates release-power caps from capacity; capacities and costs remain scenarios.

    Analytical first-order oxygen update uses the interval-average oxidative energy
    in corrected mode. Legacy mode deliberately retains right-end rectangular input.
    """
    q=defaults();q.update(overrides or {})
    if mode not in ('legacy','corrected'):raise ValueError('mode')
    if not 0<dt<=1 or not 0<q['eta']<=1 or not 0<q['recharge_efficiency']<=1:raise ValueError('dt/efficiency')
    if not 0<=q['initial_fraction']<=1:raise ValueError('initial fraction')
    if any(not math.isfinite(v) or v<0 for v in q.values()):raise ValueError('finite positive SI parameters')
    if any(q[k]<=0 for k in ['oxygen_tau_s','fast_recovery_tau_s','slow_recovery_tau_s','fast_discharge_tau_s','slow_discharge_tau_s']):raise ValueError('tau')
    if rest_s<0 or effort_s<=0 or repetitions<1:raise ValueError('protocol')
    fast=q['fast_capacity_J']*q['initial_fraction'];slow=q['slow_capacity_J']*q['initial_fraction'];initial=fast+slow
    oxygen=q['maintenance_W'];fatigue=0.;t=0.;bout=[];rows=[]
    sums=dict(oxidative_J=0.,external_J=0.,heat_J=0.,recharged_J=0.,withdrawn_J=0.)
    for rep in range(repetitions):
        work=0.
        for effort,seconds in [(True,effort_s),(False,rest_s)]:
            elapsed=0.
            while elapsed<seconds-1e-10:
                h=min(dt,seconds-elapsed)
                demand=q['demand_W']*max(q['fatigue_floor'],1-fatigue) if effort else 0.
                recovery=(q['fast_capacity_J']-fast)/q['fast_recovery_tau_s']+(q['slow_capacity_J']-slow)/q['slow_recovery_tau_s']
                target=min(q['oxygen_cap_W'],q['maintenance_W']+demand/q['eta']+recovery/q['recharge_efficiency'])
                before=oxygen;oxygen=legacy.approach(oxygen,target,h,q['oxygen_tau_s'])
                ox=oxygen*h if mode=='legacy' else target*h+(before-target)*q['oxygen_tau_s']*(1-math.exp(-h/q['oxygen_tau_s']))
                overhead=min(ox,q['maintenance_W']*h);aerobic=max(0.,ox-overhead)
                if mode=='legacy':
                    fb=fast*(1-math.exp(-h/q['fast_discharge_tau_s']));sb=slow*(1-math.exp(-h/q['slow_discharge_tau_s']))
                else:
                    fb=min(fast,q['fast_power_cap_W']*h);sb=min(slow,q['slow_power_cap_W']*h)
                external=min(demand*h,(aerobic+fb+sb)*q['eta'])
                need=max(0.,external/q['eta']-aerobic)
                wf=min(fb,need);ws=min(sb,max(0.,need-wf));withdraw=wf+ws
                fast-=wf;slow-=ws;rf=rs=0.
                if need<1e-10:
                    surplus=max(0.,aerobic-external/q['eta'])
                    rf=min((q['fast_capacity_J']-fast)*(1-math.exp(-h/q['fast_recovery_tau_s'])),surplus*q['recharge_efficiency'])
                    surplus-=rf/q['recharge_efficiency']
                    rs=min((q['slow_capacity_J']-slow)*(1-math.exp(-h/q['slow_recovery_tau_s'])),surplus*q['recharge_efficiency'])
                    fast+=rf;slow+=rs
                recharge=rf+rs;heat=ox+withdraw-recharge-external
                sums['oxidative_J']+=ox;sums['external_J']+=external;sums['heat_J']+=heat;sums['recharged_J']+=recharge;sums['withdrawn_J']+=withdraw
                fatigue=legacy.approach(fatigue,q['fatigue_rate_s_inv']*(external/h/500)*q['fatigue_recovery_tau_s'],h,q['fatigue_recovery_tau_s'])
                fatigue=min(1-q['fatigue_floor'],fatigue)
                elapsed+=h;t+=h
                if effort:work+=external
                if trace:rows.append(dict(time_s=t,effort=effort,repetition=rep+1,fast_J=fast,slow_J=slow,oxygen_W=oxygen,output_W=external/h,fatigue=fatigue,**sums,energy_residual_J=sums['oxidative_J']+initial-fast-slow-sums['external_J']-sums['heat_J']))
        bout.append(work/effort_s)
    residual=sums['oxidative_J']+initial-fast-slow-sums['external_J']-sums['heat_J']
    return np.array(bout),dict(time_s=t,fast_J=fast,slow_J=slow,fatigue=fatigue,energy_residual_J=residual,**sums),rows

def recovery_shape(depletion,tau,rest,reps=10):
    """Two identifiable candidates are effective output-decrement parameters, not PCr."""
    if not 0<=depletion<=1 or tau<=0:raise ValueError('recovery parameters')
    x=1.;out=[];r=math.exp(-rest/tau)
    for _ in range(reps):
        out.append(x);x=1-(1-(1-depletion)*x)*r
    return np.array(out)

def shape(label,params,rest,reference_W=1000.):
    n=np.arange(10)
    if label=='constant':return np.ones(10)
    if label=='linear':return 1+params['slope']*n
    if label=='monoexponential':return 1+params['amplitude']*(1-np.exp(-n/params['tau_reps']))
    if label=='empirical_recovery':return recovery_shape(params['depletion'],params['tau_s'],rest)
    if label in ('D1_existing','D2_corrected','D4_hybrid_conditional'):
        overrides={'fatigue_rate_s_inv':0.}
        if label!='D1_existing':overrides['demand_W']=reference_W
        if label=='D4_hybrid_conditional':overrides['fast_recovery_tau_s']=params['tau_s']
        powers,_,_=cycle(rest_s=rest,mode='legacy' if label=='D1_existing' else 'corrected',overrides=overrides)
        if label!='D1_existing':return powers/reference_W
        return powers/powers[0] if powers[0]>0 else np.zeros(10)
    raise ValueError(label)
