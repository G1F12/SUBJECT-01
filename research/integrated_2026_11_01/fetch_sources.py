"""Повторное получение источников в tmp; не меняет зафиксированные данные."""
from pathlib import Path
import urllib.request,json,hashlib
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
if __name__=='__main__':
    out=ROOT/'tmp'/'integrated_source_retrieval';out.mkdir(parents=True,exist_ok=True)
    for s in json.loads((BASE/'sources.json').read_text('utf8')):
        for kind in ['metadata','fulltext']:
            url=s.get(kind+'_url')
            if not url:continue
            try:
                raw=urllib.request.urlopen(url,timeout=30).read()
                suffix='.xml' if kind=='fulltext' else '.json'
                (out/(s['id']+'_'+kind+suffix)).write_bytes(raw)
                digest=hashlib.sha256(raw).hexdigest()
                print(s['id'],kind,digest,'MATCH' if digest==s.get(kind+'_sha256') else 'CHANGED: review before reuse')
            except Exception as exc:print(s['id'],kind,type(exc).__name__,str(exc))
