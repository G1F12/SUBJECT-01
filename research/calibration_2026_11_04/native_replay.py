"""Optional live native-member retrieval and real snapshot derivation, no refitting."""
import json,zipfile,contextlib,io
from unittest.mock import patch
from acquire import BASE,CACHE,RangeFile,digest,verify_native_cache
import dataset,weee,physionet
from reproduce import equal

def check():
    verify_native_cache()
    p=json.loads((BASE/'weee_retrieval.json').read_text('utf8'))
    listing=json.loads((BASE/'weee_listing.json').read_text('utf8'))
    missing=[r for r in p['files'] if not (CACHE/r['cache']).exists()]
    if missing:
        f=listing['archive'];z=zipfile.ZipFile(RangeFile(f['links']['self'],f['size']))
        for r in missing:
            b=z.read(r['member']);assert digest(b)==r['sha256'];(CACHE/r['cache']).write_bytes(b)
    for r in p['files']:assert digest((CACHE/r['cache']).read_bytes())==r['sha256']
    for split in ['development','test']:
        stages,recovery,baseline=dataset.collect(split,unlock=True)
        old=json.loads((BASE/f'{split}_stage_audit.json').read_text('utf8'))
        assert equal(stages,old['stages']) and equal(recovery,old['recovery']) and equal(baseline,old['baseline']),split
    captured={}
    def capture(path,x):captured[path.name]=x
    with contextlib.redirect_stdout(io.StringIO()),patch.object(weee,'save',capture):weee.build()
    with patch.object(physionet,'save',capture):physionet.probe()
    for name,x in captured.items():assert equal(x,json.loads((BASE/name).read_text('utf8'))),name
    print('PASS native public file hashes/CRC and measured stage summaries for three separate cohorts; no fitting, locks unchanged')

if __name__=='__main__':check()
