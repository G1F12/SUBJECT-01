"""Real CPET parsing; participant gate precedes outcome reading. No imputation."""
from pathlib import Path
import csv,json,math,hashlib
import numpy as np
from acquire import BASE,CACHE,digest,save
COLS={'vo2_L_min':'Sauerstoffaufnahme','vco2_L_min':'Kohlendioxidabgabe','power_W':'Leistung','cadence_rpm':'Trittfrequenz'}

def second(s):
    h,m,v=map(float,s.split(':'));return 3600*h+60*m+v
def finite_or_none(value):
    try:
        x=float(value);return x if math.isfinite(x) else None
    except (ValueError,TypeError):return None
def ids():
    x=json.loads((BASE/'lendt_listing.json').read_text('utf8'))
    return sorted({int(Path(m['name']).stem.split('_')[0][1:]) for m in x['members'] if m['name'].endswith('_cycle.csv')})
def native(sid,task='cycle',unlock=False):
    if sid%5==0 and not unlock:raise ValueError('test outcomes require explicit post-lock unlock')
    p=CACHE/f'P{sid}_{task}.csv'
    if not p.exists():return []
    records=json.loads((BASE/'cpet_retrieval.json').read_text('utf8'))['files']
    meta=next(r for r in records if r['cache']==p.name)
    if digest(p.read_bytes())!=meta['sha256']:raise ValueError('native source hash mismatch')
    out=[]
    for row in csv.DictReader(p.open(encoding='utf-8-sig',newline='')):
        try:
            r=dict(time_s=second(row['t']),**{k:finite_or_none(row.get(c)) for k,c in COLS.items()})
            if r['vo2_L_min'] is None or r['vco2_L_min'] is None or r['vo2_L_min']<=0 or r['vco2_L_min']<0:continue
            out.append(r)
        except (ValueError,KeyError,TypeError):continue
    if any(b['time_s']<a['time_s'] for a,b in zip(out,out[1:])):raise ValueError('nonmonotonic native time')
    # Instrument timestamps rounded to seconds: average observed duplicate breaths,
    # never insert missing values or fabricate intermediate samples.
    from itertools import groupby
    merged=[]
    for t,group in groupby(out,key=lambda r:r['time_s']):
        group=list(group);vals={k:[r[k] for r in group if r[k] is not None] for k in COLS}
        merged.append(dict(time_s=t,**{k:sum(v)/len(v) if v else None for k,v in vals.items()}))
    return merged

def window(rows,start,end,shift=0.):
    xs=[r for r in rows if start<r['time_s']-shift<=end];n=len(xs)
    pairs=[(a,b,b['time_s']-a['time_s']) for a,b in zip(xs,xs[1:]) if b['time_s']-a['time_s']<=15]
    duration=sum(h for a,b,h in pairs)
    if n<2 or duration<30 or duration/(end-start)<.8:return None
    means={}
    for k in COLS:
        available=[(a,b,h) for a,b,h in pairs if a[k] is not None and b[k] is not None];covered=sum(h for a,b,h in available)
        means[k]=sum((a[k]+b[k])*.5*h for a,b,h in available)/covered if covered>=.8*duration else None
    # Working uncertainty: temporal15s block means, not independent breath SEM.
    blocks=[]
    for t in np.arange(start,end,15):
        ys=[3.9*r['vo2_L_min']+1.1*r['vco2_L_min'] for r in xs if t<r['time_s']-shift<=t+15]
        if ys:blocks.append(float(np.mean(ys))*4184/60)
    return dict(start_s=start,end_s=end,n_breaths=n,observed_s=duration,coverage=duration/(end-start),**means,
                cost_W=(3.9*means['vo2_L_min']+1.1*means['vco2_L_min'])*4184/60,
                RER=means['vco2_L_min']/means['vo2_L_min'],block_SE_W=float(np.std(blocks,ddof=1)/math.sqrt(len(blocks))) if len(blocks)>1 else None,
                local_ATP_flux=None,PCr=None)

def participant(sid,unlock=False,shift=0.):
    rows=native(sid,'cycle',unlock);stages=[];rest=[]
    count=3 if sid>50 else 5
    expected=[50,75,100] if sid>50 else [30,60,90,120,150]
    for k in range(count):
        end=390+660*k
        r=window(rows,end-60,end,shift)
        if r:
            r.update(participant=sid,stage=k+1,task='cycle',expected_power_W=expected[k],source=f'P{sid}_cycle.csv',primary_eligible=.7<=r['RER']<=1 and r['power_W'] is not None and abs(r['power_W']-expected[k])<=2)
            stages.append(r)
        if k<count-1:
            r=window(rows,end+240,end+300,shift)
            if r:r.update(participant=sid,stage=k+1,task='interbout_recovery',source=f'P{sid}_cycle.csv');rest.append(r)
    walk=native(sid,'walk',unlock)
    baseline=window(walk,330,390)  # source-defined initial sitting(if>50) /standing(if<=50)
    if baseline:baseline.update(participant=sid,stage=0,task='sitting' if sid>50 else 'standing',source=f'P{sid}_walk.csv')
    return stages,rest,baseline

def collect(split='development',unlock=False,shift=0.):
    if split not in ('development','test','all'):raise ValueError('split')
    if split!='development' and not unlock:raise ValueError('test gated')
    use=[i for i in ids() if split=='all' or (i%5==0)==(split=='test')]
    stages=[];rest=[];base=[]
    for sid in use:
        s,r,b=participant(sid,unlock,shift);stages+=s;rest+=r
        if b:base.append(b)
    return stages,rest,base

def export(split,unlock=False):
    s,r,b=collect(split,unlock);save(BASE/f'{split}_stage_audit.json',dict(origin='REAL measured gas/power-derived summaries; no synthetichumanrows',stages=s,recovery=r,baseline=b,
        units='VO2/VCO2L/min,powerW,cadencerpm,timeS;costW from3.9VO2+1.1VCO2kcal/min',preregistration_commit='0446eaadcecb7c4ebea3613d20527a6d3fd94897'))
    print(split,'participants',len({x['participant'] for x in s}),'stage endpoints',sum(x['primary_eligible'] for x in s),'baseline',len(b),'rest',len(r))

if __name__=='__main__':export('development')
