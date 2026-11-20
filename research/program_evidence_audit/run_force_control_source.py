"""EXP-0111: published group arithmetic and linked source archive inventory."""
import hashlib,json,sys,zipfile
from pathlib import Path
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);b=p.read_bytes();sha=hashlib.sha256(b).hexdigest();md5=hashlib.md5(b).hexdigest();assert sha=='83df07ab13b0a4fa9c5b9f6f8722ad21c91250528c48ae7c7406cb04036baeb7' and md5=='b65f9ac1c44566a3bd22e36dee497a99'
with zipfile.ZipFile(p) as z:
 files=[{'name':x.filename.split('/')[-1],'size':x.file_size} for x in z.infolist() if not x.is_dir()];assert sorted(x['name'] for x in files)==['LICENSE','README.md']
j=json.loads((H/'FORCE_CONTROL_GROUP_INPUT.json').read_text(encoding='utf-8-sig'));assert j['participants']==18
r={}
for k,v in j['outcomes'].items():
 a=float(v['pre']);b=float(v['final']);assert a>0 and b>0;r[k]={'change_absolute':b-a,'final_pre_ratio':b/a,'percent_change_ratio_of_group_means':100*(b/a-1)}
out={'experiment_id':'EXP-0111','classification':'POST_VIEW_GROUP_OUTCOMES_ARCHIVE_AUDIT','archive_sha256_bytes':sha,'archive_md5_bytes':md5,'archive_file_inventory':files,'github_inspected_commit':'330dbca093e462771545e230deba0f11f16d1486','input_sha256_lf':text_sha256(H/'FORCE_CONTROL_GROUP_INPUT.json'),'protocol_sha256_lf':text_sha256(H/'FORCE_CONTROL_SOURCE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'participants':18,'group_means_arithmetic':r,'limits':['published results and archive were previewed before protocol','ratio of rounded means is not the mean individual percentage','archive lacks individual records; results cannot be reproduced from it','no measured external work or CPE45; no healthy-person enhancement claim']}
(H/'FORCE_CONTROL_SOURCE_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
