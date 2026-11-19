"""Audit minute-level workload and sparse climate records for EXP-0067."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from openpyxl import load_workbook
from run_audit import text_sha256

HERE = Path(__file__).resolve().parent
path = Path(sys.argv[1])
digest = hashlib.sha256(path.read_bytes()).hexdigest()
assert digest == "499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531"
book = load_workbook(path, read_only=True, data_only=True)
temp = list(book["Core Temp"].values)
work = list(book["Exercise Data"].values)
env = list(book["Environmental Conditions"].values)
demo = list(book["Demographics"].values)

def cols(row,start,end):
    entries = [(value, i) for i,value in enumerate(row[start:end],start) if isinstance(value,int)]
    assert len(entries)==len(dict(entries))
    return dict(entries)

tc = cols(temp[1],2,27)
pc = cols(work[1],77,101)
ac = cols(env[1],2,27)
rc = cols(env[1],27,51)
mass = {row[0]:row[4] for row in demo[1:] if isinstance(row[0],int)}
temperature = {row[1]:row for row in temp[2:] if isinstance(row[1],int)}
power = {}
for row in work[2:]:
    label = row[1]
    if isinstance(label, int):
        label = f"{label-1}-{label}"
    if isinstance(label, str) and "-" in label:
        assert label not in power
        power[label] = row
climate = {row[1]:row for row in env[2:] if isinstance(row[1],str)}
ids = sorted(set(tc)|set(pc)|set(ac)|set(rc))
eligible=[]
for i in ids:
    try:
        vals=[mass[i],temperature[1][tc[i]],temperature[45][tc[i]],temperature[60][tc[i]],power["0-1"][pc[i]],climate["5-6"][ac[i]],climate["5-6"][rc[i]]]
        if not all(isinstance(x,(int,float)) and np.isfinite(x) for x in vals):
            continue
        weight,start,end,late,p,air,rh=vals
        if 30<=weight<=200 and 34<=start<=42 and 34<=end<=43 and 0<p<600 and 0<=air<=50 and 0<=rh<=100:
            eligible.append(i)
    except (KeyError,IndexError):
        continue
assert len(eligible)==23
relative=[]
spans=[]
missing_count=0
climate_spans={"air":[],"rh":[]}
climate_missing={"air":0,"rh":0}
climate_times=[key for key in climate if int(key.split("-")[0])<45]
for i in eligible:
    sequence=[power.get(f"{minute}-{minute+1}",[None]*101)[pc[i]] for minute in range(1,45)]
    if any(not isinstance(v,(int,float)) or not np.isfinite(v) for v in sequence):
        missing_count+=1
    else:
        baseline=power["0-1"][pc[i]]
        relative.append((sum(sequence)-44*baseline)/(44*baseline)*100)
        spans.append(max(sequence)-min(sequence))
    for label, col in (("air",ac[i]),("rh",rc[i])):
        vals=[climate[key][col] for key in climate_times]
        if all(isinstance(v,(int,float)) and np.isfinite(v) for v in vals):
            climate_spans[label].append(max(vals)-min(vals))
        else:
            climate_missing[label]+=1

def summary(values):
    return {"n":len(values),"min":float(np.min(values)),"median":float(np.median(values)),"max":float(np.max(values))} if values else {"n":0}
result={
    "experiment_id":"EXP-0073","classification":"EXPLORATORY_DATA_AUDIT",
    "source_sha256":digest,"protocol_sha256_lf":text_sha256(HERE/"MCLAUGHLIN_WORK_PROTOCOL.md"),
    "numeric_time_labels": "inferred interval end, pending author confirmation",
    "runner_sha256_lf":text_sha256(Path(__file__)),
    "exp0067_eligible_n":len(eligible),"work_complete_n":len(relative),"work_incomplete_n":missing_count,
    "actual_minus_constant_work_percent":summary(relative),"within_person_power_range_W":summary(spans),
    "climate_intervals":climate_times,"climate_missing_participants":climate_missing,
    "within_person_air_range_C":summary(climate_spans["air"]),"within_person_rh_range_percentage_points":summary(climate_spans["rh"]),
}
(HERE/"MCLAUGHLIN_WORK_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
