import urllib.request
import ssl
import struct

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://amsacta.unibo.it/7710/1/DPValid_v0.zip'

# 1. Get file size
req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as r:
    total_size = int(r.headers['Content-Length'])
print(f'Total zip size: {total_size} bytes ({total_size / (1024*1024):.2f} MB)')

# 2. Fetch last 65KB to locate End of Central Directory (EOCD)
tail_size = min(65536, total_size)
headers = {'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={total_size - tail_size}-{total_size - 1}'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as r:
    tail_data = r.read()

print('Tail read bytes:', len(tail_data))
eocd_pos = tail_data.rfind(b'\x50\x4b\x05\x06')
if eocd_pos != -1:
    print('Found standard EOCD at offset:', eocd_pos)
    disk_num, cd_disk, disk_entries, total_entries, cd_size, cd_offset = struct.unpack(
        '<HHHHII', tail_data[eocd_pos+4:eocd_pos+20]
    )
    print(f'Total entries: {total_entries}, CD size: {cd_size}, CD offset: {cd_offset}')
else:
    # Check for zip64
    eocd64_locator = tail_data.rfind(b'\x50\x4b\x06\x07')
    print('Found Zip64 locator:', eocd64_locator != -1)
