import io,urllib.request,zipfile,sys,hashlib,json
from pathlib import Path
root=Path(sys.argv[1]); manifest=[]
archives=[('raw','0c050d51-54f0-4ccf-9bcd-65521c0e20c3',28559821099,[f'{p}/CSV_Data/squats_1/GroundFrame_GRFs.csv' for p in ('AB01','AB02')]),('files','03f9679f-28ce-4d8b-b195-4b3b1aa4adc9',13378286332,[f'{p}/squats_1_0lbs/{p}_squats_1_0lbs_grf.csv' for p in ('AB01','AB02')])]
for label,uid,size,names in archives:
 url=f'https://repository.gatech.edu/server/api/core/bitstreams/{uid}/content'
 class Remote(io.RawIOBase):
  def __init__(self):self.pos=0
  def seekable(self):return True
  def readable(self):return True
  def tell(self):return self.pos
  def seek(self,o,w=0):self.pos=o if w==0 else self.pos+o if w==1 else size+o;return self.pos
  def read(self,n=-1):
   n=size-self.pos if n<0 else min(n,size-self.pos)
   if not n:return b''
   a=self.pos;b=a+n-1;req=urllib.request.Request(url,headers={'Range':f'bytes={a}-{b}'})
   with urllib.request.urlopen(req,timeout=90) as r:
    assert r.status==206 and r.headers['Content-Range']==f'bytes {a}-{b}/{size}';data=r.read()
   assert len(data)==n;self.pos+=n;return data
 with zipfile.ZipFile(Remote()) as z:
  for name in names:
   data=z.read(name);p=root/label/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);manifest.append({'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'archive_url':url,'archive_size':size});print(name,len(data),flush=True)
expected=json.loads((Path(__file__).resolve().parent/'MOMENT_DIAGNOSTIC_INPUTS.json').read_text(encoding='utf-8'))['files']; assert manifest==expected; print('SHA-256 manifest verified')
