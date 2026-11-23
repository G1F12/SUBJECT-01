"""TARGET-CPE45: измерение временных рядов, многоканальная синхронизация и программная оценка кандидатных порогов (без эмпирической валидации человека)."""
from bisect import bisect_right
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from statistics import mean, median
import argparse
import json
import math
import random

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


@dataclass(frozen=True)
class ThermalSample:
    time_s: float
    core_temp_C: float
    skin_temp_C: float | None = None
    ambient_temp_C: float | None = None
    rh_pct: float | None = None


@dataclass(frozen=True)
class BaselineRecovery:
    task_id: str
    mvc_value: float
    cmj_cm: float | None = None
    va_pct: float | None = None
    pain_nrs: float | None = None


@dataclass(frozen=True)
class RecoveryProbe:
    time_s: float
    window_label: str  # e.g. post_acute, post_5min, post_45min, post_24h
    task_id: str
    mvc_value: float
    cmj_cm: float | None = None
    va_pct: float | None = None
    pain_nrs: float | None = None


CHANNELS = tuple(f.name for f in fields(Sample) if f.name != "time_s")


def number(x, name):
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
        raise ValueError(f"{name}: требуется конечное число; пропуски не заполняются")
    return float(x)


def optional_number(x, name):
    return None if x is None else number(x, name)


def label(x, name):
    if not isinstance(x, str) or not x.strip():
        raise ValueError(name)


def ratio(late, early):
    return late / early if early != 0 else None


def validate_samples(samples, max_gap_s, *, main):
    if not samples or (main and len(samples) < 2):
        raise ValueError("пустой/неполный ряд")
    previous = None
    for row in samples:
        for k, v in asdict(row).items():
            number(v, k)
        if any(getattr(row, k) < 0 for k in ("force_N", "speed_m_s", "coordination_error_m", "maneuver_error_m")):
            raise ValueError("модуль силы, скорость и ошибки должны быть неотрицательны")
        if previous is not None and not 0 < row.time_s - previous <= max_gap_s:
            raise ValueError("нестрогое время или разрыв больше разрешённого протоколом")
        previous = row.time_s
    if main and (samples[0].time_s != 0 or samples[-1].time_s != DURATION_S):
        raise ValueError("основной ряд должен покрывать ровно [0,2700] s")
    if not main and samples[0].time_s <= DURATION_S:
        raise ValueError("post измеряется отдельно, строго после 2700 s")


def interpolate(samples, t, _times=None):
    times = _times if _times is not None else [s.time_s for s in samples]
    if not times[0] <= t <= times[-1]:
        raise ValueError("экстраполяция запрещена")
    i = bisect_right(times, t) - 1
    if times[i] == t:
        return samples[i]
    left, right = samples[i], samples[i + 1]
    w = (t - left.time_s) / (right.time_s - left.time_s)
    return Sample(t, **{k: getattr(left, k) * (1 - w) + getattr(right, k) * w for k in CHANNELS})


def profile(samples, start, end, _times=None):
    number(start, "profile start")
    number(end, "profile end")
    if end < start:
        raise ValueError("обратное окно")
    times = _times if _times is not None else [s.time_s for s in samples]
    points = [interpolate(samples, start, times)]
    i_lo = bisect_right(times, start)
    i_hi = bisect_right(times, end)
    if i_hi > i_lo and times[i_hi - 1] == end:
        i_hi -= 1
    if i_hi > i_lo:
        points.extend(samples[i_lo:i_hi])
    if end > start:
        points.append(interpolate(samples, end, times))
    totals = {k: 0.0 for k in CHANNELS}
    positive = negative = 0.0
    for left, right in zip(points, points[1:]):
        dt = right.time_s - left.time_s
        for k in CHANNELS:
            totals[k] += 0.5 * (getattr(left, k) + getattr(right, k)) * dt
        a, b = left.power_W, right.power_W
        if a * b < 0:
            crossing = dt * abs(a) / (abs(a) + abs(b))
            for p, length in [(a, crossing), (b, dt - crossing)]:
                positive += 0.5 * max(0, p) * length
                negative += 0.5 * min(0, p) * length
        else:
            positive += 0.5 * (max(a, 0) + max(b, 0)) * dt
            negative += 0.5 * (min(a, 0) + min(b, 0)) * dt
    duration = end - start
    avg = {k: (totals[k] / duration if duration else getattr(points[0], k)) for k in CHANNELS}
    return dict(
        start_s=start,
        end_s=end,
        duration_s=duration,
        work_net_J=totals["power_W"],
        work_positive_J=positive,
        work_negative_J=negative,
        path_length_m=totals["speed_m_s"],
        mean_power_W=avg["power_W"],
        peak_power_W=max(s.power_W for s in points),
        mean_force_N=avg["force_N"],
        peak_force_N=max(s.force_N for s in points),
        mean_speed_m_s=avg["speed_m_s"],
        peak_speed_m_s=max(s.speed_m_s for s in points),
        peak_acceleration_m_s2=max(s.acceleration_m_s2 for s in points),
        min_acceleration_m_s2=min(s.acceleration_m_s2 for s in points),
        mean_coordination_error_m=avg["coordination_error_m"],
        mean_maneuver_error_m=avg["maneuver_error_m"],
    )


def reactions(trials, start, end, task=None, include_end=False):
    chosen = [
        x
        for x in trials
        if start <= x.time_s
        and (x.time_s < end or (include_end and x.time_s == end))
        and (task is None or x.task_id == task)
    ]
    answered = [x.latency_s for x in chosen if not x.omitted]
    correct = [x.latency_s for x in chosen if x.correct]
    n_tot = len(chosen)
    n_omit = sum(x.omitted for x in chosen)
    return dict(
        trials=n_tot,
        omissions=n_omit,
        omission_rate_pct=(100.0 * n_omit / n_tot) if n_tot else None,
        accuracy=mean(x.correct for x in chosen) if n_tot else None,
        mean_response_latency_s=mean(answered) if answered else None,
        mean_correct_latency_s=mean(correct) if correct else None,
    )


