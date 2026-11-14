# Спецификация биомеханических моделей EXP-0059

**Эксперимент:** EXP-0059  
**Дата:** 14 ноября 2026 г.  

---

## 1. Базовые физические уравнения

Суставной момент колена в изометрическом режиме описывается уравнением равновесия моментов сил:
$$\tau_{\text{knee}}(\alpha) = r_{\text{pat}}(\alpha) \cdot F_{\text{tendon}}(\alpha) - \tau_{\text{opposing}}$$

где:
- $\alpha$ — угол сгибания коленного сустава (градусы).
- $r_{\text{pat}}(\alpha) = 0.043 + 0.00018\alpha - 0.0000015\alpha^2$ [м] — плечо связки надколенника.
- $F_{\text{tendon}}$ — сила, передаваемая квадрицепсом на надколенник:
  $$F_{\text{tendon}} = F_{\text{quad}} \cdot \cos\theta$$
- $F_{\text{quad}}$ — суммарная сила мышечных волокон:
  $$F_{\text{quad}} = \sigma \cdot \text{PCSA} \cdot f_{\ell}(\alpha) \cdot a(t)$$
- $\sigma$ — удельная сила (Specific Tension, Н/см²).
- $\text{PCSA} = \frac{V_{\text{quad}}}{L_f} \cdot \cos\theta$ — физиологическая площадь сечения (см²).
- $f_{\ell}(\alpha) = 1.0 - \left(\frac{\alpha - 70}{50}\right)^2$ — множитель зависимости «сила–длина».
- $a(t)$ — уровень волевой активации ($a \approx 0.95$ при MVC).

---

## 2. Спецификация сравниваемых моделей

1. **M0 (Baseline Mean):**  
   $$\hat{\tau}_i = \bar{\tau}_{\text{train}}$$
2. **M1 (Kinematic & Anthropometric OLS):**  
   $$\hat{\tau}_i = \beta_0 + \beta_1 \cdot \text{Mass} + \beta_2 \cdot \text{Height} + \beta_3 \cdot \text{Sex} + \beta_4 \cdot \text{Angle} + \beta_5 \cdot \text{Age}$$
3. **M2 (Biomechanical PCSA Model, 1 Parameter):**  
   $$\hat{\tau}_i = \sigma_{\text{calib}} \cdot \left[ \text{PCSA}_i \cdot \cos\theta_0 \cdot f_{\ell}(\alpha_i) \cdot r_{\text{pat}}(\alpha_i) \cdot 0.95 \right]$$
   где $\sigma_{\text{calib}}$ калибруется строго на обучающих фолдах без статистических коэффициентов подгонки.
4. **M3 (Architecture + Agonist sEMG):**  
   Ridge регрессия на признаках PCSA, геометрии и нормализованной активности квадрицепса (`emg_RF`, `emg_VM`, `emg_VL`).
5. **M4 (Full Model with Antagonists):**  
   Ridge регрессия на всех антропометрических признаках и 5 каналах sEMG (агонисты + антагонисты `emg_BF`, `emg_ST`).

---

## 3. Математика изомассового масштабирования (Isomass Constraint)

Условие постоянства массы и объема мышцы:
$$V_{\text{quad}} = \text{const} \implies \text{PCSA} \cdot \frac{L_f}{\cos\theta} = \text{const}$$

При увеличении угла перистости от $\theta_0 = 14^\circ$ до $\theta$:
$$L_f(\theta) = L_{f0} \cdot \frac{\sin\theta_0}{\sin\theta}$$
$$\text{PCSA}(\theta) = \text{PCSA}_0 \cdot \frac{\sin(2\theta)}{\sin(2\theta_0)} \cdot \frac{1}{\cos\theta}$$
$$F_{\text{tendon}}(\theta) = F_0 \cdot \frac{\sin(2\theta)}{\sin(2\theta_0)}$$

Максимум статической силы достигается при $\theta = 45^\circ$, однако shortening capacity (диапазон сокращения) и $v_{\max}$ падают строго пропорционально длине пучков:
$$\frac{v_{\max}(\theta)}{v_{\max, 0}} = \frac{L_f(\theta)}{L_{f0}} = \frac{\sin\theta_0}{\sin\theta}$$
