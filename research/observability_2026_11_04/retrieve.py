"""Public retrieval only. Responses/raw stay ignored; metadata hashes and recipes are public."""
from pathlib import Path
import urllib.request,urllib.error,urllib.parse,json,hashlib,re,zipfile,io
from concurrent.futures import ThreadPoolExecutor
BASE=Path(__file__).resolve().parent;CACHE=BASE.parents[1]/'tmp/observability_raw'

def request(label,url,body=None):
    try:
        req=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,headers={'User-Agent':'SUBJECT-01 public reproducibility audit','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=25) as r:data=r.read();status=r.status;ctype=r.headers.get('Content-Type','')
        path=CACHE/(label+'.bin');path.write_bytes(data)
        return dict(label=label,url=url,request_body=body,status=status,bytes=len(data),content_type=ctype,sha256=hashlib.sha256(data).hexdigest(),cache=path.name)
    except Exception as e:return dict(label=label,url=url,request_body=body,status=getattr(e,'code',None),error=str(e),numeric_obtained=False)

def main():
    CACHE.mkdir(parents=True,exist_ok=True)
    quote=urllib.parse.quote
    query='phosphocreatine AND (oxygen OR power) AND (data OR ergometer)'
    jobs=[('europepmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=50&query='+quote(query),None),
      ('crossref','https://api.crossref.org/works?rows=15&query='+quote('phosphocreatine oxygen uptake power data'),None),
      ('openalex','https://api.openalex.org/works?per-page=15&search='+quote('phosphocreatine oxygen uptake'),None),
      ('zenodo','https://zenodo.org/api/records?size=15&q='+quote('phosphocreatine muscle'),None),
      ('figshare_search','https://api.figshare.com/v2/articles/search',{'search_for':'phosphocreatine','limit':30}),
      ('figshare_WASF3','https://api.figshare.com/v2/articles/23681013/versions/1',None),
      ('osf','https://api.osf.io/v2/nodes/?filter[title]=phosphocreatine',None),
      ('dryad_metadata','https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.08kprr59v',None),
      ('dryad_files','https://datadryad.org/api/v2/versions/348930/files',None),
      ('dryad_api_download','https://datadryad.org/api/v2/files/3450615/download',None),
      ('dryad_public_download','https://datadryad.org/downloads/file_stream/3450615',None),
      ('biovis','https://biovis.net/2025/biovisChallenges_vis/',None),
      ('frontiers_plantar','https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2020.00622/full',None),
      ('frontiers_arm','https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.599514/full',None)]
    for pmc in ['PMC7332772','PMC3560356','PMC4963215','PMC10450651','PMC13077704','PMC12984577']:
        jobs.append((pmc,'https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML',None))
    with ThreadPoolExecutor(max_workers=6) as pool:records=list(pool.map(lambda x:request(*x),jobs))
    inspected={}
    for r in records:
        if r.get('status')!=200:continue
        text=(CACHE/r['cache']).read_bytes().decode('utf8',errors='replace')
        if r['label']=='figshare_WASF3':
            x=json.loads(text);inspected['WASF3']={k:x.get(k) for k in ['title','doi','version','license','files']}
            for f in x['files']:
                rr=request('WASF3_numeric',f['download_url']);records.append(rr)
                if rr.get('status')==200:
                    data=(CACHE/rr['cache']).read_bytes();assert hashlib.md5(data).hexdigest()==f['computed_md5']
                    z=zipfile.ZipFile(io.BytesIO(data));inspected['WASF3']['archive_members']=[dict(name=i.filename,bytes=i.file_size) for i in z.infolist()]
        if r['label'].startswith('PMC'):
            inspected[r['label']]=dict(doi=re.findall(r'<article-id pub-id-type="doi">(.*?)</article-id>',text),
                supplements=re.findall(r'<supplementary-material[\s\S]*?</supplementary-material>',text),
                availability=re.findall(r'<sec[^>]*>[\s\S]{0,150}?<title>Data [Aa]vailability[\s\S]*?</sec>',text))
        if r['label']=='biovis':inspected['biovis_links']=re.findall(r'href=[\"\x27](.*?)[\"\x27]',text)
        if r['label'].startswith('frontiers'):inspected[r['label']]=sorted(set(re.findall(r'https?[^\s"<>]+(?:\.zip|\.xlsx|\.csv|\.mat)[^\s"<>]*',text)))
    result=dict(date='2026-11-04',scope='targeted reproducible search, not exhaustive systematic review',records=records,inspected=inspected,
        policy='No authentication bypass; unknown-license bytes ignored in Git; archive is downloaded publisher input, no new deliverable ZIP created; no author contact')
    (BASE/'retrieval.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(requests=len(records),statuses={r['label']:r['status'] for r in records}),ensure_ascii=True,indent=2))

if __name__=='__main__':main()
