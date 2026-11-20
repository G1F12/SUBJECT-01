"""EXP-0101: descriptive held-time comparison on previously viewed group means."""
import json,math
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=H/'CYCLING_TORQUE_INPUTS.json';src=json.loads(p.read_text(encoding='utf-8'));times=np.array(src['time_minutes'],float);assert times.tolist()==[2,4,6,8,10,12] and src['participants_reported']==16
rows=[]
for name in ('HVY','VHI'):
 y=np.array(src['group_mean_peak_torque_Nm'][name],float);assert len(y)==len(times) and np.all(np.isfinite(y)) and np.all(y>0)
 persistence=np.full(4,y[1]);linear=y[1]+(y[1]-y[0])/(times[1]-times[0])*(times[2:]-times[1]);actual=y[2:]
 rows.append({'condition':name,'training_means_Nm':y[:2].tolist(),'held_times_min':times[2:].tolist(),'held_means_Nm':actual.tolist(),'persistence_predictions_Nm':persistence.tolist(),'linear_predictions_Nm':linear.tolist(),'persistence_mae_Nm':float(abs(persistence-actual).mean()),'linear_mae_Nm':float(abs(linear-actual).mean())})
result={'experiment_id':'EXP-0101','classification':'EXPLORATORY_PREVIEWED_GROUP_TIMEPOINTS_ONLY','protocol_sha256_lf':text_sha256(H/'CYCLING_TORQUE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'input_sha256_lf':text_sha256(p),'rows':rows,'equal_condition_persistence_mae_Nm':float(np.mean([x['persistence_mae_Nm'] for x in rows])),'equal_condition_linear_mae_Nm':float(np.mean([x['linear_mae_Nm'] for x in rows])),'limits':['entire table observed before protocol','aggregate group means not participant-level','same individuals contribute repeated timepoints and intensities','no confidence interval or physiological plateau claim','no measured actual per-person work, post-exercise recovery or whole architecture']}
(H/'CYCLING_TORQUE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
