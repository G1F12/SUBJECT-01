# Черновик запроса данных Zöger и соавт. (DOI: 10.1186/s13102-025-01061-1)

> [!IMPORTANT]
> **СТАТУС: НЕ ОТПРАВЛЯТЬ.**
> Черновик письма подготовлен для согласования с пользователем. Фактическая отправка вынесена на отдельное подтверждение пользователя в соответствии с `GOVERNANCE.md`.

---

## Проверенные реквизиты адресата

- **Публикация:** Zöger, M., Nimmerichter, A., Baca, A., & Wirth, K. (2025). Reproducibility of peak force for isometric and isokinetic multi-joint leg extension exercise. *BMC Sports Science, Medicine and Rehabilitation*, 17(1), Article 14.
- **DOI:** [10.1186/s13102-025-01061-1](https://doi.org/10.1186/s13102-025-01061-1)
- **Основной адресат (Corresponding Author):** Dr. Manfred Zöger
- **Проверенные email-адреса:**
  - `manfred.zoeger@fhwn.ac.at` (институциональный адрес Fachhochschule Wiener Neustadt)
  - `a51818757@unet.univie.ac.at` (университетский адрес University of Vienna)
- **Аффилиации авторов:**
  - Department of Sport and Movement Sciences, University of Applied Sciences Wiener Neustadt, Wiener Neustadt, Austria;
  - Centre for Sports Science and University Sports, University of Vienna, Vienna, Austria.
- **Соавторы:** Alfred Nimmerichter, Arnold Baca, Klaus Wirth.
- **Заявление о доступности данных в статье:** *"The datasets generated and/or analyzed during the current study are available from the corresponding author on reasonable request."* (Открытые репозитории Zenodo/Dryad/Figshare отсутствуют).

---

## Текст запроса (Draft Letter)

**Subject:** Request for de-identified participant-level data for independent biomechanical model evaluation (Zöger et al., BMC Sports Sci Med Rehabil 2025, DOI: 10.1186/s13102-025-01061-1)

Dear Dr. Zöger and colleagues,

I am writing regarding your 2025 study, *"Reproducibility of peak force for isometric and isokinetic multi-joint leg extension exercise"* (*BMC Sports Science, Medicine and Rehabilitation*, 17:14, doi:10.1186/s13102-025-01061-1).

We are conducting a non-interventional, reproducible computational evaluation of closed-chain human musculoskeletal force transmission models during bilateral isometric leg press. Your study provides high-quality repeated isometric measurements at internal knee angles of 100° and 140° using the IsoMed 2000 dynamometer, which represents the exact postural range required to evaluate angle-transfer properties against simple anthropometric baselines.

In accordance with your data availability statement (*"available from the corresponding author on reasonable request"*), we would be very grateful if you could share a de-identified, participant-level dataset covering the isometric conditions. Specifically, the most informative variables for our evaluation would be:

1. **Participant & session identifiers:** Anonymized participant ID, sex, age, body mass (kg), height (cm), and segment lengths (femur, tibia), if measured.
2. **Trial-level force measurements:** Bilateral calibrated peak force in Newtons (and unilateral force transducer recordings, if measured separately), trial numbers across sessions (familiarization and repeat test sessions for test-retest reproducibility).
3. **Joint kinematics & device geometry:** Target knee angles (100° and 140°), measured joint angles (if verified via goniometry/kinematics), seat back / hip inclination angle, footplate angle, and foot placement coordinates.
4. **Signal processing & instrument settings:** Sampling frequency (Hz), filter type and cut-off frequency, time window used for peak force identification.
5. **Contact mechanics (optional):** Center of pressure (COP) or tangential force components on the footplate, if available.
6. **Metadata & exclusions:** Data dictionary, record of any excluded trials/outliers, and preferred citation or data-use attribution.

**Scope of use:**
- This research is strictly computational and non-interventional; no wet-lab experiments or participant interventions are performed.
- All analyses are reproducible, open-code comparisons comparing mechanical chain models against simple statistical baselines under strict out-of-sample validation.
- No personal identifying information (PII) or direct identifiers are requested.
- Any requested data embargo, specific license terms (e.g., CC BY 4.0), or citation requirements will be strictly honored.

If only a subset of these fields is shareable, even raw peak force values per participant and trial across 100° and 140° would substantially advance independent verification of knee-angle force transfer.

Thank you very much for your time and consideration.

Sincerely,  
SUBJECT-01 Research Initiative  
*Draft only — not sent; pending user confirmation.*
