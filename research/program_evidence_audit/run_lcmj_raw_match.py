"""EXP-0116: a single raw-to-derived force and filter provenance audit."""
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np
from scipy.signal import butter,detrend,lfilter
from scipy.integrate import cumulative_trapezoid
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;raw=Path(sys.argv[1]);processed=Path(sys.argv[2]);b=raw.read_bytes();rawsha=hashlib.sha256(b).hexdigest();md5=hashlib.md5(b).hexdigest();assert md5=='4f9ebe473da423d7cb19f897b00da01a' and rawsha=='9852f34119d58a2512e0801b1bb1461409292457c79d853fec3541303cc610d1';psha=hashlib.sha256(processed.read_bytes()).hexdigest();manifest=json.loads((H/'LCMJ_SOURCE_MANIFEST.json').read_text(encoding='utf8'));assert psha==manifest[0]['sha256_bytes']
rows=list(csv.reader(b.decode('utf-8-sig').splitlines()));assert rows[0]==['Time','Left','Right'];a=np.array(rows[1:],float);assert a.ndim==2 and a.shape[1]==3 and np.isfinite(a).all() and np.all(np.diff(a[:,0])>0)
s=load_workbook(processed,read_only=True,data_only=True)['Sheet1'];it=iter(s.values);head=[next(it) for _ in range(11)];assert head[0][0]=='Weight' and head[1][0]=='Frequency' and tuple(head[10][:3])==('Time','Net force (N)','Net power (W)');mass=float(head[0][1]);freq=float(head[1][1]);assert mass>0 and freq>0;z=np.array([r[:3] for r in it if r[0] is not None],float);assert np.isfinite(z).all() and np.all(np.diff(z[:,0])>0)
pos=np.searchsorted(a[:,0],z[:,0]);ok=(pos<len(a));assert ok.all();left=np.maximum(pos-1,0);pos=np.where(np.abs(a[left,0]-z[:,0])<np.abs(a[pos,0]-z[:,0]),left,pos);timediff=np.abs(a[pos,0]-z[:,0]);assert np.max(timediff)<=1e-6 and len(set(pos))==len(pos);diff=a[pos,1]+a[pos,2]-z[:,1];mae=float(np.abs(diff).mean());maxerr=float(np.abs(diff).max());matched=len(z)>=1000 and maxerr<=.01
out={'experiment_id':'EXP-0116','classification':'POST_VIEW_SINGLE_PAIR_PROVENANCE_AUDIT','raw_sha256_bytes':rawsha,'raw_md5_bytes':md5,'processed_sha256_bytes':psha,'source_manifest_sha256_lf':text_sha256(H/'LCMJ_SOURCE_MANIFEST.json'),'protocol_sha256_lf':text_sha256(H/'LCMJ_RAW_MATCH_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'xlsx_sampling_frequency_Hz':freq,'raw_median_sampling_frequency_Hz':float(1/np.median(np.diff(a[:,0]))),'processed_median_sampling_frequency_Hz':float(1/np.median(np.diff(z[:,0]))),'matched_samples':len(z),'max_time_difference_s':float(timediff.max()),'force_mae_N':mae,'force_max_error_N':maxerr,'force_gate_passed':matched,'filter_scenarios':{},'limits':['one pair; no inference about other participants or studies','author algorithm and first rows previewed; not blinded','match is internal provenance, not independent force or power validation','mass and bar load definition remain unverified','no mechanical work, CPE45 or architecture assessment']}
if matched:
 a0=detrend(z[:,1]/mass,type='linear')
 for cutoff in (.25,2.5):
  B,A=butter(2,2*cutoff/freq,btype='high');v=cumulative_trapezoid(lfilter(B,A,a0),z[:,0],initial=0);delta=z[:,1]*v-z[:,2];ab=np.abs(delta);out['filter_scenarios'][str(cutoff)]={'mae_W':float(ab.mean()),'rmse_W':float(np.sqrt(np.mean(delta**2))),'max_abs_error_W':float(ab.max()),'predefined_match':bool(ab.mean()<=1 and ab.max()<=10)}
(H/'LCMJ_RAW_MATCH_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out,indent=2))
