"""EXP-0084: holdout-patient inverse-dynamics moment-scale assessment."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
import opensim as o
from run_audit import text_sha256
H=Path(__file__).resolve().parent; root=Path(sys.argv[1]).resolve(); work=Path(sys.argv[2]).resolve(); work.mkdir(parents=True,exist_ok=True)
for r in json.loads((H/'MOMENT_HOLDOUT_INPUTS.json').read_text(encoding='utf-8'))['files']:
 assert hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
o.Logger.setLevelString('error')
def storage(p):
 with p.open() as f:
  for i,line in enumerate(f):
   if line.strip()=='endheader':break
 return pd.read_csv(p,sep=r'\s+',skiprows=i+1)
def key(df):
 df=df.copy(); df['frame']=np.rint(df.time*200).astype(int); assert df.frame.is_unique; return df
results=[]
for person,mass,static in [('AB03',113.5,4),('AB06',79.1,1)]:
 raw=root/'raw'/person; out=work/person; out.mkdir(parents=True,exist_ok=True)
 statics=pd.read_csv(raw/'Models'/'Statics.csv'); assert int(statics.loc[statics.trial=='squats_1','static'].iloc[0])==static
 modelpath=raw/'Models'/f'{person}-Scaled{static}.osim'; model=o.Model(str(modelpath)); model.initSystem()
 trc=raw/'MarkerData'/'squats_1.trc'; force=raw/'ExtLoads'/'squats_1.mot'; rawf=storage(force); alternate=rawf.copy()
 for side in ('r','l'):
  for axis in ('x','z'):alternate[f'{side}FP_moment_{axis}']=0.0
 altfile=out/'vertical_only.mot'
 with altfile.open('w',newline='') as f:
  f.write(f'EXP0084 alternative\nversion=1\nnRows={len(alternate)}\nnColumns={len(alternate.columns)}\ninDegrees=yes\nendheader\n'); alternate.to_csv(f,sep='\t',index=False,float_format='%.12g',lineterminator='\n')
 names_available=set(trc.read_text().splitlines()[3].split('\t')[2:]); markers=model.getMarkerSet(); names=[markers.get(i).getName() for i in range(markers.getSize()) if markers.get(i).getName() in names_available]; assert len(names)>=25
 for load in (0,25):
  folder=out/f'{load}lbs'; folder.mkdir(parents=True,exist_ok=True); proc=root/'files'/person/f'squats_1_{load}lbs'; reference=pd.read_csv(proc/f'{person}_squats_1_{load}lbs_angle.csv'); t0=float(reference.time.iloc[0]); t1=float(reference.time.iloc[-1]); print(person,load,'start',flush=True)
  ik=o.InverseKinematicsTool(); ik.setModel(model); ik.setMarkerDataFileName(str(trc)); ik.setStartTime(t0); ik.setEndTime(t1); ik.setOutputMotionFileName(str(folder/'ik.mot')); ik.set_report_errors(False)
  for name in names:
   task=o.IKMarkerTask(); task.setName(name); task.setWeight(1); task.setApply(True); ik.upd_IKTaskSet().cloneAndAppend(task)
  assert ik.run()
  frames=key(pd.read_csv(raw/'CSV_Data'/'squats_1'/'Joint_Angle.csv'))[['frame','knee_angle_r']].merge(key(pd.read_csv(raw/'CSV_Data'/'squats_1'/'Joint_Moments.csv'))[['frame','knee_angle_r_moment']],on='frame').merge(key(storage(folder/'ik.mot'))[['frame','time','knee_angle_r']],on='frame',suffixes=('_source','_ik'))
  angle_error=float(np.median(np.abs(frames.knee_angle_r_source-frames.knee_angle_r_ik))); alternatives={}
  for label,forcefile in [('all',force),('vertical',altfile)]:
   loads=o.ExternalLoads(); loads.setDataFileName(str(forcefile))
   for side in ('r','l'):
    ef=o.ExternalForce(); ef.setName(side+'force'); ef.setAppliedToBodyName('calcn_'+side); ef.setForceExpressedInBodyName('ground'); ef.setPointExpressedInBodyName('ground'); ef.setForceIdentifier(side+'FP_v'); ef.setPointIdentifier(side+'FP_p'); ef.setTorqueIdentifier(side+'FP_moment_'); loads.cloneAndAppend(ef)
   loads.printToXML(str(folder/f'loads_{label}.xml'))
   tool=o.InverseDynamicsTool(); excluded=o.ArrayStr(); excluded.append('Muscles'); tool.setExcludedForces(excluded); tool.setModelFileName(str(modelpath)); tool.setCoordinatesFileName(str(folder/'ik.mot')); tool.setExternalLoadsFileName(str(folder/f'loads_{label}.xml')); tool.setStartTime(t0); tool.setEndTime(t1); tool.setLowpassCutoffFrequency(6); tool.setResultsDir(str(folder)); tool.setOutputGenForceFileName(f'id_{label}.sto'); assert tool.run()
   z=frames.merge(key(storage(folder/f'id_{label}.sto'))[['frame','knee_angle_r_moment']],on='frame',suffixes=('_source','_id')); alternatives[label]={}
   for label_mask,mask in [('all',np.ones(len(z),dtype=bool)),('central',(z.time>=t0+1)&(z.time<=t1-1))]:
    x=z.loc[mask,'knee_angle_r_moment_source'].to_numpy(); y=z.loc[mask,'knee_angle_r_moment_id'].to_numpy(); valid=np.isfinite(x)&np.isfinite(y); x=x[valid];y=y[valid]
    assert len(x)>=100 and x@x>0 and np.std(x)>0 and np.std(y)>0
    alternatives[label][label_mask]={'frames':len(x),'correlation':float(np.corrcoef(x,y)[0,1]),'slope_div_mass':float(x@y/(x@x)/mass)}
  criterion=alternatives['vertical']['all']; quality=criterion['frames']>=100 and angle_error<=5 and criterion['correlation']>=.8
  results.append({'participant':person,'condition_lb':load,'mass_kg':mass,'model_static':static,'markers':len(names),'median_abs_knee_angle_difference_deg':angle_error,'comparisons':alternatives,'quality_gate':quality,'conditional_scale_gate':quality and .7<=criterion['slope_div_mass']<=1.3}); print(person,load,'done',flush=True)
primary=[x for x in results if x['condition_lb']==0]
output={'experiment_id':'EXP-0084','classification':'EXPLORATORY_HELD_PARTICIPANTS_SAME_COHORT','opensim_version':o.GetVersion(),'protocol_sha256_lf':text_sha256(H/'MOMENT_HOLDOUT_PROTOCOL.md'),'input_manifest_sha256_lf':text_sha256(H/'MOMENT_HOLDOUT_INPUTS.json'),'runner_sha256_lf':text_sha256(Path(__file__)),'results':results,'conditional_primary_gate':'PASS' if len(primary)==2 and all(x['conditional_scale_gate'] for x in primary) else 'NOT_PASSED','moment_convention':'UNRESOLVED'}
(H/'MOMENT_HOLDOUT_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8');print(json.dumps(output,indent=2))
