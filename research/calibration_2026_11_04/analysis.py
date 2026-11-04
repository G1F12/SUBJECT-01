"""Identification and falsification on REAL development gas measurements only."""
import json,math,sys
import numpy as np
from scipy.optimize import least_squares
from scipy.stats import t as student
from acquire import BASE,save,digest
import dataset,models

def kinetic_inputs():
    target=BASE/'development_kinetic_inputs.json'
    if target.exists():return json.loads(target.read_text('utf8'))
    out=[]
    for sid in dataset.ids():
        if sid%5==0:continue
        rs=dataset.native(sid);power=50 if sid>50 else 30
        candidates=[r['time_s'] for r in rs if r['time_s']<120 and r['power_W'] is not None and abs(r['power_W']-power)<=2]
        if not candidates:continue
        onset=min(candidates);use=[r for r in rs if r['time_s']<=onset+180]
        if len(use)<20:continue
        out.append(dict(participant=sid,onset_s=onset,prescribed_power_W=power,source=f'P{sid}_cycle.csv',
            time_s=[r['time_s'] for r in use],vo2_L_min=[r['vo2_L_min'] for r in use],
            origin='REAL native breath data, development only; no imputed rows'))
    save(target,out);return out

def kinetics(record):
    t=np.array(record['time_s']);y=np.array(record['vo2_L_min']);onset=record['onset_s']
    def curve(x):return x[0]+x[1]*(1-np.exp(-np.maximum(0,t-onset-x[3])/x[2]))
    init_b=float(np.clip(np.mean(y[:min(5,len(y))]),.01,1.9));amp=float(np.clip(np.mean(y[-10:])-init_b,.02,7.9))
    fits=[least_squares(lambda x:curve(x)-y,[init_b,amp,tau,delay],bounds=([0,0,1,0],[2,8,300,45]),max_nfev=300) for tau,delay in [(10,0),(30,5),(90,15)]]
    f=min(fits,key=lambda f:sum(f.fun**2));sse=float(sum(f.fun**2));sigma2=sse/max(1,len(y)-4)
    singular=np.linalg.svd(f.jac,compute_uv=False);rank=int(sum(singular>singular[0]*1e-6));profiles=[]
    for tau in sorted(set(np.geomspace(1,300,19).tolist()+[float(f.x[2])])):
        ff=least_squares(lambda z:(z[0]+z[1]*(1-np.exp(-np.maximum(0,t-onset-z[2])/tau)))-y,
            [f.x[0],f.x[1],f.x[3]],bounds=([0,0,0],[2,8,45]),max_nfev=200)
        profiles.append(dict(tau_s=tau,delta_chi2=max(0,float(sum(ff.fun**2)-sse)/max(sigma2,1e-12))))
    accepted=[r['tau_s'] for r in profiles if r['delta_chi2']<=3.84]
    finite=bool(accepted and min(accepted)>1 and max(accepted)<300)
    residual=y-curve(f.x);rho=float(np.corrcoef(residual[:-1],residual[1:])[0,1]) if np.std(residual)>0 else None
    fim=f.jac.T@f.jac/max(sigma2,1e-12)
    return dict(participant=record['participant'],n=len(y),baseline_L_min=float(f.x[0]),amplitude_L_min=float(f.x[1]),tau_s=float(f.x[2]),delay_s=float(f.x[3]),
        profile_support_95_s=[min(accepted),max(accepted)] if accepted else None,profile=profiles,
        local_rank=rank,singular_values=singular.tolist(),FIM=fim.tolist(),RMSE_L_min=float(np.sqrt(np.mean(residual**2))),residual_AR1=rho,
        finite_profile=finite,status='EFFECTIVE ONLY' if finite else 'UNIDENTIFIABLE',
        interpretation='pulmonary response parameter, conditional one-exponential+delay map; not localD2tau or mitochondrialcapacity; Gaussianprofile ignores measured residualcorrelation',
        starts_SSE=[float(sum(ff.fun**2)) for ff in fits],MDE_amplitude_approx_L_min=float(1.96*math.sqrt(sigma2)/math.sqrt(len(y))))

