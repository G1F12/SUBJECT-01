"""Bibliographic access snapshots and finite supplemental retrieval recipes."""
import json,urllib.parse
from concurrent.futures import ThreadPoolExecutor
import retrieve
DOIS=['10.1073/pnas.2302738120','10.3389/fbioe.2020.00622','10.7717/peerj.2259',
      '10.3389/fphys.2021.599514','10.1002/mrm.70337','10.3390/diagnostics16050744','10.1038/srep01182']

def one(pair):
    i,doi=pair;r=retrieve.request('SRC-'+str(i),'https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='/'))
    if r.get('status')!=200:
        failure=r
        r=retrieve.request('SRC-'+str(i)+'_epmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query='+urllib.parse.quote('DOI:'+doi))
        if r.get('status')!=200:raise ValueError(r)
        records=json.loads((retrieve.CACHE/r['cache']).read_bytes())['resultList']['result']
        x=next(v for v in records if v.get('doi','').lower()==doi.lower())
        return dict(id=f'SRC-{i:04d}',doi=doi,title=x['title'],year=int(x['pubYear']),url='https://doi.org/'+doi,metadata=r,crossref_blocker=failure,
            notices=x.get('commentCorrectionList',{}),limits='Indexed bibliography and accessible methods; Crossref rate limited, no exhaustive notices audit')
    x=json.loads((retrieve.CACHE/r['cache']).read_bytes())['message']
    return dict(id=f'SRC-{i:04d}',doi=doi,title=x['title'][0],year=x['published']['date-parts'][0][0],url='https://doi.org/'+doi,
        metadata=r,relations=x.get('relation',{}),update_to=x.get('update-to',[]),
        limits='Bibliography, accessible methods and supplementary file contents where obtained; limited notice fields, not exhaustive retraction/correction audit')

def main():
    x=list(ThreadPoolExecutor(5).map(one,enumerate(DOIS,43)))
    (retrieve.BASE/'sources.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    p=retrieve.BASE/'retrieval.json';x=json.loads(p.read_text('utf8'));labels={r['label'] for r in x['records']}
    for label,pmc in [('plantar_supp','PMC7332772'),('peerj_supp','PMC4963215'),('diagnostics_supp','PMC12984577')]:
        if label not in labels:x['records'].append(retrieve.request(label,'https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/supplementaryFiles'))
    x['web_searches']=[dict(query=q,conclusion=c) for q,c in [
      ('phosphocreatine oxygen uptake dataset Dryad','Dryad08kprr59v metadata accessible; raw401/403; no mirror numeric file obtained'),
      ('phosphocreatine site:physionet.org','No applicable result returned; not exhaustive PhysioNet inventory'),
      ('31P MRS Participants1-10','York/Mendeley DOI10.17632/3r7kmfmpyj.1 is brain photobiomodulation; excluded, no exercise power; raw not downloaded'),
      ('phosphocreatine VO2 dataset Figshare Zenodo OSF','API results and exclusions summarized in DATA_AUDIT.md; numericWASF3,plantar,PeerJ obtained')]]
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Saved seven bibliographic audits and supplemental recipes')

if __name__=='__main__':main()
