"""Pre-declared UAE surge-onset alert rule (docs/PROTOCOL-UAE-v2.md section 7). Descriptive, n = 4 seasons.

Onset of a series-season: first week from ISO week 27 at which sentinel positivity >= T for two consecutive
weeks (T_flu = 15%, T_rsv = 10%). A series-season is ELIGIBLE if positivity < T in each of its first 4 weeks.

Rules, evaluated at every origin t of the season (issue date = week_end(t) + 11 days):
  forecast rule (NABD-UAE-v1, NABD-UAE-v2): alert if the forecast median for target week t+2
      (+0.5 wk after issue) is >= T and the observed positivity at t is < T.
  census rule (persistence comparator): alert if observed positivity at t is >= 0.6*T and < T.
Only the FIRST alert per series-season counts.
  lead (weeks)  = (week_end(onset week) - issue date) / 7
  sensitivity   = eligible series-seasons whose first alert has 0 <= lead <= 4
  premature     = first alert with lead > 4;  late/missed = no alert with lead >= 0
  false alarm   = a first alert in an eligible series-season with no onset
  PPV           = first alerts followed by onset within 0..4 weeks of issue / all first alerts
"""
from __future__ import annotations

import numpy as np
import pandas as pd

T = {"flu": 15.0, "rsv": 10.0}
CENSUS_FRAC = 0.6


def onset_table(d: pd.DataFrame, key: str, seasons) -> pd.DataFrame:
    rows = []
    pct = d.pos / d.specimens * 100
    for s in seasons:
        idx = d.index[d.season == s]
        p = pct.loc[idx]
        eligible = bool((p.iloc[:4] < T[key]).all()) if len(p) >= 4 else False
        onset = None
        for a, b in zip(idx[:-1], idx[1:]):
            if p.loc[a] >= T[key] and p.loc[b] >= T[key]:
                onset = d.week_end.loc[a]
                break
        rows.append(dict(series=key, season=s, eligible=eligible, onset_week_end=onset))
    return pd.DataFrame(rows)


def evaluate(alerts: pd.DataFrame, onsets: pd.DataFrame) -> pd.DataFrame:
    """alerts: columns model, series, season, issue_date (first alert per model x series-season only
    or all candidate alerts; the first is taken here). Returns per model x series-season outcomes."""
    out = []
    for model, gm in alerts.groupby("model"):
        for _, o in onsets.iterrows():
            g = gm[(gm.series == o.series) & (gm.season == o.season)].sort_values("issue_date")
            first = g.issue_date.iloc[0] if len(g) else None
            rec = dict(model=model, series=o.series, season=o.season, eligible=o.eligible,
                       onset_week_end=o.onset_week_end, first_alert_issue=first, lead_wk=np.nan, outcome="")
            if not o.eligible:
                rec["outcome"] = "ineligible"
            elif first is None:
                rec["outcome"] = "missed" if o.onset_week_end is not None else "no_alert_no_onset"
            elif o.onset_week_end is None:
                rec["outcome"] = "false_alarm"
            else:
                lead = (pd.Timestamp(o.onset_week_end) - pd.Timestamp(first)).days / 7
                rec["lead_wk"] = round(lead, 2)
                rec["outcome"] = "hit" if 0 <= lead <= 4 else ("premature" if lead > 4 else "late")
            out.append(rec)
    return pd.DataFrame(out)


def summarise(ev: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, series), g in ev.groupby(["model", "series"]):
        e = g[g.eligible]
        with_onset = e[e.onset_week_end.notna()]
        alerts = e[e.first_alert_issue.notna()]
        hits = (e.outcome == "hit").sum()
        rows.append(dict(model=model, series=series, n_eligible=len(e), n_onsets=len(with_onset),
                         sensitivity=f"{hits}/{len(with_onset)}",
                         ppv=f"{hits}/{len(alerts)}" if len(alerts) else "n/a",
                         false_alarms=int((e.outcome == "false_alarm").sum()),
                         premature=int((e.outcome == "premature").sum()),
                         late_or_missed=int(e.outcome.isin(["late", "missed"]).sum()),
                         median_lead_wk=float(np.nanmedian(e.lead_wk)) if e.lead_wk.notna().any() else np.nan))
    return pd.DataFrame(rows)
