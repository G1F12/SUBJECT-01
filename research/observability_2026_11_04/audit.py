"""Cycle 5: conditional observation design on unchanged D2. No human-data fitting."""
from pathlib import Path
import sys,json,math,hashlib,argparse,tempfile
import numpy as np
from scipy.optimize import least_squares
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent/'recovery_2026_11_04'))
import engine

KEYS=['fast_capacity_J','slow_capacity_J','fast_power_cap_W','slow_power_cap_W',
      'fast_recovery_tau_s','slow_recovery_tau_s','eta','recharge_efficiency',
      'oxygen_tau_s','oxygen_cap_W','maintenance_W']
METABOLIC=[0,1,2,3,9,10]
NOISE={'P':20.,'O':40.,'R':.02,'A':160.}
CHANNELS={'M1':['P'],'M2':['P','O'],'M3':['P','R'],'M4':['P','A'],
          'M5':['P','O','R'],'M6':['P','O','R'],'M7':['P','O','R']}
DESIGNS=[dict(name=n,effort_s=e,rest_s=r,repetitions=k,demand_W=w,initial_fraction=f)
 for n,e,r,k,w,f in [('short_long',3,90,6,1400,1),('short_incomplete',6,12,10,1400,1),
 ('medium_rest',6,30,10,1400,1),('long_rest',6,180,5,1400,1),
 ('predepleted',6,30,10,1400,.35),('long_effort',30,60,5,1400,1),
 ('low_power',15,45,6,500,1),('high_power',15,45,6,1800,1)]]

def save(path,x):
    path.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')

def nominal():
    q=engine.defaults();q['fatigue_rate_s_inv']=0.
    return q

def trace(q,d,dt=.5):
    p,s,rows=engine.cycle(mode='corrected',trace=True,dt=dt,
        rest_s=d['rest_s'],effort_s=d['effort_s'],repetitions=d['repetitions'],
        overrides=dict(q,demand_W=d['demand_W'],initial_fraction=d['initial_fraction']))
    return np.array([[r['time_s'],r['output_W'],r['oxygen_W'],
                      r['fast_J']/q['fast_capacity_J'],r['fast_J']] for r in rows]),s

def observe(q,d,config='M1',sample_s=2.,dt=.5):
    tr,_=trace(q,d,dt);times=np.arange(sample_s,tr[-1,0]+1e-8,sample_s)
    cols={'P':1,'O':2,'R':3,'A':4}
    out=[np.interp(times,tr[:,0],tr[:,cols[c]])/NOISE[c] for c in CHANNELS[config]]
    if config in ('M6','M7'):out.append(np.array([q['eta']/.01]))
    # M7 has the same energy parameters; peripheral parameters require a separate model.
    return np.concatenate(out)

def jacobian(q,d,c,sample_s=2.,eps=1e-6,dt=.5):
    cols=[]
    for key in KEYS:
        a=dict(q);b=dict(q);a[key]*=math.exp(eps);b[key]*=math.exp(-eps)
        cols.append((observe(a,d,c,sample_s,dt)-observe(b,d,c,sample_s,dt))/(2*eps))
    return np.column_stack(cols)

def spectral(j):
    _,s,v=np.linalg.svd(j,full_matrices=False);cut=s[0]*1e-6 if s[0] else 1e-20
    rank=int(sum(s>cut));norm=np.linalg.norm(j,axis=0)
    cosine=np.divide(j.T@j,norm[:,None]*norm[None,:],out=np.zeros((j.shape[1],j.shape[1])),where=norm[:,None]*norm[None,:]>1e-20)
    cov=(v[:rank].T/s[:rank]**2)@v[:rank] if rank else np.zeros((j.shape[1],j.shape[1]))
    sd=np.sqrt(np.diag(cov));corr=np.divide(cov,sd[:,None]*sd[None,:],out=np.zeros_like(cov),where=sd[:,None]*sd[None,:]>1e-20)
    return dict(rank=rank,nullity=j.shape[1]-rank,singular_values=s.tolist(),
        ranks_by_relative_threshold={str(t):int(sum(s>s[0]*t)) for t in [1e-4,1e-6,1e-8]},
        condition_identifiable=float(s[0]/s[rank-1]) if rank else None,
        condition_full=float(s[0]/s[-1]) if rank==j.shape[1] else None,
        sensitivity_cosines=cosine.tolist(),projected_parameter_correlations=corr.tolist(),
        correlation_warning='pinv correlations only in estimable local subspace; no marginal CI for unidentified parameters',
        null_vectors=v[rank:].tolist(),FIM=(j.T@j).tolist())

