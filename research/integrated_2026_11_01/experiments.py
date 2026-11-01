"""Воспроизводимые эксперименты: python .../experiments.py [--check]."""
from pathlib import Path
import argparse,csv,json,math,tempfile,hashlib
import numpy as np
import model
BASE=Path(__file__).resolve().parent
SEED=20261101
METRICS=['force_N','peak_horizontal_W','terminal_sprint_m_s','sustainable_external_W','sustainable_proxy_m_s','effective_latency_s','prediction_error_m']

def save_csv(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader()
        for row in rows:w.writerow({k:format(v,'.10g') if isinstance(v,(float,np.floating)) else v for k,v in row.items()})

def architectures(base):
    out=[('baseline',dict(base))]
    p=dict(base,added_contractile_kg=2.);out.append(('muscle_only',p))
    p=dict(base,added_contractile_kg=2.,support_mass_kg=1.,tendon_area_m2=base['tendon_area_m2']*1.4,contact_scale=1.15,cardiac_output_m3_s=base['cardiac_output_m3_s']*1.15,evaporated_water_kg_s=base['evaporated_water_kg_s']*1.2);out.append(('coordinated',p))
    p=dict(base,moment_arm_m=base['moment_arm_m']*1.25,support_mass_kg=.5);out.append(('transmission',p))
    p=dict(base,added_contractile_kg=4.,support_mass_kg=2.,tendon_area_m2=base['tendon_area_m2']*1.8,contact_scale=1.3,cardiac_output_m3_s=base['cardiac_output_m3_s']*1.3,evaporated_water_kg_s=base['evaporated_water_kg_s']*1.5,prediction_horizon_s=.08);out.append(('internal_biohybrid_conditional',p))
    p=dict(base,support_mass_kg=.5,prediction_horizon_s=.08,sensor_noise_m=.003);out.append(('internal_predictive_sensory_conditional',p))
    return out

def validation(data,p):
    out=[]
    def row(name,obs,pred,unit,kind):out.append(dict(check=name,observed=obs,predicted=pred,residual=pred-obs,relative_error=(pred-obs)/obs,unit=unit,interpretation=kind))
    # Групповые средние: reciprocal(mean efficiency) != mean metabolic power.
    row('cycling_85W_holdout',85/.192,p['metabolic_intercept_W']+85/p['delta_efficiency'],'W','тот же cohort; не независимая выборка')
    age=np.array([20.8,28.6,35.5,42.3,48.6,55.,61.6]);rt=np.array([.2179,.221,.2248,.2277,.2336,.2364,.2391]);n=np.array([86,115,201,273,276,272,246]);coef=np.polyfit(age,rt,1,w=np.sqrt(n))
    row('reaction_independent_cohort_age41',.2378,float(np.polyval(coef,41.)),'s','другая выборка; та же статья, uncorrected')
    # Независимое исследование: фиксированная extraction из pooled studies может не переноситься.
    for q,vo,g in [(23.6,3.4,'young_men'),(17.4,2.2,'old_men'),(17.7,2.2,'young_women'),(12.3,1.4,'old_women')]:
        row('oxygen_external_'+g,vo,q*(p['arterial_content']-p['venous_content']),'L/min','внешняя выборка; SD; cohort may overlap synthesis not established')
    first=146700.;loss=400-first/900
    for observed,bout in [(94700.,2),(92000.,3),(91900.,4)]:row('thermal_constant_loss_bout'+str(bout),observed,(400-loss)*900,'J','отрицательный тест constant-loss; та же выборка')
    row('sprint_same_sample_Pmax',1680.,638*10.5/4,'W','тождество линейного FV; не независимая валидация')
    return out

def generate(output,plots=False):
    output.mkdir(exist_ok=True,parents=True);base=model.load();rng=np.random.default_rng(SEED)
    data=list(csv.DictReader((BASE/'calibration.csv').open(encoding='utf8')))
    vals=validation(data,base);save_csv(output/'validation.csv',vals)
    scenarios=[];traces=[]
    for name,p in architectures(base):
        for climate,t,rh in [('temperate',298.15,.5),('hot_humid',308.15,.8),('hot_dry',308.15,.2)]:
            pp=dict(p,air_K=t,radiant_K=t,relative_humidity=rh)
            e=model.evaluate(pp);sprint,trace=model.sprint(pp)
            scenarios.append(dict(architecture=name,climate=climate,**e,**{'sprint6_'+k:v for k,v in sprint.items()}))
            if climate=='temperate':traces.extend(dict(architecture=name,**r) for r in trace)
    save_csv(output/'scenarios.csv',scenarios);save_csv(output/'sprint.csv',traces)
    baseline=model.evaluate(base)
    # Локальная центральная эластичность; не применяется к нулевым параметрам.
    local=[]
    keys=['specific_tension_Pa','pcsa_m2','tendon_area_m2','tendon_stress_Pa','moment_arm_m','geometry_projection','sprint_F0_N','sprint_v0_m_s','body_mass_kg','cardiac_output_m3_s','arterial_content','venous_content','delta_efficiency','evaporated_water_kg_s','surface_area_m2','processing_s','internal_work_J_kg_m']
    for k in keys:
        low=dict(base);high=dict(base);low[k]*=.99;high[k]*=1.01
        l,h=model.evaluate(low),model.evaluate(high)
        local.append(dict(parameter=k,**{m:(h[m]-l[m])/(.02*baseline[m]) for m in METRICS}))
    save_csv(output/'local_sensitivity.csv',local)
    uq=[]
    # Популяционная вариабельность и неопределённость средних не смешаны с допущениями.
    for mode in ['population','mean_estimation','epistemic']:
        for i in range(256):
            p=dict(base)
            if mode in ['population','mean_estimation']:
                scale=1 if mode=='population' else 1/math.sqrt(117)
                q=float(np.clip(rng.normal(25,2.4*scale),10,40));ca=float(np.clip(rng.normal(.203,.010*scale),.15,.25));ex=float(np.clip(rng.normal(.79,.08*scale),.4,.98))
                p.update(cardiac_output_m3_s=q/60000,arterial_content=ca,venous_content=ca*(1-ex))
                # Среднее/SD из другой выборки; корреляции неизвестны.
                scale2=1 if mode=='population' else 1/3
                p.update(sprint_F0_N=float(np.clip(rng.normal(638,84*scale2),200,1100)),sprint_v0_m_s=float(np.clip(rng.normal(10.5,.74*scale2),7,14)))
                sweat_sd=.0002*(math.sqrt(18) if mode=='population' else 1)
                p['evaporated_water_kg_s']=float(np.clip(rng.normal(.0095,sweat_sd),.003,.018))/60
                p['execution_s']=float(np.clip(rng.normal(base['execution_s'],.0268 if mode=='population' else .0268/math.sqrt(1469)),.005,.25))
            else:
                p.update(internal_work_J_kg_m=rng.uniform(.1,1.2),geometry_projection=rng.uniform(.12,.23),fiber_vmax_m_s=rng.uniform(.5,1.2),hc_W_m2_K=rng.uniform(5,12),skin_K=rng.uniform(306.15,309.15),delta_efficiency=rng.uniform(.23,.32),bone_load_cap_N=rng.uniform(2500,10000))
            e=model.evaluate(p);uq.append(dict(mode=mode,index=i,**{m:e[m] for m in METRICS}))
    save_csv(output/'uncertainty.csv',uq)
    # Глобальная Sobol total-order Jansen: независимые равномерные сценарные интервалы.
    ranges={'specific_tension_Pa':(200000,430000),'tendon_area_m2':(.00008,.00018),'sprint_F0_N':(470,806),'sprint_v0_m_s':(9.02,11.98),'cardiac_output_m3_s':(20.2/60000,29.8/60000),'delta_efficiency':(.23,.32),'evaporated_water_kg_s':(.006/60,.013/60),'geometry_projection':(.12,.23),'fiber_vmax_m_s':(.5,1.2),'internal_work_J_kg_m':(.1,1.2),'processing_s':(.03,.09),'body_mass_kg':(60,90)}
    names=list(ranges);n=512;d=len(names);A=rng.random((n,d));B=rng.random((n,d))
    def sample(mat):
        out=[]
        for z in mat:
            p=dict(base)
            for k,v in zip(names,z):lo,hi=ranges[k];p[k]=lo+(hi-lo)*v
            e=model.evaluate(p);out.append([e[m] for m in METRICS])
        return np.array(out)
    ya=sample(A);yb=sample(B);variance=np.var(np.vstack([ya,yb]),axis=0);sobol=[]
    for j,k in enumerate(names):
        ab=A.copy();ab[:,j]=B[:,j];yc=sample(ab)
        numerator=.5*(ya-yc)**2
        st=np.divide(numerator.mean(axis=0),variance,out=np.zeros(len(METRICS)),where=variance>1e-20)
        # Bootstrap sampling uncertainty; not source/model uncertainty.
        ix=rng.integers(0,n,(128,n));boot=np.divide(numerator[ix].mean(axis=1),variance,out=np.zeros((128,len(METRICS))),where=variance>1e-20)
        for z,m in enumerate(METRICS):sobol.append(dict(parameter=k,metric=m,total_order=st[z],bootstrap_p05=np.quantile(boot[:,z],.05),bootstrap_p95=np.quantile(boot[:,z],.95),n=n))
    save_csv(output/'global_sensitivity.csv',sobol)
    # Конкурирующие архитектуры: 3*3*3*3*2 = 162; все uplift-параметры условные.
    grid=[]
    for mass in [0.,2.,4.]:
      for support in [0.,1.,2.]:
       for transport in [1.,1.15,1.3]:
        for cooling in [1.,1.25,1.5]:
         for horizon in [0.,.08]:
          p=dict(base,added_contractile_kg=mass,support_mass_kg=support,cardiac_output_m3_s=base['cardiac_output_m3_s']*transport,evaporated_water_kg_s=base['evaporated_water_kg_s']*cooling,tendon_area_m2=base['tendon_area_m2']*(1+.4*support),contact_scale=1+.1*support,prediction_horizon_s=horizon)
          e=model.evaluate(p)
          # Пакетные ресурсные предпосылки явно не закон биологии.
          resources=(transport<=1+.15*support+1e-9 and cooling<=1+.25*support+1e-9)
          acceptable=resources and e['prediction_error_m']<=.02 and e['mass_kg']<=81 and e['sustainable_external_W']>0
          grid.append(dict(index=len(grid),added_mass_kg=mass,support_mass_kg=support,transport_factor=transport,cooling_factor=cooling,prediction_horizon_s=horizon,feasible=acceptable,pareto=False,**{m:e[m] for m in ['mass_kg','force_N','peak_horizontal_W','sustainable_external_W','effective_latency_s','prediction_error_m']}))
    objectives=lambda r:np.array([r['force_N'],r['peak_horizontal_W'],r['sustainable_external_W'],-r['mass_kg'],-r['effective_latency_s'],-r['prediction_error_m']])
    for r in grid:
        if r['feasible']:
            a=objectives(r);r['pareto']=not any(s['feasible'] and np.all(objectives(s)>=a-1e-9) and np.any(objectives(s)>a+1e-9) for s in grid)
    save_csv(output/'pareto.csv',grid)
    # Усиление напряжения при неизменной передаче: явный plateau.
    bottle=[]
    for gain in [1,1.2,1.5,2,3]:
        p=dict(base,specific_tension_Pa=base['specific_tension_Pa']*gain);e=model.evaluate(p)
        bottle.append(dict(tension_factor=gain,**{m:e[m] for m in ['force_N','peak_horizontal_W','sustainable_external_W','mass_kg']}))
    save_csv(output/'bottlenecks.csv',bottle)
    quant={mode:{m:[float(np.quantile([r[m] for r in uq if r['mode']==mode],q)) for q in [.05,.5,.95]] for m in METRICS} for mode in ['population','mean_estimation','epistemic']}
    summary=dict(seed=SEED,calibration_rows=len(data),baseline=baseline,validation=vals,uncertainty_p05_p50_p95=quant,pareto_candidates=len(grid),feasible=sum(r['feasible'] for r in grid),pareto_count=sum(r['pareto'] for r in grid),sobol_evaluations=n*(d+2),uq_evaluations=len(uq),source_status='агрегатная частичная калибровка; интегрированная эмпирическая валидация отсутствует')
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    if plots:
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(1,2,figsize=(11,4.5))
        for mode,color in [('population','C0'),('mean_estimation','C1'),('epistemic','C2')]:
            x=[r['sustainable_external_W'] for r in uq if r['mode']==mode];ax[0].hist(x,bins=24,histtype='step',label=mode,color=color)
        ax[0].set(xlabel='Устойчивая внешняя мощность, Вт',ylabel='Число сценариев');ax[0].legend(fontsize=8)
        good=[r for r in grid if r['feasible']];front=[r for r in good if r['pareto']]
        ax[1].scatter([r['mass_kg'] for r in good],[r['sustainable_external_W'] for r in good],s=25,label='Допустимы в модели',alpha=.4)
        ax[1].scatter([r['mass_kg'] for r in front],[r['sustainable_external_W'] for r in front],s=25,label='Pareto по 6 целям')
        ax[1].set(xlabel='Полная масса, кг',ylabel='Устойчивая внешняя мощность, Вт');ax[1].legend(fontsize=8)
        fig.suptitle('Условная модель: интервалы сценариев, не клинические прогнозы');fig.tight_layout();fig.savefig(output/'constraints.png',dpi=150);plt.close(fig)
    return summary

def check():
    with tempfile.TemporaryDirectory() as td:
        generated=Path(td);generate(generated)
        for path in generated.glob('*.csv'):
            original=BASE/'results'/path.name
            a=list(csv.DictReader(original.open(encoding='utf8')));b=list(csv.DictReader(path.open(encoding='utf8')))
            assert len(a)==len(b),path.name
            for x,y in zip(a,b):
                assert x.keys()==y.keys()
                for k in x:
                    try:assert math.isclose(float(x[k]),float(y[k]),rel_tol=2e-7,abs_tol=2e-8),(path.name,k,x[k],y[k])
                    except ValueError:assert x[k]==y[k],(path.name,k)
        old=json.loads((BASE/'results/summary.json').read_text('utf8'));new=json.loads((generated/'summary.json').read_text('utf8'))
        def close(x,y):
            if isinstance(x,dict):assert x.keys()==y.keys();[close(x[k],y[k]) for k in x]
            elif isinstance(x,list):assert len(x)==len(y);[close(a,b) for a,b in zip(x,y)]
            elif isinstance(x,(int,float)):assert math.isclose(x,y,rel_tol=2e-7,abs_tol=2e-8)
            else:assert x==y
        close(old,new)
    print('PASS: воспроизведены все CSV и summary при seed',SEED)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:check()
    else:
        s=generate(BASE/'results',plots=True);print(json.dumps({k:s[k] for k in ['seed','calibration_rows','feasible','pareto_count','sobol_evaluations','uq_evaluations']},ensure_ascii=True))
