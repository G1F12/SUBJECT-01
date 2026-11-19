"""Retrieve pre-specified squat series using ZIP byte ranges; verify entry CRC."""
import concurrent.futures, hashlib, io, json, re, struct, sys, urllib.request, zlib
from pathlib import Path
from zipfile import ZipFile
URL='https://repository.gatech.edu/server/api/core/bitstreams/03f9679f-28ce-4d8b-b195-4b3b1aa4adc9/content'
SIZE=13378286332
out=Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True)
def fetch(start,end):
 req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}'})
 with urllib.request.urlopen(req,timeout=90) as r:
  if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{SIZE}': raise ValueError('invalid range response')
  b=r.read()
 if len(b)!=end-start+1: raise ValueError('incomplete range')
 return b
class Remote(io.RawIOBase):
 def __init__(self): self.pos=0
 def seekable(self): return True
 def readable(self): return True
 def tell(self): return self.pos
 def seek(self,off,whence=0):
  self.pos=off if whence==0 else self.pos+off if whence==1 else SIZE+off; return self.pos
 def read(self,n=-1):
  n=SIZE-self.pos if n<0 else min(n,SIZE-self.pos)
  if not n: return b''
  b=fetch(self.pos,self.pos+n-1); self.pos+=n; return b
with ZipFile(Remote()) as z:
 infos=[i for i in z.infolist() if re.fullmatch(r'AB\d+/squats_\d+_(?:0|25)lbs/AB\d+_squats_\d+_(?:0|25)lbs_(?:angle|velocity|moment_filt|activity_flag)\.csv',i.filename)]
def extract(i):
 start=i.header_offset; end=min(SIZE-1,start+30+65535*2+i.compress_size)
 b=fetch(start,end)
 if b[:4]!=b'PK\x03\x04': raise ValueError(i.filename)
 n,e=struct.unpack_from('<HH',b,26); data=b[30+n+e:30+n+e+i.compress_size]
 raw=zlib.decompress(data,-15) if i.compress_type==8 else data if i.compress_type==0 else None
 if raw is None or len(raw)!=i.file_size or zlib.crc32(raw)!=i.CRC: raise ValueError('CRC/size mismatch '+i.filename)
 p=out/i.filename; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)
 return {'path':i.filename,'size':len(raw),'crc32':f'{i.CRC:08x}','sha256':hashlib.sha256(raw).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: records=list(pool.map(extract,infos))
(out/'manifest.json').write_text(json.dumps({'source':URL,'archive_size':SIZE,'archive_md5_publisher_only':'3d8e5dbd208da9c0030c6d117e2e33a1','files':records},indent=2)+'\n',encoding='utf-8')
print('Extracted',len(records),'files across',len({x['path'].split('/')[0] for x in records}),'participants')
