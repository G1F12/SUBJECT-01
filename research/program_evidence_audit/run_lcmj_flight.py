"""EXP-0118: conditional ballistic consistency of archived jump velocities."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from scipy.signal import butter,detrend,lfilter
from scipy.integrate import cumulative_trapezoid
from run_audit import text_sha256
H=Path(__file__).resolve().parent;d=Path(sys.argv[1]);manifest=json.loads((H/'LCMJ_SOURCE_MANIFEST.json').read_text(encoding='utf8'));assert len(manifest)==11
g=9.81;people=[];all_durations=[];total=0;excluded=0;failed=0;power_max=0.;power_mae=0.
for f in manifest:
 b=(d/f['local_name']).read_bytes();assert hashlib.md5(b).hexdigest()==f['md5_publisher'] and hashlib.sha256(b).hexdigest()==f['sha256_bytes'];s=load_workbook(d/f['local_name'],read_only=True,data_only=True)['Sheet1'];it=iter(s.values);head=[next(it) for _ in range(11)];assert head[0][0]=='Weight' and head[1][0]=='Frequency' and tuple(head[10][:3])==('Time','Net force (N)','Net power (W)');mass=float(head[0][1]);freq=float(head[1][1]);z=np.array([r[:3] for r in it if r[0] is not None],float);assert mass>0 and freq>0 and np.isfinite(z).all() and np.all(np.diff(z[:,0])>0);B,A=butter(2,2*.25/freq,btype='high');acc=lfilter(B,A,detrend(z[:,1]/mass,type='linear'));velocity=cumulative_trapezoid(acc,z[:,0],initial=0);err=np.abs(z[:,1]*velocity-z[:,2]);power_max=max(power_max,float(err.max()));power_mae=max(power_mae,float(err.mean()))
 if err.mean()>1 or err.max()>10:failed+=1;continue
 force=z[:,1];off=round(.1*freq);assert abs(off/freq-.1)<1e-9;events=[];start=0
 while start<len(force)-off:
  hits=np.flatnonzero((force[start:-off]<50)&(force[start+off:]<50))
  if not len(hits):break
  take=start+int(hits[0]);hits=np.flatnonzero((force[take:-off]>50)&(force[take+off:]>50))
  if not len(hits):break
  land=take+int(hits[0]);assert land>take and (not events or take>events[-1][1]);events.append((take,land));start=land
 if len(events)!=20:failed+=1;continue
 diffs=[];newton=[]
 for t,l in events:
  duration=float(z[l,0]-z[t,0]);total+=1
  if not (.1<=duration<=1. and np.all(force[t:l]<50)):excluded+=1;continue
  vchange=float(velocity[l]-velocity[t]);ideal=-g*duration;estimate=float(np.trapezoid(force[t:l+1]/mass-g,z[t:l+1,0]));diffs.append(abs(vchange-ideal));newton.append(abs(vchange-estimate));all_durations.append(duration)
 if diffs:people.append({'n':len(diffs),'free_mean':float(np.mean(diffs)),'free_max':float(max(diffs)),'newton_mean':float(np.mean(newton)),'newton_max':float(max(newton))})
assert people
x=np.array([v['free_mean'] for v in people]);idx=np.random.default_rng(20261120).integers(0,len(x),(10000,len(x)));out={'experiment_id':'EXP-0118','classification':'POST_HOC_CONDITIONAL_FLIGHT_PHYSICS','manifest_sha256_lf':text_sha256(H/'LCMJ_SOURCE_MANIFEST.json'),'protocol_sha256_lf':text_sha256(H/'LCMJ_FLIGHT_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'files':len(manifest),'files_failing_power_or_event_gate':failed,'persons_with_eligible_flights':len(people),'flight_candidates':total,'flight_excluded':excluded,'eligible_flights':sum(v['n'] for v in people),'duration_range_s':[min(all_durations),max(all_durations)],'max_power_reconstruction_mae_W':power_mae,'max_power_reconstruction_abs_error_W':power_max,'mean_person_abs_deviation_freefall_m_s':float(x.mean()),'bootstrap_95_person_mean_m_s':np.quantile(x[idx].mean(axis=1),[.025,.975]).tolist(),'persons_mean_abs_error_above_0_1_m_s':int((x>.1).sum()),'max_single_flight_abs_deviation_m_s':max(v['free_max'] for v in people),'mean_person_abs_deviation_newton_proxy_m_s':float(np.mean([v['newton_mean'] for v in people])),'max_single_newton_proxy_deviation_m_s':max(v['newton_max'] for v in people),'limits':['conditional freefall and Newton proxy, Smith machine rail forces unmeasured','Weight field may differ from total moving mass','velocities reconstructed from author algorithm, not independent kinematics','previously viewed files and source code','no physical power/work validation or CPE45 inference']};(H/'LCMJ_FLIGHT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out,indent=2))
