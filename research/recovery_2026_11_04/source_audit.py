"""Snapshot bibliographic/notices and access failures; no claim of exhaustive clearance."""
from pathlib import Path
import urllib.request,urllib.error,urllib.parse,json,hashlib,re
BASE=Path(__file__).resolve().parent
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SUBJECT-01 research/1.0'}),timeout=60) as r:return r.read()
def main():
    out=[]
    for sid,doi in [('SRC-0040','10.1055/a-2940-7047'),('SRC-0041','10.1016/j.dib.2024.111114'),('SRC-0042','10.3389/fphys.2021.692622')]:
        cu='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='');cr=get(cu);obj=json.loads(cr)['message']
        eu='https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query='+urllib.parse.quote('DOI:'+doi)
        ep=get(eu);records=json.loads(ep)['resultList']['result']
        out.append(dict(id=sid,doi=doi,title=obj['title'][0],year=obj['published']['date-parts'][0][0],authors=obj.get('author',[]),accessed='2026-11-04',version='indexed published record retrieved2026-11-04',crossref_url=cu,crossref_response_sha256=hashlib.sha256(cr).hexdigest(),europepmc_url=eu,europepmc_response_sha256=hashlib.sha256(ep).hexdigest(),pmids=[r['id'] for r in records],notices=dict(crossref_relation=obj.get('relation',{}),crossref_update_to=obj.get('update-to',[]),europepmc=[r.get('commentCorrectionList',{}) for r in records]),depth='bibliography, accessible methods/data availability; limited correction/retraction field check, not exhaustive Crossmark/reverse notices'))
    files=json.loads(get('https://datadryad.org/api/v2/versions/348930/files'))
    dryad=dict(dataset_doi='10.5061/dryad.08kprr59v',metadata_version=348930,returned_file_version=314619,files=files['_embedded']['stash:files'],access_attempts=[])
    for url in ['https://datadryad.org/api/v2/files/3450615/download','https://datadryad.org/downloads/file_stream/3450615']:
        try:data=get(url);dryad['access_attempts'].append(dict(url=url,status='downloaded',bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        except urllib.error.HTTPError as e:dryad['access_attempts'].append(dict(url=url,HTTP_status=e.code,status='raw unavailable; no PCr cells inspected'))
    (BASE/'sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    (BASE/'dryad_access.json').write_text(json.dumps(dryad,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    # Inspect actual supplement links in publisher HTML; descriptions alone do not prove raw data.
    url='https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.692622/full'
    html=get(url).decode();links=re.findall(r'https?[^\s"<>]+',html)
    candidates=sorted({x for x in links if ('692622' in x and any(e in x.lower() for e in ['.doc','.xls','.pdf','supplement']))})
    (BASE/'search_log.json').write_text(json.dumps(dict(date='2026-11-04',queries=['phosphocreatine recovery dataset individual time series open data','repeated sprint recovery cycling power data supplementary','PCr VO2 power data availability recovery'],included_actual_files='OSF db3sk Power_rawdata.xlsx, VO2_rawdata.xlsx, version1, hashes in osf_provenance.json',PCr_joint_status='No joint PCr–VO2–power numeric files obtained. Dryad raw blocked. OSF lacks PCr and continuous gas traces.',frontiers_692622_candidates=candidates,frontiers_scope='supplement numeric files not obtained from publisher HTML; participant data availability not verified, not used',other_candidates=[dict(doi='10.1371/journal.pone.0139801',reason='training/recovery over days; running endpoint, not short-pause cycling identification'),dict(doi='10.1371/journal.pone.0219295',reason='running protocol; not selected after suitable independent cycling dataset was obtained')],restrictions='No author contacts or human experiments. No claim of systematic/exhaustive search.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Saved3 bibliographic audits and Dryad access results',dryad['access_attempts'])
if __name__=='__main__':main()