def comparison(early, late):
    keys = [
        "mean_power_W",
        "peak_power_W",
        "mean_force_N",
        "peak_force_N",
        "mean_speed_m_s",
        "peak_speed_m_s",
        "peak_acceleration_m_s2",
        "min_acceleration_m_s2",
        "mean_coordination_error_m",
        "mean_maneuver_error_m",
    ]
    return {
        k: dict(
            early=early[k],
            late=late[k],
            late_over_early=ratio(late[k], early[k]),
            relative_drop=(early[k] - late[k]) / early[k] if early[k] else None,
            absolute_change=late[k] - early[k],
        )
        for k in keys
    }


def _audit_sampling_and_sync(
    samples: list[Sample],
    episodes: list[Episode],
    thermal_samples: list[ThermalSample] | None,
    *,
    min_effort_hz: float | None,
    min_overall_hz: float | None,
    min_thermal_hz: float | None,
    stream_clock_offsets_s: dict[str, float] | None,
    max_sync_offset_s: float | None,
) -> dict:
    dts = [b.time_s - a.time_s for a, b in zip(samples, samples[1:])]
    dt_min, dt_med, dt_max = min(dts), median(dts), max(dts)
    overall_hz = 1.0 / dt_med if dt_med > 0 else 0.0
    overall_min_hz = 1.0 / dt_max if dt_max > 0 else 0.0

    # Intervals overlapping any effort episode (two-pointer O(N + M) sweep)
    eff_eps = [e for e in episodes if e.kind == "effort"]
    eff_dts = []
    ep_idx = 0
    n_ep = len(eff_eps)
    for a, b in zip(samples, samples[1:]):
        while ep_idx < n_ep and eff_eps[ep_idx].end_s <= a.time_s:
            ep_idx += 1
        if ep_idx < n_ep and b.time_s > eff_eps[ep_idx].start_s and a.time_s < eff_eps[ep_idx].end_s:
            eff_dts.append(b.time_s - a.time_s)
    eff_dt_max = max(eff_dts) if eff_dts else dt_max
    eff_min_hz = 1.0 / eff_dt_max if eff_dt_max > 0 else 0.0

    if min_overall_hz is not None:
        number(min_overall_hz, "min_overall_hz")
        if overall_min_hz < min_overall_hz * (1.0 - 1e-6):
            raise ValueError(
                f"недостаточная общая частота дискретизации: min={overall_min_hz:.3f} Hz < {min_overall_hz:.3f} Hz"
            )
    if min_effort_hz is not None:
        number(min_effort_hz, "min_effort_hz")
        if eff_min_hz < min_effort_hz * (1.0 - 1e-6):
            raise ValueError(
                f"недостаточная частота в effort-эпизодах: min={eff_min_hz:.3f} Hz < {min_effort_hz:.3f} Hz"
            )

    th_dt_max = None
    th_min_hz = None
    if thermal_samples is not None and len(thermal_samples) >= 2:
        th_dts = [b.time_s - a.time_s for a, b in zip(thermal_samples, thermal_samples[1:])]
        th_dt_max = max(th_dts)
        th_min_hz = 1.0 / th_dt_max if th_dt_max > 0 else 0.0
        if min_thermal_hz is not None:
            number(min_thermal_hz, "min_thermal_hz")
            if th_min_hz < min_thermal_hz * (1.0 - 1e-6):
                raise ValueError(
                    f"недостаточная частота теплового ряда: min={th_min_hz:.4f} Hz < {min_thermal_hz:.4f} Hz"
                )

    sync_status = "not_provided"
    max_abs_offset = None
    offsets_clean = None
    if stream_clock_offsets_s is not None:
        if not isinstance(stream_clock_offsets_s, dict) or not stream_clock_offsets_s:
            raise ValueError("stream_clock_offsets_s должен быть непустым словарём")
        offsets_clean = {str(k): number(v, f"clock_offset[{k}]") for k, v in stream_clock_offsets_s.items()}
        max_abs_offset = max(abs(v) for v in offsets_clean.values())
        sync_status = "checked"
        if max_sync_offset_s is not None:
            number(max_sync_offset_s, "max_sync_offset_s")
            if max_abs_offset > max_sync_offset_s + 1e-12:
                raise ValueError(
                    f"нарушение синхронизации потоков: max |offset|={max_abs_offset:.4f} s > {max_sync_offset_s:.4f} s"
                )

    return dict(
        overall_dt_min_s=dt_min,
        overall_dt_median_s=dt_med,
        overall_dt_max_s=dt_max,
        overall_median_hz=overall_hz,
        overall_min_hz=overall_min_hz,
        effort_dt_max_s=eff_dt_max,
        effort_min_hz=eff_min_hz,
        thermal_dt_max_s=th_dt_max,
        thermal_min_hz=th_min_hz,
        clock_offsets_s=offsets_clean,
        max_abs_clock_offset_s=max_abs_offset,
        sync_status=sync_status,
    )


