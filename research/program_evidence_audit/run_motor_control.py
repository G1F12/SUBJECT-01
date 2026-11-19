"""Paired exercise-rest contrasts in participant-level Stroop outcomes."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from run_audit import text_sha256

HERE=Path(__file__).resolve().parent
source=Path(sys.argv[1])
digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest=="11e53a0d89651a1851c496c5061a675f0744904c1b627f6065146e553d80c9fc"
with source.open(encoding="utf-8-sig",newline="") as stream:
    records=list(csv.DictReader(stream,delimiter="\t"))
assert len({r["id"] for r in records})==len(records)
categories=("neg","pos","neu")
sessions=("ex_pre","ex_post","re_pre","re_post")
accepted=[]
excluded=0
for row in records:
    try:
        values={}
        for metric in ("rt","acc","n"):
            for category in categories:
                for session in sessions:
                    value=float(row[f"{metric}_{category}_{session}"])
                    assert np.isfinite(value)
                    if metric=="rt": assert value>0
                    if metric=="acc": assert 0<=value<=1
                    if metric=="n": assert value>0 and value.is_integer()
                    values[(metric,category,session)]=value
        contrasts={}
        for metric in ("rt","acc"):
            means={session:np.mean([values[(metric,c,session)] for c in categories]) for session in sessions}
            contrasts[metric]=(means["ex_post"]-means["ex_pre"])-(means["re_post"]-means["re_pre"])
        accepted.append((row["order"],contrasts["rt"],contrasts["acc"]))
    except (KeyError,ValueError,AssertionError):
        excluded+=1
assert len(accepted)>1
rng=np.random.default_rng(20261120)
ix=rng.integers(0,len(accepted),(10000,len(accepted)))
result={}
for index,metric in ((1,"reaction_time_ms"),(2,"accuracy_fraction")):
    values=np.array([r[index] for r in accepted])
    result[metric]={"mean":float(values.mean()),"median":float(np.median(values)),"ci95":np.quantile(values[ix].mean(axis=1),[.025,.975]).tolist()}
out={"experiment_id":"EXP-0076","classification":"EXPLORATORY_PAIRED_AGGREGATE_DATA",
     "source_sha256":digest,"protocol_sha256_lf":text_sha256(HERE/"MOTOR_CONTROL_PROTOCOL.md"),
     "runner_sha256_lf":text_sha256(Path(__file__)),"rows":len(records),"included":len(accepted),"excluded":excluded,
     "order_counts":{order:sum(r[0]==order for r in accepted) for order in sorted({r[0] for r in accepted})},
     "contrasts_exercise_change_minus_rest_change":result}
(HERE/"MOTOR_CONTROL_RESULTS.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
