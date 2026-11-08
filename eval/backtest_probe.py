#!/usr/bin/env python3
"""
backtest_probe.py: PRELIMINARY onset-detection back-test for the merged Statement 06 concept.

What it does
  * Loads weekly influenza positivity (INF_ALL / SPEC_PROCESSED_NB) for:
      - UAE sentinel (WHO FluNet, ARE)        -> local case study, n ~ 4 seasons
      - USA non-sentinel clinical labs (FluNet) -> second real track
  * Runs causal (past-only) detectors every week:
      EARS C1, C2, C3, CUSUM(on C2 z), and TREND2 (naive 2-week-ahead log-linear
      forecaster; a placeholder for the Chronos-2 forecaster in the real build)
  * Scores each season against a PRE-SPECIFIED onset definition:
      onset = first week (ISO wk27 -> wk26 season) with positivity >= T
              for 2 consecutive weeks; T is fixed per series BEFORE looking at
              test seasons (UAE 15%, USA 10%); first season of each block = warm-up.
  * Reports lead (weeks before onset; positive = earlier) and quiet-period false alarms.

Usage
  python3 backtest_probe.py                      # uses CSVs in ./data (webfetch copies)
  python3 backtest_probe.py --fetch              # re-download FluNet (ARE, USA) live
  python3 backtest_probe.py --fetch --ilinet     # also pull Delphi ILINet (nat, issue-aware probe)
  python3 backtest_probe.py --sens               # threshold sensitivity (T +/- 5pp)

Run this locally (sandbox egress blocks who.int / delphi.cmu.edu). Requires pandas, numpy.
"""
import argparse, io, json, sys, urllib.request, urllib.parse
import numpy as np, pandas as pd
from pathlib import Path

DATA = Path(__file__).parent / "data"
FLUMART = "https://xmart-api-public.who.int/FLUMART/VIW_FNT"

def fetch_flunet(cc, origin=None, ymin=2010):
    f = f"COUNTRY_CODE eq '{cc}' and ISO_YEAR ge {ymin}"
    if origin: f += f" and ORIGIN_SOURCE eq '{origin}'"
    q = {"$filter": f, "$select": "ISO_YEAR,ISO_WEEK,ORIGIN_SOURCE,SPEC_PROCESSED_NB,INF_ALL,RSV",
         "$format": "csv"}
    url = FLUMART + "?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)
    with urllib.request.urlopen(url, timeout=120) as r:
        return pd.read_csv(io.StringIO(r.read().decode()))

def fetch_ilinet_probe():
    """Checks Delphi issue (vintage) support: same epiweek, two different issues."""
    base = "https://api.delphi.cmu.edu/epidata/fluview/"
    out = {}
    for iss in ["201805", "201815"]:
        q = {"regions": "nat", "epiweeks": "201801", "issues": iss}
        with urllib.request.urlopen(base + "?" + urllib.parse.urlencode(q), timeout=60) as r:
            out[iss] = json.loads(r.read().decode())
    return out

def load(args):
    if args.fetch:
        are = fetch_flunet("ARE", ymin=2020)
        are = are[are.ORIGIN_SOURCE == "SENTINEL"]
        usa = fetch_flunet("USA", origin="NONSENTINEL", ymin=2010)
        are.to_csv(DATA / "flunet_are_live.csv", index=False)
        usa.to_csv(DATA / "flunet_usa_live.csv", index=False)
        blocks_us = [usa]
    else:
        are = pd.read_csv(DATA / "flunet_are_webfetch.csv")
        are = are[are.ORIGIN_SOURCE == "SENTINEL"]
        blocks_us = [pd.read_csv(DATA / "flunet_usa_2015_2019.csv"),
                     pd.read_csv(DATA / "flunet_usa_2022_2026.csv")]
    return are, blocks_us

def prep(df):
    d = df.dropna(subset=["SPEC_PROCESSED_NB"]).copy()
    d["INF_ALL"] = d["INF_ALL"].fillna(0)
    d = d[d.SPEC_PROCESSED_NB > 0]
    d = d.sort_values(["ISO_YEAR", "ISO_WEEK"]).drop_duplicates(["ISO_YEAR", "ISO_WEEK"])
    d["p"] = d.INF_ALL / d.SPEC_PROCESSED_NB
    d["season"] = np.where(d.ISO_WEEK >= 27, d.ISO_YEAR, d.ISO_YEAR - 1)
    return d.reset_index(drop=True)

