"""TARGET-CPE45: измерение временных рядов, без модели физиологии/вердикта успеха."""
from dataclasses import dataclass, asdict, fields
from bisect import bisect_right
from statistics import mean
import argparse
import json
import math
from pathlib import Path

DURATION_S = 2700.0

@dataclass(frozen=True)
class Sample:
    time_s: float
    power_W: float
    force_N: float
    speed_m_s: float
    acceleration_m_s2: float
    coordination_error_m: float
    maneuver_error_m: float

@dataclass(frozen=True)
class Episode:
    start_s: float
    end_s: float
    kind: str  # effort/recovery; задаётся протоколом, не классификатором мощности
    task_id: str  # включает внешний demand, методику и условия сопоставимости

@dataclass(frozen=True)
class Trial:
    time_s: float  # время предъявления стимула
    task_id: str
    latency_s: float | None
    correct: bool
    omitted: bool = False

CHANNELS = tuple(f.name for f in fields(Sample) if f.name != 'time_s')

def number(x, name):
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
        raise ValueError(f'{name}: требуется конечное число; пропуски не заполняются')
    return x

def label(x, name):
    if not isinstance(x, str) or not x.strip():raise ValueError(name)

def ratio(late, early):
    return late / early if early != 0 else None

def validate_samples(samples, max_gap_s, *, main):
    if not samples or (main and len(samples) < 2):raise ValueError('пустой/неполный ряд')
    previous = None
    for row in samples:
        for k, v in asdict(row).items():number(v, k)
        if any(getattr(row,k) < 0 for k in ('force_N','speed_m_s','coordination_error_m','maneuver_error_m')):
            raise ValueError('модуль силы, скорость и ошибки должны быть неотрицательны')
        if previous is not None and not 0 < row.time_s-previous <= max_gap_s:
            raise ValueError('нестрогое время или разрыв больше разрешённого протоколом')
        previous = row.time_s
    if main and (samples[0].time_s != 0 or samples[-1].time_s != DURATION_S):
        raise ValueError('основной ряд должен покрывать ровно [0,2700] s')
    if not main and samples[0].time_s <= DURATION_S:
        raise ValueError('post измеряется отдельно, строго после 2700 s')

def interpolate(samples, t):
    times = [s.time_s for s in samples]
    if not times[0] <= t <= times[-1]:raise ValueError('экстраполяция запрещена')
    i = bisect_right(times,t)-1
    if times[i] == t:return samples[i]
    left,right = samples[i],samples[i+1]
    w = (t-left.time_s)/(right.time_s-left.time_s)
    return Sample(t, **{k:getattr(left,k)*(1-w)+getattr(right,k)*w for k in CHANNELS})

def profile(samples, start, end):
    number(start,'profile start');number(end,'profile end')
    if end < start:raise ValueError('обратное окно')
    points = [interpolate(samples,start)]
    points += [s for s in samples if start < s.time_s < end]
    if end > start:points.append(interpolate(samples,end))
    totals = {k:0. for k in CHANNELS}
    positive = negative = 0.
    for left,right in zip(points,points[1:]):
        dt = right.time_s-left.time_s
        for k in CHANNELS:totals[k] += .5*(getattr(left,k)+getattr(right,k))*dt
        a,b = left.power_W,right.power_W
        if a*b < 0:
            # Точный интеграл положительной/отрицательной части линейного сегмента.
            crossing = dt*abs(a)/(abs(a)+abs(b))
            for p,length in [(a,crossing),(b,dt-crossing)]:
                positive += .5*max(0,p)*length
                negative += .5*min(0,p)*length
        else:
            positive += .5*(max(a,0)+max(b,0))*dt
            negative += .5*(min(a,0)+min(b,0))*dt
    duration = end-start
    avg = {k:(totals[k]/duration if duration else getattr(points[0],k)) for k in CHANNELS}
    return dict(start_s=start,end_s=end,duration_s=duration,work_net_J=totals['power_W'],
                work_positive_J=positive,work_negative_J=negative,path_length_m=totals['speed_m_s'],
                mean_power_W=avg['power_W'],peak_power_W=max(s.power_W for s in points),
                mean_force_N=avg['force_N'],peak_force_N=max(s.force_N for s in points),
                mean_speed_m_s=avg['speed_m_s'],peak_speed_m_s=max(s.speed_m_s for s in points),
                peak_acceleration_m_s2=max(s.acceleration_m_s2 for s in points),
                min_acceleration_m_s2=min(s.acceleration_m_s2 for s in points),
                mean_coordination_error_m=avg['coordination_error_m'],
                mean_maneuver_error_m=avg['maneuver_error_m'])

