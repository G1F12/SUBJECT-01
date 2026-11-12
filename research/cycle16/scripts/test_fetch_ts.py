from parse_central_dir import csv_entries
from test_fetch_single import fetch_zip_member

t_ts_entry = [e for e in csv_entries if 'HA01_e75_torques_filt_data.csv' in e['name']][0]
t_ts_bytes = fetch_zip_member(t_ts_entry)
print('Torques filt data lines (first 5):')
for line in t_ts_bytes.decode('utf-8').splitlines()[:5]:
    print(' ', line)

emg_ts_entry = [e for e in csv_entries if 'HA01_e75_emg_nEnv_data_r1.csv' in e['name']][0]
emg_ts_bytes = fetch_zip_member(emg_ts_entry)
print('EMG nEnv data r1 lines (first 5):')
for line in emg_ts_bytes.decode('utf-8').splitlines()[:5]:
    print(' ', line)
