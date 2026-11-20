"""EXP-0100: exact noncentral-t sample-size sensitivity, not efficacy prediction."""
import hashlib,json,math
from pathlib import Path
from scipy.stats import norm,t,nct
from run_audit import text_sha256
H=Path(__file__).resolve().parent;rows=[];target=20.;alpha=.05;desired=.8
for md95 in (25.9,29.7,33.7):
 sd=md95/norm.ppf(.975)
 for effect in (20.,22.,25.,30.):
  def power(n):
   df=2*(n-1);critical=t.ppf(1-alpha,df);noncentral=(effect-target)/(sd*math.sqrt(2/n));return float(nct.sf(critical,df,noncentral))
  if effect==target:
   assert abs(power(2)-alpha)<1e-12 and abs(power(10000)-alpha)<1e-12
   rows.append({'md95_pct_of_grand_mean':md95,'assumed_sd_change_pp':sd,'true_contrast_pp':effect,'n_per_group':None,'power_any_n_under_boundary_null':alpha,'reason':'true effect equals 20 percentage point superiority boundary; rejection probability equals alpha'});continue
  low,high=2,2
  while power(high)<desired:
   high*=2;assert high<10000000
  while low<high:
   mid=(low+high)//2
   if power(mid)>=desired:high=mid
   else:low=mid+1
  n=low;actual=power(n);prev=power(n-1) if n>2 else None;assert actual>=desired and (prev is None or prev<desired)
  rows.append({'md95_pct_of_grand_mean':md95,'assumed_sd_change_pp':sd,'true_contrast_pp':effect,'n_per_group':n,'power_at_n':actual,'power_at_n_minus_1':prev})
result={'experiment_id':'EXP-0100','classification':'CONDITIONAL_DESIGN_SENSITIVITY_NOT_EFFICACY','protocol_sha256_lf':text_sha256(H/'FORCE_DETECTABILITY_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'source':'SRC-0098','assumptions':{'test':'independent equal-variance two-group noncentral t','one_sided_alpha':alpha,'desired_power':desired,'target_pp':target,'source_md95_percent_grand_mean':[25.9,29.7,33.7],'standard_deviation_mapping':'MD95 / z(0.975), hypothetical percentage points','missing_data':'none','sample_sizes':'per group'},'scenarios':rows,'limitations':['secondary published aggregates, no raw source data','source single-joint isometric protocol not leg press','individual variability and trial conditions may differ','one-sided t does not establish joint multidomain success','no actual intervention effect or probability of success inferred']}
(H/'FORCE_DETECTABILITY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
