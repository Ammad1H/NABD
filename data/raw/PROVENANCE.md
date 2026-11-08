# Raw data provenance

| File | Source | Retrieved | Notes |
|---|---|---|---|
| flunet_are_webfetch.csv | WHO FluNet xMart `VIW_FNT`, country ARE, via WebFetch | 5 Nov 2026 | original R3 copy, kept unchanged for reproducibility of the earlier probes |
| flunet_are.csv | as above, plus rows refreshed via WebFetch | **8 Nov 2026** | adds 2026-W43 NONSENTINEL (1084 specimens / 298 flu / 203 RSV) and **2026-W44 SENTINEL (342 / 92 / 36)**. Latest published sentinel week on 8 Nov = **2026-W44** (ends 1 Nov), i.e. about 7 days' lag at retrieval. W44 is a first release and may be revised. |
| flunet_usa_*.csv | WHO FluNet USA | 5 Nov 2026 | used by eval/backtest_probe.py only |
| uae_calendar.csv | Gulf News report of UAE MoE unified calendar 2026/27 (URL in file) | 8 Nov 2026 | 2026/27 rows verified; earlier winter breaks approximate (verified=False) |
| weather_ad_weekly.csv | NOAA NCEI daily-summaries AE000041217 | **not retrieved** | all NOAA hosts blocked from the sandbox; run `python3 -m adapters.weather --fetch` locally. Until then the adapter returns a placeholder labelled real=False (NOT REAL). |
