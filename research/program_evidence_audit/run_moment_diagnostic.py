"""EXP-0083: compare source forces and sensitivity to applied moment components."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
import opensim as o
from run_audit import text_sha256
H=Path(__file__).resolve().parent; root=Path(sys.argv[1]).resolve(); reconstruction=Path(sys.argv[2]).resolve(); work=Path(sys.argv[3]).resolve(); work.mkdir(parents=True,exist_ok=True)
for name in ('MOMENT_SCALE_INPUTS.json','MOMENT_DIAGNOSTIC_INPUTS.json'):
 for r in json.loads((H/name).read_text(encoding='utf-8'))['files']:
  assert hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
o.Logger.setLevelString('error')
def read_storage(path):
 with path.open() as f:
  for i,line in enumerate(f):
   if line.strip()=='endheader':break
 return pd.read_csv(path,sep=r'\s+',skiprows=i+1)
def key(df):
 df=df.copy(); df['frame']=np.rint(df['time']*200).astype(int); assert df['frame'].is_unique; return df
prior=json.loads((H/'MOMENT_SCALE_RESULTS.json').read_text(encoding='utf-8')); prior_by_id={r['participant']:r for r in prior['results']}
results=[]
for person,mass in [('AB01',78.9),('AB02',82.2)]:
 raw=root/'raw'/person; proc=root/'files'/person/'squats_1_0lbs'; original=reconstruction/person; out=work/person; out.mkdir(parents=True,exist_ok=True)
 forces_path=raw/'ExtLoads'/'squats_1.mot'; forces=read_storage(forces_path)
 # Subset 1000 Hz series onto its exactly represented 200 Hz samples.
 q=forces[np.abs(forces.time*200-np.rint(forces.time*200))<1e-6].copy(); q=key(q)
 source=key(pd.read_csv(raw/'CSV_Data'/'squats_1'/'GroundFrame_GRFs.csv')); export=key(pd.read_csv(proc/f'{person}_squats_1_0lbs_grf.csv'))
 grf=export.merge(source,on='frame',suffixes=('_processed','_raw')).merge(q,on='frame')
 force_audit={}
 for side,letter in [('right','R'),('left','L')]:
  v=grf[f'{letter}ForceY_Vertical_processed'].to_numpy(); other=grf[f'{letter}ForceY_Vertical_raw'].to_numpy(); mot=grf[f'{letter.lower()}FP_vy'].to_numpy()
  ok=np.isfinite(v)&np.isfinite(other)&np.isfinite(mot); dif1=np.abs(v[ok]-other[ok]); dif2=np.abs(v[ok]-mot[ok]); force_audit[side]={'matched_frames':int(ok.sum()),'processed_frames':len(export),'processed_vs_raw_mae_N':float(dif1.mean()),'processed_vs_mot_mae_N':float(dif2.mean()),'processed_vs_mot_max_N':float(dif2.max())}
 # Diagnostic interpretation B: remove nonvertical applied torques only.
 for side in ('r','l'):
  for axis in ('x','z'): forces[f'{side}FP_moment_{axis}']=0.0
 out_force=out/'vertical_moment_only.mot'
 with out_force.open('w',newline='') as f:
  f.write(f'EXP0083 alternative\nversion=1\nnRows={len(forces)}\nnColumns={len(forces.columns)}\ninDegrees=yes\nendheader\n'); forces.to_csv(f,sep='\t',index=False,float_format='%.12g',lineterminator='\n')
 loads=o.ExternalLoads(); loads.setDataFileName(str(out_force))
 for side in ('r','l'):
  ef=o.ExternalForce(); ef.setName(side+'force'); ef.setAppliedToBodyName('calcn_'+side); ef.setForceExpressedInBodyName('ground'); ef.setPointExpressedInBodyName('ground'); ef.setForceIdentifier(side+'FP_v'); ef.setPointIdentifier(side+'FP_p'); ef.setTorqueIdentifier(side+'FP_moment_'); loads.cloneAndAppend(ef)
 loads.printToXML(str(out/'loads.xml'))
 reference=pd.read_csv(proc/f'{person}_squats_1_0lbs_angle.csv'); t0=float(reference.time.iloc[0]); t1=float(reference.time.iloc[-1])
 tool=o.InverseDynamicsTool(); excluded=o.ArrayStr(); excluded.append('Muscles'); tool.setExcludedForces(excluded); tool.setModelFileName(str(raw/'Models'/f'{person}-Scaled1.osim')); tool.setCoordinatesFileName(str(original/'ik.mot')); tool.setExternalLoadsFileName(str(out/'loads.xml')); tool.setStartTime(t0); tool.setEndTime(t1); tool.setLowpassCutoffFrequency(6); tool.setResultsDir(str(out)); tool.setOutputGenForceFileName('alternative.sto'); assert tool.run()
 a=key(pd.read_csv(raw/'CSV_Data'/'squats_1'/'Joint_Moments.csv')); flags=key(pd.read_csv(proc/f'{person}_squats_1_0lbs_activity_flag.csv')); base=key(read_storage(original/'id.sto')); alt=key(read_storage(out/'alternative.sto'))
 z=a[['frame','knee_angle_r_moment']].merge(flags[['frame','time','right']],on='frame').merge(base[['frame','knee_angle_r_moment']],on='frame',suffixes=('_source','_all')).merge(alt[['frame','knee_angle_r_moment']],on='frame').rename(columns={'knee_angle_r_moment':'knee_angle_r_moment_vertical'})
 central=(z.time>=t0+1)&(z.time<=t1-1); active=z.right==1; masks={'all':np.ones(len(z),dtype=bool),'central':central,'active':active,'central_active':central&active}
 comparisons={}
 for name,mask in masks.items():
  comparisons[name]={}
  for config in ('all','vertical'):
   x=z.loc[mask,'knee_angle_r_moment_source'].to_numpy(); y=z.loc[mask,f'knee_angle_r_moment_{config}'].to_numpy(); valid=np.isfinite(x)&np.isfinite(y); x=x[valid]; y=y[valid]
   comparisons[name][config]={'frames':int(len(x)),'corr':float(np.corrcoef(x,y)[0,1]) if len(x)>2 and np.std(x)>0 and np.std(y)>0 else None,'slope_div_mass':float(x@y/(x@x)/mass) if len(x)>2 and x@x>0 else None}
 original_forces=read_storage(forces_path); horizontal=np.concatenate([original_forces[c].to_numpy() for c in ('rFP_moment_x','rFP_moment_z','lFP_moment_x','lFP_moment_z')]); horizontal=horizontal[np.isfinite(horizontal)]
 assert abs(comparisons['all']['all']['slope_div_mass']-prior_by_id[person]['absolute_slope_div_mass'])<1e-9
 results.append({'participant':person,'ik_sha256_bytes':hashlib.sha256((original/'ik.mot').read_bytes()).hexdigest(),'baseline_id_sha256_bytes':hashlib.sha256((original/'id.sto').read_bytes()).hexdigest(),'force_audit':force_audit,'absolute_horizontal_moment_median_Nm':float(np.median(np.abs(horizontal))),'absolute_horizontal_moment_p95_Nm':float(np.quantile(np.abs(horizontal),.95)),'comparisons':comparisons})
out={'experiment_id':'EXP-0083','classification':'EXPLORATORY_POSTHOC_DIAGNOSTIC','opensim_version':o.GetVersion(),'protocol_sha256_lf':text_sha256(H/'MOMENT_DIAGNOSTIC_PROTOCOL.md'),'input_manifest_sha256_lf':text_sha256(H/'MOMENT_DIAGNOSTIC_INPUTS.json'),'runner_sha256_lf':text_sha256(Path(__file__)),'depends_on':'EXP-0082 reconstructed ik.mot and id.sto','prior_result_sha256_lf':text_sha256(H/'MOMENT_SCALE_RESULTS.json'),'results':results,'decision':'UNRESOLVED_PENDING_SOURCE_PROCESSING'}
(H/'MOMENT_DIAGNOSTIC_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out,indent=2))
