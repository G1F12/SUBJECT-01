"""Numerical reproduction including locked external power test; hashes reject changed sources."""
from pathlib import Path
import argparse,csv,hashlib,json,math,tempfile
import diagnostics,pipeline
BASE=Path(__file__).resolve().parent
def equal(a,b):
    if isinstance(a,dict):return set(a)==set(b) and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    if isinstance(a,(float,int)) and not isinstance(a,bool):return isinstance(b,(float,int)) and math.isclose(a,b,rel_tol=2e-6,abs_tol=2e-5)
    return a==b
def read(path):
    if path.suffix=='.json':return json.loads(path.read_text('utf8'))
    def parse(v):
        try:return float(v)
        except (ValueError,TypeError):return v
    with path.open(encoding='utf8',newline='') as f:return [{k:parse(v) for k,v in r.items()} for r in csv.DictReader(f)]
def check():
    manifest=json.loads((BASE/'manifest.json').read_text('utf8'))
    for rel,sha in manifest.items():assert hashlib.sha256((BASE/rel).read_bytes()).hexdigest()==sha,rel
    pipeline.load_lock()
    with tempfile.TemporaryDirectory() as temp:
        dest=Path(temp)
        # Rebuild grouped development selection without mutating the historical lock.
        rows=pipeline.scoring_rows();params,_=pipeline.fit(rows);lock=pipeline.load_lock()
        assert equal(params,lock['models'])
        cv=[]
        for sid in lock['development_ids']:
            local,_=pipeline.fit([r for r in rows if r['participant']!=sid])
            held=[r for r in rows if r['participant']==sid]
            for label in pipeline.LABELS:
                cv.extend(dict(model=label,**r) for r in pipeline.predictions(held,label,local[label]))
        pipeline.save_csv(dest/'development_cv.csv',[dict(model=label,**pipeline.metric([r for r in cv if r['model']==label])) for label in pipeline.LABELS])
        pipeline.save_csv(dest/'development_cv_predictions.csv',[{k:r[k] for k in ['model','participant','rest_s','repetition','predicted_W','predicted_ratio']} for r in cv])
        pipeline.evaluate_test(dest);diagnostics.generate(dest)
        for p in dest.iterdir():assert equal(read(p),read(BASE/'results'/p.name)),p.name
    print('PASS recovery source/output hashes, lock, negative diagnostic and independent test reproduction')
def plots():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=BASE/'results'
    d=read(out/'test_scores.csv');boot=read(out/'test_bootstrap.csv')
    fig,ax=plt.subplots(figsize=(11,4),layout='constrained')
    y=[r['RMSE_W'] for r in d];low=[r['RMSE_p025_W'] for r in boot];high=[r['RMSE_p975_W'] for r in boot]
    ax.bar([r['model'] for r in d],y,color=['#556b8e']*3+['#b34c43','#c58144','#556b8e','#8a759e'])
    ax.errorbar(range(len(y)),y,yerr=[[v-l for v,l in zip(y,low)],[h-v for h,v in zip(high,y)]],fmt='none',ecolor='black',capsize=3)
    ax.set(ylabel='Locked-test RMSE (W)',title='7 independent participants, 189 endpoints; participant bootstrap')
    ax.tick_params(axis='x',labelrotation=18);fig.savefig(out/'independent_test.png',dpi=160);plt.close(fig)
    ident=read(out/'identifiability.json');profile=read(out/'recovery_profile.csv')
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    axes[0].semilogy(range(1,12),ident['singular_values'],'o-');axes[0].axhline(ident['singular_values'][0]*1e-6,color='gray',ls='--');axes[0].set(xlabel='Singular value index',ylabel='Sensitivity singular value',title='Scenario Jacobian: rank7 /11')
    axes[1].semilogx([r['tau_s'] for r in profile],[r['delta_profile_chi2'] for r in profile]);axes[1].set(xlabel='Effective recovery tau (s)',ylabel='Profile delta chi-square (working noise model)',title='Real development data: flat profile at depletion0')
    fig.savefig(out/'identifiability.png',dpi=160);plt.close(fig)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:check()
    else:
        plots()
        paths=[p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.json','.csv','.png','.md'} and p.name!='manifest.json']
        pipeline.save_json(BASE/'manifest.json',{p.relative_to(BASE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
