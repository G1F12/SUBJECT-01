"""EXP-0119: algebraic decomposition of conditional flight velocity differences."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from scipy.signal import butter,detrend,lfilter
from scipy.integrate import cumulative_trapezoid
from run_audit import text_sha256
H=Path(__file__).resolve().parent;d=Path(sys.argv[1]);manifest=json.loads((H/'LCMJ_SOURCE_MANIFEST.json').read_text(encoding='utf8'));prior=json.loads((H/'LCMJ_FLIGHT_RESULTS.json').read_text(encoding='utf8'));people=[];failed=0;excluded=0;maxclosure=0.;g=9.81
for f in manifest:
 p=d/f['local_name'];b=p.read_bytes();assert hashlib.md5(b).hexdigest()==f['md5_publisher'] and hashlib.sha256(b).hexdigest()==f['sha256_bytes'];it=iter(load_workbook(p,read_only=True,data_only=True)['Sheet1'].values);head=[next(it) for _ in range(11)];assert head[0][0]=='Weight' and head[1][0]=='Frequency' and tuple(head[10][:3])==('Time','Net force (N)','Net power (W)');m=float(head[0][1]);fs=float(head[1][1]);z=np.array([r[:3] for r in it if r[0] is not None],float);assert m>0 and fs>0 and np.isfinite(z).all() and np.all(np.diff(z[:,0])>0);t=z[:,0];force=z[:,1];n=force/m-g;de=detrend(force/m,type='linear');B,A=butter(2,2*.25/fs,btype='high');hi=lfilter(B,A,de);v=cumulative_trapezoid(hi,t,initial=0);err=np.abs(force*v-z[:,2]);
 if err.mean()>1 or err.max()>10:failed+=1;continue
 off=round(.1*fs);assert abs(off/fs-.1)<1e-9;events=[];start=0
 while start<len(force)-off:
  hits=np.flatnonzero((force[start:-off]<50)&(force[start+off:]<50))
  if not len(hits):break
  take=start+int(hits[0]);hits=np.flatnonzero((force[take:-off]>50)&(force[take+off:]>50))
  if not len(hits):break
  land=take+int(hits[0]);assert land>take and (not events or take>events[-1][1]);events.append((take,land));start=land
 if len(events)!=20:failed+=1;continue
 results=[];errors=[]
 for a,b in events:
  dt=t[b]-t[a]
  if not (.1<=dt<=1 and np.all(force[a:b]<50)):excluded+=1;continue
  sl=slice(a,b+1);dn=float(np.trapezoid(n[sl],t[sl]));dd=float(np.trapezoid(de[sl],t[sl]));dh=float(np.trapezoid(hi[sl],t[sl]));partd=dd-dn;parth=dh-dd;closure=partd+parth-(dh-dn);maxclosure=max(maxclosure,abs(closure));results.append([partd,parth,dh-dn]);errors.append(abs(dh-dn))
 if not results:continue
 q=force[t<t[0]+.5];assert len(q)>2 and q.mean()>0;people.append({'components':np.mean(results,axis=0),'abs_error':np.mean(errors),'quiet_ratio':float(q.mean()/(m*g)),'quiet_cv_percent':float(q.std(ddof=1)/q.mean()*100),'count':len(results)})
assert len(people)==11 and sum(p['count'] for p in people)==220 and failed==excluded==0 and maxclosure<1e-8
A=np.array([p['components'] for p in people]);idx=np.random.default_rng(20261120).integers(0,len(A),(10000,len(A)));stats={}
for j,k in enumerate(('detrend_minus_newton','filter_minus_detrend','filter_minus_newton')):stats[k]={'mean_signed_m_s':float(A[:,j].mean()),'person_bootstrap_95_m_s':np.quantile(A[idx,j].mean(axis=1),[.025,.975]).tolist()}
mean_abs=float(np.mean([p['abs_error'] for p in people]));assert abs(mean_abs-prior['mean_person_abs_deviation_newton_proxy_m_s'])<1e-9
ratio=[p['quiet_ratio'] for p in people];cv=[p['quiet_cv_percent'] for p in people];out={'experiment_id':'EXP-0119','classification':'POST_HOC_ALGEBRAIC_DECOMPOSITION','manifest_sha256_lf':text_sha256(H/'LCMJ_SOURCE_MANIFEST.json'),'prior_result_sha256_lf':text_sha256(H/'LCMJ_FLIGHT_RESULTS.json'),'protocol_sha256_lf':text_sha256(H/'LCMJ_FILTER_DECOMPOSITION_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'people':len(people),'accepted_flights':sum(p['count'] for p in people),'failed_files':failed,'excluded_flights':excluded,'signed_components':stats,'max_closure_error_m_s':maxclosure,'mean_absolute_difference_vs_newton_proxy_m_s':mean_abs,'initial_half_second_force_weight_ratio_range':[min(ratio),max(ratio)],'initial_half_second_cv_percent_range':[min(cv),max(cv)],'files_initial_cv_at_most_5_percent':sum(x<=5 for x in cv),'limits':['Newton reference is conditional on unknown total mass and guide forces','algorithmic components not causal physiological effects','first 0.5s stability does not prove mass or no guide support','previously viewed records; no independent motion data','no calibrated power work or CPE45 conclusion']};(H/'LCMJ_FILTER_DECOMPOSITION_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out,indent=2))
