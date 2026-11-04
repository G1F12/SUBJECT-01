"""CPE45 energy-ledger surrogate, SI. No physiological efficacy/safety prediction."""
from pathlib import Path
import importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('subject01_integrated',ROOT/'research/integrated_2026_11_01/model.py')
integrated=importlib.util.module_from_spec(spec);spec.loader.exec_module(integrated)
sys.path.insert(0,str(ROOT))
from tools import cpe45
BASE=Path(__file__).resolve().parent

def load():return json.loads((BASE/'config.json').read_text('utf8'))
def approach(x,target,dt,tau):return target+(x-target)*math.exp(-dt/tau)

def allocate(aerobic,metabolic,fast,slow,d,h):
    """Shared ATP-equivalent reserve ledger for translation and cycling tests, joules."""
    need=max(0.,metabolic-aerobic)
    take_fast=min(fast*(1-math.exp(-h/d['fast_discharge_tau_s'])),need)
    take_slow=min(slow*(1-math.exp(-h/d['slow_discharge_tau_s'])),max(0.,need-take_fast))
    if need>take_fast+take_slow+1e-5:raise ArithmeticError('unpaid work')
    fast-=take_fast;slow-=take_slow;add_fast=add_slow=0.
    if need<1e-10:
        surplus=max(0.,aerobic-metabolic)
        add_fast=min((d['fast_capacity_J']-fast)*(1-math.exp(-h/d['fast_recovery_tau_s'])),surplus*d['recharge_efficiency'])
        surplus-=add_fast/d['recharge_efficiency']
        add_slow=min((d['slow_capacity_J']-slow)*(1-math.exp(-h/d['slow_recovery_tau_s'])),surplus*d['recharge_efficiency'])
        fast+=add_fast;slow+=add_slow
    return fast,slow,add_fast+add_slow,take_fast+take_slow

def protocol(config,name):
    """Exact event boundaries; patterned scenarios are explicitly not measured protocols."""
    pattern=config['protocols'][name];out=[];t=0.
    while t<config['duration_s']:
        for part in pattern:
            end=min(config['duration_s'],t+part['duration_s'])
            out.append(dict(start_s=t,end_s=end,**part))
            t=end
            if t>=config['duration_s']:break
    return out

def validate(config,p,d,dt):
    integrated.validate(p)
    if not math.isfinite(dt) or not 0<dt<=1:raise ValueError('dt in (0,1] s')
    if not math.isfinite(config['duration_s']) or config['duration_s']<=0:raise ValueError('duration')
    if not math.isfinite(config['fatigue_reference_W']) or config['fatigue_reference_W']<=0:raise ValueError('fatigue_reference_W')
    expected=set(load()['dynamic'])
    if set(d)!=expected:raise ValueError('dynamic schema')
    for k,v in d.items():
        if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<0:raise ValueError(k)
    for k in expected-{'fast_capacity_J','slow_capacity_J','fatigue_rate_s_inv','slow_component_max_W'}:
        if d[k]<=0:raise ValueError(k)
    if d['recharge_efficiency']>1 or d['fatigue_floor']>1:raise ValueError('fraction')
    for parts in config['protocols'].values():
        if not parts:raise ValueError('empty pattern')
        for part in parts:
            if part['duration_s']<=0 or not math.isfinite(part['duration_s']) or not 0<=part['intensity']<=1 or part['kind'] not in ('effort','recovery'):raise ValueError('protocol')

