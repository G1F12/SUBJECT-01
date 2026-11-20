"""EXP-0095: fixed-order-group transfer with participant bootstrap."""
import csv,hashlib,io,json,math,sys,zipfile
from pathlib import Path
import numpy as np
from run_audit import text_sha256
H=Path(__file__).resolve().parent; data=Path(sys.argv[1]);digest=hashlib.sha256(data.read_bytes()).hexdigest();assert digest=='250bcb84c25ea9cea86711cc088598c30295a9f59f7ce295be2b935cff787383'
z=zipfile.ZipFile(data)
def table(name):return list(csv.DictReader(io.StringIO(z.read('Subject_Data/'+name).decode('utf-8-sig'),newline='')))
raw=table('Task_Times.csv'); blank_rows=sum(all(not (v or '').strip() for v in r.values()) for r in raw); t=[r for r in raw if any((v or '').strip() for v in r.values())]; force=table('Forces_Sh.csv'); ids=[r['Sub'].strip() for r in t];assert len(ids)==len(set(ids)); force_by_id={r['Sub'].strip():r for r in force};assert len(force_by_id)==len(force)
sets={'A':[],'B':[]};excluded=[];intensities={'25':[],'45':[]}
for r in t:
 try:
  g=r['Group'].strip();x=float(r['StSh25']);y=float(r['StSh45']);assert g in sets and all(math.isfinite(a) and a>0 for a in (x,y));sets[g].append((x,y)); fr=force_by_id.get(r['Sub'].strip(),{})
  for label in intensities:
   raw=fr.get('SI_Sh'+label,'').strip().rstrip('%')
   try:
    value=float(raw)
    if math.isfinite(value) and value>0:intensities[label].append(value)
   except ValueError:pass
 except (ValueError,AssertionError):excluded.append({'id':r['Sub'].strip(),'reason':'invalid group or missing/nonpositive time'})
assert all(len(v)>=5 for v in sets.values())
results=[]
for train,test,seed in (('A','B',20261120),('B','A',20261121)):
 a=np.array(sets[train]);b=np.array(sets[test]);assert np.ptp(a[:,0])>0
 X=np.column_stack([np.ones(len(a)),a[:,0]]); coef=np.linalg.lstsq(X,a[:,1],rcond=None)[0]; pred=coef[0]+coef[1]*b[:,0]; baseline=np.full(len(b),a[:,1].mean()); y=b[:,1];err0=abs(baseline-y);err1=abs(pred-y);delta=err0-err1
 indexes=np.random.default_rng(seed).integers(0,len(y),(10000,len(y)));ci=np.quantile(delta[indexes].mean(axis=1),[.025,.975]); r2=None if np.ptp(y)==0 else float(1-np.sum((pred-y)**2)/np.sum((y-y.mean())**2))
 results.append({'train_group':train,'test_group':test,'train_n':len(a),'test_n':len(b),'train_intercept_s':float(coef[0]),'train_slope':float(coef[1]),'baseline_prediction_s':float(a[:,1].mean()),'model_mae_s':float(err1.mean()),'baseline_mae_s':float(err0.mean()),'paired_advantage_s':float(delta.mean()),'paired_bootstrap_95_s':ci.tolist(),'model_bias_s':float((pred-y).mean()),'baseline_bias_s':float((baseline-y).mean()),'target_range_s':[float(y.min()),float(y.max())],'model_r2':r2,'negative_prediction_count':int(np.sum(pred<0)),'decision':'linear_superior' if ci[0]>0 else 'constant_superior' if ci[1]<0 else 'uncertain'})
result={'experiment_id':'EXP-0095','classification':'OBSERVATIONAL_TRANSFER_BETWEEN_ORDER_GROUPS','zip_sha256_bytes':digest,'protocol_sha256_lf':text_sha256(H/'SWIFTIES_TRANSFER_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'source_count':len(t),'blank_structural_rows':blank_rows,'excluded':excluded,'actual_relative_intensities_pct':{k:{'n':len(v),'min':min(v),'mean':sum(v)/len(v),'max':max(v)} for k,v in intensities.items()},'comparisons':results,'limitations':['published data and first rows seen before protocol','nonrandomized order and participant differences confounded','task termination may include pain','not post-exercise strength or biochemical recovery','upper limb 1-minute tasks not CPE45 or lower limb architecture']}
(H/'SWIFTIES_TRANSFER_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
