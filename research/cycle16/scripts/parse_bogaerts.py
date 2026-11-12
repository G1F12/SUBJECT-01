import pypdf
import re
import pandas as pd
from pathlib import Path

pdf_path = Path("D:/SUBJECT-01/research/cycle16/Bogaerts_S1_Table.pdf")
out_dir = Path("D:/SUBJECT-01/research/cycle16/data/bogaerts")
out_dir.mkdir(parents=True, exist_ok=True)
out_csv = out_dir / "bogaerts_2017_data.csv"

reader = pypdf.PdfReader(str(pdf_path))

def clean_lines(p):
    return [l.strip() for l in reader.pages[p].extract_text().split('\n') if l.strip()]

rows_l1 = []
rows_l2 = []
rows_l3 = []

# Block 1
rows_l1.extend(clean_lines(0)[1:])
rows_l2.extend([l for l in clean_lines(4)[1:] if 'Displacement' not in l])
rows_l3.extend([l for l in clean_lines(8)[1:] if 'Displacement' not in l])

# Block 2
rows_l1.extend(clean_lines(1))
rows_l2.extend([l for l in clean_lines(5) if 'Displacement' not in l])
rows_l3.extend([l for l in clean_lines(9) if 'Displacement' not in l])

# Block 3
rows_l1.extend(clean_lines(2))
rows_l2.extend([l for l in clean_lines(6) if 'Displacement' not in l])
rows_l3.extend([l for l in clean_lines(10) if 'Displacement' not in l])

# Block 4
rows_l1.extend(clean_lines(3))
rows_l2.extend([l for l in clean_lines(7) if 'Displacement' not in l])
rows_l3.extend([l for l in clean_lines(11) if 'Displacement' not in l])

print(f"Counts: L1={len(rows_l1)}, L2={len(rows_l2)}, L3={len(rows_l3)}")

parsed_records = []
for i in range(len(rows_l1)):
    s1 = rows_l1[i]
    s2 = rows_l2[i]
    s3 = rows_l3[i]
    
    m = re.match(r'(\d+)(Female|Male)\s+(\d+)\s+(\d+)([LR])\s+(PAS|ISO)\s+(\d+)', s1)
    if not m:
        raise ValueError(f"Row {i} L1 mismatch: {s1}")
    patient, gender, age, weight, leg, activation, rep = m.groups()
    
    parts_l2 = [float(p.replace(',', '.')) for p in s2.split()]
    if len(parts_l2) != 7:
        raise ValueError(f"Row {i} L2 mismatch: {s2}")
    time, disp_sup, disp_mid, disp_deep, strain_sup, strain_mid, strain_deep = parts_l2
    
    parts_l3 = [float(p.replace(',', '.')) for p in s3.split()]
    if len(parts_l3) != 5:
        raise ValueError(f"Row {i} L3 mismatch: {s3}")
    torque, disp_diff_sup_mid, disp_diff_mid_deep, strain_diff_sup_mid, strain_diff_mid_deep = parts_l3
    
    parsed_records.append({
        'participant_id': int(patient),
        'gender': gender,
        'age': int(age),
        'weight_kg': float(weight),
        'leg': leg,
        'activation': activation,
        'rep': int(rep),
        'time': int(time),
        'disp_sup_mm': disp_sup,
        'disp_mid_mm': disp_mid,
        'disp_deep_mm': disp_deep,
        'strain_sup_pct': strain_sup,
        'strain_mid_pct': strain_mid,
        'strain_deep_pct': strain_deep,
        'torque_nm_kg': torque,
        'disp_diff_sup_mid_mm': disp_diff_sup_mid,
        'disp_diff_mid_deep_mm': disp_diff_mid_deep,
        'strain_diff_sup_mid_pct': strain_diff_sup_mid,
        'strain_diff_mid_deep_pct': strain_diff_mid_deep
    })

df = pd.DataFrame(parsed_records)
df.to_csv(out_csv, index=False)
print(f"Successfully saved {len(df)} rows to {out_csv}")
print("Head:")
print(df.head(4))
print("Summary stats by activation:")
print(df.groupby('activation')[['strain_sup_pct', 'strain_mid_pct', 'strain_deep_pct', 'torque_nm_kg']].mean())
