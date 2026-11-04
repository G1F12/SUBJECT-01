"""Offline replay of real-data snapshots and fixed locked test, never retuning it."""
from pathlib import Path
import json,math,hashlib,tempfile,io,contextlib
from unittest.mock import patch
from acquire import BASE
import models,analysis

def equal(a,b,rtol=2e-6,atol=2e-5):
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal(a[k],b[k],rtol,atol) for k in a)
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(equal(x,y,rtol,atol) for x,y in zip(a,b))
    if isinstance(a,(int,float)) and not isinstance(a,bool):return isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=rtol,abs_tol=atol)
    return a==b

def differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        return sum((differences(a[k],b[k],path+'/'+str(k)) for k in a if k in b),[])
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return sum((differences(x,y,path+'/'+str(k)) for k,(x,y) in enumerate(zip(a,b))),[])
    return [] if equal(a,b,1e-3,1e-3) else [dict(path=path,replayed=a,archived=b)]

def check():
    m=json.loads((BASE/'manifest.json').read_text('utf8'))
    for r,h in m.items():assert hashlib.sha256((BASE/r).read_bytes()).hexdigest()==h,r
    lock=models.load_lock();assert equal(models.fit(models.rows()),lock['parameters'])
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)
        with contextlib.redirect_stdout(io.StringIO()),patch.object(models,'save',lambda path,x: __import__('acquire').save(out/path.name,x)):
            models.evaluate()  # fixed archivedlock; numericalreplay is not a secondindependenttest
        analysis.generate(out)
        for p in out.glob('*.json'):
            a=json.loads(p.read_text('utf8'));b=json.loads((BASE/'results'/p.name).read_text('utf8'))
            # Pulmonarycurvefit precision is .001s/.001modelunits, below native1sclock;
            # physical identities, metrics and locks retain tighter default tolerance.
            ok=equal(a,b,1e-3,1e-3) if p.name=='parameter_identification.json' else equal(a,b)
            if not ok:print(json.dumps(differences(a,b)[:30],indent=2),flush=True)
            assert ok,p.name
    print('PASS cycle6 source/output hashes, code/developmentlock, realdata identification and fixedtest replay; CPE45 NOT VALIDATED')

if __name__=='__main__':check()
