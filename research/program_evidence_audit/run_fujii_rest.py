"""Investigate initial thermal drift using the pre-exercise Fujii windows."""
from collections import defaultdict
from datetime import datetime, time, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from statistics import mean

import numpy as np
from openpyxl import load_workbook
from run_audit import load_runner, sha256, text_sha256
from run_thermal_transfer import FILES, metadata

HERE = Path(__file__).resolve().parent
data_dir = Path(sys.argv[1])
for name, expected in FILES.items():
    assert sha256(data_dir/name) == expected
characteristics, sessions = metadata(data_dir/"metadata.xlsx")
book = load_workbook(data_dir/"metadata.xlsx", read_only=True, data_only=True)
available = set()
month_day = None
temperatures = []
for row in book["Timing"].values:
    head = re.match(r"^(\d+)/(\d+)\s", str(row[0]))
    if head:
        month_day = (int(head[1]), int(head[2]))
        temperatures = [int(re.match(r"\d+", str(row[i]))[0]) for i in (2,6,10)]
    elif row[1] in characteristics:
        for col, ambient in zip((2,6,10), temperatures):
            rest, onset, wind = row[col:col+3]
            if not all(isinstance(t, time) for t in (rest, onset, wind)):
                continue
            arbitrary = datetime(2000, 1, 1)
            if datetime.combine(arbitrary, onset) - timedelta(seconds=285) >= datetime.combine(arbitrary, rest):
                available.add((row[1], month_day, ambient, onset, wind))
sessions = [session for session in sessions if session in available]
by_date = defaultdict(list)
for i,(person, date, ambient, onset, wind) in enumerate(sessions):
    by_date[(person, *date)].append(i)
years = defaultdict(set)
windows = defaultdict(dict)
duplicates = set()
book = load_workbook(data_dir/"dataset.xlsx", read_only=True, data_only=True)
rows = iter(book["pred20250509"].values)
assert next(rows)[:4] == ("time", "participant id", "day #", "T_es")
for timestamp, person, _, observed, *_ in rows:
    if not isinstance(timestamp, datetime):
        continue
    for i in by_date.get((person, timestamp.month, timestamp.day), ()):
        years[i].add(timestamp.year)
        if not isinstance(observed, (int,float)) or not math.isfinite(observed):
            continue
        onset = datetime.combine(timestamp.date(), sessions[i][3])
        relative = (timestamp - onset).total_seconds()
        for offset in (-270, 0):
            if abs(relative-offset) <= 15:
                key=(i,offset)
                if timestamp in windows[key]:
                    duplicates.add(key)
                windows[key][timestamp] = observed
cases=[]
for i,(person, date, ambient, onset, wind) in enumerate(sessions):
    keys=((i,-270),(i,0))
    if len(years[i]) == 1 and all(k not in duplicates and len(windows[k]) >= 21 for k in keys):
        cases.append((person,ambient,mean(windows[keys[1]].values())-mean(windows[keys[0]].values())))
assert len(cases) > 0
module = load_runner(63)
source_path = HERE.parent/"exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py"
source = source_path.read_text(encoding="utf-8")
old = "T = np.array([37.0, 35.8, 34.0, 33.0], dtype=float)"
assert source.count(old)==1
context={"__name__":"uniform_initial_model","__file__":str(source_path)}
exec(compile(source.replace(old,"T = np.array([37.0, 37.0, 37.0, 37.0], dtype=float)").replace("T_art = 36.85","T_art = 37.0"),str(source_path),"exec"),context)
models={"nominal":module.simulate_4layer_pennes_2700s,"uniform":context["simulate_4layer_pennes_2700s"]}
scores={}
for initial, solver in models.items():
    for mode in ("rest","exercise"):
        person_errors=defaultdict(list)
        for person, ambient, observed in cases:
            mass, power = characteristics[person]
            output=solver(0 if mode=="rest" else power,1.0,ambient,0.5,body_mass_kg=mass)
            trace={row["time_s"]:row["T_core_C"] for row in output["trace_30s"]}
            predicted=trace[270]-trace[0]
            person_errors[person].append((abs(predicted-observed),predicted-observed,predicted))
        values=np.array([np.mean(v,axis=0) for _,v in sorted(person_errors.items())])
        scores[f"{initial}_{mode}"]={"mae_C":float(values[:,0].mean()),"bias_C":float(values[:,1].mean()),"mean_predicted_change_C":float(values[:,2].mean())}
baseline=defaultdict(list)
for person, ambient, observed in cases: baseline[person].append(observed)
result={"experiment_id":"EXP-0071","classification":"EXPLORATORY_OBSERVED_REST_AND_MODEL_SENSITIVITY","protocol_sha256_lf":text_sha256(HERE/"FUJII_REST_PROTOCOL.md"),"runner_sha256_lf":text_sha256(Path(__file__)),"source_sha256":FILES,"eligible_sessions":len(cases),"eligible_participants":len(baseline),"mean_observed_change_C":float(mean(mean(v) for v in baseline.values())),"persistence_mae_C":float(mean(mean(abs(x) for x in v) for v in baseline.values())),"scores":scores}
(HERE/"FUJII_REST_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
