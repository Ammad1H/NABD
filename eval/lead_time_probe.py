#!/usr/bin/env python3
"""
lead_time_probe.py: PRELIMINARY test of the question a hospital buyer asks:
"Does a forecast give me an earlier, equally reliable surge warning than my own census?"

US analogue, using real CDC FluSight hub data with real-time vintages:
  data/flusight/time-series.csv  (hubverse; as_of = data release; target 'wk inc flu hosp',
                                  state weekly flu admissions per 100k = 'weekly_rate')

Decision points: every published vintage (as_of) in Oct–May.
  Both rules decide using data through L = last week contained in that vintage.
  CENSUS rule (the hospital's own trailing count; generously given FINAL, revised values, 0 lag):
      alarm if final_rate[L] >= alpha * T
  FORECAST rule (uses ONLY the vintage available at the time; noisy, preliminary values):
      log-linear growth fit on the last 3 vintage weeks -> projected rate at L+2
      alarm if projected[L+2] >= beta * T   (and current vintage rate >= 0.25*T, a noise floor)
Surge onset S (per state-season, from FINAL data): first week with rate >= T for 2 consecutive weeks.
Per state-season, first alarm at or before S is recorded:
      lead = S - first_alarm_week (weeks);  'premature' if lead > 4 weeks; 'miss' if no alarm by S.
Sweep alpha / beta, then compare median lead at matched premature-alarm rate.

Everything is pre-specified in this header. T thresholds 2, 3 (primary), 5 per 100k/week.
Output: printed tables + results/lead_time_probe.csv.  Label all results PRELIMINARY.

Usage:  python3 lead_time_probe.py [--fetch]
  --fetch  re-download time-series.csv from the FluSight hub (GitHub raw).
"""
import argparse, sys, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
TS = HERE / "data" / "flusight" / "time-series.csv"
RAW = "https://raw.githubusercontent.com/cdcepi/FluSight-forecast-hub/main/target-data/time-series.csv"
SEASONS = {"2023/24": ("2023-10-01", "2024-05-31"),
           "2024/25": ("2024-10-01", "2025-05-31"),
           "2025/26": ("2025-10-01", "2026-05-31")}

def load(fetch):
    if fetch:
        TS.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(RAW, TS)
    ts = pd.read_csv(TS, parse_dates=["as_of", "target_end_date"])
    ts = ts[(ts.target == "wk inc flu hosp") & (ts.location != "US")]
    final = ts[ts.as_of == ts.as_of.max()].set_index(["location", "target_end_date"]).weekly_rate
    return ts, final

def onset(series, T):
    v = series.values; d = series.index
    for i in range(len(v) - 1):
        if v[i] >= T and v[i + 1] >= T:
            return d[i]
    return None

def run(ts, final, T):
    rows = []
    for sname, (a, b) in SEASONS.items():
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        vint = sorted(ts.as_of[(ts.as_of >= a) & (ts.as_of <= b)].unique())
        sub = ts[ts.as_of.isin(vint)]
        for loc, g in sub.groupby("location"):
            try:
                f = final.loc[loc]
            except KeyError:
                continue
            f = f[(f.index >= a) & (f.index <= b)].sort_index()
            S = onset(f, T)
            for asof, gv in g.groupby("as_of"):
                gv = gv.sort_values("target_end_date")
                L = gv.target_end_date.max()
                if L < a:
                    continue
                last = gv.tail(3)
                if len(last) < 3:
                    continue
                y = np.log(last.weekly_rate.values + 0.1)
                x = np.arange(3)
                slope = np.polyfit(x, y, 1)[0]
                proj = float(np.exp(y[-1] + 2 * slope) - 0.1)
                cur_v = float(last.weekly_rate.values[-1])
                cur_f = float(f.get(L, np.nan))
                rows.append(dict(season=sname, loc=loc, asof=asof, L=L, S=S, proj=proj,
                                 cur_v=cur_v, cur_f=cur_f))
    return pd.DataFrame(rows)

def score(df, rule, k, T):
    out = []
    for (s, loc), g in df.groupby(["season", "loc"]):
        g = g.sort_values("L")
        S = g.S.iloc[0]
        if rule == "census":
            al = g[g.cur_f >= k * T]
        else:
            al = g[(g.proj >= k * T) & (g.cur_v >= 0.25 * T)]
        if S is None or pd.isna(S):
            out.append(dict(surge=False, alarm=len(al) > 0, lead=np.nan))
            continue
        al = al[al.L <= S]
        if len(al) == 0:
            out.append(dict(surge=True, alarm=False, lead=np.nan))
        else:
            out.append(dict(surge=True, alarm=True, lead=(S - al.L.iloc[0]).days / 7))
    o = pd.DataFrame(out)
    sv = o[o.surge]
    return dict(n_surge=len(sv), n_nosurge=int((~o.surge).sum()),
                fa_nosurge=int((o[~o.surge].alarm).sum()),
                miss=float((~sv.alarm).mean()),
                premature=float((sv.lead > 4).mean()),
                med_lead=float(sv.lead.median()),
                useful_1to4=float(((sv.lead >= 1) & (sv.lead <= 4)).mean()))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args()
    ts, final = load(a.fetch)
    res = []
    for T in (2.0, 3.0, 5.0):
        df = run(ts, final, T)
        for rule, ks in (("census", np.round(np.arange(0.3, 1.01, 0.1), 2)),
                         ("forecast", np.round(np.arange(0.6, 2.01, 0.2), 2))):
            for k in ks:
                r = score(df, rule, k, T); r.update(T=T, rule=rule, k=k); res.append(r)
    R = pd.DataFrame(res)
    (HERE / "results").mkdir(exist_ok=True)
    R.to_csv(HERE / "results" / "lead_time_probe.csv", index=False)
    pd.set_option("display.width", 160)
    print("PRELIMINARY: US state flu admissions, real-time vintages, 2023/24-2025/26")
    for T, g in R.groupby("T"):
        print(f"\nT = {T}/100k/wk  (state-seasons with surge: {g.n_surge.iloc[0]}, without: {g.n_nosurge.iloc[0]})")
        print(g[["rule", "k", "med_lead", "useful_1to4", "premature", "miss", "fa_nosurge"]].round(2).to_string(index=False))
    # matched comparison: best median lead with premature <= 10%
    print("\nMatched comparison (premature-alarm rate <= 10%, miss <= 10%): best median lead")
    for T, g in R.groupby("T"):
        for rule in ("census", "forecast"):
            c = g[(g.rule == rule) & (g.premature <= 0.10) & (g.miss <= 0.10)]
            if len(c):
                b = c.sort_values(["med_lead", "useful_1to4"], ascending=False).iloc[0]
                print(f"T={T} {rule:8s} k={b.k}: median lead {b.med_lead:.1f} wk, useful(1-4wk) {b.useful_1to4:.0%}, premature {b.premature:.0%}, miss {b.miss:.0%}")
            else:
                print(f"T={T} {rule:8s}: no setting meets the constraint")

if __name__ == "__main__":
    main()
