import urllib.request
import ssl
import struct
import zlib
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://amsacta.unibo.it/7710/1/DPValid_v0.zip'

def fetch_zip_member(entry):
    offset = entry['local_offset']
    # Read local header (30 bytes + name + extra)
    headers = {'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={offset}-{offset + 100}'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as r:
        header_data = r.read()
    
    assert header_data[:4] == b'\x50\x4b\x03\x04', 'Invalid local header'
    name_len, extra_len = struct.unpack('<HH', header_data[26:30])
    data_start = offset + 30 + name_len + extra_len
    data_end = data_start + entry['comp_size'] - 1
    
    headers = {'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={data_start}-{data_end}'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as r:
        compressed_data = r.read()
        
    if entry['method'] == 0:
        return compressed_data
    elif entry['method'] == 8:
        decompressor = zlib.decompressobj(-15)
        return decompressor.decompress(compressed_data)
    else:
        raise ValueError(f"Unsupported compression method {entry['method']}")

# Test fetching Demographics.csv
from parse_central_dir import csv_entries

demo_entry = [e for e in csv_entries if 'Demographics.csv' in e['name']][0]
print('Fetching:', demo_entry['name'])
demo_bytes = fetch_zip_member(demo_entry)
print('Demographics content:')
print(demo_bytes.decode('utf-8'))
