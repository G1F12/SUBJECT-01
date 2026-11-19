# Каноническая спецификация Архитектуры А (SUBJECT-01 Architecture A Canonical Specification)

**Идентификатор:** `EXP-0064` · **Статус программы:** завершение вычислительного и протокольного плана [PLAN.md](file:///D:/SUBJECT-01/PLAN.md) и [MASTER_ROADMAP.md](file:///D:/SUBJECT-01/MASTER_ROADMAP.md)  
**Категория зрелости:** Смешанная триада (`EVIDENCE-BASED` якоря + `MODEL_ONLY / CONDITIONAL POTENTIAL` системный синтез + `DATA_BLOCKED` для внешнего двустороннего жима и 2700-с CPE45)

---

## 1. Инварианты безопасности и эпистемологические границы

1. `TARGET-CPE45 = NOT EXTERNALLY VALIDATED` (подтверждено инвариантом [CPE45.json](file:///D:/SUBJECT-01/research/targets/CPE45.json): `historical_experiments_cpe45_status = "not_assessed"`, `success_thresholds = null`).
2. `BIOLOGICAL INTERVENTIONS = NO_GO` (любые генетические, фармакологические или хирургические вмешательства на человеке запрещены).
3. `STRENGTH +20% = THEORETICALLY_FEASIBLE_WITH_COORDINATED_TENDON_ADAPTATION` (**не валидирована in vivo**).
4. `EXP-0061 (Bilateral Isometric Leg Press Cohort Transfer) = DATA_BLOCKED` (0 из 6 кандидатов прошли гейты допуска; парный бутстрэп выполнен на односуставном референсе `DPValid` со сменой протокола `PROTOCOL_SHIFT_SINGLE_JOINT_REFERENCE`).

---

## 2. Столп 1: Сократительный профиль и многосуставная замкнутая цепь (`EXP-0059`, `EXP-0061`)

- **Калибровка удельного напряжения (`DPValid`, $N = 20$):** $\sigma = 26.41 \pm 4.70\text{ Н/см}^2$ ($95\%$ MC-интервал $[17.58, 44.98]\text{ Н/см}^2$, [`NEG-0058`](file:///D:/SUBJECT-01/registry/negative_results.json#L469-L475)).
- **Односуставный референсный бенчмарк (`DPValid`, парный кластерный бутстрэп $B = 10\,000$):** модель PCSA `M2` даёт $\Delta R^2_{\text{pooled}} = +0.0735$ ($95\%$ ДИ `[+0.0259, +0.1428]`) относительно простой антропометрии `Baseline F0` и `+0.0081` (`[-0.0903, +0.1173]`) относительно `M1` — оба попадают в **`Outcome 3: INCONCLUSIVE`** при $\Delta_{\min} = 0.08$.
- **Стратегия 2 Архитектуры А (односуставный оптимум, $V = \text{const}$):** $\Delta\theta = +2.0^\circ$ ($14^\circ \to 16^\circ$), $\Delta\sigma = +8\%$, $\Delta\tilde{v}_{\max} = +12\%$, $\Delta\text{CSA} = +15\%$, $\Delta\text{UTS} = +8\% \implies$ момент **$+21.9\%$**, $v_{\max}$ **-1.7%**, мощность **$+19.8\%$**.
- **Многосуставная 3-DOF замкнутая цепь жима (`EXP-0061`, `MODEL_ONLY`):**
  * Наивное $a_i \equiv 0.95$ несовместно (точечная невязка `253.7` Н·м, выход $x_{\text{COP}} = +0.1706$ м за границу $+0.16$ м).
  * Изолированный рост квадрицепса $+20\%$ передаётся на платформу с потерями: $+15.27\%$ ($\eta_{\text{chain}} = 0.764$ при $100^\circ$ колена).
  * Согласованная перестройка цепи (Стратегия 2 по разгибателям бедра, колена и голеностопа) обеспечивает **$+21.64\%$** силы на упоре ($\eta_{\text{chain}} = 0.988$), а с реципрокным торможением антагонистов ($-25\%$) — **$+21.78\%$**.

---

## 3. Столп 2: Вязкоупругий предел энтезиса ($dF/dt$) и гетерохрония (`EXP-0060`, `EXP-0062`)

- **Закон сохранения циклического ресурса (`FND-0063`):** $(1 + \Delta_{\text{CSA}}) (1 + \Delta_{\text{UTS}}) \ge \lambda_F$. Для $\lambda_F = 1.20$ адаптация Case 2C ($+15\%$ CSA, $+10\%$ UTS) снижает $\sigma_{\text{nom}}$ до `40.13` МПа и даёт $1.678\times$ расчётного ресурса при одноосном циклическом нагружении.
- **Многослойная вязкоупругая модель сдвига ($dF/dt = 20\,000\text{ Н/с}$, калибровка по Bogaerts $N = 10$):**
  * Глубокий слой перегружен относительно поверхностного (коэффициент смещения `1.232`, коэффициент напряжения $k_{\text{deep}} = 1.120$).
  * На уровне $4800\text{ Н}$ ($+20\%$ от базы `EXP-0060`): без адаптации $\sigma_{\text{vM,peak}} = 58.83$ МПа ($SF_{\text{local}} = 1.61$); Case 2C восстанавливает $SF_{\text{local}} = 2.05 \ge 1.50$.
  * На уровне пикового баллистического 100% MVC ($7661\text{ Н}$): без адаптации $\sigma_{\text{vM,peak}} = 92.20$ МПа **превышает порог текучести коллагена $85\text{ МПа}$** ($SF_{\text{local}} = 1.03$); Case 2C снижает $\sigma_{\text{vM,peak}}$ до `79.91` МПа ($< 85$ МПа, но $SF_{\text{local}} = 1.31 < 1.50$), указывая на необходимость ограничения взрывных 100% MVC баллистических фронтов либо $\Delta\text{CSA} > 20\%$ на энтезисе.
- **Гетерохрония ремоделирования (`BLOCKER-03`):** несогласованное форсирование `TARGET-ADAPT25` ($\tau_m = 12$ дн. против $\tau_t = 90$ дн.) вызывает пик усталостного риска **`2.94x`** на 3.0-й неделе; синхронизированная прогрессия по сухожилию (H2) удерживает риск на `1.00x`.

---

## 4. Столп 3: 4-слойная биотермодинамика Пеннеса и огибающая CPE45 (`EXP-0063`)

- **Эмпирические якоря:** Malaga CPET (`N = 846` уникальных субъектов, c_ox = `21.374` кДж/л O2) и ACTES (`N = 21`). Максимальная невязка баланса энергии модели за 2700 с: `0.00e+00` Дж.
- **Непрерывная высоковыходная нагрузка ($360\text{ Вт}$, $+20\%$ от $300\text{ Вт}$, $D = 1.00$):** во всех исследованных климатах $\ge 20^\circ\text{C}$ температура ядра превышает $39.5^\circ\text{C}$ (`39.81 °C` за `2365` с в умеренном климате и `42.16 °C` за `1350` с в жарком влажном); при умеренной нагрузке $300\text{ Вт}$ перегрев наступает во всех тёплых и жарких климатах ($28\text{–}35^\circ\text{C}$).
- **Допустимая прерывистая огибающая (`D_max` для $T_{\text{core}} < 39.5^\circ\text{C}$ на 2700 с при $360\text{ Вт}$):**
  * Умеренный климат (`20°C, 50% RH`): $D \le 0.92$ (с `AEGIS-01` падает до $D \le 0.69$, потеря `-25.0%`);
  * Тёплый (`28°C, 60% RH`): $D \le 0.74$;
  * Жаркий сухой (`35°C, 30% RH`): $D \le 0.59$;
  * Жаркий влажный (`32°C, 80% RH`): $D \le 0.65$ (для непрерывной работы $360\text{ Вт}$ требуется внешний сосудистый теплосъём `420 Вт`).

---

## 5. Итоговая матрица решений программы SUBJECT-01 (`DEC-0026`)

| Направление / Цель | Итоговый статус | Категория зрелости | Обоснование и граничное условие |
|---|---|---|---|
| **TARGET-FORCE20 (Architecture A)** | **`CONDITIONAL_POTENTIAL_MODEL_FEASIBLE_NOT_VALIDATED_IN_VIVO`** | `CONDITIONAL POTENTIAL` | Closed-chain Strategy 2 reaches +21.64% bilateral force with Case 2C SF_local=2.05 at 4800 N; extreme ballistic 100% MVC (7661 N) drops local enthesis SF to 1.31 < 1.50 without extra CSA or dF/dt cap. |
| **EXP-0061 (Bilateral Leg Press External Test)** | **`DATA_BLOCKED`** | `EVIDENCE_GATE_BLOCKED` | 0/6 audited datasets pass open bilateral isometric leg press requirements; DPValid single-joint reference yields Outcome 3 INCONCLUSIVE (N=20). |
| **TARGET-ADAPT25 (+25% Speed)** | **`HOLD_RATE_LIMITED_BY_COLLAGEN_SYNTHESIS`** | `CONDITIONAL POTENTIAL` | Uncoordinated +25% adaptation accelerates transient tendon damage 2.94x around week 3.0; risk eliminated (1.00x) only under tendon-paced progression H2. |
| **TARGET-CPE45 (2700 s Endurance)** | **`NOT_EXTERNALLY_VALIDATED_CONDITIONAL_HOLD`** | `MODEL_ONLY_INTERMITTENT_ENVELOPE` | Continuous 360 W breaches 39.5 C in all tested climates (temperate 20 C in 2365 s, hot-humid 32 C in 1350 s); safe over 2700 s only via intermittent pacing (D <= 0.92 at 20 C, D <= 0.65 at 32 C/80%RH) or active external cooling. |
| **AEGIS-01 Integration (PR #9)** | **`CONDITIONAL_HOLD`** | `HOLD` | Skin barrier (-35% evaporative conductance, +2 kg) reduces temperate safe duty cycle by 14.0% at 300 W and 25.0% at 360 W, compounding BLOCKER-01. |
| **Architecture B (Bioengineered Muscle)** | **`DISQUALIFIED_NO_GO`** | `NO_GO` | Preserved from DEC-0021 (compartment syndrome, microvascular ischemia, periosteal avulsion). |
| **Architecture C (Internal Biohybrid)** | **`HOLD_BREAKTHROUGH_DEPENDENT`** | `HOLD / BREAKTHROUGH_DEPENDENT` | Preserved from DEC-0021 (internal heat rejection and reflex latency incompatibilities). |
| **Biological Human Interventions** | **`NO_GO`** | `HARD_INVARIANT_NO_GO` | Hard program invariant strictly enforced. |
| **MTJCore Programme** | **`COMPLETED_HOLD_PENDING_NEW_EVIDENCE`** | `COMPLETED / HOLD_PENDING_NEW_EVIDENCE` | Preserved from DEC-0023 (manuscript v1.0.3-commsbio-submission prepared, awaiting independent non-Oxford/non-Copenhagen cohort). |
