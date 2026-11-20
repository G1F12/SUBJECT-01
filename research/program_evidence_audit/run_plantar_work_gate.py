#!/usr/bin/env python3
"""Reproducible structural audit; does not infer the article cohort or physical sign."""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
import openpyxl

HERE = Path(__file__).resolve().parent
HASHES = ["c38628fa2a682ca784f9254d51c2b373b831f0e39929e3ea8640bdd368db3dcd", "d58b3e596fb7a5d9d8aa91e511112e7fa4a6e6b98cbe7a3fad2c7d20d518a541"]
def sha(b): return hashlib.sha256(b).hexdigest()
def run(zpath, xpath):
    zb, xb = zpath.read_bytes(), xpath.read_bytes()
    if [sha(zb), sha(xb)] != HASHES: raise ValueError("input SHA-256 mismatch")
    tab = openpyxl.load_workbook(io.BytesIO(xb), read_only=True, data_only=True).active
    rows = list(tab.iter_rows(min_row=3, values_only=True))
    data = {str(r[0]):r for r in rows if r[0]}
    z = zipfile.ZipFile(io.BytesIO(zb))
    names = sorted(n for n in z.namelist() if n.endswith(".xlsx"))
    counts = {"sheets":0,"finite_rows":0,"bad_rows":0,"bad_rows_before_final_sample":0,"time_steps":0,"non_100hz_steps":0,"duration_matches":0,"start_angle_matches":0,"end_angle_matches":0,"summary_mapping_comparisons":0}
    examples=[]
    for n in names:
        idx=int(n[len("Subjekt"):len("Subjekt")+2]); sid=f"S{idx:03}"
        if sid not in data: raise ValueError("missing summary id "+sid)
        wb=openpyxl.load_workbook(io.BytesIO(z.read(n)), read_only=True, data_only=True)
        for j, sheet in enumerate(wb):
            if j>=6: raise ValueError("unexpected sheet count")
            a=[]; bad_before_last=0; pending_bad=0
            for row in sheet.iter_rows(min_row=2,values_only=True):
                try:
                    v=tuple(float(x) for x in row[:4])
                    if len(v)!=4 or not all(math.isfinite(x) for x in v): raise ValueError()
                    a.append(v); bad_before_last+=pending_bad; pending_bad=0
                except (ValueError,TypeError): counts["bad_rows"]+=1; pending_bad+=1
            counts["bad_rows_before_final_sample"]+=bad_before_last
            if len(a)<2: raise ValueError("empty segment")
            counts["sheets"]+=1; counts["finite_rows"]+=len(a)
            dt=[a[i][0]-a[i-1][0] for i in range(1,len(a))]
            counts["time_steps"]+=len(dt); counts["non_100hz_steps"]+=sum(abs(x-0.01)>1e-6 for x in dt)
            summary=data[sid]; base=13+7*j
            dur, start, end = summary[base:base+3]
            counts["summary_mapping_comparisons"]+=1
            counts["duration_matches"]+=abs((a[-1][0]-a[0][0])-float(dur))<0.011
            counts["start_angle_matches"]+=abs(a[0][1]-float(start))<1e-5
            counts["end_angle_matches"]+=abs(a[-1][1]-float(end))<1e-5
            # Both integrals use the complete exported segment; no assumption about physical muscle work sign.
            wa=sum((x[2]+y[2])*0.5*math.radians(y[1]-x[1]) for x,y in zip(a,a[1:]))
            wt=sum((x[2]*x[3]+y[2]*y[3])*0.5*math.radians(y[0]-x[0]) for x,y in zip(a,a[1:]))
            examples.append((wa,wt))
        if len(wb.sheetnames)!=6: raise ValueError("unexpected sheet count")
    diffs=[abs(a-b) for a,b in examples]
    sums=[abs(a+b) for a,b in examples]
    return {"input_sha256":HASHES,"archive_files":len(names),"summary_ids":len(data),"ids_match":len(names)==len(data),"published_participants":20,"table_sex_code_counts":{str(k):sum(r[1]==k for r in data.values()) for k in (1,2)},"structure":counts,"angular_and_speed_integral_abs_difference_J":{"median":sorted(diffs)[len(diffs)//2],"max":max(diffs)},"angular_and_speed_integral_opposite_sign_abs_sum_J":{"median":sorted(sums)[len(sums)//2],"max":max(sums)},"limitations":"Audit only; no allocation of the 21 rows to the 20-person article cohort; segment signs not validated; work is not an effect or equal-work comparison."}
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("zip",type=Path);ap.add_argument("table",type=Path);args=ap.parse_args()
    result=run(args.zip,args.table)
    out=json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    (HERE/"PLANTAR_WORK_GATE_RESULTS.json").write_text(out,encoding="utf-8",newline="\n")
    print(out)