def scale(q,k):
    out=dict(q);out['eta']*=k
    for i in METABOLIC:out[KEYS[i]]/=k
    return out

def quotient(q):
    """Mechanical-equivalent storage J and power W; eta is removed, not estimated."""
    return {KEYS[i]+'_mechanical_equivalent':q['eta']*q[KEYS[i]] for i in METABOLIC[:4]}|{
        'oxidative_excess_cap_mechanical_W':q['eta']*(q['oxygen_cap_W']-q['maintenance_W']),
        **{k:q[k] for i,k in enumerate(KEYS) if i not in METABOLIC and k!='eta'}}

def reduced_trace(z,d,dt=.5):
    # Gauge representative eta=1 is computational coordinates, never a physiological eta.
    q=nominal();q['eta']=1.
    for i in METABOLIC[:4]:q[KEYS[i]]=z[KEYS[i]+'_mechanical_equivalent']
    q['maintenance_W']=0.;q['oxygen_cap_W']=z['oxidative_excess_cap_mechanical_W']
    for k in ['fast_recovery_tau_s','slow_recovery_tau_s','recharge_efficiency','oxygen_tau_s']:q[k]=z[k]
    return trace(q,d,dt)

def projection():
    g=np.zeros(11);g[6]=1;g[METABOLIC]=-1
    # Fixed orthonormal complement of the analytic scale generator.
    q=nominal();h=np.zeros(11);h[9]=1/q['oxygen_cap_W'];h[10]=1/q['maintenance_W'];h/=np.linalg.norm(h)
    _,_,v=np.linalg.svd(np.vstack([g,h]),full_matrices=True)
    return v[2:].T,g

def criterion(j,b):
    s=np.linalg.svd(j@b,compute_uv=False);rank=int(sum(s>s[0]*1e-6))
    return dict(rank=rank,dimension=b.shape[1],logdet=float(2*np.log(s).sum()) if rank==b.shape[1] else None,
                lambda_min=float(s[-1]**2) if rank==b.shape[1] else 0.)

def recover_recurrence():
    """Multi-start, nonlinear profile, noise and misspecification on effective output model."""
    rest=np.repeat([6.,18.,90.],9);rep=np.tile(np.arange(1,10),3)
    def pred(x):return np.concatenate([engine.recovery_shape(x[0],x[1],r)[1:] for r in [6,18,90]])
    truth=np.array([.18,60.]);clean=pred(truth);rng=np.random.default_rng(20261104)
    cases=[]
    for sigma,missing,shift,discrepancy in [(0.,0.,0.,0.),(.02,0,0,0),(.05,0,0,0),(.02,.3,0,0),(.02,0,2.,0),(.02,0,0,.04)]:
        fits=[]
        for run in range(6):
            mask=rng.random(len(clean))>=missing
            shifted=np.concatenate([engine.recovery_shape(.18,60,r+shift)[1:] for r in [6,18,90]])
            y=shifted+discrepancy*(1-np.exp(-rep/3))+rng.normal(0,sigma,len(clean))
            opts=[least_squares(lambda x:(pred(x)-y)[mask],s,bounds=([0,1],[.8,600]),xtol=1e-10,ftol=1e-10,gtol=1e-10) for s in [[.1,20],[.4,150]]]
            fit=min(opts,key=lambda f:sum(f.fun**2));fits.append(dict(depletion=float(fit.x[0]),tau_s=float(fit.x[1]),RMSE_ratio=float(np.sqrt(np.mean((pred(fit.x)-clean)**2))),success=bool(fit.success)))
        cases.append(dict(sigma=sigma,missing_fraction=missing,rest_timing_error_s=shift,systematic_potentiation=discrepancy,fits=fits))
    profiles=[]
    for r in [6.,18.,90.]:
        y=engine.recovery_shape(.18,60,r)[1:]
        curve=[]
        for tau in np.geomspace(5,600,45):
            f=least_squares(lambda x:(engine.recovery_shape(x[0],tau,r)[1:]-y)/.02,[.15],bounds=([0],[.8]))
            curve.append(dict(tau_s=float(tau),depletion=float(f.x[0]),chi2=float(sum(f.fun**2))))
        accepted=[x['tau_s'] for x in curve if x['chi2']<=3.84]
        profiles.append(dict(rest_s=r,curve=curve,conditional_grid_95_support_s=[min(accepted),max(accepted)] if accepted else None,warning='expected synthetic profile, Gaussian known sigma; grid truncated; no empirical confidence claim'))
    return dict(origin='SYNTHETIC ONLY',truth=truth.tolist(),cases=cases,profiles=profiles)