def _analyze_thermal(
    thermal_samples: list[ThermalSample] | None,
    *,
    max_thermal_gap_s: float,
    medical_abort_core_temp_C: float,
) -> dict:
    if thermal_samples is None:
        return dict(status="not_measured", peak_core_temp_C=None, medical_abort_triggered=None)
    if len(thermal_samples) < 2:
        raise ValueError("тепловой ряд должен содержать >=2 точек")
    number(max_thermal_gap_s, "max_thermal_gap_s")
    if max_thermal_gap_s <= 0:
        raise ValueError("max_thermal_gap_s должен быть > 0")
    prev = None
    for row in thermal_samples:
        t = number(row.time_s, "thermal.time_s")
        tc = number(row.core_temp_C, "thermal.core_temp_C")
        if not 30.0 <= tc <= 45.0:
            raise ValueError(f"нефизиологичная core_temp_C={tc}")
        optional_number(row.skin_temp_C, "thermal.skin_temp_C")
        optional_number(row.ambient_temp_C, "thermal.ambient_temp_C")
        rh = optional_number(row.rh_pct, "thermal.rh_pct")
        if rh is not None and not 0.0 <= rh <= 100.0:
            raise ValueError("thermal.rh_pct вне [0,100]")
        if prev is not None and not 0 < t - prev <= max_thermal_gap_s:
            raise ValueError("нестрогое время или разрыв в тепловом ряде превышает max_thermal_gap_s")
        prev = t
    if thermal_samples[0].time_s > max_thermal_gap_s or thermal_samples[-1].time_s < DURATION_S - max_thermal_gap_s:
        raise ValueError("тепловой ряд не покрывает интервал [0,2700] s в пределах max_thermal_gap_s")

    peak_tc = max(x.core_temp_C for x in thermal_samples)
    time_above_38_5 = 0.0
    time_above_39_0 = 0.0
    for a, b in zip(thermal_samples, thermal_samples[1:]):
        dt = b.time_s - a.time_s
        avg_t = 0.5 * (a.core_temp_C + b.core_temp_C)
        if avg_t >= 38.5:
            time_above_38_5 += dt
        if avg_t >= 39.0:
            time_above_39_0 += dt
    return dict(
        status="measured_not_validated",
        n_samples=len(thermal_samples),
        start_core_temp_C=thermal_samples[0].core_temp_C,
        end_core_temp_C=thermal_samples[-1].core_temp_C,
        peak_core_temp_C=peak_tc,
        delta_core_temp_C=thermal_samples[-1].core_temp_C - thermal_samples[0].core_temp_C,
        time_above_38_5_s=time_above_38_5,
        time_above_39_0_s=time_above_39_0,
        medical_abort_ceiling_C=medical_abort_core_temp_C,
        medical_abort_triggered=bool(peak_tc >= medical_abort_core_temp_C),
    )


def _analyze_recovery_battery(
    recovery_probes: list[RecoveryProbe] | None,
    baseline_recovery: BaselineRecovery | None,
    post45_window_bounds_s: dict[str, tuple[float, float]] | None,
) -> dict:
    if recovery_probes is None:
        if baseline_recovery is not None:
            raise ValueError("baseline_recovery передан без recovery_probes")
        return dict(status="not_measured", probes={})
    if not recovery_probes:
        raise ValueError("пустой список recovery_probes")
    if baseline_recovery is None:
        raise ValueError("для оценки recovery_probes требуется baseline_recovery")
    label(baseline_recovery.task_id, "baseline_recovery.task_id")
    base_mvc = number(baseline_recovery.mvc_value, "baseline_recovery.mvc_value")
    if base_mvc <= 0:
        raise ValueError("baseline_recovery.mvc_value должен быть > 0")
    base_cmj = optional_number(baseline_recovery.cmj_cm, "baseline_recovery.cmj_cm")
    if base_cmj is not None and base_cmj <= 0:
        raise ValueError("baseline_recovery.cmj_cm должен быть > 0")
    base_va = optional_number(baseline_recovery.va_pct, "baseline_recovery.va_pct")
    optional_number(baseline_recovery.pain_nrs, "baseline_recovery.pain_nrs")

    seen_windows = set()
    probes_out = {}
    for p in recovery_probes:
        t = number(p.time_s, "recovery_probe.time_s")
        if t <= DURATION_S:
            raise ValueError("recovery_probe.time_s обязан быть строго > 2700 s")
        label(p.window_label, "recovery_probe.window_label")
        label(p.task_id, "recovery_probe.task_id")
        if p.task_id != baseline_recovery.task_id:
            raise ValueError(
                f"несовпадение task_id в post45 recovery_probe ({p.task_id} != {baseline_recovery.task_id})"
            )
        if p.window_label in seen_windows:
            raise ValueError(f"дублирующееся окно post45: {p.window_label}")
        seen_windows.add(p.window_label)
        if post45_window_bounds_s is not None:
            if p.window_label not in post45_window_bounds_s:
                raise ValueError(f"неизвестное окно post45: {p.window_label}")
            lo, hi = post45_window_bounds_s[p.window_label]
            if not lo <= t <= hi:
                raise ValueError(f"метка времени {t} s вне допустимого окна {p.window_label} [{lo}, {hi}]")

        mvc = number(p.mvc_value, "recovery_probe.mvc_value")
        if mvc < 0:
            raise ValueError("recovery_probe.mvc_value не может быть отрицательным")
        cmj = optional_number(p.cmj_cm, "recovery_probe.cmj_cm")
        if cmj is not None and cmj < 0:
            raise ValueError("recovery_probe.cmj_cm не может быть отрицательным")
        va = optional_number(p.va_pct, "recovery_probe.va_pct")
        pain = optional_number(p.pain_nrs, "recovery_probe.pain_nrs")
        if pain is not None and not 0.0 <= pain <= 10.0:
            raise ValueError("recovery_probe.pain_nrs вне [0, 10]")

        probes_out[p.window_label] = dict(
            time_s=t,
            task_id=p.task_id,
            mvc_value=mvc,
            mvc_retention_pct=100.0 * mvc / base_mvc,
            cmj_cm=cmj,
            cmj_retention_pct=(100.0 * cmj / base_cmj) if (cmj is not None and base_cmj is not None) else None,
            va_pct=va,
            va_delta_pp=(va - base_va) if (va is not None and base_va is not None) else None,
            pain_nrs=pain,
        )
    return dict(
        status="measured_not_validated",
        baseline_task_id=baseline_recovery.task_id,
        baseline_mvc_value=base_mvc,
        baseline_cmj_cm=base_cmj,
        probes=probes_out,
    )


