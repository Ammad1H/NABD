# Deviations from PROTOCOL v1.0

| ID | Date (UTC) | Stage | Change | Reason | Test results seen? |
|---|---|---|---|---|---|
| D1 | 2026-11-08 | Pre-test, during model build (before tuning finished) | The NABD-EEQ grid gains the option `strata ∈ {pooled, level3}`. `level3` pools rolling-origin log-errors within three level strata (≤20, 20–200, >200 weekly admissions at the origin) instead of across all locations. The family ("empirical error quantiles pooled over locations") is unchanged. The option is chosen by the same 2023/24 tuning criterion. | A smoke test on a 2023/24 date showed pooled log-errors make large-state intervals implausibly wide (US 1%–99% range ≈ 690–15,900 when the last observation was 2,763), because small-count states dominate the log-error distribution. | **No.** No test-season (2024/25, 2025/26) score had been computed. |
| D2 | 2026-11-08 | Pre-test | Stale-vintage handling (PROTOCOL §2.3) is implemented as extra steps of the same damped trend; for EEQ the errors of step min(s+k, 4) are used. | Implementation detail the protocol left open. | **No.** |