def recover_reduced():
    """Nonlinear nine-combination recovery, no assumption of recovering eta/basal cost."""
    z=quotient(nominal());keys=list(z);truth=np.array(list(z.values()));rng=np.random.default_rng(19)
    ds=[DESIGNS[i] for i in [2,5,7]]
    def pred(logx):
        zz=dict(zip(keys,truth*np.exp(logx)));out=[]
        for d in ds:
            tr,_=reduced_trace(zz,d);t=np.arange(2,tr[-1,0]+1e-8,2)
            out.extend(np.interp(t,tr[:,0],tr[:,1])/20.)
        return np.array(out)
    clean=pred(np.zeros(9));fits=[]
    upper=np.full(9,.4);upper[keys.index('recharge_efficiency')]=min(.4,math.log(1/z['recharge_efficiency']))
    for name,sigma,missing,drift in [('clean',0,0,0),('noise20W',1,0,0),('missing30pct',1,.3,0),('unmodelled_drift',1,0,1)]:
        y=clean+rng.normal(0,sigma,len(clean))+drift*np.linspace(0,2,len(clean));mask=rng.random(len(clean))>=missing
        options=[]
        for start in [.03,-.04]:
            initial=np.minimum(np.full(9,start),upper*.9)
            f=least_squares(lambda x:(pred(x)-y)[mask],initial,bounds=(np.full(9,-.4),upper),max_nfev=60,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8)
            options.append(f)
        f=min(options,key=lambda x:sum(x.fun**2));estimated=truth*np.exp(f.x)
        fits.append(dict(case=name,log_parameter_error=f.x.tolist(),estimated_combinations=dict(zip(keys,estimated.tolist())),
            max_relative_parameter_error=float(abs(estimated/truth-1).max()),prediction_RMSE_W=float(np.sqrt(np.mean((pred(f.x)-clean)**2))*20),
            success=bool(f.success),nfev=int(f.nfev),bound_hit=bool(np.any(abs(f.x)>.399)),starts_cost=[float(sum(x.fun**2)) for x in options]))
    return dict(origin='SYNTHETIC D2 quotient only; one draw per stress condition, no coverage claim',truth=z,training_designs=[d['name'] for d in ds],fits=fits)

