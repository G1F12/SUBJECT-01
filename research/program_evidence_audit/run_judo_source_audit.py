import csv,hashlib,json,sys,math
from collections import Counter,defaultdict
from pathlib import Path
import openpyxl
from run_audit import text_sha256
H=Path(__file__).resolve().parent;root=Path(sys.argv[1]); names={
'73':'Cleaned_Macierz_EEG_HiN_M_73kg (1).xlsx','81':'Cleaned_Macierz_EEG_HiN_M_81kg (1).xlsx','90':'Cleaned_Macierz_EEG_HiN_M_90kg.xlsx','100':'Cleaned_Macierz_EEG_HiN_M_100kg.xlsx',
'readme':'README_EEG_HiN_Judo.docx','codebook':'Codebook_EEG_HiN_Judo (1).docx','participants':'Participants_Metadata_Judo.csv'}
expected={'73':'81584eac25be315524199368a7b931597897808c6734a4d83bd825f94e6f970b','81':'53c46960f342874b1de03c7351fb8d51032cc15b6efd2c6b051ce9863b5ad435','90':'ff6b9603959dfed4759e119cb6123daa008732c79014032d82bbaf344e2092e6','100':'4f2a4d307d7cff1a2f47c5dd2f33c901d2a68a8ae4daed9968f427bc4ead6fa9','readme':'fbe4ec1569634bd3c57ef9dd16d3af953c0dedc5d86020af43bfe8800ac34884','codebook':'6350ba960807b88be9af63c5711eccca5a7140bf60df132de09d0f184a7c2854','participants':'88205e1e20722e06b12c195111f2f5d3c4d4e98f1f78e3913ee5d592d6c0b0d4'}
paths={k:root/('subject01-judo-'+n) for k,n in names.items()}; hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()};assert hashes==expected
stats={};allids=set();total_rep=defaultdict(Counter);total_vel=[]
for label in ('73','81','90','100'):
 w=openpyxl.load_workbook(paths[label],read_only=True,data_only=True)
 def load(sheet):
  data=iter(w[sheet].values);hdr=next(data);assert len(hdr)==len(set(hdr));return [dict(zip(hdr,r)) for r in data if any(v is not None for v in r)]
 rows=load('Raw_Strength');vel=load('TW_FI_SEI');power=load('Peak_Power')
 ids={str(r['Subject_ID']) for r in rows};allids.update(ids); conditions=defaultdict(set);keys=Counter()
 for r in rows:
  key=(str(r['Subject_ID']),str(r['Group_Clean']),str(r['%_Obciążenia']));keys[key]+=1;conditions[str(r['Subject_ID'])].add(str(r['Group_Clean']))
 repeated=sum(len(v)>1 for v in conditions.values()); time_fields={'pre':'PRZED','post':'PO_drop','24h':'POST_24h','48h':'POST_48h','72h':'POST_72h'}
 for time,suffix in time_fields.items():
  for name in (f'Przysiady_70%_{suffix}',f'Przysiady_85%_{suffix}',f'Wyciskanie_70%_{suffix}',f'Wyciskanie_85%_{suffix}'):
   assert name in rows[0],name
   for r in rows:
    x=r[name];c=total_rep[time]
    if isinstance(x,(int,float)) and math.isfinite(x):
     c['numeric']+=1
     if abs(x-round(x))>1e-8:c['noninteger']+=1
    else:c['missing_or_nonnumeric']+=1
 for r in vel:
  for k,x in r.items():
   if '_TW_' in k and isinstance(x,(int,float)) and math.isfinite(x):total_vel.append(float(x))
 stats[label]={'rows_raw_strength':len(rows),'unique_ids':len(ids),'conditions':dict(Counter(str(r['Group_Clean']) for r in rows)),'ids_with_multiple_conditions':repeated,'duplicate_id_condition_load_keys':sum(v-1 for v in keys.values() if v>1),'power_rows':len(power),'power_unique_ids':len({str(r['Subject_ID']) for r in power})}
with paths['participants'].open(encoding='utf-8-sig',newline='') as f: metadata=list(csv.DictReader(f))
metadata_summary={'rows':len(metadata),'unique_participant_ids':len({r['ParticipantID'] for r in metadata}),'conditions':dict(Counter(r['Condition'] for r in metadata)),'linkage_to_workbooks':'unverified, identifier formats differ'}
result={'metadata_summary':metadata_summary,'experiment_id':'EXP-0097','classification':'SOURCE_ADMISSION_AUDIT_NOT_HUMAN_VALIDATION','protocol_sha256_lf':text_sha256(H/'JUDO_SOURCE_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'input_sha256_bytes':hashes,'by_weight_file':stats,'unique_ids_across_files':len(allids),'repetition_values':{k:dict(v) for k,v in total_rep.items()},'velocity_fields':{'numeric_count':len(total_vel),'minimum':min(total_vel),'maximum':max(total_vel),'nonpositive_count':sum(x<=0 for x in total_vel),'above_3_as_documented_m_s':sum(x>3 for x in total_vel)},'admission':'DATA_BLOCKED_PENDING_SOURCE_CLARIFICATION','limitations':['summary descriptions and individual rows previously viewed','fractional values can represent undocumented averages or processing','identity linkage is based on supplied Subject_ID only','threshold 3 m/s is a diagnostic flag not a biological limit','peak power data not validated; no CPE45 or architecture outcome']}
(H/'JUDO_SOURCE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
