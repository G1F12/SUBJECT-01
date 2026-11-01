"""Связанная модель ограничений; все внутренние величины SI. Не цифровой двойник."""
from pathlib import Path
import json, math
import numpy as np
BASE=Path(__file__).resolve().parent

def load():
    return {k:v['value'] for k,v in json.loads((BASE/'parameters.json').read_text('utf8')).items()}

def validate(p):
    schema=json.loads((BASE/'parameters.json').read_text('utf8'))
    if set(p)!=set(schema): raise ValueError('Неполный/неизвестный набор параметров')
    for k,v in p.items():
        lo,hi=schema[k]['bounds']
        if not math.isfinite(v) or not lo<=v<=hi: raise ValueError(k)
    if p['venous_content']>p['arterial_content']: raise ValueError('Cv > Ca')
    if p['skin_K']<=0 or p['air_K']<=0 or p['radiant_K']<=0:raise ValueError('Kelvin')

def muscle(p, shortening_m_s=0):
    area=p['pcsa_m2']+p['added_contractile_kg']/(p['tissue_density_kg_m3']*p['fiber_length_m']*p['parallel_groups'])
    fl=math.exp(-((p['normalized_length']-1)/p['fl_width'])**2)
    z=max(0,shortening_m_s)/p['fiber_vmax_m_s']
    fv=max(0,(1-z)/(1+z/p['hill_curvature']))
    f=p['specific_tension_Pa']*area*fl*fv*math.cos(p['pennation_rad'])
    # Операционный предел нагрузки; не разрывная/усталостная прочность.
    tendon=p['tendon_area_m2']*p['tendon_stress_Pa']
    bone=p['bone_load_cap_N']
    return min(f,tendon,bone),f,tendon

def heat_capacity(p):
    mass=p['body_mass_kg']+p['added_contractile_kg']+p['support_mass_kg']
    return mass*p['heat_capacity_J_kg_K']

def heat_loss(p):
    hc=p['hc_W_m2_K']*math.sqrt(max(p['air_speed_m_s'],.1)/p['air_speed_reference_m_s'])
    area=p['surface_area_m2']
    dry=hc*area*(p['skin_K']-p['air_K'])+p['emissivity']*5.670374419e-8*area*(p['skin_K']**4-p['radiant_K']**4)
    def vapor(t):
        c=t-273.15
        return .61078*math.exp(17.27*c/(c+237.3))  # kPa
    emax=max(0,16.5*hc*area*(vapor(p['skin_K'])-p['relative_humidity']*vapor(p['air_K'])))
    evaporative=min(p['evaporated_water_kg_s']*p['latent_J_kg'],emax)
    return dry+evaporative,dry,evaporative

def energy(p):
    vo2=p['cardiac_output_m3_s']*(p['arterial_content']-p['venous_content'])
    aerobic=vo2*p['oxygen_energy_J_m3']
    maintenance=p['metabolic_intercept_W']+p['maintenance_W_kg']*(p['added_contractile_kg']+p['support_mass_kg'])
    loss,dry,evap=heat_loss(p)
    heat_budget=loss+heat_capacity(p)*p['allowed_delta_K']/p['duration_s']
    oxygen_cap=max(0,(aerobic-maintenance)*p['delta_efficiency'])
    thermal_cap=max(0,(heat_budget-maintenance)*p['delta_efficiency']/(1-p['delta_efficiency']))
    return dict(vo2_m3_s=vo2,aerobic_W=aerobic,maintenance_W=maintenance,heat_loss_W=loss,dry_W=dry,evaporative_W=evap,oxygen_mechanical_W=oxygen_cap,thermal_mechanical_W=thermal_cap)

def horizontal_force(p,v):
    # Эффективная передача от одного агрегированного сустава к COM.
    ratio=p['moment_arm_m']/p['external_lever_m']*p['geometry_projection']
    u=ratio*v
    transmitted,_,_=muscle(p,u)
    joint_cap=p['parallel_groups']*transmitted*ratio
    # Независимый эмпирический предел применения силы к опоре.
    envelope=p['sprint_F0_N']*max(0,1-v/p['sprint_v0_m_s'])*p['contact_scale']
    m=p['body_mass_kg']+p['added_contractile_kg']+p['support_mass_kg']
    friction=p['friction_coefficient']*m*9.80665
    return min(joint_cap,envelope,friction)

def drag(p,v):return .5*p['air_density_kg_m3']*p['CdA_m2']*v*v

