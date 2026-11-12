from parse_central_dir import csv_entries
from test_fetch_single import fetch_zip_member

t_max_entry = [e for e in csv_entries if 'HA01_e75_torques_filt_max.csv' in e['name']][0]
t_max_bytes = fetch_zip_member(t_max_entry)
print('Torques filt max:')
print(t_max_bytes.decode('utf-8'))

emg_max_entry = [e for e in csv_entries if 'HA01_e75_emg_env_max_r1.csv' in e['name']][0]
emg_max_bytes = fetch_zip_member(emg_max_entry)
print('EMG env max r1:')
print(emg_max_bytes.decode('utf-8'))