def detectors(p):
    n = len(p); out = {k: np.zeros(n, bool) for k in ["C1", "C2", "C3", "CUSUM", "TREND2"]}
    z2 = np.full(n, np.nan); S = 0.0
    for t in range(n):
        if t >= 7:
            b = p[t-7:t]; mu, sd = b.mean(), max(b.std(ddof=1), 0.01)
            out["C1"][t] = (p[t]-mu)/sd > 3
        if t >= 9:
            b = p[t-9:t-2]; mu, sd = b.mean(), max(b.std(ddof=1), 0.01)
            z2[t] = (p[t]-mu)/sd
            out["C2"][t] = z2[t] > 3
            S = max(0.0, S + z2[t] - 0.5); out["CUSUM"][t] = S > 4
            if out["CUSUM"][t]: S = 0.0
        if t >= 11:
            c3 = sum(max(0, z2[t-k]-1) for k in range(3) if not np.isnan(z2[t-k]))
            out["C3"][t] = c3 > 2
    return out

def trend2(p, T):
    n = len(p); a = np.zeros(n, bool)
    for t in range(3, n):
        y = np.log(np.clip(p[t-3:t+1], 1e-3, None)); x = np.arange(4)
        slope = np.polyfit(x, y, 1)[0]
        fc = np.exp(y[-1] + 2*slope)
        a[t] = (fc >= T) and (p[t] < T) and slope > 0
    return a

def onset_week(seg_p, T):
    for i in range(len(seg_p)-1):
        if seg_p[i] >= T and seg_p[i+1] >= T: return i
    return None

def evaluate(d, T, label, warmup_seasons=1):
    p = d.p.values
    al = detectors(p); al["TREND2"] = trend2(p, T)
    rows = []
    seasons = sorted(d.season.unique())[warmup_seasons:]
    for s in seasons:
        idx = np.where(d.season.values == s)[0]
        if len(idx) < 20: continue
        o = onset_week(p[idx], T)
        if o is None: continue
        on = idx[o]
        r = {"series": label, "season": f"{s}/{str(s+1)[2:]}",
             "onset": f"{d.ISO_YEAR[on]}w{d.ISO_WEEK[on]:02d}", "p_onset": round(p[on], 3)}
        quiet = [i for i in idx if p[i] < T/2 and not (on-6 <= i <= on)]
        for k, a in al.items():
            win = [i for i in range(max(idx[0], on-6), on+3) if a[i]]
            r[f"lead_{k}"] = (on - win[0]) if win else None
            r[f"fa_{k}"] = int(sum(a[i] for i in quiet))
        r["quiet_wks"] = len(quiet)
        rows.append(r)
    return pd.DataFrame(rows)

def boot_ci(x, B=5000, seed=0):
    x = np.array([v for v in x if v is not None and not pd.isna(v)], float)
    if len(x) < 2: return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    m = [rng.choice(x, len(x)).mean() for _ in range(B)]
    return (x.mean(), *np.percentile(m, [2.5, 97.5]))

def summarise(res):
    dets = ["C1", "C2", "C3", "CUSUM", "TREND2"]
    lines = []
    for lab, g in res.groupby("series"):
        lines.append(f"\n== {lab}: n={len(g)} seasons ==")
        for k in dets:
            m, lo, hi = boot_ci(g[f"lead_{k}"].tolist())
            det = g[f"lead_{k}"].notna().sum()
            fa = g[f"fa_{k}"].sum(); qw = g["quiet_wks"].sum()
            lines.append(f"  {k:7s} detected {det}/{len(g)} onsets in window | mean lead {m:5.2f} wk "
                         f"(boot95 {lo:5.2f},{hi:5.2f}) | quiet-period false alarms {fa}/{qw} wks")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true"); ap.add_argument("--ilinet", action="store_true")
    ap.add_argument("--sens", action="store_true")
    a = ap.parse_args()
    are, us_blocks = load(a)
    configs = [(0.15, 0.10)]
    if a.sens: configs += [(0.10, 0.05), (0.20, 0.15)]
    for T_ae, T_us in configs:
        res = [evaluate(prep(are), T_ae, f"UAE sentinel T={T_ae:.2f}")]
        for i, b in enumerate(us_blocks):
            res.append(evaluate(prep(b), T_us, f"USA clinical T={T_us:.2f}"))
        res = pd.concat(res, ignore_index=True)
        pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
        print(res[["series", "season", "onset", "p_onset"] +
                  [c for c in res.columns if c.startswith("lead_")]].to_string(index=False))
        print(summarise(res))
    if a.ilinet:
        try:
            v = fetch_ilinet_probe()
            for iss, js in v.items():
                ep = js.get("epidata") or []
                print(f"Delphi ILINet nat 201801 @issue {iss}: wili={ep[0]['wili'] if ep else 'NA'}")
            print("If the two wili values differ, issue-aware (vintage) back-testing works.")
        except Exception as e:
            print("Delphi probe failed:", e)

if __name__ == "__main__":
    main()