def _analyze_cognitive_windows(
    trials: list[Trial],
    *,
    early_end_s: float,
    late_start_s: float,
    post45_window_bounds_s: dict[str, tuple[float, float]] | None,
) -> dict:
    cog_tasks = sorted({x.task_id for x in trials})
    out = {}
    for task in cog_tasks:
        ra = reactions(trials, 0.0, early_end_s, task, include_end=False)
        rb = reactions(trials, late_start_s, DURATION_S, task, include_end=True)
        rt_a = ra["mean_correct_latency_s"]
        rt_b = rb["mean_correct_latency_s"]
        acc_a = ra["accuracy"]
        acc_b = rb["accuracy"]

        post_windows = {}
        if post45_window_bounds_s is not None:
            for wname, (lo, hi) in post45_window_bounds_s.items():
                rp = reactions(trials, lo, hi, task, include_end=True)
                if rp["trials"] > 0:
                    rt_p = rp["mean_correct_latency_s"]
                    acc_p = rp["accuracy"]
                    post_windows[wname] = dict(
                        reaction=rp,
                        delta_correct_latency_ms=((rt_p - rt_a) * 1000.0) if (rt_a is not None and rt_p is not None) else None,
                        accuracy_change_pp=((acc_p - acc_a) * 100.0) if (acc_a is not None and acc_p is not None) else None,
                    )
        else:
            rp_all = reactions(trials, DURATION_S + 1e-9, 1e12, task, include_end=True)
            if rp_all["trials"] > 0:
                rt_p = rp_all["mean_correct_latency_s"]
                acc_p = rp_all["accuracy"]
                post_windows["post_all"] = dict(
                    reaction=rp_all,
                    delta_correct_latency_ms=((rt_p - rt_a) * 1000.0) if (rt_a is not None and rt_p is not None) else None,
                    accuracy_change_pp=((acc_p - acc_a) * 100.0) if (acc_a is not None and acc_p is not None) else None,
                )

        out[task] = dict(
            early=ra,
            late=rb,
            delta_correct_latency_ms=((rt_b - rt_a) * 1000.0) if (rt_a is not None and rt_b is not None) else None,
            delta_correct_latency_pct=(100.0 * (rt_b - rt_a) / rt_a) if (rt_a not in (None, 0.0) and rt_b is not None) else None,
            correct_latency_late_over_early=ratio(rt_b, rt_a) if (rt_a is not None and rt_b is not None) else None,
            accuracy_change_pp=((acc_b - acc_a) * 100.0) if (acc_a is not None and acc_b is not None) else None,
            late_accuracy_pct=(acc_b * 100.0) if acc_b is not None else None,
            late_omission_rate_pct=rb["omission_rate_pct"],
            post45_windows=post_windows,
        )
    return out