def individual_affine(rs):
    out=[]
    for sid in sorted({r['participant'] for r in rs}):
        rr=[r for r in rs if r['participant']==sid];x=np.array([[1,r['power_W']] for r in rr]);y=np.array([r['cost_W'] for r in rr]);beta=np.linalg.lstsq(x,y,rcond=None)[0]
        s=np.linalg.svd(x,compute_uv=False);n=len(y);res=y-x@beta;df=n-2;ci=None;cor=None
        if df>0 and s[-1]>s[0]*1e-8:
            cov=np.linalg.inv(x.T@x)*float(res@res)/df;half=student.ppf(.975,df)*np.sqrt(np.diag(cov));ci=np.column_stack([beta-half,beta+half]).tolist()
            cor=float(cov[0,1]/math.sqrt(cov[0,0]*cov[1,1])) if cov[0,0]*cov[1,1]>0 else None
        slope_bound=ci[1] if ci else None
        eff_ci=[1/slope_bound[1],1/slope_bound[0]] if slope_bound and slope_bound[0]>0 else None
        out.append(dict(participant=sid,n_stages=n,intercept_W=float(beta[0]),incremental_cost_W_per_W=float(beta[1]),
            effective_delta_efficiency=float(1/beta[1]) if beta[1]>0 else None,coefficient_95_intervals=ci,effective_efficiency_95=eff_ci,
            rank=int(sum(s>s[0]*1e-8)),condition=float(s[0]/s[-1]),intercept_slope_correlation=cor,
            status='EFFECTIVE ONLY' if eff_ci else 'UNIDENTIFIABLE',
            interpretation='profileSSE/t-equivalent linear Gaussian inference; small3..5stages and serial/systematicmeasurementuncertainty not fully covered; notηD2'))
    return out

def fit_affine(rows):return models.fit(rows)['affine']
def perturb(rows,gO=1.,gC=1.,bO=0.,bC=0.,cO=3.9,cC=1.1):
    return [dict(r,cost_W=((r['vo2_L_min']*gO+bO)*cO+(r['vco2_L_min']*gC+bC)*cC)*4184/60) for r in rows]

