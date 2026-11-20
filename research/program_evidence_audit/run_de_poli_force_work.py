"""EXP-0109: descriptive arithmetic from published rounded group means."""
import json
from pathlib import Path
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=H/'DE_POLI_TABLE3_INPUT.json';j=json.loads(p.read_text(encoding='utf-8-sig'));assert set(j['groups'])=={'SIT','control'}
r={}
for group,g in j['groups'].items():
 assert set(g)=={'pre_training','post_training'}
 vals={k:v['post_exercise_N']/v['baseline_N'] for k,v in g.items() if v['baseline_N']>0 and v['post_exercise_N']>0};assert len(vals)==2
 r[group]={'retention_ratio_of_group_means':vals,'change_in_ratio_percentage_points':100*(vals['post_training']-vals['pre_training'])}
r['difference_in_group_changes_percentage_points']=r['SIT']['change_in_ratio_percentage_points']-r['control']['change_in_ratio_percentage_points']
out={'experiment_id':'EXP-0109','classification':'POST_VIEW_GROUP_SUMMARY_ONLY_INDIVIDUAL_DATA_BLOCKED','input_sha256_lf':text_sha256(p),'protocol_sha256_lf':text_sha256(H/'DE_POLI_FORCE_WORK_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'results':r,'limitations':['ratio of rounded group means, not mean individual retention','no paired uncertainty, no individual mechanical work','relative intensity matched rather than same absolute work','no individual data, CPE45 or architecture outcome']}
(H/'DE_POLI_FORCE_WORK_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
