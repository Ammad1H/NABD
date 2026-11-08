# NABD pilot data specification (R3-3)

**Purpose.** This is the exact table a partner (a hospital group, or DoH/ADPHC) would share for a **12-week shadow pilot** of NABD: forecasts are issued and scored but never acted on. It is the first step from public WHO surveillance to a hospital's own operational counts.

**Status.** The specification and connector (`adapters/pilot.py`), the suppression rules, the shadow scorer (`uae/pilot_shadow.py`) and tests (`tests/test_pilot.py`) are **built**. No partner data has been received. The example file `data/pilot/SYNTHETIC_pilot_example.csv` is **SYNTHETIC**: invented shapes for a fictional facility `SYN_HOSP_A`, used only to test the connector. Nothing computed from it is evidence.

---

## 1. What is shared: one aggregate table, no individuals

| Column | Type | Allowed values | Notes |
|---|---|---|---|
| `period_start` | date | ISO date | The Monday of the week (preferred), or the day |
| `granularity` | text | `week` (preferred), `day` | Weekly is strongly preferred; see §3 |
| `facility_code` | text | `^[A-Z0-9_]{2,16}$` | An opaque code chosen by the partner; NABD never needs the facility name |
| `region` | text | `ABU_DHABI`, `AL_AIN`, `AL_DHAFRA`, `ALL` | Abu Dhabi Emirate regions |
| `measure` | text | `ed_visits_ari`, `ed_visits_ili`, `admissions_ari`, `admissions_rsv`, `admissions_flu`, `lab_tests_rsv`, `lab_pos_rsv`, `lab_tests_flu`, `lab_pos_flu`, `occupied_beds_paeds_resp` | Fixed vocabulary; no free text |
| `age_band` | text | `0-5m`, `6-23m`, `2-4y`, `5-14y`, `15-49y`, `50-64y`, `65+y`, `all` | The infant bands match RSV immunisation eligibility questions |
| `count` | number ≥ 0 | | Blank if suppressed |
| `suppressed` | bool | | Set by the partner or by the connector |
| `synthetic` | bool | | `false` for real partner data |

**Rejected on load:** any column whose name looks like a person-level identifier (e.g. `patient_id`, `emirates_id`, `mrn`, `dob`, `name`, `phone`, `insurance`), any column not in the table above, any value outside the vocabularies, and duplicate keys. The same guard (`adapters/schemas.reject_person_level`) protects every NABD input.

