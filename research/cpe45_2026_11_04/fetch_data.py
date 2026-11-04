"""Retrieve public metadata and CC BY source bytes; never overwrite changed data."""
from pathlib import Path
import hashlib,json,urllib.request,urllib.parse
BASE=Path(__file__).resolve().parent
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SUBJECT-01 research provenance/1.0'}),timeout=90).read()
def preserve(path,data):
    if path.exists() and path.read_bytes()!=data:raise ValueError(f'archived source changed: {path.name}; save a separately dated audit instead')
    path.write_bytes(data)
def main():
    raw=BASE/'data';raw.mkdir(exist_ok=True)
    article=json.loads(fetch('https://api.figshare.com/v2/articles/21704402/versions/1'))
    file=article['files'][0];data=fetch(file['download_url'])
    assert hashlib.md5(data).hexdigest()==file['computed_md5']
    path=raw/file['name']
    preserve(path,data)
    record=dict(article_id=article['id'],version=article['version'],license=article['license'],file=file,sha256=hashlib.sha256(data).hexdigest(),retrieved='2026-11-04',attribution='Chmura P et al. (2022), PLOS ONE 17(12):e0276314, doi:10.1371/journal.pone.0276314')
    preserve(raw/'dataset_provenance.json',(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    dois=['10.1113/jphysiol.1995.sp020533','10.1152/jappl.1996.80.3.876','10.1046/j.1365-201x.1998.00378.x','10.1371/journal.pone.0276314','10.1152/japplphysiol.00144.2009','10.1249/MSS.0000000000000443','10.1249/MSS.0000000000000800','10.1007/s00421-011-2019-8']
    out=[]
    for i,doi in enumerate(dois,32):
        query=urllib.parse.quote('DOI:'+doi)
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query='+query
        ep=fetch(url);crossurl='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
        cr=fetch(crossurl);obj=json.loads(cr)['message'];results=json.loads(ep)['resultList']['result']
        preserve(raw/f'SRC-{i:04d}_europepmc.json',ep)
        # Store only our extracted bibliography/notices, not licensed abstracts/full papers.
        out.append(dict(id=f'SRC-{i:04d}',doi=doi,title=obj['title'][0],year=obj.get('published',{}),url='https://doi.org/'+doi,accessed='2026-11-04',version='published indexed record as retrieved',metadata_url=url,metadata_sha256=hashlib.sha256(ep).hexdigest(),crossref_url=crossurl,crossref_sha256=hashlib.sha256(cr).hexdigest(),notice_check=dict(crossref_relation=obj.get('relation',{}),crossref_update_to=obj.get('update-to',[]),europepmc=[dict(pmid=r.get('id'),commentCorrection=r.get('commentCorrectionList',{}),isRetracted=r.get('isRetracted')) for r in results]),review_depth='bibliography, abstract and selected accessible methods; not exhaustive Crossmark/reverse notice review'))
    preserve(BASE/'sources.json',(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
if __name__=='__main__':main()
