"""Download selected raw-data files for EXP-0084; verify ZIP CRC and SHA256."""
import hashlib, io, json, sys, urllib.request
from pathlib import Path
from zipfile import ZipFile
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'MOMENT_HOLDOUT_INPUTS.json').read_text(encoding='utf-8'))
url=manifest['raw_archive_url']; size=manifest['raw_archive_size']; root=Path(sys.argv[1])
class Remote(io.RawIOBase):
 def __init__(self): self.pos=0
 def seekable(self): return True
 def readable(self): return True
 def tell(self): return self.pos
 def seek(self,offset,whence=0):
  self.pos=offset if whence==0 else self.pos+offset if whence==1 else size+offset; return self.pos
 def read(self,n=-1):
  n=size-self.pos if n<0 else min(n,size-self.pos)
  if not n: return b''
  start=self.pos; end=start+n-1; req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
  with urllib.request.urlopen(req,timeout=90) as r:
   if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{size}': raise ValueError('incorrect range')
   data=r.read()
  if len(data)!=n: raise ValueError('incomplete download')
  self.pos+=n; return data
with ZipFile(Remote()) as z:
 for record in manifest['files']:
  if not record['path'].startswith('raw/'): continue
  data=z.read(record['path'][4:])
  if hashlib.sha256(data).hexdigest()!=record['sha256']: raise ValueError('source hash mismatch')
  path=root/record['path']; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
  print(record['path'],len(data),flush=True)
print('Processed files require retrieve_squat_data.py into <root>/files')