**Suggested definitions** (to be agreed with the partner's clinical coders; NABD does not need diagnosis-level data):
- ARI/ILI ED visits follow the partner's existing syndromic definitions (e.g. ICD-10 J00–J22 for ARI);
- `admissions_rsv` / `admissions_flu` are laboratory-confirmed admissions;
- `occupied_beds_paeds_resp` is the census at a fixed hour.

**Where it would come from.** Abu Dhabi already captures these signals:
- **Tableegh**, the DoH automated notification platform, generates notifications in real time from ICD-10 codes and laboratory-confirmed results. It is integrated with **Malaffi**, the Emirate's health information exchange ([DoH digital platforms](https://doh.gov.ae/en/programs-initiatives/DigitalPlatforms), VERIFIED 8 Nov 2026).
- A partner would export **weekly aggregates** of what these systems already hold. NABD never connects to Malaffi or Tableegh directly in the pilot.
- Field names above are NABD's own; mapping to Tableegh/Malaffi internal fields is UNVERIFIED (not publicly documented) and is done by the partner.

## 2. Small-cell protection (enforced in code)

1. **Primary suppression:** any count from 1 to 9 (k = 10) is blanked.
2. **Complementary suppression:** within each (week, facility, region, measure), if exactly one age band is suppressed, the next-smallest released band is also suppressed, so the value can't be recovered from the all-ages total. If every other band is zero, a zero band is suppressed instead.
3. **No back-imputation:** a week with any suppressed cell is NaN in the model series. It is never filled in.
4. `check_suppressed` refuses any table that still releases a 1–9 count or leaves a single suppressed band.

k = 10 is NABD's default. The partner's own disclosure-control rule takes precedence if it is stricter.

## 3. Granularity: why weekly

Daily counts of lab-confirmed RSV admissions at one hospital are usually under 10, so under k = 10 almost every day would be suppressed. The connector demonstrated this on the synthetic file: the daily RSV admissions series was entirely suppressed, and the scorer returned NOT COMPUTABLE. **Weekly** aggregation keeps the signal above k. Daily is only useful for high-volume measures (e.g. ARI ED visits).

## 4. Governance checklist (before any real data moves)

- [ ] Written data-sharing agreement naming purpose (shadow forecasting evaluation only), retention (end of pilot + 90 days), and deletion.
- [ ] Partner confirms compliance with the **Abu Dhabi Healthcare Information and Cyber Security Standard (ADHICS)** for the export ([DoH announcement](https://www.doh.gov.ae/en/news/department-of-health-launches-abu-dhabi-healthcare-information-and-cyber-security); [ADHICS document](https://www.doh.gov.ae/-/media/032019_ADHICS.ashx)).
- [ ] Data stays in the UAE (in-country hosting). UAE health-data localisation rules apply to cross-border transfer ([overview](https://usuaebusiness.org/?p=35610); legal confirmation needed).
- [ ] AI governance per the **DoH Policy on Artificial Intelligence in Healthcare (2018)**: clear governance, auditable validation statements, regular audits reported to DoH, and boundaries on data access ([Al Tamimi summary](https://www.tamimi.com/news/new-policy-on-artificial-intelligence-in-healthcare-issued-by-the-department-of-health-abu-dhabi)). The pre-registered protocol and the public ledger are NABD's audit trail.
- [ ] Only aggregate counts; the table in §1 is the full schema.
- [ ] Ethics/IRB determination by the partner. An aggregate operational-evaluation pilot may be exempt, but that is the partner's call.
- [ ] Named partner owner and named NABD owner; the forecasts are not used for clinical decisions during the pilot.

## 5. How NABD fits the pilot data

- **Inputs:**
  - the partner's weekly `admissions_rsv`, `admissions_flu` and `ed_visits_ari` (all ages, and the infant bands where released);
  - plus the public WHO FluNet UAE positivity NABD already uses.
- **Forecast:** 1–3-week-ahead weekly counts with the 23 FluSight quantiles. Every round is issued into the same hashed, anchored ledger as the public forecasts.
- **Wiring:** `adapters.pilot.load_pilot()` → `to_series()` → forecaster → `uae.pilot_shadow.shadow_score()`.

## 6. Pre-specified exit criteria (from SPEC §5.6; fixed before any partner data)

- **Primary:** relative WIS of NABD's 1–3-week forecasts vs **persistence of the hospital's own census**, as a ratio of sums over all scored weeks, **< 0.9**.
- **Calibration:** 80% interval coverage within **0.70–0.90**.
- **Secondary:**
  - whether national FluNet positivity adds skill beyond the hospital's own series (feed-removal ablation);
  - absolute error in bed-days over the next 14 days;
  - onset-alarm lead vs the hospital's own threshold rule at a matched false-alarm rate. Expected parity, per the US analysis.
- **If the criteria are not met,** we say so. The pilot is a test, not a deployment.

`python -m uae.pilot_shadow` runs the scorer end-to-end on the SYNTHETIC file with a stand-in forecaster, to show the mechanics. Its output is not evidence.

## 7. Commands

```bash
python -m adapters.pilot synthetic                                   # (re)write the SYNTHETIC example
python -m adapters.pilot validate path/to/partner_export.csv        # schema + suppression check
python -m uae.pilot_shadow                                          # mechanics demo (synthetic only)
python -m pytest -q tests/test_pilot.py
```
