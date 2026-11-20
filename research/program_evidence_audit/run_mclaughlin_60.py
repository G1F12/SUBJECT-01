"""EXP-0086: retrospective 59-minute external thermal trajectory evaluation."""
import hashlib,inspect,json,math,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import lumped_peak,text_sha256
H=Path(__file__).resolve().parent; ROOT=H.parents[1]; path=Path(sys.argv[1]); digest=hashlib.sha256(path.read_bytes()).hexdigest(); assert digest=='499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531'
book=load_workbook(path,read_only=True,data_only=True)
temp=list(book['Core Temp'].values); work=list(book['Exercise Data'].values); env=list(book['Environmental Conditions'].values); demo=list(book['Demographics'].values)
def cols(row,start,end):
 pairs=[(v,i) for i,v in enumerate(row[start:end],start) if isinstance(v,int)]; assert len(pairs)==len(dict(pairs)); return dict(pairs)
tc=cols(temp[1],2,27); pc=cols(work[1],77,101); ac=cols(env[1],2,27); rc=cols(env[1],27,51)
mass={r[0]:r[4] for r in demo[1:] if isinstance(r[0],int)}; temperatures={r[1]:r for r in temp[2:] if isinstance(r[1],int)}
powers={}
for row in work[2:]:
 label=row[1]; label=f'{label-1}-{label}' if isinstance(label,int) else label
 if isinstance(label,str) and '-' in label:
  assert label not in powers; powers[label]=row
climates={r[1]:r for r in env[2:] if isinstance(r[1],str)}
ids=sorted(set(tc)|set(pc)|set(ac)|set(rc)); eligible=[]; excluded=0
for person in ids:
 try:
  weight=mass[person]; t1,t45,t60=(temperatures[t][tc[person]] for t in (1,45,60)); air=climates['5-6'][ac[person]]; rh=climates['5-6'][rc[person]]; initial=powers['0-1'][pc[person]]; series=[powers[f'{m}-{m+1}'][pc[person]] for m in range(1,60)]
  vals=[weight,t1,t45,t60,air,rh,initial,*series]
  if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in vals):raise ValueError('missing')
  if not (30<=weight<=200 and all(34<=v<=43 for v in (t1,t45,t60)) and 0<=air<=50 and 0<=rh<=100 and all(0<v<600 for v in [initial,*series])):raise ValueError('out-of-range')
  eligible.append((weight,t1,t45,t60,air,rh/100,initial,series))
 except (KeyError,IndexError,ValueError):excluded+=1
assert len(eligible)>3
thermal_path=ROOT/'research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py'; source=thermal_path.read_text(encoding='utf-8'); assert source.count('duration_s = 2700.0')==1; source=source.replace('duration_s = 2700.0','duration_s = 3540.0'); needle='        if step % trace_stride == 0:'; assert source.count(needle)==1; source=source.replace(needle,'        p_now = float(power_schedule(t_now))\n'+needle)
ctx={'__name__':'mclaughlin_60','__file__':str(thermal_path)}; exec(compile(source,str(thermal_path),'exec'),ctx); solver=ctx['simulate_4layer_pennes_2700s']; vap=ctx['saturation_vapor_pressure_kpa']
# Same lumped equations, returning the full per-step trace and using participant mass.
def lumped_trace(series,weight,air,rh):
 cap=weight*3470+3.2*3800; initial=sum(c*t for c,t in zip([weight*3470*s for s in (.35,.42,.16,.07)]+[3.2*3800],(37,35.8,34,33,36.85)))/cap
 t=initial; output=[t]; area=1.92; ambient_vap=rh*vap(air)
 for p in series:
  dry=area*(7.8*(t-air)+.95*5.670374419e-8*((t+273.15)**4-(air+273.15)**4)); drive=max(0.,t-37+.15*(t-33)); emax=max(0.,16.5*7.8*area*(vap(t)-ambient_vap)); sweat=(1.20/3600)*.72*2.42e6*min(1.,drive/1.5); metab=82+p/.21; resp=max(8.,metab*(.075+.0014*(34-air))); heat=88+p*(1/.21-1)
  t+=5*(heat-dry-min(sweat,emax)-resp)/cap; output.append(t)
 return np.array(output)-initial
