"""Post-lock falsification, identifiability and scenario verification; never retunes test models."""
from pathlib import Path
import csv,json,math
import numpy as np
import engine,pipeline,dataset
BASE=Path(__file__).resolve().parent

def legacy_counterfactual(rest=90.,dt=.5,overrides=None,initial_oxygen=None,constant_release=False):
    """Instrumented copy of old cycle; exact baseline parity tested separately."""
    q=engine.defaults();q.update(overrides or {});q['fatigue_rate_s_inv']=0
    fast=q['fast_capacity_J'];slow=q['slow_capacity_J'];oxygen=q['maintenance_W'] if initial_oxygen is None else initial_oxygen
    work=[]
    for rep in range(10):
        total=0.
        for effort,seconds in [(True,6),(False,rest)]:
            for _ in range(round(seconds/dt)):
                demand=q['demand_W'] if effort else 0.
                recovery=(q['fast_capacity_J']-fast)/q['fast_recovery_tau_s']+(q['slow_capacity_J']-slow)/q['slow_recovery_tau_s']
                target=min(q['oxygen_cap_W'],q['maintenance_W']+demand/q['eta']+recovery/q['recharge_efficiency'])
                oxygen=engine.legacy.approach(oxygen,target,dt,q['oxygen_tau_s'])
                aero=max(0.,oxygen-q['maintenance_W'])*dt
                fb=min(fast,q['fast_power_cap_W']*dt) if constant_release else fast*(1-math.exp(-dt/q['fast_discharge_tau_s']))
                sb=min(slow,q['slow_power_cap_W']*dt) if constant_release else slow*(1-math.exp(-dt/q['slow_discharge_tau_s']))
                external=min(demand*dt,(aero+fb+sb)*q['eta']);metabolic=external/q['eta']
                if constant_release:
                    need=max(0.,metabolic-aero);wf=min(fb,need);ws=min(sb,max(0.,need-wf));fast-=wf;slow-=ws
                    if need<1e-10:fast,slow,_,_=engine.legacy.allocate(aero,metabolic,fast,slow,q,dt)
                else:fast,slow,_,_=engine.legacy.allocate(aero,metabolic,fast,slow,q,dt)
                if effort:total+=external
        work.append(total/6)
    return np.array(work)

def historic_rows():
    path=BASE.parent/'cpe45_2026_11_04/results/observations.csv'
    with path.open(encoding='utf8',newline='') as f:raw=list(csv.DictReader(f))
    out=[]
    for sid in range(2,23,2):
        group=[r for r in raw if int(r['participant'])==sid and r['condition']=='Thermoneutral']
        first=next(r['mean_power_W'] for r in group if r['repetition']=='1')
        if not first:continue
        for r in group:
            if int(r['repetition'])>1 and r['mean_power_W']:
                out.append(dict(participant=sid,repetition=int(r['repetition']),reference_W=float(first),power_W=float(r['mean_power_W'])))
    return out

def old_metrics(shape):
    e=np.array([shape[r['repetition']-1]*r['reference_W']-r['power_W'] for r in historic_rows()])
    return dict(MAE_W=float(np.mean(abs(e))),RMSE_W=float(np.sqrt(np.mean(e**2))),bias_W=float(np.mean(e)))

def normalized_vector(q,mode='corrected'):
    out=[]
    for rest in [12,18,24,90]:
        powers,_,_=engine.cycle(rest_s=rest,mode=mode,overrides=dict(q,fatigue_rate_s_inv=0))
        out.extend(powers[1:]/powers[0])
    return np.array(out)

