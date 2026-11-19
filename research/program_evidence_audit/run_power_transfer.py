"""Participant-held-out transfer of first-two-sprint power to tenth sprint."""
from collections import defaultdict
import csv
import json
from pathlib import Path
import sys
import numpy as np
from sklearn.linear_model import LinearRegression
from run_audit import text_sha256

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/recovery_2026_11_04"))
from dataset import power_rows
chmura_path=ROOT/"research/cpe45_2026_11_04/results/observations.csv"

def aggregate(rows, keys):
    groups=defaultdict(dict)
    for row in rows:
        if row["condition"]!="Thermoneutral": continue
        if row["mean_power_W"]:
            groups[row["participant"]][int(row["repetition"])]=float(row["mean_power_W"])
    return [(int(k),0,v[1],v[2],v[10]) for k,v in groups.items() if all(x in v and v[x]>0 for x in (1,2,10))]

with chmura_path.open(encoding="utf-8",newline="") as f:
    chmura=aggregate(csv.DictReader(f),None)
groups=defaultdict(dict)
for row in power_rows(split="all",unlock=True):
    groups[(row["participant"],row["rest_s"])][row["repetition"]]=row["power_W"]
jutlah=[(person,rest,v[1],v[2],v[10]) for (person,rest),v in groups.items() if all(x in v and v[x]>0 for x in (1,2,10))]
assert len(chmura)>3 and len({r[0] for r in jutlah})>3

def train(rows):
    x=np.array([[r[3]/r[2]] for r in rows])
    y=np.array([r[4]/r[2] for r in rows])
    return LinearRegression().fit(x,y)

def predict(test, train_rows):
    model=train(train_rows)
    return [(r[0],r[4],r[2],float(r[2]*model.predict([[r[3]/r[2]]])[0])) for r in test]

def loso(rows):
    return [item for person in sorted({r[0] for r in rows}) for item in predict([r for r in rows if r[0]==person],[r for r in rows if r[0]!=person])]

def score(rows):
    grouped=defaultdict(list)
    errors=[]
    for person, actual, baseline, estimate in rows:
        grouped[person].append((abs(baseline-actual),abs(estimate-actual)))
        errors.append((baseline-actual,estimate-actual))
    pairs=np.array([np.mean(grouped[p],axis=0) for p in sorted(grouped)])
    delta=pairs[:,0]-pairs[:,1]
    rng=np.random.default_rng(20261120)
    ix=rng.integers(0,len(delta),(10000,len(delta)))
    raw=np.array(errors)
    return {"participants":len(grouped),"conditions":len(rows),
            "participant_weighted_MAE_baseline_W":float(pairs[:,0].mean()),
            "participant_weighted_MAE_linear_W":float(pairs[:,1].mean()),
            "observation_weighted_RMSE_baseline_W":float(np.sqrt(np.mean(raw[:,0]**2))),
            "observation_weighted_RMSE_linear_W":float(np.sqrt(np.mean(raw[:,1]**2))),
            "observation_weighted_bias_baseline_W":float(raw[:,0].mean()),
            "observation_weighted_bias_linear_W":float(raw[:,1].mean()),
            "paired_MAE_baseline_minus_linear_W":float(delta.mean()),
            "paired_ci95_W":np.quantile(delta[ix].mean(axis=1),[.025,.975]).tolist()}

result={"experiment_id":"EXP-0075","classification":"EXPLORATORY_REUSED_DATA",
        "protocol_sha256_lf":text_sha256(HERE/"POWER_TRANSFER_PROTOCOL.md"),
        "runner_sha256_lf":text_sha256(Path(__file__)),"chmura_csv_sha256_lf":text_sha256(chmura_path),
        "jutlah_input_sha256":"b5cb03007190a63dae6a118a7a604cd906273f93febf42957a2e7799df16da20",
        "chmura_loso":score(loso(chmura)),"jutlah_loso":score(loso(jutlah)),
        "chmura_to_jutlah":score(predict(jutlah,chmura))}
(HERE/"POWER_TRANSFER_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
