"""EXP-0120: conditional alternate velocity sensitivity for repeated jump power."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from scipy.integrate import cumulative_trapezoid
from run_audit import text_sha256
H=Path(__file__).resolve().parent;d=Path(sys.argv[1]);manifest=json.loads((H/'LCMJ_SOURCE_MANIFEST.json').read_text(encoding='utf8'));prior=json.loads((H/'LCMJ_SOURCE_GATE_RESULTS.json').read_text(encoding='utf8'));g=9.81;records=[];excluded=0
for f in manifest:
 p=d/f['local_name'];b=p.read_bytes();assert hashlib.md5(b).hexdigest()==f['md5_publisher'] and hashlib.sha256(b).hexdigest()==f['sha256_bytes'];it=iter(load_workbook(p,read_only=True,data_only=True)['Sheet1'].values);head=[next(it) for _ in range(11)];assert head[0][0]=='Weight' and head[1][0]=='Frequency' and tuple(head[10][:3])==('Time','Net force (N)','Net power (W)');freq=float(head[1][1]);z=np.array([r[:3] for r in it if r[0] is not None],float);assert freq>0 and np.isfinite(z).all() and np.all(np.diff(z[:,0])>0);t=z[:,0];force=z[:,1];q=force[t<t[0]+.5];assert len(q)>2 and q.mean()>0;mass=float(q.mean()/g);offset=round(.1*freq);assert abs(offset/freq-.1)<1e-9;events=[];start=0
 while start<len(force)-offset:
  hit=np.flatnonzero((force[start:-offset]<50)&(force[start+offset:]<50))
  if not len(hit):break
  a=start+int(hit[0]);hit=np.flatnonzero((force[a:-offset]>50)&(force[a+offset:]>50))
  if not len(hit):break
  b=a+int(hit[0]);assert b>a and (not events or a>events[-1][1]);events.append((a,b));start=b
 if len(events)!=20:excluded+=1;continue
 auth=[];alt=[];valid=True
 for i in range(18):
  landing=events[i][1];takeoff=events[i+1][0];nextlanding=events[i+1][1];flight=t[nextlanding]-t[takeoff]
  if not (.1<=flight<=1. and takeoff>landing and np.all(force[takeoff:nextlanding]<50)):valid=False;break
  sl=slice(landing,takeoff+1);a=force[sl]/mass-g;integ=cumulative_trapezoid(a,t[sl],initial=0);v=g*flight/2-(integ[-1]-integ);x=float(np.max(force[landing:takeoff]*v[:-1]));y=float(np.max(z[landing:takeoff,2]));
  if x<=0 or y<=0:valid=False;break
  alt.append(x);auth.append(y)
 if not valid:excluded+=1;continue
 a=np.array(auth);b=np.array(alt);ae=float(a[:4].mean());al=float(a[14:18].mean());be=float(b[:4].mean());bl=float(b[14:18].mean());records.append([ae,al,100*(al/ae-1),be,bl,100*(bl/be-1)])
assert len(records)==11 and excluded==0;A=np.array(records);p=prior['descriptive'];assert abs(A[:,0].mean()-p['mean_early_power_W'])<1e-6 and abs(A[:,1].mean()-p['mean_late_power_W'])<1e-6 and abs(A[:,2].mean()-p['mean_paired_change_percent'])<1e-6
idx=np.random.default_rng(20261120).integers(0,11,(10000,11));delta=A[:,5]-A[:,2]
def ci(x):return np.quantile(x[idx].mean(axis=1),[.025,.975]).tolist()
r={'experiment_id':'EXP-0120','classification':'POST_HOC_CONDITIONAL_ALTERNATIVE_NOT_VALIDATION','manifest_sha256_lf':text_sha256(H/'LCMJ_SOURCE_MANIFEST.json'),'prior_result_sha256_lf':text_sha256(H/'LCMJ_SOURCE_GATE_RESULTS.json'),'protocol_sha256_lf':text_sha256(H/'LCMJ_POWER_SENSITIVITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'participants':len(A),'excluded_files':excluded,'published_power_early_mean_W':float(A[:,0].mean()),'published_power_late_mean_W':float(A[:,1].mean()),'published_mean_change_percent':float(A[:,2].mean()),'conditional_proxy_early_mean_W':float(A[:,3].mean()),'conditional_proxy_late_mean_W':float(A[:,4].mean()),'conditional_mean_change_percent':float(A[:,5].mean()),'conditional_mean_change_bootstrap_95':ci(A[:,5]),'paired_alternative_minus_published_pp':float(delta.mean()),'paired_bootstrap_95_pp':ci(delta),'individual_difference_range_pp':[float(delta.min()),float(delta.max())],'limits':['same previously viewed data and post-hoc method','estimated system mass and equal height ballistic constraint are assumptions','unknown Smith guide forces and independent kinematics','force times reconstructed velocity is not validated human mechanical power or work','no FORCE20 or CPE45 assessment']};(H/'LCMJ_POWER_SENSITIVITY_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
