"""EXP-0121: paired leg press force recovery, explicitly not mechanical work."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);b=p.read_bytes();sha=hashlib.sha256(b).hexdigest();md5=hashlib.md5(b).hexdigest();assert sha=='295cbe90ebb84e7bfa3cd2804d81f87663b16088bdc06021256343d6f57acb9e' and md5=='cbc93d9a8e3de139c2794be81e88f2a9';w=load_workbook(p,read_only=True,data_only=True);leg=w['Leg Press Data'];mvc=w['MVC'];conditions=[('LL',2,4,4,6),('HL',18,20,20,22)];V={};F={}
for name,legtitle,legstart,mvctitle,mvcstart in conditions:
 assert leg.cell(legtitle,1).value==('LOW LOAD' if name=='LL' else 'HIGH LOAD') and mvc.cell(mvctitle,1).value==('LOW LOAD' if name=='LL' else 'HIGH LOAD');assert [mvc.cell(mvctitle+1,c).value for c in range(3,7)]==['Pre','5 min','45 min','24 hour'];load={};force={}
 for r in range(legstart,legstart+12):
  id=leg.cell(r,2).value;loadid=leg.cell(r,8).value;mass=leg.cell(r,14).value;reps=[leg.cell(r,c).value for c in range(15,19)];total=leg.cell(r,19).value;volume=leg.cell(r,20).value;assert id==loadid and id not in load and isinstance(mass,(int,float)) and np.isfinite(mass) and mass>0 and all(isinstance(v,(int,float)) and np.isfinite(v) and v>=0 and float(v).is_integer() for v in reps) and sum(reps)==total and abs(mass*total-volume)<.01;load[id]=float(volume)
 for r in range(mvcstart,mvcstart+12):
  id=mvc.cell(r,2).value;vals=np.array([mvc.cell(r,c).value for c in range(3,7)],float);assert id not in force and np.isfinite(vals).all() and np.all(vals>0);force[id]=vals
 assert set(load)==set(force)==set(range(1,13));V[name]=np.array([load[i] for i in range(1,13)]);F[name]=np.array([force[i] for i in range(1,13)])
assert abs(V['LL'].mean()-4134)/4134<.05 and abs(V['HL'].mean()-5065)/5065<.05
LL=100*(F['LL'][:,1:]/F['LL'][:,[0]]-1);HL=100*(F['HL'][:,1:]/F['HL'][:,[0]]-1);idx=np.random.default_rng(20261120).integers(0,12,(10000,12));paired=HL-LL;out={}
for j,name in enumerate(('5min','45min','24h')):
 d=paired[:,j];out[name]={'mean_LL_percent':float(LL[:,j].mean()),'mean_HL_percent':float(HL[:,j].mean()),'mean_HL_minus_LL_pp':float(d.mean()),'paired_bootstrap_95_pp':np.quantile(d[idx].mean(axis=1),[.025,.975]).tolist()}
x=np.stack([LL[:,0],HL[:,0]],axis=1);y=np.stack([LL[:,1],HL[:,1]],axis=1);pred=np.zeros_like(y)
for i in range(12):
 mask=np.arange(12)!=i;trainx=x[mask].reshape(-1);trainy=y[mask].reshape(-1);coef=np.linalg.lstsq(np.column_stack([np.ones(len(trainx)),trainx]),trainy,rcond=None)[0];pred[i,:]=coef[0]+coef[1]*x[i,:]
baseerr=np.abs(x-y).mean(axis=1);modelerr=np.abs(pred-y).mean(axis=1);adv=baseerr-modelerr
result={'experiment_id':'EXP-0121','classification':'PARTIALLY_PREVIEWED_EXISTING_CROSSOVER_NON_BFR_ONLY','source_sha256_bytes':sha,'source_md5_bytes':md5,'protocol_sha256_lf':text_sha256(H/'NORBURY_FORCE_RECOVERY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'participants':12,'source_gate':{'mean_LL_volume_kg_repetitions':float(V['LL'].mean()),'mean_HL_volume_kg_repetitions':float(V['HL'].mean()),'LL_fourth_set_unique_counts':sorted({leg.cell(r,18).value for r in range(4,16)})},'paired_force_percent':out,'prediction_45min':{'persistence_mae_pp':float(baseerr.mean()),'linear_lopo_mae_pp':float(modelerr.mean()),'base_minus_model_mae_pp':float(adv.mean()),'bootstrap_95_pp':np.quantile(adv[idx].mean(axis=1),[.025,.975]).tolist()},'limits':['low-load 12 participant values and article previewed before protocol','volume kg repetitions is not external mechanical work in joules','short task then 45-minute recovery not 45-minute performance','12 men; unequal loads and durations; knee extension not bilateral leg press','no temperature movement control tissue or whole architecture outcome']};(H/'NORBURY_FORCE_RECOVERY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