def identifiability():
    q=engine.defaults();keys=['fast_capacity_J','slow_capacity_J','fast_power_cap_W','slow_power_cap_W','fast_recovery_tau_s','slow_recovery_tau_s','eta','recharge_efficiency','oxygen_tau_s','oxygen_cap_W','maintenance_W']
    columns=[];eps=1e-4
    for key in keys:
        low=dict(q);high=dict(q);low[key]*=math.exp(-eps);high[key]*=math.exp(eps)
        columns.append((normalized_vector(high)-normalized_vector(low))/(2*eps))
    jac=np.column_stack(columns);u,s,v=np.linalg.svd(jac,full_matrices=False)
    rank=int(np.sum(s>s[0]*1e-6))
    norms=np.linalg.norm(jac,axis=0);corr=np.divide(jac.T@jac,norms[:,None]*norms[None,:],out=np.zeros((len(keys),len(keys))),where=(norms[:,None]*norms[None,:])>1e-20)
    scaled=dict(q)
    for k in ['fast_capacity_J','slow_capacity_J','fast_power_cap_W','slow_power_cap_W','demand_W','oxygen_cap_W','maintenance_W']:scaled[k]*=2
    scale_error=float(np.max(abs(normalized_vector(q)-normalized_vector(scaled))))
    # Stronger invariance even with absolute mechanical outputs: eta*k, all metabolic
    # energies/powers divided by k leaves external power unchanged.
    equiv=dict(q);k=1.2;equiv['eta']*=k
    for key in ['fast_capacity_J','slow_capacity_J','fast_power_cap_W','slow_power_cap_W','oxygen_cap_W','maintenance_W']:equiv[key]/=k
    a=engine.cycle(mode='corrected',overrides=dict(q,fatigue_rate_s_inv=0))[0]
    b=engine.cycle(mode='corrected',overrides=dict(equiv,fatigue_rate_s_inv=0))[0]
    return dict(parameters=keys,output_count=36,relative_log_jacobian=jac.tolist(),singular_values=s.tolist(),relative_rank_threshold=1e-6,rank=rank,sensitivity_cosines=corr.tolist(),normalized_energy_scale_symmetry_error=scale_error,absolute_eta_metabolic_scale_symmetry_error_W=float(np.max(abs(a-b))),interpretation='exact scaling symmetries prevent absolute capacities/efficiency identification from power alone; rank is local scenario diagnostic, not physiological fit')

