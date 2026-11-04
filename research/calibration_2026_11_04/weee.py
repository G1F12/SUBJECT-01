"""Separate exploratory oxygen-only cohort; no fusion into CPET individuals."""
import csv,json,datetime
import numpy as np
from acquire import BASE,CACHE,save,digest

def build():
    prov=json.loads((BASE/'weee_retrieval.json').read_text('utf8'))
    for f in prov['files']:
        assert digest((CACHE/f['cache']).read_bytes())==f['sha256']
    study=next(CACHE.glob('WEEE_*Study*'));protocol=list(csv.DictReader(study.open(encoding='utf-8-sig')));out=[]
    names=['Sit','Stand','Cycle1','Cycle2','Run1','Run2']
    for meta in protocol:
        sid=meta['Participant'];file=CACHE/f'WEEE_{sid}_DataAverage.csv'
        rows=[]
        for r in csv.DictReader(file.open(encoding='utf-8-sig')):
            try:
                t=datetime.datetime.fromisoformat(r['Time']);v=float(r['VO2[mL/min]'])/1000
                if v>0 and np.isfinite(v):rows.append((t,v))
            except (ValueError,KeyError):continue
        for i,phase in enumerate(names):
            try:
                start=datetime.datetime.fromisoformat(meta['Start_'+phase]);end=datetime.datetime.fromisoformat(meta['Start_'+names[i+1]]) if i<5 else max(t for t,v in rows)
            except (ValueError,KeyError):continue
            use=[v for t,v in rows if end-datetime.timedelta(seconds=60)<t<=end and t>=start]
            eligible=len(use)>=48
            value=float(np.mean(use)) if use else None
            out.append(dict(cohort='WEEE',participant=sid,phase=phase,valid_samples_last60=len(use),eligible=eligible,vo2_L_min=value,
                conditional_cost_W_RER07_to1=[value*(3.9+1.1*q)*4184/60 for q in [.7,1.]] if value else None,
                VCO2='NOT OBSERVED',mechanical_power_W='NOT OBSERVED; speedkmh is not W',PCr='NOT OBSERVED',
                units='absolute pulmonaryL/min; derivedfuelW boundedonlyunderassumedRERrange; noindividualCPETfusion'))
    result=dict(origin='REAL independent oxygen-only cohort',participants=len(protocol),rows=out,
        state='oxygen baseline measured, energy only conditionallybounded; noefficiencyidentification',
        data_license=prov['license'],doi=prov['doi'],source_hashes=[dict(member=f['member'],sha256=f['sha256']) for f in prov['files']])
    save(BASE/'weee_oxygen_summary.json',result)
    print('WEEE',len(protocol),'participants',sum(r['eligible'] for r in out),'eligiblephasewindows; noVCO2/noW')

if __name__=='__main__':build()