def generate(out):
    out.mkdir(parents=True,exist_ok=True);q=nominal();b,g=projection()
    # Designs are separately restarted at specified known initial fraction.
    cache={};records=[]
    for d in DESIGNS:
        for c in CHANNELS:
            j=jacobian(q,d,c);cache[d['name'],c]=j
            records.append(dict(design=d['name'],configuration=c,duration_s=(d['effort_s']+d['rest_s'])*d['repetitions'],
                observations=len(j),**spectral(j),quotient_criterion=criterion(j,b)))
    combined={}
    for c in CHANNELS:
        j=np.vstack([cache[d['name'],c] for d in DESIGNS])
        # eta anchor is once per study, remove duplicated anchors across designs.
        if c in ('M6','M7'):
            j=np.vstack([*[cache[d['name'],c][:-1] for d in DESIGNS],cache[DESIGNS[0]['name'],c][-1:]])
        combined[c]=spectral(j)
    save(out/'measurement_sets.json',dict(keys=KEYS,noise=NOISE,records=records,combined=combined))
    sym=[];red=[]
    for d in DESIGNS:
        a,sa=trace(q,d);t,sb=trace(scale(q,1.2),d);r,sr=reduced_trace(quotient(q),d)
        shifted=dict(q,oxygen_cap_W=q['oxygen_cap_W']+100,maintenance_W=q['maintenance_W']+100)
        sh,_=trace(shifted,d)
        sym.append(dict(design=d['name'],baseline_shift_power_error_W=float(abs(a[:,1]-sh[:,1]).max()),baseline_shift_reserve_error_J=float(abs(a[:,4]-sh[:,4]).max()),power_max_abs_W=float(abs(a[:,1]-t[:,1]).max()),relative_PCr_max_abs=float(abs(a[:,3]-t[:,3]).max()),
            oxygen_scale_error_W=float(abs(a[:,2]/1.2-t[:,2]).max()),reserve_scale_error_J=float(abs(a[:,4]/1.2-t[:,4]).max())))
        red.append(dict(design=d['name'],power_max_abs_W=float(abs(a[:,1]-r[:,1]).max()),relative_PCr_max_abs=float(abs(a[:,3]-r[:,3]).max()),energy_residual_J=sa['energy_residual_J'],
            reduced_energy_residual_mechanical_J=sr['energy_residual_J']))
    save(out/'symmetry_reduction.json',dict(symmetry=sym,reduction=red,quotient=quotient(q),generator=g.tolist()))
    y=observe(q,DESIGNS[2],'M1');profiles=[]
    for k in [.8,1,1.2]:
        for shift in [-50,0,100]:
            qq=scale(q,k);qq['maintenance_W']+=shift;qq['oxygen_cap_W']+=shift
            residual=observe(qq,DESIGNS[2],'M1')-y
            profiles.append(dict(eta_scale=k,baseline_shift_W=shift,negative2loglikelihood_difference=float(residual@residual),
                origin='exact conditional synthetic profile path with all transformed nuisance parameters'))
    save(out/'exact_profiles.json',profiles)
    # Common nine-dimensional power quotient; singular cases get no determinant score.
    robust=[]
    for d in DESIGNS:
        corners=[]
        for factor in [.8,1.,1.2]:
            qq=dict(q)
            for key in ['fast_capacity_J','slow_capacity_J','fast_recovery_tau_s','slow_recovery_tau_s']:qq[key]*=factor
            j=cache[d['name'],'M5'] if factor==1 else jacobian(qq,d,'M5')
            duration=(d['effort_s']+d['rest_s'])*d['repetitions']
            corners.append(dict(factor=factor,**criterion(j,b),full_calibrated_M5=criterion(j,np.eye(11)),
                full_M5_per600s=criterion(j*math.sqrt(600/duration),np.eye(11))))
        ok=all(x['logdet'] is not None for x in corners)
        robust.append(dict(design=d['name'],corners=corners,worst_logdet=min(x['logdet'] for x in corners) if ok else None,worst_lambda_min=min(x['lambda_min'] for x in corners)))
    d_rank=sorted([r for r in robust if r['worst_logdet'] is not None],key=lambda r:-r['worst_logdet'])
    e_rank=sorted([r for r in robust if r['worst_logdet'] is not None],key=lambda r:-r['worst_lambda_min'])
    gains=[]
    for c in CHANNELS:
        j=np.vstack([cache[d['name'],c][:-1] if c in ('M6','M7') else cache[d['name'],c] for d in DESIGNS])
        if c in ('M6','M7'):j=np.vstack([j,cache[DESIGNS[0]['name'],c][-1:]])
        for n in [1,4]:
            repeated=j*math.sqrt(n)
            if c in ('M6','M7'):repeated[-1]=j[-1]
            gains.append(dict(configuration=c,repetitions_multiplier=n,**criterion(repeated,b)))
    full_ok=[r for r in robust if all(x['full_calibrated_M5']['logdet'] is not None for x in r['corners'])]
    full_d=sorted(full_ok,key=lambda r:-min(x['full_calibrated_M5']['logdet'] for x in r['corners']))
    full_e=sorted(full_ok,key=lambda r:-min(x['full_calibrated_M5']['lambda_min'] for x in r['corners']))
    save(out/'design.json',dict(common_basis=b.tolist(),robust=robust,D_order=[r['design'] for r in d_rank],E_order=[r['design'] for r in e_rank],
        full_calibrated_M5_D_order=[r['design'] for r in full_d],full_calibrated_M5_E_order=[r['design'] for r in full_e],
        per600s_M5_D_order=[r['design'] for r in sorted(full_ok,key=lambda r:-min(x['full_M5_per600s']['logdet'] for x in r['corners']))],
        per600s_M5_E_order=[r['design'] for r in sorted(full_ok,key=lambda r:-min(x['full_M5_per600s']['lambda_min'] for x in r['corners']))],channel_vs_repeats=gains,
        warning='fixed common quotient, conditional noise and local log coordinates; not determinant of singular full FIM; corners not a physiological prior; durations differ, no universal clinical ranking'))
    # Sampling, dropout, correlated-error whitening and instrument lag on one design.
    d=DESIGNS[2];base=cache[d['name'],'M5'];stress=[]
    for sample in [1.,2.,6.,12.]:
        j=jacobian(q,d,'M5',sample)
        stress.append(dict(kind='sampling',value=sample,**criterion(j,b)))
    rng=np.random.default_rng(51)
    for missing in [.1,.3,.5]:stress.append(dict(kind='MCAR_missing',value=missing,**criterion(base[rng.random(len(base))>missing],b)))
    for noise in [.5,1.,2.]:stress.append(dict(kind='noise_multiplier',value=noise,**criterion(base/noise,b)))
    # AR1 whitening independently within the three channels, rho=.7, unit marginal variance.
    n=len(base)//3;j=base.copy()
    for k in range(3):
        a=base[k*n:(k+1)*n];j[k*n+1:(k+1)*n]=(a[1:]-.7*a[:-1])/math.sqrt(1-.7**2)
    stress.append(dict(kind='AR1_whitened',value=.7,**criterion(j,b)))
    # Relative sensor delay: hold power clock fixed, lag O and PCr independently.
    sync=[];y=observe(q,d,'M5');n=len(y)//3;times=np.arange(2,2*n+1,2.)
    for lag in [.5,2.,5.]:
        shifted=y.copy()
        for k in [1,2]:shifted[k*n:(k+1)*n]=np.interp(times-lag,times,y[k*n:(k+1)*n])
        delta=shifted-y;bias=np.linalg.lstsq(base,delta,rcond=1e-6)[0]
        sync.append(dict(lag_s=lag,local_log_parameter_bias=bias.tolist(),norm_bias=float(np.linalg.norm(bias)),
            residual_chi2_at_truth=float(delta@delta),residual_chi2_after_local_refit=float(np.sum((delta-base@bias)**2)),
            warning='first-order local bias diagnostic, not nonlinear estimator or human sensor calibration'))
    conv=[]
    for dt in [.5,.25,.125]:
        a,s=trace(q,d,dt);y=observe(q,d,'M5',dt=dt)
        conv.append(dict(dt_s=dt,energy_residual_J=s['energy_residual_J'],work_J=s['external_J'],output=y.tolist(),rank=spectral(jacobian(q,d,'M5',dt=dt))['rank']))
    save(out/'stress.json',dict(stress=stress,synchronization=sync,convergence=conv,synthetic=recover_recurrence()))
    # Explicit nuisance-gain extension: uncalibrated VO2 and PCr energy gains restore symmetry.
    j=np.vstack([cache[d['name'],'M5'] for d in DESIGNS]);y=np.concatenate([observe(q,d,'M5') for d in DESIGNS])
    oxygen_gain=np.zeros_like(y);offset=0
    for d in DESIGNS:
        yy=observe(q,d,'M5');n=len(yy)//3;oxygen_gain[offset+n:offset+2*n]=yy[n:2*n];offset+=len(yy)
    ext=np.column_stack([j,oxygen_gain]);gg=np.r_[g,1.]
    save(out/'calibration.json',dict(unknown_VO2_gain_direction_residual=float(np.linalg.norm(ext@gg)),
         finite_difference_relative_residual=float(np.linalg.norm(ext@gg)/np.linalg.norm(ext)),
         unknown_gain_local=spectral(ext),meaning='oxygen gain transforms k; relative PCr invariant; absolute PCr additionally needs known concentration-volume-energy conversion'))
    finite=[]
    for eps in [1e-3,1e-4,1e-5,1e-6,1e-7]:
        j=np.vstack([jacobian(q,d,'M1',eps=eps) for d in DESIGNS])
        finite.append(dict(eps=eps,singular_values=np.linalg.svd(j,compute_uv=False).tolist(),rank=spectral(j)['rank']))
    save(out/'finite_difference.json',finite)
    save(out/'reduced_recovery.json',recover_reduced())
    # Closed-form, separate twitch observation model: not parameters added to D2.
    times=np.arange(0,361,5.);rate=.001;tau=90.;effort_end=60.
    def twitch(x):
        a,t=x
        return 1-np.where(times<=effort_end,a*t*(1-np.exp(-times/t)),a*t*(1-np.exp(-effort_end/t))*np.exp(-(times-effort_end)/t))
    xx=np.array([rate,tau]);tj=np.column_stack([(twitch(xx*np.exp(np.eye(2)[i]*1e-6))-twitch(xx*np.exp(-np.eye(2)[i]*1e-6)))/(2e-6*.02) for i in range(2)])
    save(out/'peripheral.json',dict(origin='separate synthetic twitch map; fatigue not equated to PCr',parameters=['rate_s_inv','tau_s'],spectral=spectral(tj),
        assumptions='known baseline, known activation history, twitch=1-fatigue with calibrated gain; unknown gain confounds rate; voluntary MVC alone does not separate central activation'))
    summary=dict(origin='conditional computational evidence only',combined_ranks={c:combined[c]['rank'] for c in CHANNELS},
       D_order=[r['design'] for r in d_rank],E_order=[r['design'] for r in e_rank],
       symmetry_max_W=max(x['power_max_abs_W'] for x in sym),reduction_max_W=max(x['power_max_abs_W'] for x in red),
       new_external_validation=False,NO_GO=True,CPE45='NOT EXTERNALLY VALIDATED')
    save(out/'summary.json',summary);return summary

def equivalent(a,b):
    if isinstance(a,dict):return a.keys()==b.keys() and all(equivalent(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
    if isinstance(a,(float,int)) and not isinstance(a,bool):return isinstance(b,(float,int)) and math.isclose(a,b,rel_tol=2e-4,abs_tol=2e-5)
    return a==b

def check():
    manifest=json.loads((BASE/'manifest.json').read_text('utf8'))
    for rel,h in manifest.items():assert hashlib.sha256((BASE/rel).read_bytes()).hexdigest()==h,rel
    with tempfile.TemporaryDirectory() as td:
        out=Path(td);generate(out)
        for p in out.glob('*.json'):
            a=json.loads(p.read_text('utf8'));b=json.loads((BASE/'results'/p.name).read_text('utf8'))
            # SVD null-vector signs and degenerate subspace bases are not unique.
            def strip(x):
                if isinstance(x,dict):return {k:strip(v) for k,v in x.items() if k not in ('null_vectors','projected_parameter_correlations')}
                if isinstance(x,list):return [strip(v) for v in x]
                return x
            assert equivalent(strip(a),strip(b)),p.name
    print('PASS cycle5 hashes and numerical replay; no new human validation')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:check()
    else:print(json.dumps(generate(BASE/'results'),indent=2))
