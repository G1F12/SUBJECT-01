"""Read obtained public numeric files; no source values redistributed, no validation split."""
from pathlib import Path
import sys,io,zipfile,json,hashlib,re,urllib.request
import numpy as np
import h5py,xlrd
from scipy.optimize import least_squares
BASE=Path(__file__).resolve().parent;CACHE=BASE.parents[1]/'tmp/observability_raw'
sys.path.insert(0,str(BASE.parent/'recovery_2026_11_04'))
from dataset import sheets

def sha(data):return hashlib.sha256(data).hexdigest()
def get(label):
    record=next(r for r in json.loads((BASE/'retrieval.json').read_text('utf8'))['records'] if r['label']==label)
    p=CACHE/record['cache']
    if not p.exists():
        CACHE.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen(record['url'],timeout=90) as r:p.write_bytes(r.read())
    data=p.read_bytes()
    # EuropePMC creates wrapper archives: pin individual members below, not ZIP timestamps.
    if not label.endswith('_supp') and sha(data)!=record['sha256']:raise ValueError('source changed '+label)
    return data

def inspect():
    z=zipfile.ZipFile(io.BytesIO(get('WASF3_numeric')))
    name='Primary data for WASF3 in CFS/Figure 1/Figure 1A.xlsx';data=z.read(name)
    p=CACHE/'WASF3_1A.xlsx';p.write_bytes(data);rows=sheets(p)['Sheet1']
    numeric=[(int(r['A']),r) for _,r in rows if r.get('A') and str(r['A']).isdigit()]
    assert [n for n,_ in numeric]==list(range(1,88))
    fits=[]
    for col in 'BCDEFG':
        y=np.array([float(r[col]) for n,r in numeric if 41<=n<=69])
        t=np.arange(1,len(y)+1)*7.5
        for free in [False,True]:
            model=lambda x:(x[2] if free else 1)-x[0]*np.exp(-t/x[1])
            f=least_squares(lambda x:model(x)-y,[.3,60,.98] if free else [.3,60],bounds=([0,1,.5],[1,600,1.5]) if free else ([0,1],[1,600]))
            err=model(f.x)-y
            fits.append(dict(series_column=col,participant='S2' if col in 'BC' else 'S1',visit=2 if col in 'FG' else 1,free_asymptote=free,
                tau_s=float(f.x[1]),asymptote=float(f.x[2]) if free else 1.,MAE_relative=float(np.mean(abs(err))),RMSE_relative=float(np.sqrt(np.mean(err**2))),bias_relative=float(np.mean(err)),n=len(y)))
    wasf=dict(doi='10.25444/nhlbi.23681013.v1',member=name,member_sha256=sha(data),participants=2,scans=6,rows_per_curve=87,numeric_PCr_cells=522,
        units='PCr/pre-exercise PCr; dimensionless, not absolute chemical reserve',sample_s=7.5,
        protocol='methods: 180s rest,120s foot exercise at30% maximum lifted weight,360s recovery; second scan after25min; S1 visit repeated months later',
        timing_caveat='source index1..87 only; methods duration predicts88 samples. Exploratory recovery mapping index41 onset+7.5s assumed; 29points index41..69 end217.5s, article describes3.75min. No synchronization to human VO2/power.',
        fits=fits,interpretation='exploratory in-sample relative PCr kinetics only; asymptote dependence; no independent test, no physiological D2 fitting; fibroblast OCR is not human pulmonary VO2')
    z=zipfile.ZipFile(io.BytesIO(get('plantar_supp')));inner=z.read('Data_Sheet_1.ZIP');a=zipfile.ZipFile(io.BytesIO(inner))
    mats={};arrays={}
    for n in a.namelist():
        if n.startswith('__') or not n.endswith('.mat'):continue
        data=a.read(n)
        with h5py.File(io.BytesIO(data)) as f:
            variables={}
            def read(k,v):
                if isinstance(v,h5py.Dataset) and v.dtype.kind in 'fiu' and v.size>10:
                    arr=v[()];variables[k]=dict(shape=list(arr.shape),finite=bool(np.isfinite(arr).all()))
                    arrays[k]=arr.ravel()
                if isinstance(v,h5py.Dataset) and v.dtype==np.uint16:
                    variables[k]=dict(text=''.join(chr(int(x)) for x in v[()].ravel()))
            f.visititems(read)
        mats[Path(n).name]=dict(sha256=sha(data),variables=variables)
    # MATLAB table object stores named PCr/time vectors through HDF5 references.
    time=arrays['#refs#/d'];pcr=arrays['#refs#/f']
    assert len(time)==len(pcr)==144 and np.all(np.diff(time)>0)
    dt=np.diff(time)
    plantar=dict(doi='10.3389/fbioe.2020.00622',inner_sha256=sha(inner),participants=1,files=mats,
        time_points=144,time_range_s=[float(time[0]),float(time[-1])],sample_interval_range_s=[float(dt.min()),float(dt.max())],
        PCr_units='mmol/l calibrated using assumed resting ATP8.2mmol/l; not independently absolute',
        stored_labels=['time_s','paradigm1','PCr_mmol_l','Pi_mmol_l','ATP_mmol_l','pH'],
        metadata_verification='HDF character arrays and table references read; paradigm1 is protocol indicator, not measured power',
        paradigm_values=np.unique(arrays['#refs#/e']).tolist(),
        kinematics_time_s=[float(arrays['time'][0]),float(arrays['time'][-1])],kinematics_samples=len(arrays['time']),
        manuscript='one subject; separate MRI,EMG andMRS experiments; prescribed20%MVC; MRS nominal5s,180s load and1500s recovery described; released time subset ends600.26s',
        limitations='No continuous VO2. Energy_exp11points is PCr-derived J/kg with assumed enthalpy21kJ/mol and cell-water conversion. Not independent cost anchor. Separate EMG acquisition; no synchronized absolute jointpower in obtained MATs.')
    z=zipfile.ZipFile(io.BytesIO(get('peerj_supp')));data=z.read('peerj-04-2259-s003.xls');book=xlrd.open_workbook(file_contents=data);s=book.sheet_by_index(0)
    ids={s.cell_value(i,0) for i in range(s.nrows) if re.fullmatch(r'CW\d+-2',str(s.cell_value(i,0)))}
    peerj=dict(doi='10.7717/peerj.2259',member='peerj-04-2259-s003.xls',member_sha256=sha(data),participants=len(ids),sheet_rows=s.nrows,sheet_columns=s.ncols,
        format='BIFF XLS; mixed raw, repeated sex-group summaries, formulas and figures. 17 unique participant labels, not34 independent people.',
        protocol='25%MVC knee extension every5s for300s;6exercise and6recovery MRS blocks of50s;300s recovery',
        units='signal amplitudes, ratios, pH, model-calculated mmol/kg and kPCr; not independently calibrated total reserve J',
        limitations='No VO2, no calibrated continuous mechanical W series; coarse50s windows cannot resolve6s effort/recovery; load kg and WE ratio are not watt time series. Participant-name column exists; raw stays ignored.')
    z=zipfile.ZipFile(io.BytesIO(get('diagnostics_supp')));data=z.read('diagnostics-16-00744-s001.zip');inner=zipfile.ZipFile(io.BytesIO(data))
    diagnostics=dict(doi='10.3390/diagnostics16050744',inner_sha256=sha(data),members=inner.namelist(),numeric_time_series_obtained=False,
                     scope='supplement contains only PDF, not numeric time series; n5, nominal2s MRS from methods; raw on request')
    return dict(WASF3=wasf,plantar=plantar,peerj=peerj,diagnostics=diagnostics,external_validation=False)

if __name__=='__main__':
    x=inspect();target=BASE/'data_inventory.json'
    if '--check' in sys.argv:
        from audit import equivalent
        assert equivalent(x,json.loads(target.read_text('utf8')))
        print('PASS pinned numeric members, content inventory and exploratory PCr replay')
    else:
        target.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        print('Saved numeric inventory; no new independent validation')
