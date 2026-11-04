"""Public source retrieval with immutable hashes; unlicensed raw files stay in ignored cache."""
from pathlib import Path
import hashlib,json,urllib.request,urllib.error
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
CACHE=ROOT/'tmp/recovery_raw'
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SUBJECT-01 research/1.0'}),timeout=60) as r:return r.read()
def save_json(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def retrieve_osf():
    if (BASE/'osf_provenance.json').exists():
        verify_cache()
        return json.loads((BASE/'osf_provenance.json').read_text('utf8'))['files']
    CACHE.mkdir(parents=True,exist_ok=True)
    listing=json.loads(get('https://api.osf.io/v2/nodes/db3sk/files/osfstorage/?page%5Bsize%5D=100'))
    out=[]
    for item in listing['data']:
        a=item['attributes']
        if a['name'] not in ['Power_rawdata.xlsx','VO2_rawdata.xlsx']:continue
        url=item['links']['download'];data=get(url);sha=hashlib.sha256(data).hexdigest()
        assert sha==a['extra']['hashes']['sha256']
        path=CACHE/a['name']
        if path.exists() and path.read_bytes()!=data:raise ValueError('source changed')
        path.write_bytes(data)
        out.append(dict(name=a['name'],file_id=item['id'],version=a['current_version'],modified=a['date_modified'],download_url=url,metadata_url=item['links']['self'],bytes=len(data),sha256=sha,license='OSF node_license=null; public read access, redistribution permission not established; raw not committed'))
    save_json(BASE/'osf_provenance.json',dict(node='db3sk',article_doi='10.1055/a-2940-7047',pmid='42712884',retrieved='2026-11-04',files=out,preregistration_commit='9f25664',attribution='Jutlah LBL et al., Work-to-rest ratios in repeated sprint assessments: A replication study (2026)'))
    return out
def verify_cache():
    p=json.loads((BASE/'osf_provenance.json').read_text('utf8'))
    CACHE.mkdir(parents=True,exist_ok=True)
    for f in p['files']:
        path=CACHE/f['name']
        if not path.exists():path.write_bytes(get(f['download_url']))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=f['sha256']:raise ValueError('source hash mismatch: '+f['name'])
    return CACHE
if __name__=='__main__':
    print(json.dumps(retrieve_osf(),indent=2))