def simulate(config=None,name='mixed',architecture='baseline',climate='temperate',dt=.25,overrides=None,integrated_overrides=None,keep_trace=True):
    config=load() if config is None else config
    p=integrated.load();p.update(config['architectures'][architecture]);p.update(config['climates'][climate]);p.update(integrated_overrides or {})
    d=dict(config['dynamic']);d.update(overrides or {});validate(config,p,d,dt)
    eps=protocol(config,name);mass=p['body_mass_kg']+p['added_contractile_kg']+p['support_mass_kg']
    cap=integrated.energy(p)['aerobic_W'];maintenance=integrated.energy(p)['maintenance_W']
    if cap<maintenance:raise ValueError('baseline maintenance cannot be paid aerobically')
    fast=d['fast_capacity_J'];slow=d['slow_capacity_J'];initial=fast+slow
    oxygen=maintenance;fatigue=0.;slow_component=0.;heat=0.;sweat=0.;v=0.;t=0.;epi=0
    sums={k:0. for k in ['oxidative_J','external_J','internal_J','heat_generated_J','heat_lost_J','recharged_J','withdrawn_J','unmet_work_J','braking_J','drag_J']}
    trace=[];episodes=[];limiting={'mechanical':0.,'energetic':0.};current=None
    while t<config['duration_s']-1e-9:
        ep=eps[epi];h=min(dt,ep['end_s']-t,config['duration_s']-t)
        if current is None:
            current=dict(start_s=t,end_s=ep['end_s'],kind=ep['kind'],task_id=ep['task_id'],work_J=0.,force_integral_Ns=0.,peak_force_N=0.,peak_power_W=0.,speed_integral_m=0.,peak_speed_m_s=0.,peak_acceleration_m_s2=0.,fast_start_J=fast,slow_start_J=slow,fatigue_start=fatigue)
        # Peripheral surrogate acts on contractile force and shortening speed before tendon/contact caps.
        available=max(d['fatigue_floor'],1-fatigue)
        pp=dict(p,specific_tension_Pa=p['specific_tension_Pa']*available,fiber_vmax_m_s=p['fiber_vmax_m_s']*math.sqrt(available))
        force_cap=integrated.horizontal_force(pp,v)
        requested=force_cap*ep['intensity']
        resistance=integrated.drag(p,v)
        # Recovery/maneuver is a loaded translational surrogate. Brake work exits to environment.
        brake=mass*v/d['braking_tau_s'] if ep.get('brake',False) else 0.
        free_v=max(0.,v-(resistance+brake)*h/mass)
        raw_v=max(0.,v+(requested-resistance-brake)*h/mass)
        def mechanics(nv):
            distance=.5*(v+nv)*h
            external=max(0.,.5*mass*(nv*nv-v*v)+(resistance+brake)*distance)
            internal=p['internal_work_J_kg_m']*mass*distance
            return external,internal,distance
        ext,internal,distance=mechanics(raw_v)
        recharge_need=(d['fast_capacity_J']-fast)/d['fast_recovery_tau_s']+(d['slow_capacity_J']-slow)/d['slow_recovery_tau_s']
        slow_target=d['slow_component_max_W']*ep['intensity'] if ep['kind']=='effort' else 0.
        slow_component=approach(slow_component,slow_target,h,d['slow_component_tau_s'])
        target=min(cap,maintenance+(ext+internal)/(p['delta_efficiency']*h)+slow_component+recharge_need/d['recharge_efficiency'])
        oxygen=approach(oxygen,target,h,d['oxygen_tau_s'])
        ox=oxygen*h
        overhead=min(ox, (maintenance+slow_component)*h)
        aerobic=max(0.,ox-overhead)
        fast_budget=min(fast,fast*(1-math.exp(-h/d['fast_discharge_tau_s'])))
        slow_budget=min(slow,slow*(1-math.exp(-h/d['slow_discharge_tau_s'])))
        budget=(aerobic+fast_budget+slow_budget)*p['delta_efficiency']
        demanded=ext+internal
        if demanded>budget:
            lo,hi=free_v,raw_v
            for _ in range(32):
                mid=(lo+hi)/2;a,b,_=mechanics(mid)
                if a+b<=budget:lo=mid
                else:hi=mid
            raw_v=lo;ext,internal,distance=mechanics(raw_v)
            # If even unpowered coasting internal cost exceeds budget, it cannot be paid.
            # Treat as external passive motion: cap internal dissipation; record unpaid demand.
            internal=min(internal,max(0.,budget-ext))
            limiting['energetic']+=h
        else:limiting['mechanical']+=h
        mech=ext+internal;metabolic=mech/p['delta_efficiency']
        fast,slow,recharge,withdraw=allocate(aerobic,metabolic,fast,slow,d,h)
        # Exact first law: oxidative input + reserve withdrawal = external work + body heat + stored reserve.
        generated=ox+withdraw-recharge-ext
        sweat_target=min(p['evaporated_water_kg_s'],max(0.,generated/h)/p['latent_J_kg']+max(0.,heat)/d['sweat_feedback_J_s_kg'])
        sweat=approach(sweat,sweat_target,h,d['sweat_tau_s'])
        skin=p['skin_K']+d['skin_fraction']*heat/integrated.heat_capacity(p)
        thermal=dict(p,skin_K=skin,evaporated_water_kg_s=sweat)
        loss=integrated.heat_loss(thermal)[0]*h
        heat+=generated-loss
        exertion=(mech/h)/max(1.,config['fatigue_reference_W'])
        target_fatigue=d['fatigue_rate_s_inv']*exertion
        recovery_tau=d['fatigue_recovery_tau_s']
        fatigue=fatigue*math.exp(-h/recovery_tau)+target_fatigue*recovery_tau*(1-math.exp(-h/recovery_tau))
        fatigue=min(1-d['fatigue_floor'],fatigue)
        accel=(raw_v-v)/h
        actual_force=ext/distance if distance>0 else 0.
        power=ext/h
        vals=dict(oxidative_J=ox,external_J=ext,internal_J=internal,heat_generated_J=generated,heat_lost_J=loss,recharged_J=recharge,withdrawn_J=withdraw,unmet_work_J=max(0,demanded-mech),braking_J=brake*distance,drag_J=resistance*distance)
        for k,x in vals.items():sums[k]+=x
        current['work_J']+=ext;current['force_integral_Ns']+=actual_force*h;current['peak_force_N']=max(current['peak_force_N'],actual_force);current['peak_power_W']=max(current['peak_power_W'],power)
        current['speed_integral_m']+=distance;current['peak_speed_m_s']=max(current['peak_speed_m_s'],raw_v);current['peak_acceleration_m_s2']=max(current['peak_acceleration_m_s2'],accel)
        t=round(t+h,10)
        if keep_trace:
            trace.append(dict(time_s=t,interval_start_s=t-h,task_id=ep['task_id'],kind=ep['kind'],power_W=power,force_N=actual_force,force_cap_N=force_cap,speed_m_s=raw_v,acceleration_m_s2=accel,fast_J=fast,slow_J=slow,oxygen_W=oxygen,vo2_L_min=oxygen/p['oxygen_energy_J_m3']*60000,available_contractile_fraction=1-fatigue,slow_component_W=slow_component,stored_heat_J=heat,body_delta_K=heat/integrated.heat_capacity(p),sweat_kg_s=sweat,**sums))
        v=raw_v
        if abs(t-ep['end_s'])<1e-8:
            duration=t-current['start_s']
            current.update(mean_power_W=current['work_J']/duration,mean_force_N=current['force_integral_Ns']/duration,mean_speed_m_s=current['speed_integral_m']/duration,fast_end_J=fast,slow_end_J=slow,fatigue_end=fatigue)
            episodes.append(current);current=None;epi+=1
    efforts=[e for e in episodes if e['kind']=='effort']
    early=[e for e in efforts if e['end_s']<=config['early_end_s']];late=[e for e in efforts if e['start_s']>=config['late_start_s']]
    matched={}
    for task in sorted({e['task_id'] for e in early}&{e['task_id'] for e in late}):
        a=[e for e in early if e['task_id']==task];b=[e for e in late if e['task_id']==task]
        avg=lambda rows,key:sum(e[key] for e in rows)/len(rows)
        matched[task]={key:dict(early=avg(a,key),late=avg(b,key),late_over_early=cpe45.ratio(avg(b,key),avg(a,key))) for key in ['mean_power_W','peak_power_W','mean_force_N','peak_force_N','mean_speed_m_s']}
    residual=sums['oxidative_J']+initial-fast-slow-sums['external_J']-sums['heat_generated_J']
    kinetic_residual=sums['external_J']-.5*mass*v*v-sums['drag_J']-sums['braking_J']
    summary=dict(architecture=architecture,climate=climate,protocol=name,duration_s=t,dt_s=dt,mass_kg=mass,fast_J=fast,slow_J=slow,available_contractile_fraction=1-fatigue,stored_heat_J=heat,body_delta_K=heat/integrated.heat_capacity(p),thermal_envelope_exceeded=heat/integrated.heat_capacity(p)>p['allowed_delta_K'],terminal_speed_m_s=v,energy_residual_J=residual,kinetic_residual_J=kinetic_residual,heat_residual_J=heat-sums['heat_generated_J']+sums['heat_lost_J'],early_late=matched,limiting_seconds=limiting,**sums,reaction=None,accuracy=None,coordination=None,tissue_damage=None,post45_status='not_measured; terminal states are model states only',validation_status='not_empirically_validated',target_achievement='not_assessed',intervention_status='NO_GO')
    return summary,trace,episodes

def measurement_bridge(trace,episodes):
    """Use existing measurement module without inventing coordination observations.

    Its strict Sample schema requires measured errors. Only mechanical profiles are
    called using explicitly synthetic zero placeholders, which are removed from output.
    Full analyze is deliberately not called: no accuracy/coordination observations exist.
    """
    samples=[cpe45.Sample(0,trace[0]['power_W'],trace[0]['force_N'],0,trace[0]['acceleration_m_s2'],0,0)]
    samples += [cpe45.Sample(r['time_s'],r['power_W'],r['force_N'],r['speed_m_s'],r['acceleration_m_s2'],0,0) for r in trace]
    profile=cpe45.profile(samples,0,2700)
    return {k:v for k,v in profile.items() if 'error' not in k} | dict(origin='simulated mechanical channels only; trapezoidal sampled estimate; authoritative work is finite-volume ledger',reaction=None,accuracy=None,coordination=None)
