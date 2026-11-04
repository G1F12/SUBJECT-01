"""Cycle6 public acquisition, including bounded HTTP Range ZIP reading. No auth bypass."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,io,zipfile
BASE=Path(__file__).resolve().parent;CACHE=BASE.parents[1]/'tmp/calibration_raw'
def digest(b):return hashlib.sha256(b).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def fetch(label,url,body=None):
    CACHE.mkdir(parents=True,exist_ok=True)
    try:
        req=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,headers={'User-Agent':'SUBJECT-01 public research audit','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=30) as r:b=r.read();status=r.status;ctype=r.headers.get('Content-Type')
        (CACHE/(label+'.bin')).write_bytes(b)
        return dict(label=label,url=url,status=status,content_type=ctype,bytes=len(b),sha256=digest(b),cache=label+'.bin')
    except Exception as e:return dict(label=label,url=url,status=getattr(e,'code',None),error=str(e),numeric_obtained=False)

class RangeFile(io.RawIOBase):
    def __init__(self,url,size):self.url=url;self.size=size;self.pos=0;self.requests=[];self.blocks={}
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        if self.pos<0:raise ValueError('negative offset')
        return self.pos
    def read(self,n=-1):
        if n<0:n=self.size-self.pos
        n=min(n,self.size-self.pos)
        if n==0:return b''
        if n>100_000_000:raise ValueError('bounded public extraction, request too large')
        parts=[];left=n
        while left:
            start=self.pos//1048576*1048576;end=min(self.size-1,start+1048575)
            if start not in self.blocks:
                req=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}','User-Agent':'SUBJECT-01 public range retrieval'})
                with urllib.request.urlopen(req,timeout=45) as r:
                    if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/'):raise ValueError('server did not honor public byte range; full multiGB download refused')
                    b=r.read(end-start+2)
                if len(b)!=end-start+1:raise ValueError('truncated range')
                self.requests.append(dict(start=start,end=end,bytes=len(b),sha256=digest(b)));self.blocks[start]=b
            offset=self.pos-start;take=min(left,len(self.blocks[start])-offset)
            parts.append(self.blocks[start][offset:offset+take]);self.pos+=take;left-=take
        return b''.join(parts)

def list_lendt():
    meta=fetch('lendt_metadata','https://zenodo.org/api/records/13477128')
    x=json.loads((CACHE/meta['cache']).read_bytes());f=x['files'][0];r=RangeFile(f['links']['self'],f['size'])
    z=zipfile.ZipFile(r);members=[dict(name=i.filename,bytes=i.file_size,compressed=i.compress_size,CRC32=i.CRC) for i in z.infolist()]
    save(BASE/'lendt_listing.json',dict(metadata=meta,doi=x['doi'],version=x['metadata']['version'],license=x['metadata']['license'],archive=f,members=members,range_requests=r.requests,
        archive_checksum_status='advertised whole-fileMD5, NOT verified because only public ranges obtained; extracted members get CRC32 and SHA256'))
    print(json.dumps([m for m in members if any(s in m['name'].lower() for s in ['cpet','log_master','readme','ee_','metabolic','stage'])],ensure_ascii=True,indent=2))

def extract_members(names):
    x=json.loads((BASE/'lendt_listing.json').read_text('utf8'));f=x['archive'];r=RangeFile(f['links']['self'],f['size']);z=zipfile.ZipFile(r);out=[]
    for name in names:
        dest=CACHE/Path(name).name
        if dest.exists():
            import binascii
            b=dest.read_bytes()
            if len(b)!=z.getinfo(name).file_size or binascii.crc32(b)!=z.getinfo(name).CRC:raise ValueError('cached source mismatch')
        else:b=z.read(name)  # zipfile checks original CRC32 after decompression
        dest=CACHE/Path(name).name
        if dest.exists() and dest.read_bytes()!=b:raise ValueError('source member changed')
        dest.write_bytes(b)
        out.append(dict(member=name,cache=dest.name,bytes=len(b),sha256=digest(b),CRC32=z.getinfo(name).CRC,archive_url=f['links']['self'],doi=x['doi'],version=x['version'],license=x['license']))
    return out,r.requests

def retrieve_cpet():
    from concurrent.futures import ThreadPoolExecutor
    x=json.loads((BASE/'lendt_listing.json').read_text('utf8'))
    names=[m['name'] for m in x['members'] if '/CPET/' in m['name'] and m['name'].endswith(('_cycle.csv','_walk.csv'))]
    files,requests=extract_members(names)
    save(BASE/'cpet_retrieval.json',dict(files=files,requests=requests,total_range_bytes=sum(r['bytes'] for r in requests),raw_policy='publicCCBY4; raw cache ignored; no new ZIP created'))
    print('Obtained',len(files),'native CSV members with CRC32/SHA256; rangebytes',sum(r['bytes'] for r in requests))

def verify_native_cache():
    x=json.loads((BASE/'cpet_retrieval.json').read_text('utf8'))['files']
    missing=[f['member'] for f in x if not (CACHE/f['cache']).exists()]
    if missing:extract_members(missing)
    for f in x:
        if digest((CACHE/f['cache']).read_bytes())!=f['sha256']:raise ValueError('pinned native member mismatch: '+f['member'])
    print('PASS',len(x),'native member SHA256; no provenance snapshot overwritten')

if __name__=='__main__':
    import sys
    if '--verify-cache' in sys.argv:verify_native_cache()
    elif '--cpet' in sys.argv:retrieve_cpet()
    else:list_lendt()
