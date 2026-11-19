"""Sweep uncertainty in the static torque-to-tendon-force interface."""
import itertools
import json
import math
from pathlib import Path
from run_audit import text_sha256

HERE=Path(__file__).resolve().parent
original=HERE/"CHAIN_TENDON_RESULTS.json"
data=json.loads(original.read_text(encoding="utf-8"))["cases"]
deep=1.1204

def sf(force,csa,uts,rate):
    dynamic=1+0.24*rate*0.18*(1-math.exp(-force/rate/0.18))/force
    axial=force/csa*deep*(1+0.55*(dynamic-1))
    local=axial*math.sqrt(1+3*(0.195*dynamic**0.35)**2)
    return uts/local

out=[]
for pose in ("flexed_100deg_int","extended_140deg_int"):
    group=[x for x in data if x["posture"]==pose and x["scenario"]=="strategy_2_coordinated_chain"]
    for csa,uts,rate in itertools.product((1.0,1.15),(1.0,1.08,1.10),(2000,20000)):
        row=next(x for x in group if x["csa_multiplier"]==csa and x["uts_multiplier"]==uts and x["rate_N_s"]==rate)
        force=row["equivalent_tendon_force_N"]
        def evaluate(mult):
            return sf(force/mult,104*csa,95*uts,rate)
        assert abs(evaluate(1)-row["local_sf"])<0.001
        low,high=0.5,2.0
        assert evaluate(low)<1.5 and evaluate(high)>1.5
        for _ in range(60):
            mid=(low+high)/2
            if evaluate(mid)<1.5: low=mid
            else: high=mid
        assert abs(evaluate(high)-1.5)<1e-10
        values={str(mult):round(evaluate(mult),5) for mult in (0.8,0.9,1.0,1.1,1.2)}
        out.append({"posture":pose,"csa_multiplier":csa,"uts_multiplier":uts,"rate_N_s":rate,"sf_by_arm_multiplier":values,"arm_multiplier_for_sf15":high})
result={"experiment_id":"EXP-0078","classification":"MODEL_ONLY_INTERFACE_SENSITIVITY","protocol_sha256_lf":text_sha256(HERE/"TENDON_INTERFACE_PROTOCOL.md"),"input_sha256_lf":text_sha256(original),"runner_sha256_lf":text_sha256(Path(__file__)),"cases":out}
(HERE/"TENDON_INTERFACE_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
for pose in ("flexed_100deg_int","extended_140deg_int"):
    rows=[x for x in out if x["posture"]==pose]
    thresholds=[x["arm_multiplier_for_sf15"] for x in rows]
    print(pose,"threshold range",min(thresholds),max(thresholds),"within arm 0.8-1.2",sum(0.8<=x<=1.2 for x in thresholds))