def evaluate(p):
    validate(p)
    e=energy(p); f,raw,tc=muscle(p)
    m=p['body_mass_kg']+p['added_contractile_kg']+p['support_mass_kg']
    speeds=np.linspace(0,p['sprint_v0_m_s'],201)
    forces=np.array([horizontal_force(p,float(v)) for v in speeds])
    peak=float(np.max(forces*speeds))
    lo,hi=0.,p['sprint_v0_m_s']
    for _ in range(50):
        v=(lo+hi)/2
        if horizontal_force(p,v)>drag(p,v):lo=v
        else:hi=v
    power=min(peak,e['oxygen_mechanical_W'],e['thermal_mechanical_W'])
    # Внутренняя работа включена как неопределённый расход на единицу пути.
    lo_s,hi_s=0.,hi
    for _ in range(50):
        v=(lo_s+hi_s)/2
        demand=drag(p,v)*v+p['internal_work_J_kg_m']*m*v
        if demand<=power:lo_s=v
        else:hi_s=v
    heat=e['maintenance_W']+power*(1/p['delta_efficiency']-1)
    storage=heat-e['heat_loss_W']
    # Компоненты задержки — неидентифицируемое разложение измеренной суммы.
    latency=p['sensory_s']+p['processing_s']+p['transmission_s']+p['execution_s']
    effective_latency=max(0,latency-p['prediction_horizon_s'])
    prediction_error=math.hypot(p['sensor_noise_m'],.5*p['unexpected_acceleration_m_s2']*p['prediction_horizon_s']**2)
    bottleneck=min([('механика',peak),('кислород',e['oxygen_mechanical_W']),('тепло',e['thermal_mechanical_W'])],key=lambda x:x[1])[0]
    return dict(steady_feasible=(e['maintenance_W']<=e['heat_loss_W']+heat_capacity(p)*p['allowed_delta_K']/p['duration_s']+1e-9 and e['maintenance_W']<=e['aerobic_W']),incremental_compliance_m_N=1/p['tendon_stiffness_N_m'],mass_kg=m,force_N=f,muscle_unclipped_N=raw,tendon_operating_cap_N=tc,torque_Nm=f*p['moment_arm_m'],peak_horizontal_W=peak,terminal_sprint_m_s=hi,sustainable_external_W=power,sustainable_proxy_m_s=hi_s,latency_s=latency,effective_latency_s=effective_latency,prediction_error_m=prediction_error,stored_heat_J=storage*p['duration_s'],delta_temperature_K=storage*p['duration_s']/heat_capacity(p),bottleneck=bottleneck,**e)

def sprint(p,seconds=6.,dt=.01):
    """Энергетически ограниченное ускорение, конечный анаэробный резерв."""
    if not math.isfinite(seconds) or not math.isfinite(dt) or not 0<dt<=seconds<=60:raise ValueError('seconds/dt')
    validate(p);e=energy(p);m=p['body_mass_kg']+p['added_contractile_kg']+p['support_mass_kg']
    v=x=work=reserve_used=heat=maintenance_paid=maintenance_deficit=aerobic_used=0.; reserve=p['anaerobic_reserve_J']; rows=[]
    for i in range(round(seconds/dt)):
        t=i*dt;force=horizontal_force(p,v)
        # За шаг точно оплачивается прирост кинетической энергии + работа против drag.
        d=drag(p,v); next_v=max(0,v+(force-d)/m*dt)
        delta_ke=.5*m*(next_v**2-v*v)
        distance=.5*(v+next_v)*dt
        mech=delta_ke+d*distance+p['internal_work_J_kg_m']*m*distance
        aerobic_total=e['aerobic_W']*(1-math.exp(-t/p['oxygen_tau_s']))*dt
        maintenance_need=e['maintenance_W']*dt
        reserve_for_maintenance=min(reserve,max(0,maintenance_need-aerobic_total))
        reserve-=reserve_for_maintenance;reserve_used+=reserve_for_maintenance
        paid=min(maintenance_need,aerobic_total+reserve_for_maintenance)
        maintenance_paid+=paid;maintenance_deficit+=maintenance_need-paid
        aerobic=max(0,aerobic_total-maintenance_need)
        budget=(aerobic+reserve)*p['delta_efficiency']
        if mech>budget:
            low,high=0.,next_v
            for _ in range(35):
                nv=(low+high)/2;ds=.5*(v+nv)*dt
                needed=.5*m*(nv*nv-v*v)+d*ds+p['internal_work_J_kg_m']*m*ds
                if needed<=budget:low=nv
                else:high=nv
            next_v=low;distance=.5*(v+next_v)*dt
            mech=.5*m*(next_v*next_v-v*v)+d*distance+p['internal_work_J_kg_m']*m*distance
        mech=max(0,mech)
        metabolic=mech/p['delta_efficiency'];used=max(0,metabolic-aerobic)
        reserve=max(0,reserve-used);reserve_used+=used
        heat+=metabolic-mech+paid
        aerobic_used+=min(aerobic_total,maintenance_need)+min(metabolic,aerobic)
        work+=mech;x+=distance;v=next_v
        if i%10==0:rows.append(dict(time_s=round((i+1)*dt,6),speed_m_s=v,distance_m=x,reserve_J=reserve))
    return dict(speed_m_s=v,distance_m=x,mechanical_work_J=work,metabolic_work_J=work/p['delta_efficiency'],heat_generated_J=heat,reserve_used_J=reserve_used,reserve_remaining_J=reserve,maintenance_paid_J=maintenance_paid,maintenance_deficit_J=maintenance_deficit,aerobic_used_J=aerobic_used),rows