def analyze(
    samples,
    episodes,
    trials=(),
    *,
    early_end_s,
    late_start_s,
    max_gap_s,
    post_samples=None,
    post_task_id=None,
    thermal_samples=None,
    max_thermal_gap_s=60.0,
    recovery_probes=None,
    baseline_recovery=None,
    post45_window_bounds_s=None,
    min_effort_hz=None,
    min_overall_hz=None,
    min_thermal_hz=None,
    stream_clock_offsets_s=None,
    max_sync_offset_s=None,
    body_mass_kg=None,
    critical_power_W=None,
    medical_abort_core_temp_C=39.5,
):
    """Все окна и допустимые параметры задаёт протокол. Сам по себе analyze() не присваивает empirical PASS."""
    for k, v in [("early_end_s", early_end_s), ("late_start_s", late_start_s), ("max_gap_s", max_gap_s)]:
        number(v, k)
    if not 0 < early_end_s <= late_start_s < DURATION_S or max_gap_s <= 0:
        raise ValueError("неправильные окна/допустимый gap")
    validate_samples(samples, max_gap_s, main=True)
    if not episodes:
        raise ValueError("нет эпизодов")
    boundary = 0.0
    for ep in episodes:
        number(ep.start_s, "start")
        number(ep.end_s, "end")
        label(ep.task_id, "task_id")
        if ep.kind not in ("effort", "recovery") or ep.start_s != boundary or ep.end_s <= ep.start_s:
            raise ValueError("эпизоды должны без перекрытий/дыр разбивать [0,2700]")
        boundary = ep.end_s
    if boundary != DURATION_S or {e.kind for e in episodes} != {"effort", "recovery"}:
        raise ValueError("требуются полная длительность, усилия и восстановление")
    if post_samples is not None:
        label(post_task_id, "post_task_id")
        validate_samples(post_samples, max_gap_s, main=False)
    elif post_task_id is not None:
        raise ValueError("task_id без post данных")

    # Validate thermal, recovery battery, sampling rate, and stream sync
    thermal_out = _analyze_thermal(
        thermal_samples,
        max_thermal_gap_s=max_thermal_gap_s,
        medical_abort_core_temp_C=medical_abort_core_temp_C,
    )
    recovery_battery_out = _analyze_recovery_battery(
        recovery_probes,
        baseline_recovery,
        post45_window_bounds_s,
    )
    sampling_sync_out = _audit_sampling_and_sync(
        samples,
        episodes,
        thermal_samples,
        min_effort_hz=min_effort_hz,
        min_overall_hz=min_overall_hz,
        min_thermal_hz=min_thermal_hz,
        stream_clock_offsets_s=stream_clock_offsets_s,
        max_sync_offset_s=max_sync_offset_s,
    )

    # Validate cognitive trials
    allowed_post_ranges: list[tuple[float, float]] = []
    if post_samples is not None:
        allowed_post_ranges.append((post_samples[0].time_s, post_samples[-1].time_s))
    if post45_window_bounds_s is not None:
        for wname, bounds in post45_window_bounds_s.items():
            lo, hi = number(bounds[0], f"post45_window[{wname}][0]"), number(bounds[1], f"post45_window[{wname}][1]")
            if lo <= DURATION_S or hi < lo:
                raise ValueError(f"некорректные границы окна post45 {wname}: [{lo}, {hi}]")
            allowed_post_ranges.append((lo, hi))

    last = -1.0
    for x in trials:
        number(x.time_s, "trial time")
        label(x.task_id, "trial task")
        if x.time_s <= last or x.time_s < 0:
            raise ValueError("нестрогое время trials")
        last = x.time_s
        if not isinstance(x.correct, bool) or not isinstance(x.omitted, bool):
            raise ValueError("boolean trial flags")
        if x.omitted:
            if x.correct or x.latency_s is not None:
                raise ValueError("пропущенный ответ не correct и без latency")
        else:
            number(x.latency_s, "latency")
            if x.latency_s < 0:
                raise ValueError("отрицательная latency")
        if x.time_s > DURATION_S:
            if not any(lo <= x.time_s <= hi for lo, hi in allowed_post_ranges):
                raise ValueError("trial вне основных/post наблюдений")

    sample_times = [s.time_s for s in samples]
    per_episode = [
        dict(
            kind=e.kind,
            task_id=e.task_id,
            **profile(samples, e.start_s, e.end_s, sample_times),
            reaction=reactions(trials, e.start_s, e.end_s, include_end=e.end_s == DURATION_S),
        )
        for e in episodes
    ]
    effort = [x for x in per_episode if x["kind"] == "effort"]
    early = [x for x in effort if x["end_s"] <= early_end_s]
    late = [x for x in effort if x["start_s"] >= late_start_s]
    if not early or not late:
        raise ValueError("нет целого effort в раннем/позднем окне")
    matched = sorted({x["task_id"] for x in early} & {x["task_id"] for x in late})
    comparisons = {}
    for task in matched:
        a = [x for x in early if x["task_id"] == task]
        b = [x for x in late if x["task_id"] == task]
        avg = lambda rows: {k: mean(r[k] for r in rows) for k in a[0] if isinstance(a[0][k], (int, float))}
        av, bv = avg(a), avg(b)
        ra = reactions(trials, 0, early_end_s, task)
        rb = reactions(trials, late_start_s, DURATION_S, task, True)
        latency_ratio = (
            ratio(rb["mean_correct_latency_s"], ra["mean_correct_latency_s"])
            if ra["mean_correct_latency_s"] is not None and rb["mean_correct_latency_s"] is not None
            else None
        )
        accuracy_change = rb["accuracy"] - ra["accuracy"] if ra["accuracy"] is not None and rb["accuracy"] is not None else None
        comparisons[task] = dict(
            early_episodes=len(a),
            late_episodes=len(b),
            metrics=comparison(av, bv),
            work_per_episode_late_over_early=ratio(bv["work_net_J"], av["work_net_J"])
            if len({x["duration_s"] for x in a + b}) == 1
            else None,
            reaction_early=ra,
            reaction_late=rb,
            correct_latency_late_over_early=latency_ratio,
            accuracy_change=accuracy_change,
        )

    recovery = []
    for a, b in zip(effort, effort[1:]):
        if a["task_id"] != b["task_id"]:
            continue
        if b["start_s"] == a["end_s"]:
            continue
        ref = next((x for x in early if x["task_id"] == a["task_id"]), None)
        recovery.append(
            dict(
                task_id=a["task_id"],
                recovery_start_s=a["end_s"],
                recovery_end_s=b["start_s"],
                recovery_duration_s=b["start_s"] - a["end_s"],
                next_over_previous_power=ratio(b["mean_power_W"], a["mean_power_W"]),
                power_change_W=b["mean_power_W"] - a["mean_power_W"],
                restored_fraction_to_early=ratio(b["mean_power_W"] - a["mean_power_W"], ref["mean_power_W"] - a["mean_power_W"])
                if ref
                else None,
            )
        )

    post = dict(status="not_measured", metrics=None, comparison_to_early=None)
    if post_samples is not None:
        metrics = profile(post_samples, post_samples[0].time_s, post_samples[-1].time_s)
        reference = [x for x in early if x["task_id"] == post_task_id]
        ref = {k: mean(x[k] for x in reference) for k in metrics} if reference else None
        post_reaction = reactions(trials, post_samples[0].time_s, post_samples[-1].time_s, post_task_id, True)
        early_reaction = reactions(trials, 0, early_end_s, post_task_id)
        post = dict(
            status="measured_not_validated",
            task_id=post_task_id,
            metrics=metrics,
            comparison_to_early=comparison(ref, metrics) if ref else None,
            reaction=post_reaction,
            reaction_reference_early=early_reaction,
        )

    total_prof = profile(samples, 0, DURATION_S, sample_times)
    bm = optional_number(body_mass_kg, "body_mass_kg")
    if bm is not None and bm <= 0:
        raise ValueError("body_mass_kg должен быть > 0")
    cp = optional_number(critical_power_W, "critical_power_W")
    if cp is not None and cp <= 0:
        raise ValueError("critical_power_W должен быть > 0")
    submax_eps = [x for x in effort if x["task_id"] == "submax_sustained_165s"]
    submax_mean_w = mean(x["mean_power_W"] for x in submax_eps) if submax_eps else None
    demand_norm = dict(
        work_positive_J=total_prof["work_positive_J"],
        work_positive_kJ=total_prof["work_positive_J"] / 1000.0,
        body_mass_kg=bm,
        work_positive_kJ_per_kg=(total_prof["work_positive_J"] / 1000.0 / bm) if bm is not None else None,
        critical_power_W=cp,
        submax_mean_power_W=submax_mean_w,
        submax_mean_power_pct_cp=(100.0 * submax_mean_w / cp) if (submax_mean_w is not None and cp is not None) else None,
    )

    cog_early_late = _analyze_cognitive_windows(
        list(trials),
        early_end_s=early_end_s,
        late_start_s=late_start_s,
        post45_window_bounds_s=post45_window_bounds_s,
    )

    result = dict(
        target_id="TARGET-CPE45",
        duration_s=DURATION_S,
        target_achievement="not_assessed",
        physiological_validation=False,
        protocol=dict(
            early_end_s=early_end_s,
            late_start_s=late_start_s,
            max_gap_s=max_gap_s,
            interpolation="piecewise_linear; no extrapolation; extrema sampled not true continuous maxima",
        ),
        sampling_and_sync=sampling_sync_out,
        demand_normalization=demand_norm,
        total=total_prof,
        episodes=per_episode,
        reaction=reactions(trials, 0, DURATION_S, include_end=True),
        early_late=comparisons,
        cognitive_early_late=cog_early_late,
        unmatched_task_ids=sorted({x["task_id"] for x in early + late} - set(matched)),
        observed_recovery=recovery,
        thermal=thermal_out,
        recovery_battery=recovery_battery_out,
        post45=post,
    )

    def check_finite(value):
        if isinstance(value, dict):
            for x in value.values():
                check_finite(x)
        elif isinstance(value, list):
            for x in value:
                check_finite(x)
        elif isinstance(value, float) and not math.isfinite(value):
            raise ValueError("численное переполнение результата")

    check_finite(result)
    return result


