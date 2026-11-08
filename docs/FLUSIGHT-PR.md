# Draft pull-request text for the CDC FluSight hub (NOT SUBMITTED)

Use only if the team decides to participate (docs/PUBLISH.md §5). Fill the ⟨…⟩ fields first.

**Title:** NABD-v1: ⟨first submission | forecast⟩ for reference date ⟨YYYY-MM-DD⟩

**Body:**

> This PR adds ⟨model metadata `model-metadata/NABD-v1.yml` and⟩ the forecast `model-output/NABD-v1/⟨YYYY-MM-DD⟩-NABD-v1.csv` for `wk inc flu hosp` (quantiles, horizons 0–3, all 53 locations).
>
> NABD-v1 is a two-member quantile ensemble (a damped log-linear trend GLM plus empirical error quantiles) from a student team at MBZUAI (Abu Dhabi, UAE). It is built as a respiratory forecasting hub for the UAE, and we use the FluSight hub as our external benchmark. The model is frozen: the configuration was tuned on 2023/24 only and has not changed since (protocol: ⟨public repo URL⟩/blob/main/docs/PROTOCOL.md).
>
> In our retrospective evaluation (2024/25–2025/26, vintage-correct inputs), NABD-v1 did **not** meet non-inferiority against the FluSight-ensemble (relative WIS 1.22, 95% CI 1.01–1.52). We therefore set `designated_model: false` and do not ask for inclusion in the ensemble. We are submitting prospectively so that our track record is scored independently by the hub.
>
> Contact: ⟨name, email⟩. Repository: ⟨public repo URL⟩.

**Checklist before opening the PR:**
- [ ] `scripts/flusight_wednesday.sh ⟨date⟩` printed `RESULT: PASS` (apart from any metadata placeholders you have now filled)
- [ ] `designated_model: false` in the metadata
- [ ] The file is named `⟨date⟩-NABD-v1.csv` and sits under `model-output/NABD-v1/`
- [ ] Submitted before Wednesday 11 PM US Eastern for that reference date (check the hub README for the current deadline)
- [ ] After merge: record the PR URL and the file SHA-256 in `ledger/LEDGER.md`
