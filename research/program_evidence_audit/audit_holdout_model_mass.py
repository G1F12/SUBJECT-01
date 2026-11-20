"""Post hoc check: subject model masses versus dataset README masses."""
import hashlib,json,sys
from pathlib import Path
import opensim as o
from run_audit import text_sha256
H=Path(__file__).resolve().parent; root=Path(sys.argv[1]);o.Logger.setLevelString('error')
files=[]
for name in ['MOMENT_SCALE_INPUTS.json','MOMENT_HOLDOUT_INPUTS.json']:
 files.extend(json.loads((H/name).read_text(encoding='utf-8'))['files'])
expected={r['path']:r['sha256'] for r in files}; out=[]
for p,n,mass in [('AB01',1,78.9),('AB02',1,82.2),('AB03',4,113.5),('AB06',1,79.1)]:
 path=root/'raw'/p/'Models'/f'{p}-Scaled{n}.osim'; rel=path.relative_to(root).as_posix(); sha=hashlib.sha256(path.read_bytes()).hexdigest(); assert sha==expected[rel]; model=o.Model(str(path)); state=model.initSystem(); out.append({'participant':p,'model_mass_kg':model.getTotalMass(state),'readme_mass_kg':mass,'model_sha256':sha})
res={'classification':'POSTHOC_DESCRIPTIVE','experiment_id':'EXP-0084','runner_sha256_lf':text_sha256(Path(__file__)),'results':out}
(H/'MOMENT_HOLDOUT_MASS_AUDIT.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8'); print(json.dumps(res,indent=2))