def _eval_bound(val: float | None, op: str, limit: float, missing_reason: str) -> dict:
    if val is None:
        return dict(value=None, op=op, threshold=limit, status="NOT_ASSESSED", reason=missing_reason)
    tol = 1e-7 * max(1.0, abs(limit))
    if op == "<=":
        passed = val <= limit + tol
    elif op == "<":
        passed = val < limit
    else:
        passed = val >= limit - tol
    return dict(
        value=round(float(val), 5),
        op=op,
        threshold=limit,
        status="PASS" if passed else "FAIL",
        reason="ok" if passed else f"violated ({val:.4f} not {op} {limit})",
    )


def evaluate_session(analysis: dict, spec: dict, *, arm: str = "temperate_20C") -> dict:
    """Evaluate one participant's analyze() output against a pre-registered candidate spec.
    Never treats NOT_ASSESSED as PASS; separates research PASS ceiling from medical abort rule.
    """
    if arm not in ("temperate_20C", "warm_acclimatized_32C"):
        raise ValueError(f"неизвестная ветка протокола arm='{arm}'")
    thr = spec["candidate_success_thresholds"]
    req = spec["sampling_and_sync_requirements"]
    mech = thr["mechanical_retention_late_vs_early"]
    spat = thr["spatial_motor_control_meters"]
    cog_cfg = thr["concurrent_cognitive_control"]
    th_cfg = thr["thermoregulatory_limits"]
    rec_cfg = thr["post45_recovery_vector"]
    dem_cfg = thr["absolute_demand_floor"]

    checks: dict[str, dict] = {}
    ss = analysis["sampling_and_sync"]
    dn = analysis["demand_normalization"]
    el = analysis["early_late"]
    cel = analysis["cognitive_early_late"]
    th = analysis["thermal"]
    rb = analysis["recovery_battery"]

    # 0. Sampling rate and multi-channel synchronization audit
    checks["sampling_effort_min_hz"] = _eval_bound(
        ss.get("effort_min_hz"), ">=", req["min_effort_hz"], "effort sampling rate unavailable"
    )
    checks["sampling_overall_min_hz"] = _eval_bound(
        ss.get("overall_min_hz"), ">=", req["min_overall_hz"], "overall sampling rate unavailable"
    )
    checks["sampling_thermal_min_hz"] = _eval_bound(
        ss.get("thermal_min_hz"), ">=", req["min_thermal_hz"], "thermal sampling rate not measured"
    )
    checks["sync_max_abs_offset_s"] = _eval_bound(
        ss.get("max_abs_clock_offset_s"), "<=", req["max_sync_offset_s"], "stream_clock_offsets_s not provided"
    )

    # 1. Demand floor
    checks["work_positive_kJ_per_kg"] = _eval_bound(
        dn["work_positive_kJ_per_kg"], ">=", dem_cfg["work_positive_2700s_kJ_per_kg_min"], "body_mass_kg not provided"
    )
    checks["submax_prescription_pct_cp"] = _eval_bound(
        dn["submax_mean_power_pct_cp"], ">=", dem_cfg["submax_prescription_min_pct_cp"], "critical_power_W or submax episodes missing"
    )

    # 2. Mechanical retention
    exp_tid = mech["explosive_task_id"]
    sub_tid = mech["submax_task_id"]
    exp_drop = (
        el[exp_tid]["metrics"]["peak_power_W"]["relative_drop"] * 100.0
        if exp_tid in el and el[exp_tid]["metrics"]["peak_power_W"]["relative_drop"] is not None
        else None
    )
    sub_drop = (
        el[sub_tid]["metrics"]["mean_power_W"]["relative_drop"] * 100.0
        if sub_tid in el and el[sub_tid]["metrics"]["mean_power_W"]["relative_drop"] is not None
        else None
    )
    checks["explosive_peak_power_drop_pct"] = _eval_bound(exp_drop, "<=", mech["explosive_peak_power_drop_pct_max"], f"{exp_tid} unmatched/missing")
    checks["submax_mean_power_drop_pct"] = _eval_bound(sub_drop, "<=", mech["submax_mean_power_drop_pct_max"], f"{sub_tid} unmatched/missing")

    # Worst-case force & velocity drop across matched effort tasks
    force_drops = [v["metrics"]["peak_force_N"]["relative_drop"] * 100.0 for v in el.values() if v["metrics"]["peak_force_N"]["relative_drop"] is not None]
    vel_drops = [v["metrics"]["mean_speed_m_s"]["relative_drop"] * 100.0 for v in el.values() if v["metrics"]["mean_speed_m_s"]["relative_drop"] is not None]
    checks["in_task_peak_force_drop_pct"] = _eval_bound(max(force_drops) if force_drops else None, "<=", mech["in_task_peak_force_drop_pct_max"], "no matched effort tasks")
    checks["in_task_velocity_drop_pct"] = _eval_bound(max(vel_drops) if vel_drops else None, "<=", mech["in_task_velocity_drop_pct_max"], "no matched effort tasks")

    rec_ratios = [r["next_over_previous_power"] for r in analysis["observed_recovery"] if r["next_over_previous_power"] is not None]
    checks["between_effort_recovery_ratio"] = _eval_bound(mean(rec_ratios) if rec_ratios else None, ">=", mech["between_effort_recovery_ratio_min"], "no observed between-effort recovery")

    # 3. Spatial coordination & maneuver error in meters (relative % increase & absolute m increase)
    coord_rel = [(-v["metrics"]["mean_coordination_error_m"]["relative_drop"] * 100.0) for v in el.values() if v["metrics"]["mean_coordination_error_m"]["relative_drop"] is not None]
    coord_abs = [v["metrics"]["mean_coordination_error_m"]["absolute_change"] for v in el.values()]
    man_rel = [(-v["metrics"]["mean_maneuver_error_m"]["relative_drop"] * 100.0) for v in el.values() if v["metrics"]["mean_maneuver_error_m"]["relative_drop"] is not None]
    man_abs = [v["metrics"]["mean_maneuver_error_m"]["absolute_change"] for v in el.values()]
    checks["coordination_error_rel_increase_pct"] = _eval_bound(max(coord_rel) if coord_rel else None, "<=", spat["coordination_error_m_rel_increase_pct_max"], "no matched coordination channel")
    checks["coordination_error_abs_increase_m"] = _eval_bound(max(coord_abs) if coord_abs else None, "<=", spat["coordination_error_m_abs_increase_max"], "no matched coordination channel")
    checks["maneuver_error_rel_increase_pct"] = _eval_bound(max(man_rel) if man_rel else None, "<=", spat["maneuver_error_m_rel_increase_pct_max"], "no matched maneuver channel")
    checks["maneuver_error_abs_increase_m"] = _eval_bound(max(man_abs) if man_abs else None, "<=", spat["maneuver_error_m_abs_increase_max"], "no matched maneuver channel")

    # 4. Concurrent cognitive control (matched by cognitive_task_id, enforcing min_cognitive_trials_per_window)
    cog_tid = cog_cfg["cognitive_task_id"]
    min_tr = int(req["min_cognitive_trials_per_window"])
    cog = cel.get(cog_tid)
    if cog is None or cog["early"]["trials"] < min_tr or cog["late"]["trials"] < min_tr:
        reason = f"cognitive task '{cog_tid}' missing or <{min_tr} trials in early/late window"
        for k in (
            "cognitive_rt_increase_ms",
            "cognitive_rt_increase_pct",
            "cognitive_accuracy_drop_pp",
            "cognitive_accuracy_abs_pct",
            "cognitive_omission_rate_pct",
        ):
            checks[k] = dict(value=None, op="?", threshold=None, status="NOT_ASSESSED", reason=reason)
    else:
        checks["cognitive_rt_increase_ms"] = _eval_bound(cog["delta_correct_latency_ms"], "<=", cog_cfg["correct_latency_increase_ms_max"], "no correct trials")
        checks["cognitive_rt_increase_pct"] = _eval_bound(cog["delta_correct_latency_pct"], "<=", cog_cfg["correct_latency_increase_pct_max"], "no correct trials")
        acc_drop_pp = -cog["accuracy_change_pp"] if cog["accuracy_change_pp"] is not None else None
        checks["cognitive_accuracy_drop_pp"] = _eval_bound(acc_drop_pp, "<=", cog_cfg["accuracy_drop_pp_max"], "accuracy unavailable")
        checks["cognitive_accuracy_abs_pct"] = _eval_bound(cog["late_accuracy_pct"], ">=", cog_cfg["accuracy_absolute_min_pct"], "accuracy unavailable")
        checks["cognitive_omission_rate_pct"] = _eval_bound(cog["late_omission_rate_pct"], "<=", cog_cfg["omission_rate_pct_max"], "omissions unavailable")

    # 5. Thermal research efficacy ceiling (SEPARATE from medical abort rule)
    res_ceiling = (
        th_cfg["research_pass_ceiling_temperate_20C"]
        if arm == "temperate_20C"
        else th_cfg["research_pass_ceiling_warm_acclimatized_32C"]
    )
    checks["thermal_research_ceiling_C"] = _eval_bound(th["peak_core_temp_C"], "<", res_ceiling, "thermal series not measured")
    if th["peak_core_temp_C"] is None:
        med_abort = None
    else:
        med_abort = bool(th["medical_abort_triggered"] or th["peak_core_temp_C"] >= th_cfg["medical_abort_ceiling_C"])

    # 6. post45 recovery battery
    probes = rb.get("probes", {})
    p_ac = probes.get("post_acute")
    p_45 = probes.get("post_45min")
    p_24 = probes.get("post_24h")
    checks["post45_acute_mvc_retention_pct"] = _eval_bound(p_ac["mvc_retention_pct"] if p_ac else None, ">=", rec_cfg["post_acute_mvc_retention_pct_min"], "post_acute probe missing")
    checks["post45_45min_mvc_retention_pct"] = _eval_bound(p_45["mvc_retention_pct"] if p_45 else None, ">=", rec_cfg["post_45min_mvc_retention_pct_min"], "post_45min probe missing")
    checks["post45_24h_mvc_retention_pct"] = _eval_bound(p_24["mvc_retention_pct"] if p_24 else None, ">=", rec_cfg["post_24h_mvc_retention_pct_min"], "post_24h probe missing")
    checks["post45_24h_cmj_retention_pct"] = _eval_bound(p_24["cmj_retention_pct"] if p_24 else None, ">=", rec_cfg["post_24h_cmj_retention_pct_min"], "post_24h CMJ missing")
    checks["post45_24h_tendon_pain_nrs"] = _eval_bound(p_24["pain_nrs"] if p_24 else None, "<=", rec_cfg["post_24h_tendon_pain_nrs_max"], "post_24h pain NRS missing")

    # post_45min cognitive check (also enforces min_cognitive_trials_per_window)
    p45_cog = cog["post45_windows"].get("post_45min") if cog else None
    p45_cog_ok = p45_cog is not None and p45_cog["reaction"]["trials"] >= min_tr
    checks["post45_45min_cog_accuracy_drop_pp"] = _eval_bound(
        (-p45_cog["accuracy_change_pp"]) if (p45_cog_ok and p45_cog["accuracy_change_pp"] is not None) else None,
        "<=",
        rec_cfg["post_45min_cog_accuracy_drop_pp_max"],
        f"post_45min cognitive trials missing or <{min_tr}",
    )
    checks["post45_45min_cog_rt_increase_ms"] = _eval_bound(
        p45_cog["delta_correct_latency_ms"] if p45_cog_ok else None,
        "<=",
        rec_cfg["post_45min_cog_rt_increase_ms_max"],
        f"post_45min cognitive trials missing or <{min_tr}",
    )

    statuses = [c["status"] for c in checks.values()]
    if med_abort is True or "FAIL" in statuses:
        overall = "FAIL"
    elif "NOT_ASSESSED" in statuses or med_abort is None:
        overall = "NOT_ASSESSED"
    else:
        overall = "CANDIDATE_SOFTWARE_PASS"

    return dict(
        spec_id=spec["spec_id"],
        arm=arm,
        empirical_validation=False,
        medical_abort_triggered=med_abort,
        overall_status=overall,
        n_pass=statuses.count("PASS"),
        n_fail=statuses.count("FAIL"),
        n_not_assessed=statuses.count("NOT_ASSESSED"),
        channels=checks,
    )


