import urllib.request
import ssl
import struct
import zlib
from pathlib import Path
import pandas as pd
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(str(Path(__file__).parent))
from parse_central_dir import csv_entries

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://amsacta.unibo.it/7710/1/DPValid_v0.zip'

out_dir = Path("D:/SUBJECT-01/research/cycle16/data/dpvalid")
out_dir.mkdir(parents=True, exist_ok=True)

def fetch_zip_member_bytes(entry):
    offset = entry['local_offset']
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

# 1. Fetch Demographics if needed
demo_path = out_dir / "Demographics.csv"
if not demo_path.exists():
    demo_entry = [e for e in csv_entries if 'Demographics.csv' in e['name']][0]
    demo_bytes = fetch_zip_member_bytes(demo_entry)
    with open(demo_path, 'wb') as f:
        f.write(demo_bytes)
    print(f"Saved {demo_path}")

# 2. Plan files to download
subjects = [f"HA{i:02d}" for i in range(1, 21)]
conditions = [
    ('EXT_75', 'e75', 'extension', 75),
    ('EXT_90', 'e90', 'extension', 90),
    ('FLEX_75', 'f75', 'flexion', 75),
    ('FLEX_90', 'f90', 'flexion', 90)
]

download_tasks = [] # (entry, local_path)

for subj in subjects:
    subj_dir = out_dir / subj
    subj_dir.mkdir(parents=True, exist_ok=True)
    for cond_dir, cond_code, action, angle in conditions:
        t_name = f"{subj}_{cond_code}_torques_filt_max.csv"
        t_matches = [e for e in csv_entries if t_name in e['name'] and subj in e['name']]
        if t_matches:
            target = subj_dir / t_name
            if not target.exists():
                download_tasks.append((t_matches[0], target))
        
        for r_num in range(1, 5):
            r_str = f"r{r_num}"
            emg_name = f"{subj}_{cond_code}_emg_env_max_{r_str}.csv"
            emg_matches = [e for e in csv_entries if emg_name in e['name'] and subj in e['name']]
            if emg_matches:
                target = subj_dir / emg_name
                if not target.exists():
                    download_tasks.append((emg_matches[0], target))

print(f"Tasks to download: {len(download_tasks)}")

def download_one(item):
    entry, target_path = item
    try:
        data = fetch_zip_member_bytes(entry)
        target_path.write_bytes(data)
        return True
    except Exception as ex:
        print(f"Failed {target_path.name}: {ex}")
        return False

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_one, item) for item in download_tasks]
    done_count = 0
    for fut in as_completed(futures):
        if fut.result():
            done_count += 1
        if done_count % 25 == 0 or done_count == len(download_tasks):
            print(f"Downloaded {done_count}/{len(download_tasks)} files...")

# 3. Parse all files and assemble dataset
records = []
for subj in subjects:
    subj_dir = out_dir / subj
    for cond_dir, cond_code, action, angle in conditions:
        t_name = f"{subj}_{cond_code}_torques_filt_max.csv"
        t_path = subj_dir / t_name
        if not t_path.exists():
            continue
        
        t_text = t_path.read_text(encoding='utf-8', errors='ignore').strip()
        t_lines = [l.strip() for l in t_text.split('\n') if l.strip()]
        if len(t_lines) < 2:
            continue
        sep = ';' if ';' in t_lines[0] else ','
        t_header = [x.strip() for x in t_lines[0].split(sep)]
        t_vals = [float(x.strip()) for x in t_lines[1].split(sep)]
        torque_map = dict(zip(t_header, t_vals))
        
        for r_num in range(1, len(t_vals) + 1):
            r_str = f"r{r_num}"
            if r_str not in torque_map:
                continue
            torque_val = torque_map[r_str]
            emg_name = f"{subj}_{cond_code}_emg_env_max_{r_str}.csv"
            emg_path = subj_dir / emg_name
            if not emg_path.exists():
                continue
            
            emg_text = emg_path.read_text(encoding='utf-8', errors='ignore').strip()
            emg_lines = [l.strip() for l in emg_text.split('\n') if l.strip()]
            if len(emg_lines) < 2:
                continue
            e_sep = ';' if ';' in emg_lines[0] else ','
            emg_headers = [x.strip() for x in emg_lines[0].split(e_sep)]
            emg_vals = [float(x.strip()) for x in emg_lines[1].split(e_sep)]
            emg_map = dict(zip(emg_headers, emg_vals))
            
            rec = {
                'participant_id': subj,
                'action': action,
                'angle_deg': angle,
                'condition_code': cond_code,
                'rep': r_str,
                'torque_nm': torque_val,
                'emg_BF': emg_map.get('BF', None),
                'emg_ST': emg_map.get('ST', None),
                'emg_RF': emg_map.get('RF', None),
                'emg_VM': emg_map.get('VM', None),
                'emg_VL': emg_map.get('VL', None),
                'emg_GL': emg_map.get('GL', None),
                'emg_VL_contra': emg_map.get('VL_2', None),
                'emg_BF_contra': emg_map.get('BF_2', None),
            }
            records.append(rec)

df_trials = pd.DataFrame(records)
demo_df = pd.read_csv(demo_path, sep=';')
demo_df.columns = [c.strip().lower() for c in demo_df.columns]
demo_df = demo_df.rename(columns={'id': 'participant_id'})

df_merged = pd.merge(df_trials, demo_df, on='participant_id', how='left')
merged_csv = out_dir / "dpvalid_isometric_trials.csv"
df_merged.to_csv(merged_csv, index=False)
print(f"Successfully assembled {len(df_merged)} rows to {merged_csv}")
print(df_merged.groupby(['action', 'angle_deg'])['torque_nm'].agg(['count', 'mean', 'std', 'min', 'max']))
