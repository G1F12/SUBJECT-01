import urllib.request
import ssl
import struct

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://amsacta.unibo.it/7710/1/DPValid_v0.zip'
cd_offset = 2109881225
cd_size = 481810

headers = {'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={cd_offset}-{cd_offset + cd_size - 1}'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as r:
    cd_data = r.read()

print('CD read length:', len(cd_data))

entries = []
pos = 0
while pos < len(cd_data):
    if cd_data[pos:pos+4] != b'\x50\x4b\x01\x02':
        break
    (
        version_made, version_needed, flags, method, mod_time, mod_date,
        crc32, comp_size, uncomp_size, name_len, extra_len, comment_len,
        disk_start, int_attr, ext_attr, local_header_offset
    ) = struct.unpack('<HHHHHHIIIHHHHHII', cd_data[pos+4:pos+46])
    name = cd_data[pos+46:pos+46+name_len].decode('utf-8', errors='replace')
    entries.append({
        'name': name,
        'comp_size': comp_size,
        'uncomp_size': uncomp_size,
        'local_offset': local_header_offset,
        'method': method,
        'crc32': crc32
    })
    pos += 46 + name_len + extra_len + comment_len

print(f'Parsed {len(entries)} file entries.')

csv_entries = [e for e in entries if e['name'].lower().endswith('.csv')]
stl_entries = [e for e in entries if e['name'].lower().endswith('.stl')]
print(f'CSV entries: {len(csv_entries)}, STL entries: {len(stl_entries)}')

total_csv_compressed = sum(e['comp_size'] for e in csv_entries)
print(f'Total CSV compressed size: {total_csv_compressed} bytes ({total_csv_compressed / (1024*1024):.2f} MB)')

# Show some examples
print('\nSample CSV files:')
for e in csv_entries[:15]:
    print(f"  {e['name']} ({e['uncomp_size']} bytes)")