def _boot_ci_stdlib(values: list[float], rng: random.Random, n_boot: int, alpha_two_sided: float = 0.05) -> tuple[float, float]:
    n = len(values)
    means = []
    for _ in range(n_boot):
        s = 0.0
        for _ in range(n):
            s += values[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    lo_i = max(0, int(math.floor((alpha_two_sided / 2.0) * n_boot)))
    hi_i = min(n_boot - 1, int(math.ceil((1.0 - alpha_two_sided / 2.0) * n_boot)) - 1)
    return means[lo_i], means[hi_i]


def evaluate_cohort(
    session_analyses: list[dict],
    spec: dict,
    *,
    arm: str = "temperate_20C",
    n_boot: int = 2000,
    seed: int = 20260420,
) -> dict:
    """Participant-clustered bootstrap IUT evaluation across N sessions (stdlib only)."""
    if len(session_analyses) < 2:
        raise ValueError("для когортной оценки неопределённости требуется N >= 2 участников")
    per_sub = [evaluate_session(a, spec, arm=arm) for a in session_analyses]
    rng = random.Random(seed)
    channel_names = list(per_sub[0]["channels"].keys())

    cohort_channels = {}
    for ch in channel_names:
        vals = [s["channels"][ch]["value"] for s in per_sub if s["channels"][ch]["value"] is not None]
        op = next((s["channels"][ch]["op"] for s in per_sub if s["channels"][ch]["op"] != "?"), None)
        limit = next((s["channels"][ch]["threshold"] for s in per_sub if s["channels"][ch]["threshold"] is not None), None)
        if len(vals) < len(per_sub) or op is None or limit is None:
            cohort_channels[ch] = dict(
                n_valid=len(vals),
                n_total=len(per_sub),
                mean=round(mean(vals), 5) if vals else None,
                ci95_two_sided=None,
                op=op,
                threshold=limit,
                status="NOT_ASSESSED",
                reason="missing participant observations (no imputation)",
            )
            continue
        ci_lo, ci_hi = _boot_ci_stdlib(vals, rng, n_boot, alpha_two_sided=0.05)
        if op == "<=":
            ok = ci_hi <= limit
        elif op == "<":
            ok = ci_hi < limit
        else:
            ok = ci_lo >= limit
        cohort_channels[ch] = dict(
            n_valid=len(vals),
            n_total=len(per_sub),
            mean=round(mean(vals), 5),
            ci95_two_sided=[round(ci_lo, 5), round(ci_hi, 5)],
            op=op,
            threshold=limit,
            status="PASS" if ok else "FAIL",
        )

    n_aborts = sum(1 for s in per_sub if s["medical_abort_triggered"] is True)
    any_abort_missing = any(s["medical_abort_triggered"] is None for s in per_sub)
    ch_statuses = [c["status"] for c in cohort_channels.values()]
    if n_aborts > 0 or "FAIL" in ch_statuses:
        overall = "FAIL"
    elif "NOT_ASSESSED" in ch_statuses or any_abort_missing:
        overall = "NOT_ASSESSED"
    else:
        overall = "CANDIDATE_COHORT_SOFTWARE_PASS"

    return dict(
        spec_id=spec["spec_id"],
        arm=arm,
        n_participants=len(per_sub),
        empirical_validation=False,
        statistical_method="Intersection-Union Test (conservative two-sided 95% participant-clustered bootstrap CI; FWER <= 0.025)",
        medical_aborts_n=n_aborts,
        overall_cohort_status=overall,
        channels=cohort_channels,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text("utf-8-sig"))
    pbounds = (
        {k: tuple(v) for k, v in data["post45_window_bounds_s"].items()}
        if "post45_window_bounds_s" in data
        else None
    )
    result = analyze(
        [Sample(**x) for x in data["samples"]],
        [Episode(**x) for x in data["episodes"]],
        [Trial(**x) for x in data.get("trials", [])],
        **data["protocol"],
        post_samples=[Sample(**x) for x in data["post_samples"]] if "post_samples" in data else None,
        post_task_id=data.get("post_task_id"),
        thermal_samples=[ThermalSample(**x) for x in data["thermal_samples"]] if "thermal_samples" in data else None,
        recovery_probes=[RecoveryProbe(**x) for x in data["recovery_probes"]] if "recovery_probes" in data else None,
        baseline_recovery=BaselineRecovery(**data["baseline_recovery"]) if "baseline_recovery" in data else None,
        post45_window_bounds_s=pbounds,
        stream_clock_offsets_s=data.get("stream_clock_offsets_s"),
        body_mass_kg=data.get("body_mass_kg"),
        critical_power_W=data.get("critical_power_W"),
    )
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8", newline="\n")
