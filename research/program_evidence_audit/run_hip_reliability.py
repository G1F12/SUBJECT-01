"""EXP-0112: hip force test-retest contrasts in a partly previewed cohort."""
import hashlib,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);b=p.read_bytes();sha=hashlib.sha256(b).hexdigest();md5=hashlib.md5(b).hexdigest();assert sha=='d699188590e249a992d8290eee02edf5864c7b47a017f0857b66d88c1cde77b2' and md5=='ae0e9cbcb5a6de5ea2a176bb54a25f67'
w=load_workbook(p,read_only=True,data_only=True);s=w['Sheet1'];raw=list(s.values);assert tuple(raw[0][:8])==('id','anon','day','protocol','system','leg','rep','peakforce');data={}
for row in raw[1:]:
 id,anon,day,protocol,system,leg,rep,force=row[:8];k=(id,day,protocol,system,leg,rep);assert k not in data and isinstance(force,(int,float)) and np.isfinite(force) and force>0;data[k]=float(force)
ids=sorted({k[0] for k in data});assert len(ids)==25 and len(data)==1200
mean={}
for id in ids:
 for day in (1,2):
  for protocol in ('hf','he'):
   for system in ('ff','hhd'):
    for leg in ('l','r'):
     mean[(id,day,protocol,system,leg)]=np.mean([data[(id,day,protocol,system,leg,r)] for r in (1,2,3)])
validation=[np.mean([mean[(i,d,'he','ff',l)]-mean[(i,d,'he','hhd',l)] for i in ids]) for d in (1,2) for l in ('l','r')];assert min(validation)>=27.04 and max(validation)<=46.38
idx=np.random.default_rng(20261120).integers(0,25,(10000,25));out={};agreement={}
for protocol in ('hf','he'):
 for system in ('ff','hhd'):
  for leg in ('l','r'):
   x=np.array([mean[(i,1,protocol,system,leg)] for i in ids]);y=np.array([mean[(i,2,protocol,system,leg)] for i in ids]);delta=100*(y/x-1);out[f'{protocol}_{system}_{leg}']={'n':len(x),'day1_mean_N':float(x.mean()),'day2_mean_N':float(y.mean()),'mean_change_percent':float(delta.mean()),'median_change_percent':float(np.median(delta)),'central_95_percentiles':np.quantile(delta,[.025,.975]).tolist(),'mean_change_bootstrap_95':np.quantile(delta[idx].mean(axis=1),[.025,.975]).tolist(),'increase_ge_20_percent':int((delta>=20).sum()),'decrease_le_minus_20_percent':int((delta<=-20).sum())}
 for leg in ('l','r'):
  d=np.array([mean[(i,1,protocol,'ff',leg)]-mean[(i,1,protocol,'hhd',leg)] for i in ids]);agreement[f'{protocol}_{leg}']={'bias_ff_minus_hhd_N':float(d.mean()),'limits_mean_plus_minus_1_96_sd_N':[float(d.mean()-1.96*d.std(ddof=1)),float(d.mean()+1.96*d.std(ddof=1))]}
r={'experiment_id':'EXP-0112','classification':'PARTIALLY_PREVIEWED_INDEPENDENT_RETEST_COHORT','source_sha256_bytes':sha,'source_md5_bytes':md5,'protocol_sha256_lf':text_sha256(H/'HIP_RELIABILITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'participants':25,'records':len(data),'source_gate_extension_bias_day_leg_N':list(map(float,validation)),'strata':out,'day1_device_agreement':agreement,'limits':['article and first 3 data rows viewed before protocol','25 recreational cyclists 22 men; single-joint isometric hip task','day-to-day changes include learning and real variation','not a false positive rate or direct calibration for leg press FORCE20','device flexion positions differ','no work heat motor control recovery or CPE45']};(H/'HIP_RELIABILITY_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
