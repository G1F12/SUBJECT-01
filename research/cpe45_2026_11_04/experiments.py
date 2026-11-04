"""Reproduce EXP-0011..0014: python research/cpe45_2026_11_04/experiments.py [--check]."""
from pathlib import Path
import argparse,csv,hashlib,json,math,platform,tempfile
import numpy as np
import model,validation
BASE=Path(__file__).resolve().parent

def save_json(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def save_csv(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader()
        for row in rows:w.writerow({k:format(v,'.10g') if isinstance(v,(float,np.floating)) else v for k,v in row.items()})
def flatten(s):
    return {k:v for k,v in s.items() if not isinstance(v,(dict,list))}|dict(energy_limited_s=s['limiting_seconds']['energetic'],mechanical_limited_s=s['limiting_seconds']['mechanical'])
def generate(out,plots=False):
    out.mkdir(parents=True,exist_ok=True);config=model.load();seed=config['seed'];rng=np.random.default_rng(seed)
    raw,pred,scores,participant,meta=validation.evaluate()
    save_csv(out/'observations.csv',raw);save_csv(out/'validation_predictions.csv',pred);save_csv(out/'validation_scores.csv',scores);save_csv(out/'validation_participants.csv',participant);save_json(out/'validation.json',meta)
    summaries=[];episode_rows=[];recovery=[];retention=[];bridges={};plot_traces={}
    cases=[(a,c,'mixed') for a in config['architectures'] for c in config['climates']]+[('baseline','temperate',p) for p in config['protocols'] if p!='mixed']
    for a,c,p in cases:
        s,tr,eps=model.simulate(config,name=p,architecture=a,climate=c)
        case=f'{a}__{c}__{p}';summaries.append(s)
        # One-second snapshots plus every task boundary; cumulative ledger retains full integration.
        boundaries={e['end_s'] for e in eps}
        sampled=[r for r in tr if abs(r['time_s']-round(r['time_s']))<1e-8 or r['time_s'] in boundaries]
        save_csv(out/f'trace__{case}.csv',sampled)
        episode_rows += [dict(case=case,**e) for e in eps]
        for task,metrics in s['early_late'].items():
            for metric,values in metrics.items():retention.append(dict(case=case,task_id=task,metric=metric,**values))
        for e in eps:
            if e['kind']=='recovery':recovery.append(dict(case=case,start_s=e['start_s'],end_s=e['end_s'],fast_start_J=e['fast_start_J'],fast_end_J=e['fast_end_J'],slow_start_J=e['slow_start_J'],slow_end_J=e['slow_end_J'],fatigue_start=e['fatigue_start'],fatigue_end=e['fatigue_end']))
        if p=='mixed':bridges[case]=model.measurement_bridge(tr,eps)
        if a=='baseline' and p=='mixed':plot_traces[c]=sampled
    save_csv(out/'scenarios.csv',[flatten(s) for s in summaries]);save_csv(out/'episodes.csv',episode_rows);save_csv(out/'retention.csv',retention);save_csv(out/'recovery.csv',recovery);save_json(out/'measurement_bridge.json',bridges)
    # Independent uniform *scenario* uncertainty; not human population distributions.
    ranges={'fast_capacity_J':[4000,12000],'slow_capacity_J':[11000,33000],'fast_recovery_tau_s':[40,160],'slow_recovery_tau_s':[300,1200],'oxygen_tau_s':[20,40],'fatigue_rate_s_inv':[0,.003],'fatigue_recovery_tau_s':[150,600],'slow_component_max_W':[0,340]}
    uq=[]
    for i in range(64):
        params={k:float(rng.uniform(*interval)) for k,interval in ranges.items()}
        s,_,_=model.simulate(config,overrides=params,keep_trace=False)
        uq.append(dict(run=i,**params,work_J=s['external_J'],fast_end_J=s['fast_J'],slow_end_J=s['slow_J'],delta_K=s['body_delta_K'],contractile_fraction=s['available_contractile_fraction']))
    save_csv(out/'uncertainty.csv',uq)
    baseline=next(s for s in summaries if s['architecture']=='baseline' and s['climate']=='temperate' and s['protocol']=='mixed')
    sensitivity=[]
    for k in ranges:
        for factor in [.8,1.2]:
            s,_,_=model.simulate(config,overrides={k:config['dynamic'][k]*factor},keep_trace=False)
            sensitivity.append(dict(parameter=k,factor=factor,value=config['dynamic'][k]*factor,work_J=s['external_J'],relative_work_change=s['external_J']/baseline['external_J']-1,delta_K=s['body_delta_K'],fast_end_J=s['fast_J']))
    save_csv(out/'sensitivity.csv',sensitivity)
    convergence=[]
    for step in [.5,.25,.125,.0625]:
        s,_,_=model.simulate(config,dt=step,keep_trace=False)
        convergence.append(dict(dt_s=step,work_J=s['external_J'],fast_J=s['fast_J'],delta_K=s['body_delta_K'],energy_residual_J=s['energy_residual_J'],kinetic_residual_J=s['kinetic_residual_J']))
    save_csv(out/'convergence.csv',convergence)
    negative=[]
    for label,over in [('zero_reserves',{'fast_capacity_J':0,'slow_capacity_J':0}),('no_peripheral_fatigue',{'fatigue_rate_s_inv':0}),('slow_recovery',{'fast_recovery_tau_s':800,'slow_recovery_tau_s':6000})]:
        s,_,_=model.simulate(config,overrides=over,keep_trace=False);negative.append(dict(test=label,**flatten(s)))
    p=model.integrated.load();q=p['metabolic_intercept_W']/((p['arterial_content']-p['venous_content'])*p['oxygen_energy_J_m3'])
    s,_,_=model.simulate(config,overrides={'fast_capacity_J':0,'slow_capacity_J':0,'slow_component_max_W':0},integrated_overrides={'cardiac_output_m3_s':q},keep_trace=False)
    negative.append(dict(test='no_exercise_energy',**flatten(s)))
    save_csv(out/'negative.csv',negative)
    quant=lambda n:{k:[float(np.quantile([r[k] for r in uq[:n]],q)) for q in [.05,.5,.95]] for k in ['work_J','fast_end_J','slow_end_J','delta_K','contractile_fraction']}
    summary=dict(seed=seed,cases=len(cases),UQ_runs=64,uncertainty_type='independent uniform epistemic scenarios, not confidence/credible intervals',ranges=ranges,uq_p05_p50_p95=quant(64),uq_prefix32_p05_p50_p95=quant(32),baseline=baseline,scenarios=summaries,validation=meta,convergence=convergence,source_commit='070a7343e522ca9fdbe37d3c0f7e3e0894bc7e30',agent='OpenAI Codex; single agent, no independent scientific review',environment=dict(python=platform.python_version(),numpy=np.__version__),instructions='User CPE45 A-H; code, config, sources, tests and this script fully specify reproduction. No intervention validation.')
    save_json(out/'summary.json',summary)
    if plots:
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(3,2,figsize=(12,10),layout='constrained')
        for climate,tr in plot_traces.items():
            t=np.array([r['time_s']/60 for r in tr])
            for ax,key,title in [(axes[0,0],'fast_J','Fast reserve (J)'),(axes[0,1],'slow_J','Slow reserve (J)'),(axes[1,0],'oxygen_W','Oxidative input (W)'),(axes[1,1],'body_delta_K','One-node temperature change (K)'),(axes[2,0],'available_contractile_fraction','Contractile fraction (conditional)')]:
                ax.plot(t,[r[key] for r in tr],label=climate,linewidth=1);ax.set(xlabel='Time (min)',ylabel=title)
        for climate in config['climates']:
            rows=[e for e in episode_rows if e['case']==f'baseline__{climate}__mixed' and e['task_id']=='acceleration_max']
            axes[2,1].plot([e['start_s']/60 for e in rows],[e['mean_power_W'] for e in rows],label=climate)
        axes[2,1].set(xlabel='Time (min)',ylabel='Mean acceleration episode power (W)')
        for ax in axes.flat:ax.grid(alpha=.2);ax.legend(fontsize=8)
        fig.suptitle('CPE45 conditional simulation — not empirical validation')
        fig.savefig(out/'dynamics.png',dpi=150);plt.close(fig)
        fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
        val=[r for r in scores if r['split']=='validation'];ax.bar([r['model'] for r in val],[r['RMSE_W'] for r in val]);ax.set(ylabel='Held-participant RMSE (W)',title='6 s cycling endpoint; first sprint supplied as input');ax.tick_params(axis='x',labelrotation=15);fig.savefig(out/'validation.png',dpi=150);plt.close(fig)

def equivalent(a,b):
    if isinstance(a,dict):return set(a)==set(b) and all(equivalent(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
    if isinstance(a,(int,float)) and not isinstance(a,bool):return isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=2e-7,abs_tol=2e-5)
    return a==b
def check():
    manifest=json.loads((BASE/'manifest.json').read_text('utf8'))
    for rel,sha in manifest.items():
        assert hashlib.sha256((BASE/rel).read_bytes()).hexdigest()==sha,rel
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp);generate(out)
        for path in out.iterdir():
            old=BASE/'results'/path.name
            if path.suffix=='.json':
                a=json.loads(old.read_text('utf8'));b=json.loads(path.read_text('utf8'))
                if path.name=='summary.json':a.pop('environment');b.pop('environment')
            else:
                def rows(p):
                    def value(v):
                        try:return float(v)
                        except (ValueError,TypeError):return v
                    with p.open(encoding='utf8',newline='') as f:return [{k:value(v) for k,v in r.items()} for r in csv.DictReader(f)]
                a,b=rows(old),rows(path)
            assert equivalent(a,b),path.name
    print('PASS: CPE45 source/output hashes and numerical reproduction; no empirical CPE45 claim')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:check()
    else:
        generate(BASE/'results',True)
        paths=[p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.csv','.json','.xlsx','.png'} and p.name!='manifest.json']
        save_json(BASE/'manifest.json',{p.relative_to(BASE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
        print('Saved reproducible CPE45 experiments')