def synthetic_control():
    """No human measurements: exact synthetic effective recurrence parameter recovery."""
    true_d=.18;true_tau=60.;rows=[]
    for rest in [12,18,24]:
        for rep,value in enumerate(engine.recovery_shape(true_d,true_tau,rest),1):
            if rep>1:rows.append(dict(rest_s=rest,repetition=rep,ratio=float(value)))
    y=np.array([r['ratio'] for r in rows]);n=np.array([r['repetition']-1 for r in rows]);ix=np.array([r['rest_s']//6-2 for r in rows]);fits=[]
    # Dedicated grid includes true values, independent of real-data model-selection grid.
    for d in np.linspace(.08,.28,41):
        for tau in np.linspace(20,100,81):
            shapes=np.array([engine.recovery_shape(float(d),float(tau),r) for r in [12,18,24]])
            fits.append((float(np.mean((shapes[ix,n]-y)**2)),float(d),float(tau)))
    best=min(fits)
    tau_variation=float(np.max(abs(engine.recovery_shape(0,1,12)-engine.recovery_shape(0,600,12))))
    return dict(origin='SYNTHETIC SOFTWARE CONTROL, not human data',true_depletion=true_d,true_tau_s=true_tau,recovered_depletion=best[1],recovered_tau_s=best[2],MSE=best[0],zero_depletion_tau1_vs600_max_difference=tau_variation)

def generate(out):
    out.mkdir(exist_ok=True,parents=True);q=engine.defaults();base=legacy_counterfactual();counter=[]
    experiments=[('unchanged',{},None,False),('demand_500W',{'demand_W':500},None,False),('demand_1500W',{'demand_W':1500},None,False),('capacity_double',{'fast_capacity_J':16000,'slow_capacity_J':44000},None,False),('recovery_fast10s',{'fast_recovery_tau_s':10},None,False),('recovery_slow800s',{'fast_recovery_tau_s':800},None,False),('fast_discharge_tau2s',{'fast_discharge_tau_s':2},None,False),('oxygen_tau10s',{'oxygen_tau_s':10},None,False),('warm_oxygen800W',{},800,False),('maintenance_zero',{'maintenance_W':0},None,False),('release_power_independent_capacity',{},None,True)]
    for name,params,initial,release in experiments:
        powers=legacy_counterfactual(overrides=params,initial_oxygen=initial,constant_release=release);shape=powers/powers[0]
        counter.append(dict(counterfactual=name,origin='viewed old holdout diagnostic, not new validation',first_nominal_W=float(powers[0]),late_over_first=float(shape[-1]),**old_metrics(shape)))
    pipeline.save_csv(out/'historical_counterfactuals.csv',counter)
    # Exact timing/accounting tests distinguish implementation error from model structure.
    convergence=[]
    for mode in ['legacy','corrected']:
        for dt in [.5,.25,.125,.0625]:
            p,s,_=engine.cycle(dt=dt,mode=mode,overrides={'fatigue_rate_s_inv':0})
            convergence.append(dict(mode=mode,dt_s=dt,first_W=float(p[0]),last_W=float(p[-1]),late_over_first=float(p[-1]/p[0]),**s))
    pipeline.save_csv(out/'convergence.csv',convergence)
    response=[]
    for rest in [0,6,12,24,90,300]:
        for initial in [0,.25,.75,1]:
            powers,s,_=engine.cycle(rest_s=rest,mode='corrected',overrides={'fatigue_rate_s_inv':0,'initial_fraction':initial})
            response.append(dict(rest_s=rest,initial_fraction=initial,first_W=float(powers[0]),last_W=float(powers[-1]),**s))
    pipeline.save_csv(out/'pause_depletion.csv',response)
    sensitivity=[]
    for key in ['fast_capacity_J','fast_power_cap_W','fast_recovery_tau_s','recharge_efficiency','oxygen_tau_s','eta','maintenance_W']:
        for factor in [.8,1.2]:
            p,s,_=engine.cycle(rest_s=18,mode='corrected',overrides={key:q[key]*factor,'fatigue_rate_s_inv':0})
            sensitivity.append(dict(parameter=key,factor=factor,first_W=float(p[0]),last_W=float(p[-1]),work_J=s['external_J']))
    pipeline.save_csv(out/'sensitivity.csv',sensitivity)
    rng=np.random.default_rng(pipeline.SEED);uq=[]
    for run in range(64):
        params={key:float(q[key]*rng.uniform(.75,1.25)) for key in ['fast_capacity_J','slow_capacity_J','fast_power_cap_W','fast_recovery_tau_s','slow_recovery_tau_s','oxygen_tau_s','eta']}
        p,s,_=engine.cycle(rest_s=18,mode='corrected',overrides=dict(params,fatigue_rate_s_inv=0))
        uq.append(dict(run=run,**params,first_W=float(p[0]),last_W=float(p[-1]),late_over_first=float(p[-1]/p[0]),work_J=s['external_J'],energy_residual_J=s['energy_residual_J']))
    pipeline.save_csv(out/'uncertainty.csv',uq)
    # Exact 2700s with 6+12s cycles; mathematical stability, not human endurance evidence.
    p,s,trace=engine.cycle(rest_s=12,repetitions=150,mode='corrected',dt=.25,trace=True,overrides={'fatigue_rate_s_inv':0})
    pipeline.save_csv(out/'stability_2700s.csv',[r for r in trace if abs(r['time_s']-round(r['time_s']))<1e-9])
    identity=identifiability();pipeline.save_json(out/'identifiability.json',identity)
    # Parameter profiles over *development* data remain flat at d=0.
    profile=list(csv.DictReader((BASE/'results/recovery_profile.csv').open(encoding='utf8')))
    summary=dict(historical_RMSE_reproduced_W=counter[0]['RMSE_W'],old_holdout_status='viewed diagnostic only, original files untouched',synthetic_control=synthetic_control(),identifiability={k:v for k,v in identity.items() if k not in ['relative_log_jacobian','sensitivity_cosines']},empirical_recovery_profile=dict(tau_grid_min_s=1,tau_grid_max_s=600,delta_profile_chi2_max=max(float(r['delta_profile_chi2']) for r in profile),identified=False,reason='depletion fitted zero; all tau values give the same observed output'),UQ=dict(runs=64,type='independent epistemic uniform .75..1.25 multipliers, not human distribution or confidence interval',work_J_p05_p50_p95=[float(np.quantile([r['work_J'] for r in uq],x)) for x in [.05,.5,.95]]),stability_2700s=s,NO_GO=True,CPE45='NOT EXTERNALLY VALIDATED')
    pipeline.save_json(out/'diagnostic_summary.json',summary)
    return summary
if __name__=='__main__':print(json.dumps(generate(BASE/'results'),indent=2))
