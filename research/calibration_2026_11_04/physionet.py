"""Finite public CPET content probe; exploratory participant, never a holdout."""
import csv,io,json,statistics
from acquire import BASE,CACHE,fetch,save,digest

def probe():
    records=json.loads((BASE/'physionet_probe.json').read_text('utf8'))
    for r in records:
        p=CACHE/r['cache']
        if not p.exists():
            got=fetch(r['label'],r['url']);assert got.get('sha256')==r['sha256']
        assert digest(p.read_bytes())==r['sha256']
    sums=(CACHE/'but_checksums.bin').read_text('utf8')
    for r in records[2:]:
        name=r['url'].split('/1.0.0/')[1]
        assert any(r['sha256'] in line and name in line for line in sums.splitlines())
    rows=list(csv.DictReader(io.StringIO((CACHE/'but_101_cpet.bin').read_text('utf-8-sig')),delimiter=';'))
    def sec(r):
        a,b=r['t'].split(':');return float(a)*60+float(b)
    ts=[sec(r) for r in rows];phases={}
    for phase in sorted({r['Phase'] for r in rows}):
        rr=[r for r in rows if r['Phase']==phase]
        phases[phase]=dict(rows=len(rr),first_s=sec(rr[0]),last_s=sec(rr[-1]),
            recorded_WR_W_range=[min(float(r['WR']) for r in rr),max(float(r['WR']) for r in rr)],
            VO2_L_min_range=[min(float(r['VO2']) for r in rr),max(float(r['VO2']) for r in rr)])
    result=dict(doi='10.13026/hv8f-3w60',version='1.0.0',license='CC BY 4.0',
        numeric_participants_obtained=1,participant='BUT-CGM-101',source_population=60,
        source_records=65,warning='154/155 repeated records share CPET; not independent people',
        rows=len(rows),median_interval_s=statistics.median(b-a for a,b in zip(ts,ts[1:])),phases=phases,
        units_from_actual_summary=dict(VO2='L/min',VCO2='L/min',WR='W',EE='kcal/h'),
        missing=['PCr','active muscle volume','local ATP flux','independent efficiency'],
        rights='public CC BY4 license file obtained; raw ignored, only content summary redistributed',
        interpretation='WarmUp/Test/CoolDown recorded. CoolDown WR is active workload, not zero-cost passive rest. EE is gas-derived, not an independent calorimeter.',
        validation='NOT DONE; exploratory opened participant, no parameter fitting or model comparison')
    save(BASE/'physionet_summary.json',result);return result

if __name__=='__main__':print(json.dumps(probe(),indent=2))
