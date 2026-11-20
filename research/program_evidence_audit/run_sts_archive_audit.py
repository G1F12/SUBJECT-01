"""EXP-0110: exact duplicate and shape audit of a versioned STS archive."""
import csv,hashlib,io,json,sys,zipfile
from pathlib import Path
from collections import defaultdict,Counter
from run_audit import text_sha256
H=Path(__file__).resolve().parent;p=Path(sys.argv[1]);data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();md5=hashlib.md5(data).hexdigest();assert sha=='4b0b7dc8e13439bb96d0afa1bbd2a55a57fbeda7d46ea879ecf953785b9d2351' and md5=='2f8a8fcb1b8e4fd1361ce938ead90d33'
groups=defaultdict(list)
with zipfile.ZipFile(p) as z:
 names=[n for n in z.namelist() if n.endswith('.txt') and n.startswith(('STS_data/Men/','STS_data/Women/'))];assert len(names)==60 and len(set(names))==60;assert Counter(n.split('/')[1] for n in names)=={'Men':30,'Women':30}
 for n in names:groups[hashlib.sha256(z.read(n)).hexdigest()].append(n)
 raw=z.read('STS_data/Processing/Data_STS.csv');csvsha=hashlib.sha256(raw).hexdigest();rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));assert rows and len({len(x) for x in rows})==1;cols=list(zip(*rows));coldups=[(i+1,j+1) for i in range(len(cols)) for j in range(i+1,len(cols)) if cols[i]==cols[j]];rowcounts=Counter(tuple(r) for r in rows)
dup=[v for v in groups.values() if len(v)>1];patterns=Counter('cross' if len({n.split('/')[1] for n in v})>1 else v[0].split('/')[1] for v in dup)
out={'experiment_id':'EXP-0110','classification':'EXPLORATORY_SOURCE_QUALITY_AUDIT','archive_sha256_bytes':sha,'archive_md5_bytes':md5,'processed_csv_sha256_bytes':csvsha,'protocol_sha256_lf':text_sha256(H/'STS_ARCHIVE_AUDIT_PROTOCOL.md'),'runner_sha256_lf':text_sha256(Path(__file__)),'raw_txt_files':len(names),'unique_raw_txt_sha256':len(groups),'duplicate_raw_groups':len(dup),'duplicate_raw_group_sizes':sorted([len(v) for v in dup]),'files_in_duplicate_groups':sum(map(len,dup)),'duplicate_groups_by_category':dict(patterns),'csv_rows':len(rows),'csv_columns':len(cols),'identical_column_pairs_1based':coldups,'duplicate_csv_row_groups':sum(v>1 for v in rowcounts.values()),'duplicate_csv_rows_in_groups':sum(v for v in rowcounts.values() if v>1),'limits':['article file list first TXT record and first CSV rows previewed','identical files do not establish participant identity or reason','no validated mapping from processed rows to participants','column equality is not proof of an error','no direct force work post-exercise strength or CPE45 measurement']}
(H/'STS_ARCHIVE_AUDIT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
