"""Replay the McLaughlin thermal model with time-varying inputs."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from run_audit import text_sha256

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
audit_path = HERE/"run_mclaughlin_work_audit.py"
audit_source = audit_path.read_text(encoding="utf-8")
section = audit_source.split("relative=[]")[0]
context = {"__name__":"work_input_loader","__file__":str(audit_path)}
exec(compile(section,str(audit_path),"exec"), context)
eligible=context["eligible"]
power=context["power"]
climate=context["climate"]
pc,ac,rc,tc=(context[k] for k in ("pc","ac","rc","tc"))
mass=context["mass"]
temps=context["temperature"]
assert len(eligible)==23

solver_path=ROOT/"research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py"
solver_source=solver_path.read_text(encoding="utf-8")
needle="        if step % trace_stride == 0:"
assert solver_source.count(needle)==1
replacement="""        p_now = float(power_schedule(t_now))
        temp_amb_C, rel_humidity = climate_schedule(t_now)
        if step % trace_stride == 0:"""
solver_context={"__name__":"scheduled_solver","__file__":str(solver_path)}
exec(compile(solver_source.replace(needle,replacement),str(solver_path),"exec"),solver_context)
solver=solver_context["simulate_4layer_pennes_2700s"]
control_context={"__name__":"reference_solver","__file__":str(solver_path)}
exec(compile(solver_source,str(solver_path),"exec"),control_context)
reference=control_context["simulate_4layer_pennes_2700s"]

modes=("constant","variable","shift_minus","shift_plus","variable_climate")
observed=[]
predicted={m:[] for m in modes}
work_joules={m:[] for m in modes}
for participant in eligible:
    initial=power["0-1"][pc[participant]]
    air=climate["5-6"][ac[participant]]
    humidity=climate["5-6"][rc[participant]]/100
    recorded=[power[f"{k}-{k+1}"][pc[participant]] for k in range(0,46)]
    assert all(isinstance(x,(float,int)) and 0 < x < 600 for x in recorded)
    series=[(5,air,humidity)]
    for minute in (9,20,24,35,39):
        row=climate[f"{minute}-{minute+1}"]
        series.append((minute,row[ac[participant]],row[rc[participant]]/100))
    expected_change=temps[45][tc[participant]]-temps[1][tc[participant]]
    observed.append(expected_change)
    kwargs={"body_mass_kg":mass[participant],"dt_s":5.0}
    reference_run=reference(initial,1.0,air,humidity,**kwargs)
    for mode in modes:
        shift={"constant":0,"variable":0,"shift_minus":-1,"shift_plus":1,"variable_climate":0}[mode]
        def power_schedule(t, mode=mode, shift=shift):
            if mode=="constant":
                return initial
            return recorded[max(0,min(45,1+int(t//60)+shift))]
        def climate_schedule(t, mode=mode):
            if mode!="variable_climate":
                return air,humidity
            absolute=1+t/60
            chosen=series[0]
            for record in series:
                if record[0]<=absolute:
                    chosen=record
            return chosen[1],chosen[2]
        solver_context["power_schedule"]=power_schedule
        solver_context["climate_schedule"]=climate_schedule
        run=solver(initial,1.0,air,humidity,**kwargs)
        assert run["energy_balance_error_J"]<0.001
        trace={r["time_s"]:r["T_core_C"] for r in run["trace_30s"]}
        predicted[mode].append(trace[2640]-trace[0])
        work_joules[mode].append(sum(power_schedule(t)*5 for t in range(0,2640,5)))
        if mode=="constant":
            assert run==reference_run
    assert abs(work_joules["variable"][-1] - sum(recorded[1:45])*60)<1e-6

observed=np.array(observed)
indices=np.random.default_rng(20261120).integers(0,len(observed),size=(10000,len(observed)))
errors={m:abs(np.asarray(predicted[m])-observed) for m in modes}
outcomes={}
for mode in modes:
    residual=np.asarray(predicted[mode])-observed
    difference=errors["constant"]-errors[mode]
    outcomes[mode]={"mae_C":float(errors[mode].mean()),"bias_C":float(residual.mean()),"mean_work_J":float(np.mean(work_joules[mode])),"paired_constant_minus_mode_mae_C":float(difference.mean()),"paired_ci95_C":np.quantile(difference[indices].mean(axis=1),[.025,.975]).tolist()}
result={"experiment_id":"EXP-0074","classification":"EXPLORATORY_REUSED_DATA","source_sha256":context["digest"],"protocol_sha256_lf":text_sha256(HERE/"MCLAUGHLIN_VARIABLE_PROTOCOL.md"),"runner_sha256_lf":text_sha256(Path(__file__)),"n":len(eligible),"timestamp_assumption":"numeric labels are interval ends, pending confirmation","outcomes":outcomes}
(HERE/"MCLAUGHLIN_VARIABLE_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