def reactions(trials, start, end, task=None, include_end=False):
    chosen = [x for x in trials if start <= x.time_s and (x.time_s < end or include_end and x.time_s == end)
              and (task is None or x.task_id == task)]
    answered = [x.latency_s for x in chosen if not x.omitted]
    correct = [x.latency_s for x in chosen if x.correct]
    return dict(trials=len(chosen),omissions=sum(x.omitted for x in chosen),
                accuracy=mean(x.correct for x in chosen) if chosen else None,
                mean_response_latency_s=mean(answered) if answered else None,
                mean_correct_latency_s=mean(correct) if correct else None)

def comparison(early, late):
    # Знак не обрезается: потенциация/улучшение не маскируются под нулевой decrement.
    keys = ['mean_power_W','peak_power_W','mean_force_N','peak_force_N',
            'mean_speed_m_s','peak_speed_m_s','peak_acceleration_m_s2','min_acceleration_m_s2',
            'mean_coordination_error_m','mean_maneuver_error_m']
    return {k:dict(early=early[k],late=late[k],late_over_early=ratio(late[k],early[k]),
                   relative_drop=(early[k]-late[k])/early[k] if early[k] else None,
                   absolute_change=late[k]-early[k]) for k in keys}

def analyze(samples, episodes, trials=(), *, early_end_s, late_start_s, max_gap_s,
            post_samples=None, post_task_id=None):
    """Все окна и допустимый gap задаёт протокол. Успех цели не классифицируется."""
    for k,v in [('early_end_s',early_end_s),('late_start_s',late_start_s),('max_gap_s',max_gap_s)]:number(v,k)
    if not 0 < early_end_s <= late_start_s < DURATION_S or max_gap_s <= 0:
        raise ValueError('неправильные окна/допустимый gap')
    validate_samples(samples,max_gap_s,main=True)
    if not episodes:raise ValueError('нет эпизодов')
    boundary = 0.
    for ep in episodes:
        number(ep.start_s,'start');number(ep.end_s,'end');label(ep.task_id,'task_id')
        if ep.kind not in ('effort','recovery') or ep.start_s != boundary or ep.end_s <= ep.start_s:
            raise ValueError('эпизоды должны без перекрытий/дыр разбивать [0,2700]')
        boundary = ep.end_s
    if boundary != DURATION_S or {e.kind for e in episodes} != {'effort','recovery'}:
        raise ValueError('требуются полная длительность, усилия и восстановление')
    if post_samples is not None:
        label(post_task_id,'post_task_id');validate_samples(post_samples,max_gap_s,main=False)
    elif post_task_id is not None:raise ValueError('task_id без post данных')
    last = -1.
    for x in trials:
        number(x.time_s,'trial time');label(x.task_id,'trial task')
        if x.time_s <= last or x.time_s < 0:raise ValueError('нестрогое время trials')
        last = x.time_s
        if not isinstance(x.correct,bool) or not isinstance(x.omitted,bool):raise ValueError('boolean trial flags')
        if x.omitted:
            if x.correct or x.latency_s is not None:raise ValueError('пропущенный ответ не correct и без latency')
        else:
            number(x.latency_s,'latency')
            if x.latency_s < 0:raise ValueError('отрицательная latency')
        if x.time_s > DURATION_S and (post_samples is None or not post_samples[0].time_s <= x.time_s <= post_samples[-1].time_s):
            raise ValueError('trial вне основных/post наблюдений')
    per_episode = [dict(kind=e.kind,task_id=e.task_id,**profile(samples,e.start_s,e.end_s),
                        reaction=reactions(trials,e.start_s,e.end_s,include_end=e.end_s==DURATION_S)) for e in episodes]
    effort = [x for x in per_episode if x['kind']=='effort']
    early = [x for x in effort if x['end_s'] <= early_end_s]
    late = [x for x in effort if x['start_s'] >= late_start_s]
    if not early or not late:raise ValueError('нет целого effort в раннем/позднем окне')
    matched = sorted({x['task_id'] for x in early}&{x['task_id'] for x in late})
    comparisons = {}
    for task in matched:
        a,b = [x for x in early if x['task_id']==task],[x for x in late if x['task_id']==task]
        avg = lambda rows:{k:mean(r[k] for r in rows) for k in a[0] if isinstance(a[0][k],(int,float))}
        av,bv = avg(a),avg(b)
        ra=reactions(trials,0,early_end_s,task)
        rb=reactions(trials,late_start_s,DURATION_S,task,True)
        latency_ratio=(ratio(rb['mean_correct_latency_s'],ra['mean_correct_latency_s'])
                       if ra['mean_correct_latency_s'] is not None and rb['mean_correct_latency_s'] is not None else None)
        accuracy_change=(rb['accuracy']-ra['accuracy'] if ra['accuracy'] is not None and rb['accuracy'] is not None else None)
        comparisons[task] = dict(early_episodes=len(a),late_episodes=len(b),metrics=comparison(av,bv),
            work_per_episode_late_over_early=ratio(bv['work_net_J'],av['work_net_J']) if len({x['duration_s'] for x in a+b})==1 else None,
            reaction_early=ra,reaction_late=rb,
            correct_latency_late_over_early=latency_ratio,accuracy_change=accuracy_change)
    recovery = []
    for a,b in zip(effort,effort[1:]):
        if a['task_id'] != b['task_id']:continue
        # Разрыв состоит из recovery: effort соседние в списке, эпизоды — полное разбиение.
        if b['start_s'] == a['end_s']:continue
        ref = next((x for x in early if x['task_id']==a['task_id']),None)
        recovery.append(dict(task_id=a['task_id'],recovery_start_s=a['end_s'],recovery_end_s=b['start_s'],
            recovery_duration_s=b['start_s']-a['end_s'],next_over_previous_power=ratio(b['mean_power_W'],a['mean_power_W']),
            power_change_W=b['mean_power_W']-a['mean_power_W'],
            restored_fraction_to_early=ratio(b['mean_power_W']-a['mean_power_W'],ref['mean_power_W']-a['mean_power_W']) if ref else None))
    post = dict(status='not_measured',metrics=None,comparison_to_early=None)
    if post_samples is not None:
        metrics = profile(post_samples,post_samples[0].time_s,post_samples[-1].time_s)
        reference = [x for x in early if x['task_id']==post_task_id]
        ref = {k:mean(x[k] for x in reference) for k in metrics} if reference else None
        post_reaction=reactions(trials,post_samples[0].time_s,post_samples[-1].time_s,post_task_id,True)
        early_reaction=reactions(trials,0,early_end_s,post_task_id)
        post = dict(status='measured_not_validated',task_id=post_task_id,metrics=metrics,
                    comparison_to_early=comparison(ref,metrics) if ref else None,
                    reaction=post_reaction,reaction_reference_early=early_reaction)
    result = dict(target_id='TARGET-CPE45',duration_s=DURATION_S,target_achievement='not_assessed',
        physiological_validation=False,protocol=dict(early_end_s=early_end_s,late_start_s=late_start_s,max_gap_s=max_gap_s,
        interpolation='piecewise_linear; no extrapolation; extrema sampled not true continuous maxima'),
        total=profile(samples,0,DURATION_S),episodes=per_episode,
        reaction=reactions(trials,0,DURATION_S,include_end=True),early_late=comparisons,
        unmatched_task_ids=sorted({x['task_id'] for x in early+late}-set(matched)),
        observed_recovery=recovery,post45=post)
    def check_finite(value):
        if isinstance(value,dict):
            for x in value.values():check_finite(x)
        elif isinstance(value,list):
            for x in value:check_finite(x)
        elif isinstance(value,float) and not math.isfinite(value):
            raise ValueError('численное переполнение результата')
    check_finite(result)
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();data=json.loads(args.input.read_text('utf-8-sig'))
    result=analyze([Sample(**x) for x in data['samples']],[Episode(**x) for x in data['episodes']],
        [Trial(**x) for x in data.get('trials',[])],**data['protocol'],
        post_samples=[Sample(**x) for x in data['post_samples']] if 'post_samples' in data else None,
        post_task_id=data.get('post_task_id'))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