def generate(out):
    out.mkdir(exist_ok=True,parents=True);rs=models.rows();snap=json.loads((BASE/'development_stage_audit.json').read_text('utf8'));lock=models.load_lock()
    affine=individual_affine(rs);kin=[kinetics(r) for r in kinetic_inputs()]
    save(out/'parameter_identification.json',dict(origin='REAL development records',individual_systemic_affine=affine,pulmonary_kinetics=kin,
        D2physiological_parameters='UNIDENTIFIABLE; no conversion from systemiccoefficients',PCr='NOT OBSERVED innewcohort',peripheral_fatigue='NOT OBSERVED'))
    anchors=[]
    for task in ['standing','sitting']:
        r=[v for v in snap['baseline'] if v['task']==task];v=[v['cost_W'] for v in r]
        anchors.append(dict(task=task,participants=len(r),cost_W_quantiles=np.quantile(v,[0,.25,.5,.75,1]).tolist(),
            oxygen_L_min_quantiles=np.quantile([x['vo2_L_min'] for x in r],[.05,.5,.95]).tolist(),
            status='MEASURED pulmonarygas; DERIVED independent-of-D2 systemicfuelcost; not fastingRMR orlocalM'))
    gross=[r['power_W']/r['cost_W'] for r in rs]
    save(out/'anchors.json',dict(baseline=anchors,systemic_cost_derived_from_independent_measuredgas=True,
        gross_ratio_quantiles=np.quantile(gross,[.05,.5,.95]).tolist(),gross_ratio_status='EFFECTIVE ONLY; conditional lower bound onηlocal if no reserve withdrawal/anaerobicinput and correctfuelmap',
        interbout_windows=len(snap['recovery']),recovery=snap['recovery'],
        local_absolute_ATP_scale_found=False,local_M_found=False,absolute_reserve_J='NOT OBSERVED',
        fusion='sameparticipant cycle andwalkfiles distinguished; Cycle5PCr cohorts not assigned to these participants'))
    stress=[];base=fit_affine(rs)
    for name,kwargs in [('O2gain-.1',dict(gO=.9)),('O2gain+.1',dict(gO=1.1)),('bothgain-.05',dict(gO=.95,gC=.95)),('bothgain+.05',dict(gO=1.05,gC=1.05)),
       ('O2offset-.1Lmin',dict(bO=-.1)),('O2offset+.1Lmin',dict(bO=.1)),('CO2offset+.1Lmin',dict(bC=.1)),('precise_Weir',dict(cO=3.941,cC=1.106))]:
        p=fit_affine(perturb(rs,**kwargs));stress.append(dict(test=name,intercept_W=p[0],slope_W_per_W=p[1]/100,delta_eff=100/p[1],origin='realdata sensitivity, no new human observations'))
    # Timing summaries are archived before replay; no raw network dependency inCI.
    timing_path=BASE/'development_timing_sensitivity.json'
    if timing_path.exists():timing=json.loads(timing_path.read_text('utf8'))
    else:
        timing=[]
        for shift in [-15.,-5.,5.,15.]:
            stages,_,_=dataset.collect(shift=shift);use=[dict(r,baseline_W=None) for r in stages if r['primary_eligible']]
            p=fit_affine(use);timing.append(dict(shift_s=shift,stage_count=len(use),intercept_W=p[0],slope_W_per_W=p[1]/100))
        save(timing_path,timing)
    # Actual designP supports rank2, but adding instrumentgain+offset leaves rank2/4.
    p=np.array([r['power_W'] for r in rs]);a,b=base[0],base[1]/100
    j=np.column_stack([np.ones(len(p)),p,a+b*p,np.ones(len(p))]);singular=np.linalg.svd(j,compute_uv=False)
    gain_null=np.array([-a,-b,1.,0.]);offset_null=np.array([1.,0.,0.,-1.])
    save(out/'falsification.json',dict(gain_offset=stress,timing=timing,
        realdesign_gain_offset_rank=int(sum(singular>singular[0]*1e-8)),parameters=['systemicintercept','systemicslope','instrumentgain','instrumentoffset'],singular_values=singular.tolist(),
        gain_null_residual=float(np.max(abs(j@gain_null))),offset_null_residual=float(np.max(abs(j@offset_null))),
        active_volume=dict(status='NOT OBSERVED',factors=[.5,2.],PCrenergy_conversion_factors=[.5,2.],claim='algebraic measurement conversion only; no synthetichumancapacity assigned'),
        ATP_reference=dict(status='NOT OBSERVED',factors=[.8,1.2],chemical_energy_scaling=[.8,1.2],claim='Cycle5ATPnormalizedPCr is assumption-dependent, not new independent absolute anchor'),
        task_mismatch='standing/sitting baseline transfer tocycling fails to define unloadedcyclingM; see lockedbaseline_slope result',
        incomplete_recovery='gas gaps during most5minrests; recoveryτ NOT OBSERVED, not no-recovery effect',
        active_rest='cadence absent inmostrecoverygaps; onezeroWwindowcadence4.15rpm is not representative passiveRMR',
        transport='unknownlocalallocation,otherconsumers,delay/filter persist despite absolute systemicgas',
        structural_error='quadratic vs affine difference and firsttransitionresiduals; improvedcost fit is not correctedreserve dynamics',
        power_vs_absence='flat or boundarypulmonaryτ profiles markedUNIDENTIFIABLE; insufficientsample/amplitudesignal not evidenceofabsentphysiology'))
    vals=[r['effective_delta_efficiency'] for r in affine if r['effective_delta_efficiency'] is not None]
    rng=np.random.default_rng(20261107);ids=sorted({r['participant'] for r in rs});coef=[]
    for _ in range(2000):
        draw=rng.choice(ids,len(ids));sample=[]
        for ix,sid in enumerate(draw):sample.extend(dict(r,participant=ix) for r in rs if r['participant']==sid)
        fit=fit_affine(sample);coef.append([fit[0],fit[1]/100,100/fit[1]])
    save(out/'systemic_parameter_uncertainty.json',dict(parameters=['intercept_W','slope_W_per_W','effective_delta_efficiency'],
        estimate=[base[0],base[1]/100,100/base[1]],participant_bootstrap_95=np.quantile(coef,[.025,.975],axis=0).tolist(),
        draws=2000,participants=len(ids),seed=20261107,meaning='conditional whole-body empirical coefficients; not localη/M; calibration/gain/offset systematicerrors excluded'))
    statuses=[
      dict(quantity='pulmonaryVO2/VCO2',status='MEASURED',scope='nativebreathgas with devicecalibration stated; instrumentuniterror unknown'),
      dict(quantity='mechanicalW',status='MEASURED',scope='recorded prescribedergometerload; not maximalpower capacity or independent torque×velocity trace'),
      dict(quantity='systemicfuelcostW',status='EFFECTIVE ONLY',scope='derivedfrommeasuredVO2/VCO2 byexplicitWeirtypeequation; not measuredheat/ATP'),
      dict(quantity='systemiccostinterceptandslope',status='IDENTIFIED',scope='conditional affineobservationmodel on51developmentparticipants; clusterintervals; no localphysiologyassignment'),
      dict(quantity='mechanicalefficiencyηD2',status='UNIDENTIFIABLE',scope='systemicdeltaefficiency is EFFECTIVEONLY, with conditional intervals and gain/otherconsumer ambiguity'),
      dict(quantity='baselineposturegas',status='MEASURED',scope='standing37/sitting16developmentpeople; otherfile/task; not fastingRMR'),
      dict(quantity='localM/oxidativeQ',status='UNIDENTIFIABLE',scope='localallocation,otherconsumers,gain/offset unknown'),
      dict(quantity='Cf,Cs,Lf,Ls,rechargeefficiency,recoverytaus',status='UNIDENTIFIABLE',scope='noPCr/absoluteactivevolume, no validrecoverygas exceptsinglewindow; noreserveexcitationproof'),
      dict(quantity='pulmonaryeffectiveτ',status='EFFECTIVE ONLY',scope='30finiteconditionalprofiles;21UNIDENTIFIABLE; notlocalτoxygen or mitochondrialcapacity'),
      dict(quantity='PCr/ATP/Pi/pH/activevolume/MVC/twitch',status='NOT OBSERVED',scope='newCPET/WEEEcohorts; Cycle5PCrnotmergedacrosspersons'),
      dict(quantity='WEEEfuelcost',status='BOUNDED',scope='onlyunderexplicitRER.7..1; noVCO2 orW, not independent absoluteefficiency'),
    ]
    save(out/'parameter_status.json',dict(rows=statuses,warning='labels apply tospecifiedmeasurementmap; IDENTIFIEDconditionalcoefficients are not11D2parameters',
        constant_test_calibration='UNIDENTIFIABLE intercept/slope because constantprediction hasrank1; archivedminimum-normdiagnosticcoefficients are not interpreted',
        reduced_model='9D quotient retained unchanged; absoluteEsys requiresseparatelyfittedobservationlayer'))
    summary=dict(origin='real human calibration and limited validation',development_participants=len({r['participant'] for r in rs}),development_primary_endpoints=len(rs),
        systemic_affine_intercept_W=base[0],systemic_incremental_cost_W_per_W=base[1]/100,systemic_effective_delta_efficiency=100/base[1],
        individual_efficiency_quantiles=np.quantile(vals,[.05,.5,.95]).tolist(),pulmonary_fits=len(kin),finite_conditional_tau_profiles=sum(r['finite_profile'] for r in kin),
        systemic_metabolic_anchor=True,local_ATP_anchor=False,local_rest_anchor=False,reduced_D2_parameters=9,
        mechanical_power_validation='NOT DONE',TARGET_CPE45='NOT EXTERNALLY VALIDATED',NO_GO=True)
    save(out/'summary.json',summary);return summary

if __name__=='__main__':print(json.dumps(generate(BASE/'results'),indent=2))
