"""EXP-0082: reconstruct IK/ID for scale audit; run with OpenSim 4.6."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import opensim as o
from run_audit import text_sha256
HERE=Path(__file__).resolve().parent
root=Path(sys.argv[1]); work=Path(sys.argv[2]); work.mkdir(parents=True,exist_ok=True)
manifest=json.loads((HERE/'MOMENT_SCALE_INPUTS.json').read_text(encoding='utf-8'))
for r in manifest['files']:
 assert hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'], r['path']
o.Logger.setLevelString('error')
def storage(p):
 with p.open() as f:
  for i,line in enumerate(f):
   if line.strip()=='endheader': break
 return pd.read_csv(p,sep=r'\s+',skiprows=i+1)
results=[]
for person,mass in [('AB01',78.9),('AB02',82.2)]:
 raw=root/'raw'/person; proc=root/'files'/person/'squats_1_0lbs'; out=work/person; out.mkdir(parents=True,exist_ok=True)
 statics=pd.read_csv(raw/'Models'/'Statics.csv'); assert int(statics.loc[statics.trial=='squats_1','static'].iloc[0])==1
 modelpath=raw/'Models'/f'{person}-Scaled1.osim'; model=o.Model(str(modelpath)); model.initSystem()
 trc=raw/'MarkerData'/'squats_1.trc'; force=raw/'ExtLoads'/'squats_1.mot'
 reference_angle=pd.read_csv(proc/f'{person}_squats_1_0lbs_angle.csv'); t0=float(reference_angle.time.iloc[0]); t1=float(reference_angle.time.iloc[-1])
 names_available=set(trc.read_text().splitlines()[3].split('\t')[2:]); markers=model.getMarkerSet(); names=[markers.get(i).getName() for i in range(markers.getSize()) if markers.get(i).getName() in names_available]; assert len(names)==35
 ik=o.InverseKinematicsTool(); ik.setModel(model); ik.setMarkerDataFileName(str(trc)); ik.setStartTime(t0); ik.setEndTime(t1); ik.setOutputMotionFileName(str(out/'ik.mot')); ik.set_report_errors(False)
 for name in names:
  task=o.IKMarkerTask(); task.setName(name); task.setWeight(1); task.setApply(True); ik.upd_IKTaskSet().cloneAndAppend(task)
 assert ik.run()
 loads=o.ExternalLoads(); loads.setDataFileName(str(force))
 for side in ('r','l'):
  f=o.ExternalForce(); f.setName(side+'force'); f.setAppliedToBodyName('calcn_'+side); f.setForceExpressedInBodyName('ground'); f.setPointExpressedInBodyName('ground'); f.setForceIdentifier(side+'FP_v'); f.setPointIdentifier(side+'FP_p'); f.setTorqueIdentifier(side+'FP_moment_'); loads.cloneAndAppend(f)
 loads.printToXML(str(out/'loads.xml'))
 tool=o.InverseDynamicsTool(); excluded=o.ArrayStr(); excluded.append('Muscles'); tool.setExcludedForces(excluded); tool.setModelFileName(str(modelpath)); tool.setCoordinatesFileName(str(out/'ik.mot')); tool.setExternalLoadsFileName(str(out/'loads.xml')); tool.setStartTime(t0); tool.setEndTime(t1); tool.setLowpassCutoffFrequency(6); tool.setResultsDir(str(out)); tool.setOutputGenForceFileName('id.sto'); assert tool.run()
 angles=pd.read_csv(raw/'CSV_Data'/'squats_1'/'Joint_Angle.csv'); moments=pd.read_csv(raw/'CSV_Data'/'squats_1'/'Joint_Moments.csv')
 z=angles.merge(moments,on='time').merge(storage(out/'ik.mot'),on='time',suffixes=('_orig','_ik')).merge(storage(out/'id.sto'),on='time')
 x=z.knee_angle_r_moment_x.to_numpy(); y=z.knee_angle_r_moment_y.to_numpy(); mask=np.isfinite(x)&np.isfinite(y); x=x[mask]; y=y[mask]
 median_angle=float(np.median(np.abs(z.knee_angle_r_orig-z.knee_angle_r_ik))); corr=float(np.corrcoef(x,y)[0,1]); slope=float(x@y/(x@x)); ratio=abs(slope)/mass
 results.append({'participant':person,'mass_kg':mass,'frames':int(len(x)),'markers':len(names),'median_abs_knee_angle_difference_deg':median_angle,'correlation':corr,'signed_slope_Nm_per_source_unit':slope,'absolute_slope_div_mass':ratio,'quality_gate':abs(corr)>=0.8 and median_angle<=5,'h1_gate':0.7<=abs(slope)<=1.3,'h2_gate':0.7<=ratio<=1.3})
quality=all(x['quality_gate'] for x in results); h1=quality and all(x['h1_gate'] for x in results); h2=quality and all(x['h2_gate'] for x in results)
output={'experiment_id':'EXP-0082','classification':'EXPLORATORY_RECONSTRUCTION','opensim_version':o.GetVersion(),'protocol_sha256_lf':text_sha256(HERE/'MOMENT_SCALE_PROTOCOL.md'),'inputs_manifest_sha256_lf':text_sha256(HERE/'MOMENT_SCALE_INPUTS.json'),'runner_sha256_lf':text_sha256(Path(__file__)),'results':results,'decision':'H1_SUPPORTED' if h1 else 'H2_SUPPORTED' if h2 else 'UNRESOLVED'}
(HERE/'MOMENT_SCALE_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps(output,indent=2))
