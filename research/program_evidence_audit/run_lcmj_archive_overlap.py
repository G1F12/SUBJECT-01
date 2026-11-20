"""EXP-0117: source-matched repeated-jump recordings across two archives."""
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from scipy.signal import butter,detrend,lfilter
from scipy.integrate import cumulative_trapezoid
from run_audit import text_sha256
H=Path(__file__).resolve().parent;rawdir=Path(sys.argv[1]);procdir=Path(sys.argv[2]);rm=json.loads((H/'LCMJ_RAW_MANIFEST.json').read_text(encoding='utf8'));pm=json.loads((H/'LCMJ_SOURCE_MANIFEST.json').read_text(encoding='utf8'));assert len(rm)==10 and len(pm)==11
raw=[];processed=[]
for f in rm:
 b=(rawdir/f['local_name']).read_bytes();assert hashlib.md5(b).hexdigest()==f['md5_publisher'] and hashlib.sha256(b).hexdigest()==f['sha256_bytes'];rows=list(csv.reader(b.decode('utf-8-sig').splitlines()));assert rows[0]==['Time','Left','Right'];a=np.array(rows[1:],float);assert a.ndim==2 and a.shape[1]==3 and np.isfinite(a).all() and np.all(np.diff(a[:,0])>0);raw.append(a)
for f in pm:
 p=procdir/f['local_name'];b=p.read_bytes();assert hashlib.md5(b).hexdigest()==f['md5_publisher'] and hashlib.sha256(b).hexdigest()==f['sha256_bytes'];s=load_workbook(p,read_only=True,data_only=True)['Sheet1'];it=iter(s.values);head=[next(it) for _ in range(11)];assert head[0][0]=='Weight' and head[1][0]=='Frequency' and tuple(head[10][:3])==('Time','Net force (N)','Net power (W)');mass=float(head[0][1]);freq=float(head[1][1]);z=np.array([r[:3] for r in it if r[0] is not None],float);assert mass>0 and freq>0 and len(z)>=1000 and np.isfinite(z).all() and np.all(np.diff(z[:,0])>0);processed.append((z,mass,freq))
def match(a,z):
 pos=np.searchsorted(a[:,0],z[:,0]);
 if np.any(pos>=len(a)):return None
 left=np.maximum(pos-1,0);pos=np.where(np.abs(a[left,0]-z[:,0])<np.abs(a[pos,0]-z[:,0]),left,pos)
 if len(np.unique(pos))!=len(pos) or np.max(np.abs(a[pos,0]-z[:,0]))>1e-6:return None
 df=a[pos,1]+a[pos,2]-z[:,1]
 if np.max(np.abs(df))>.01:return None
 return float(np.max(np.abs(df)))
pairs=[]
for i,(z,mass,freq) in enumerate(processed):
 sample=z[np.linspace(0,len(z)-1,101,dtype=int)]
 for k,a in enumerate(raw):
  if match(a,sample) is not None:
   err=match(a,z)
   if err is not None:pairs.append((i,k,err))
counts_p={i:sum(x[0]==i for x in pairs) for i in range(len(processed))};counts_r={k:sum(x[1]==k for x in pairs) for k in range(len(raw))};unique=[(i,k,e) for i,k,e in pairs if counts_p[i]==1 and counts_r[k]==1];ambiguous=[(i,k,e) for i,k,e in pairs if counts_p[i]!=1 or counts_r[k]!=1];errs={'.25':[],'2.5':[]};export_500=0;maximum_force=0.
for i,k,e in unique:
 z,mass,freq=processed[i];export_500+=bool(abs(freq-500)<1e-9 and abs(1/np.median(np.diff(z[:,0]))-500)<.01);maximum_force=max(maximum_force,e);acc=detrend(z[:,1]/mass,type='linear')
 for cutoff,key in ((.25,'.25'),(2.5,'2.5')):
  B,A=butter(2,2*cutoff/freq,btype='high');v=cumulative_trapezoid(lfilter(B,A,acc),z[:,0],initial=0);diff=z[:,1]*v-z[:,2];mae=float(np.mean(np.abs(diff)));m=float(np.max(np.abs(diff)));errs[key].append({'mae':mae,'max':m,'pass':mae<=1 and m<=10})
summary={}
for key,e in errs.items():
 summary[key]={'passes':sum(x['pass'] for x in e),'mae_range_W':[min(x['mae'] for x in e),max(x['mae'] for x in e)] if e else None,'max_abs_error_range_W':[min(x['max'] for x in e),max(x['max'] for x in e)] if e else None}
out={'experiment_id':'EXP-0117','classification':'POST_VIEW_ARCHIVE_OVERLAP_AUDIT','raw_manifest_sha256_lf':text_sha256(H/'LCMJ_RAW_MANIFEST.json'),'processed_manifest_sha256_lf':text_sha256(H/'LCMJ_SOURCE_MANIFEST.json'),'protocol_sha256_lf':text_sha256(H/'LCMJ_ARCHIVE_OVERLAP_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'raw_files':len(raw),'processed_files':len(processed),'unique_matched_pairs':len(unique),'ambiguous_candidate_pairs':len(ambiguous),'raw_without_match':sum(v==0 for v in counts_r.values()),'processed_without_match':sum(v==0 for v in counts_p.values()),'matched_export_500Hz':export_500,'max_force_difference_N':maximum_force,'filter_reconstruction':summary,'limits':['one pair known before protocol; no independent validation','signal matches do not establish identity, all session mappings or physical accuracy','acquisition versus export frequency unresolved','load mass and velocity processing not independently verified','no work, CPE45 or whole-architecture assessment']}
(H/'LCMJ_ARCHIVE_OVERLAP_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out,indent=2))
