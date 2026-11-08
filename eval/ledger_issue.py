#!/usr/bin/env python3
"""NABD forecast ledger: issue one frozen, hashed forecast round (baseline-v0).

Method: empirical analog quantiles.
- For each series (UAE sentinel influenza positivity, RSV positivity), take the h-week change in log-odds
  observed in past seasons in calendar weeks within +/-3 of the current week, keeping windows with the same
  recent-trend sign (last 2-week change) when at least 8 such windows exist.
- Apply the quantiles of those changes to the current log-odds.
This is a transparent BASELINE, not the final model. Chronos-2/GLM forecasts are added as further rows later.

Usage:
  python3 ledger_issue.py --csv data/flunet_are_webfetch.csv           # from cached data
  python3 ledger_issue.py --fetch                                       # pull fresh WHO FluNet (xMart) first
Output: ledger/<issue_date>_baseline-v0.csv plus a SHA-256 line appended to ledger/LEDGER.md.
Commit and push both IMMEDIATELY. The public commit time is the timestamp.
"""
import argparse, datetime as dt, hashlib, os, sys
import numpy as np, pandas as pd

Q = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]
URL = ("https://xmart-api-public.who.int/FLUMART/VIW_FNT?$format=csv&$filter=COUNTRY_CODE%20eq%20%27ARE%27"
       "%20and%20ISO_YEAR%20ge%202022&$select=ISO_YEAR,ISO_WEEK,ORIGIN_SOURCE,SPEC_PROCESSED_NB,INF_ALL,RSV")

def logit(p): p = np.clip(p, 1e-3, 1 - 1e-3); return np.log(p / (1 - p))
def expit(x): return 1 / (1 + np.exp(-x))

def load(args):
    if args.fetch:
        d = pd.read_csv(URL)
    else:
        d = pd.read_csv(args.csv)
    d = d[d.ORIGIN_SOURCE == "SENTINEL"].copy()
    d = d.groupby(["ISO_YEAR", "ISO_WEEK"], as_index=False)[["SPEC_PROCESSED_NB", "INF_ALL", "RSV"]].sum(min_count=1)
    d = d.sort_values(["ISO_YEAR", "ISO_WEEK"]).reset_index(drop=True)
    d["season"] = np.where(d.ISO_WEEK >= 27, d.ISO_YEAR, d.ISO_YEAR - 1)
    d["flu"] = d.INF_ALL / d.SPEC_PROCESSED_NB
    d["rsv"] = d.RSV / d.SPEC_PROCESSED_NB
    return d

def iso_add(y, w, h):
    day = dt.date.fromisocalendar(int(y), int(w), 7) + dt.timedelta(weeks=h)
    c = day.isocalendar(); return c[0], c[1]

def forecast(d, col):
    s = d.dropna(subset=[col]).reset_index(drop=True)
    last = s.iloc[-1]; cur_season = last.season
    x = logit(s[col].values)
    trend = np.sign(x[-1] - x[-3]) if len(x) >= 3 else 0
    out = []
    for h in range(1, 5):
        deltas, deltas_same = [], []
        for i in range(2, len(s) - h):
            if s.season[i] == cur_season:
                continue
            if abs(((s.ISO_WEEK[i] - last.ISO_WEEK + 26) % 52) - 26) > 3:
                continue
            dlt = x[i + h] - x[i]
            deltas.append(dlt)
            if np.sign(x[i] - x[i - 2]) == trend:
                deltas_same.append(dlt)
        use = deltas_same if len(deltas_same) >= 8 else deltas
        ty, tw = iso_add(last.ISO_YEAR, last.ISO_WEEK, h)
        qs = np.quantile(use, Q)
        for q, v in zip(Q, qs):
            out.append(dict(series=f"UAE_sentinel_{col}_positivity", origin_week=f"{int(last.ISO_YEAR)}-W{int(last.ISO_WEEK):02d}",
                            target_week=f"{ty}-W{tw:02d}", horizon=h, quantile=q, value=round(float(expit(x[-1] + v)), 4),
                            n_analogs=len(use), trend_conditioned=len(deltas_same) >= 8))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv", default="data/flunet_are_webfetch.csv")
    ap.add_argument("--fetch", action="store_true"); args = ap.parse_args()
    d = load(args)
    rows = forecast(d, "flu") + forecast(d, "rsv")
    issue = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    os.makedirs("ledger", exist_ok=True)
    path = f"ledger/{issue}_baseline-v0.csv"
    df = pd.DataFrame(rows); df.insert(0, "model", "NABD-baseline-v0"); df.insert(0, "issued_utc", issue)
    # Honest horizon: weeks between the ISSUE date and the end of the target ISO week.
    # With the ~10-11 day WHO FluNet lag, data-horizon h=1 is already past at issue (a nowcast).
    today = dt.datetime.now(dt.timezone.utc).date()
    def wk_end(s):
        y, w = s.split("-W"); return dt.date.fromisocalendar(int(y), int(w), 7)
    df["target_week_end"] = df.target_week.map(lambda s: wk_end(s).isoformat())
    df["weeks_ahead_of_issue"] = df.target_week.map(lambda s: round((wk_end(s) - today).days / 7, 1))
    df["horizon_label"] = df.weeks_ahead_of_issue.map(lambda x: "nowcast (already ended)" if x <= 0 else f"+{x} wk")
    df.to_csv(path, index=False)
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    with open("ledger/LEDGER.md", "a") as f:
        f.write(f"| {issue} | {path} | {h} | data source: {'WHO xMart live' if args.fetch else args.csv} |\n")
    print(df[df["quantile"].isin([0.1, 0.5, 0.9])].pivot_table(index=["series", "target_week", "horizon_label"], columns="quantile", values="value"))
    print("\nSHA-256:", h, "\nNow: git add ledger && git commit -m 'ledger issue' && git push  (the public commit time is the timestamp)")

if __name__ == "__main__":
    main()
