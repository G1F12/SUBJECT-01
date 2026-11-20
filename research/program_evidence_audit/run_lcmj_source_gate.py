"""EXP-0114: prespecified LCMJ power-series source admission gate."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;d=Path(sys.argv[1]);manifest=json.loads((H/'LCMJ_SOURCE_MANIFEST.json').read_text(encoding='utf8'));assert len(manifest)==11;summary=[];valid=[];issues=[]
for f in manifest:
 p=d/f['local_name'];b=p.read_bytes();assert hashlib.md5(b).hexdigest()==f['md5_publisher'] and hashlib.sha256(b).hexdigest()==f['sha256_bytes'];s=load_workbook(p,read_only=True,data_only=True)['Sheet1'];it=iter(s.values);head=[next(it) for _ in range(11)];assert head[0][0]=='Weight' and head[1][0]=='Frequency' and head[7][0]=='Ave max prop power (W)' and tuple(head[10][:3])==('Time','Net force (N)','Net power (W)');freq=float(head[1][1]);ref=float(head[7][1]);a=np.array([r[:3] for r in it if r[0] is not None],dtype=float);assert freq>0 and ref>0 and len(a)>0 and np.isfinite(a).all() and np.all(np.diff(a[:,0])>0);force=a[:,1];power=a[:,2];offset=round(.1*freq);assert abs(offset/freq-.1)<1e-9;events=[];start=0
 while start<len(force)-offset:
  hits=np.flatnonzero((force[start:-offset]<50)&(force[start+offset:]<50))
  if not len(hits):break
  take=start+int(hits[0]);hits=np.flatnonzero((force[take:-offset]>50)&(force[take+offset:]>50))
  if not len(hits):break
  land=take+int(hits[0]);assert land>take and (not events or take>events[-1][1]);events.append((take,land));start=land
 maxima=[float(np.max(power[events[i][1]:events[i+1][0]])) for i in range(len(events)-1) if events[i+1][0]>events[i][1]];discrepancy=abs(np.mean(maxima)/ref-1)*100 if len(maxima)==19 else None;ok=len(events)==20 and len(maxima)==19 and all(v>0 for v in maxima) and discrepancy is not None and discrepancy<=2;summary.append({'flights':len(events),'intervals':len(maxima),'source_summary_deviation_percent':float(discrepancy) if discrepancy is not None else None,'gate_pass':ok});
 if ok:valid.append(maxima)
 if not ok:issues.append('event_count_or_summary_mismatch')
result={'experiment_id':'EXP-0114','classification':'SOURCE_GATE_ONLY' if issues else 'SOURCE_GATE_PASSED_EXPLORATORY','protocol_sha256_lf':text_sha256(H/'LCMJ_SOURCE_GATE_PROTOCOL.md'),'manifest_sha256_lf':text_sha256(H/'LCMJ_SOURCE_MANIFEST.json'),'runner_sha256_lf':text_sha256(Path(__file__)),'source_files':11,'pass_count':len(valid),'flight_count_distribution':{str(n):sum(x['flights']==n for x in summary) for n in sorted({x['flights'] for x in summary})},'summary_discrepancy_percent_range':[min(x['source_summary_deviation_percent'] for x in summary if x['source_summary_deviation_percent'] is not None),max(x['source_summary_deviation_percent'] for x in summary if x['source_summary_deviation_percent'] is not None)] if any(x['source_summary_deviation_percent'] is not None for x in summary) else None,'limits':['source article, code and first row of one workbook previewed','published workbook power is derived; processing and filter mismatch unresolved','no independent force power or whole architecture validation']}
if not issues:
 a=np.array(valid);early=a[:,0:4].mean(axis=1);late=a[:,14:18].mean(axis=1);delta=(late/early-1)*100;idx=np.random.default_rng(20261120).integers(0,11,(10000,11));result['descriptive']={'mean_early_power_W':float(early.mean()),'mean_late_power_W':float(late.mean()),'mean_paired_change_percent':float(delta.mean()),'paired_bootstrap_95_percent':np.quantile(delta[idx].mean(axis=1),[.025,.975]).tolist(),'persistence_mean_absolute_error_W':float(np.mean(np.abs(late-early)))}
(H/'LCMJ_SOURCE_GATE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