reference_source=inspect.getsource(lumped_peak).replace('def lumped_peak(powers, step_s, ambient_C, humidity, vapor_pressure):','def lumped_final_weighted(powers, step_s, ambient_C, humidity, vapor_pressure, weight):').replace('75 * 3470','weight * 3470').replace('    return peak_C','    return temp_C')
reference_globals=dict(lumped_peak.__globals__); exec(reference_source,reference_globals); lumped_reference=reference_globals['lumped_final_weighted']
observed={'full':[],'late':[]}; pred={k:{n:[] for n in ('persistence','pennes_variable','pennes_constant','lumped_variable')} for k in observed}; actual_work=[]; constant_work=[]
for weight,t1,t45,t60,air,rh,initial,series in eligible:
 tracepowers=np.repeat(series,12); assert len(tracepowers)==708; actual_work.append(float(tracepowers.sum()*5)); constant_work.append(initial*3540)
 curves={}
 for label,values in [('pennes_variable',tracepowers),('pennes_constant',np.full(708,initial))]:
  ctx['power_schedule']=lambda t,values=values:float(values[min(707,int(t//5))]); run=solver(initial,1.,air,rh,body_mass_kg=weight,dt_s=5.); assert run['energy_balance_error_J']<.01
  points={r['time_s']:r['T_core_C'] for r in run['trace_30s']}; curves[label]=(points[2640]-points[0],points[3540]-points[2640])
 lt=lumped_trace(tracepowers,weight,air,rh); initial_lumped=sum(c*t for c,t in zip([weight*3470*v for v in (.35,.42,.16,.07)]+[3.2*3800],(37,35.8,34,33,36.85)))/(weight*3470+3.2*3800); assert abs(lumped_reference(tracepowers,5.,air,rh,vap,weight)-initial_lumped-lt[708])<1e-9; assert abs(lumped_reference(tracepowers[:528],5.,air,rh,vap,weight)-initial_lumped-lt[528])<1e-9; curves['lumped_variable']=(float(lt[528]),float(lt[708]-lt[528])); curves['persistence']=(0.,0.)
 observed['full'].append(t60-t1); observed['late'].append(t60-t45)
 for name,(before45,late) in curves.items():pred['full'][name].append(before45+late); pred['late'][name].append(late)
rng=np.random.default_rng(20261120); indices=rng.integers(0,len(eligible),(10000,len(eligible))); metrics={}
for horizon in observed:
 actual=np.array(observed[horizon]); err={k:np.abs(np.array(v)-actual) for k,v in pred[horizon].items()}; tests={}
 for name in err:
  residual=np.array(pred[horizon][name])-actual; diff=err[name]-err['pennes_variable']; tests[name]={'mae_C':float(err[name].mean()),'bias_C':float(residual.mean()),'paired_mae_minus_pennes_C':float(diff.mean()),'paired_ci95_C':np.quantile(diff[indices].mean(axis=1),[.025,.975]).tolist()}
 metrics[horizon]={'mean_observed_change_C':float(actual.mean()),'models':tests}
result={'experiment_id':'EXP-0086','classification':'EXPLORATORY_REUSED_COHORT_LONGER_HORIZON','source_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'MCLAUGHLIN_60_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'thermal_sha256_lf':text_sha256(thermal_path),'lumped_reference_sha256_lf':text_sha256(H/'run_audit.py'),'included_participants':len(eligible),'excluded_count':excluded,'mean_actual_work_J':float(np.mean(actual_work)),'mean_constant_work_J':float(np.mean(constant_work)),'time_label_assumption':'numeric labels are interval ends','metrics':metrics}
(H/'MCLAUGHLIN_60_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
