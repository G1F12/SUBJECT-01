"""EXP-0113: descriptive group contrasts and non-measured nominal HIIT work."""
import json
from pathlib import Path
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=H/'LEG_PRESS_HIIT_INPUT.json';j=json.loads(p.read_text(encoding='utf-8-sig'));assert j['n']==15 and j['reliability_cohort_n']==13
r={}
for k,v in j['group_means'].items():
 assert all(x>0 for x in v.values());r[k]={t:100*(v[t]/v['rest']-1) for t in ('min10','h6','h24')}
seconds=j['sets']*j['reps_per_set']*j['effort_seconds'];nominal=seconds*j['load_fraction']*j['group_wvo2max_W'];lo,hi=j['peak_force_range_N'];upper=j['upper_limit_of_agreement_N'];assert seconds==480 and lo<hi
out={'experiment_id':'EXP-0113','classification':'POST_VIEW_GROUP_ONLY_NOMINAL_NOT_MEASURED','input_sha256_lf':text_sha256(p),'protocol_sha256_lf':text_sha256(H/'LEG_PRESS_HIIT_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'ratio_of_group_means_percent_change':r,'nominal_active_s':seconds,'nominal_constant_work_J_not_observed':nominal,'other_cohort_upper_loa_relative_to_range_percent':[100*upper/hi,100*upper/lo],'other_cohort_20percent_force_range_N':[.2*lo,.2*hi],'limits':['previously viewed published group data not participant-level','nominal effort work is not observed work or a bound','separate cohorts and different trial aggregation; overlap unknown','not an individual confidence interval or established FORCE20 test','no 45-minute protocol or whole architecture validation']};(H/'LEG_PRESS_HIIT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
