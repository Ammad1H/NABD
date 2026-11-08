#!/usr/bin/env python3
"""ensemble_vs_persistence.py: PRELIMINARY. Does a forecast beat 'carry the census forward'
for the SIZE of the next 0-3 weeks? Uses the CDC FluSight hub's own archived real-time
forecasts: FluSight-ensemble vs FluSight-baseline (persistence: median = last reported week).
Both were made in real time on the same data, so scoring both against FINAL truth is fair
between them. Target: state weekly flu admissions (counts), horizons 0-3, quantile WIS.
Usage: python3 ensemble_vs_persistence.py <path-to-FluSight-forecast-hub-clone>"""
import sys, glob
from pathlib import Path
import numpy as np, pandas as pd
hub = Path(sys.argv[1] if len(sys.argv) > 1 else "FluSight-forecast-hub")
ts = pd.read_csv(hub / "target-data/time-series.csv", parse_dates=["as_of", "target_end_date"])
ts = ts[ts.target == "wk inc flu hosp"]
truth = ts[ts.as_of == ts.as_of.max()][["location", "target_end_date", "observation"]]
def load(m):
    fs = sorted(glob.glob(str(hub / f"model-output/{m}/*.csv")))
    d = pd.concat([pd.read_csv(f, dtype={"location": str}) for f in fs])
    d = d[(d.target == "wk inc flu hosp") & (d.output_type == "quantile") & (d.horizon >= 0)]
    d["target_end_date"] = pd.to_datetime(d.target_end_date); d["q"] = d.output_type_id.astype(float)
    return d
def wis(g, y):
    qs = g.sort_values("q"); q = qs.q.values; v = qs.value.values
    # pinball-loss form of WIS (Bracher et al. 2021): mean over quantiles of 2*pinball
    return float(np.mean(2 * np.where(y < v, (1 - q) * (v - y), q * (y - v))))
res = {}
for m in ("FluSight-ensemble", "FluSight-baseline"):
    d = load(m).merge(truth, on=["location", "target_end_date"])
    d = d[d.location != "US"]
    rows = []
    for k, g in d.groupby(["reference_date", "location", "horizon"]):
        y = g.observation.iloc[0]
        lo50, hi50 = np.interp([.25, .75], g.sort_values("q").q, g.sort_values("q").value)
        lo95, hi95 = np.interp([.025, .975], g.sort_values("q").q, g.sort_values("q").value)
        rows.append(dict(reference_date=k[0], location=k[1], horizon=k[2], wis=wis(g, y),
                         c50=lo50 <= y <= hi50, c95=lo95 <= y <= hi95))
    res[m] = pd.DataFrame(rows)
e, b = res["FluSight-ensemble"], res["FluSight-baseline"]
j = e.merge(b, on=["reference_date", "location", "horizon"], suffixes=("_e", "_b"))
j["season"] = np.where(pd.to_datetime(j.reference_date).dt.month >= 8,
                       pd.to_datetime(j.reference_date).dt.year, pd.to_datetime(j.reference_date).dt.year - 1)
print("PRELIMINARY: FluSight-ensemble vs FluSight-baseline (persistence), state flu admissions, final truth")
rng = np.random.default_rng(0)
for s, g in j.groupby("season"):
    for h, gh in g.groupby("horizon"):
        rel = gh.wis_e.sum() / gh.wis_b.sum()
        dates = gh.reference_date.unique(); boots = []
        for _ in range(500):
            pick = rng.choice(dates, len(dates)); x = pd.concat([gh[gh.reference_date == p] for p in pick])
            boots.append(x.wis_e.sum() / x.wis_b.sum())
        lo, hi = np.percentile(boots, [2.5, 97.5])
        print(f"season {s}/{(s+1)%100:02d} h={h}: rel WIS ens/persist = {rel:.2f} [{lo:.2f},{hi:.2f}]  "
              f"cov50 ens {gh.c50_e.mean():.0%} persist {gh.c50_b.mean():.0%}  cov95 ens {gh.c95_e.mean():.0%} persist {gh.c95_b.mean():.0%}  n={len(gh)}")
j.to_csv(Path(__file__).parent / "results" / "ensemble_vs_persistence.csv", index=False)
