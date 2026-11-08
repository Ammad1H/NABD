"""G12: out-of-sample test of the frozen UAE method on other GCC countries' WHO FluNet data.

Pre-registered in docs/PREREG-GCC.md, locked in docs/LOCK-GCC.json BEFORE any GCC data were downloaded.
Scoring refuses to run unless the lock verifies (kit prereg.assert_locked).

Run (repo root):
  python3 -m uae.gcc --selftest     # runs the whole pipeline on the UAE file (already-seen data) as a code check
  python3 -m uae.gcc --score        # scores data/raw/flunet_gcc.csv (after the lock + download)

Design (frozen): forward-in-time. For each country and evaluation season S in 2022/23..2025/26, models are
fitted once at the start of S on that country's own qualifying seasons < S (2020/21 excluded), then forecast
every origin t of S using data through t only (information rule), horizons h = 1..4 data weeks (issue-relative
nowcast, +0.5, +1.5, +2.5 wk with a 1-week simulated publication lag). No pooling across countries.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))

from nabd_kit.prereg import assert_locked  # noqa: E402

from adapters.schemas import reject_person_level  # noqa: E402
from uae.features_v2 import ramadan_weekly  # noqa: E402
from uae.models import Analog, H, NabdUAE, Persistence, QUANTILES, expit, logit  # noqa: E402
from uae.models_v2 import NabdUAEv2  # noqa: E402
from uae.scoring import covered, wis  # noqa: E402

OUT = ROOT / "results" / "gcc"
LOCK = ROOT / "docs" / "LOCK-GCC.json"
PLAN = ["docs/PREREG-GCC.md"]
CODE = ["uae/gcc.py", "uae/models.py", "uae/models_v2.py", "uae/features_v2.py", "uae/scoring.py"]
CONFIG = dict(countries=["OMN", "QAT", "BHR", "KWT", "SAU"], eval_seasons=[2022, 2023, 2024, 2025],
              exclude_training_seasons=[2020], min_year=2015,
              qualify=dict(min_reported_frac=0.8, min_median_specimens=20),
              sentinel_min_qualifying_eval_seasons=3, min_training_seasons=2, min_scored_eval_seasons=2,
              primary=dict(model="NABD-UAE-v1 method", pathogen="flu", comparator="persistence",
                           success="pooled rel WIS < 1 and bootstrap 95% upper < 1"),
              secondary=["vs seasonal-analog", "per country", "RSV", "NABD-UAE-v2-GCC (school_win=0)",
                         "coverage 50/95"],
              bootstrap=dict(unit="country-season", B=2000, seed=0), quantiles=QUANTILES, horizons=list(H))
SER = {"flu": "flu_pos", "rsv": "rsv_pos"}


def iso_week_end(y, w):
    return pd.Timestamp(dt.date.fromisocalendar(int(y), int(w), 7))


def tidy(raw: pd.DataFrame) -> pd.DataFrame:
    reject_person_level(raw, "FluNet GCC")
    d = raw.rename(columns={"COUNTRY_CODE": "country", "ISO_YEAR": "iso_year", "ISO_WEEK": "iso_week",
                            "ORIGIN_SOURCE": "origin", "SPEC_PROCESSED_NB": "specimens", "INF_ALL": "flu_pos",
                            "RSV": "rsv_pos"})
    d = d[["country", "iso_year", "iso_week", "origin", "specimens", "flu_pos", "rsv_pos"]].copy()
    d = d[d.iso_year >= CONFIG["min_year"]]
    d = d.groupby(["country", "iso_year", "iso_week", "origin"], as_index=False).sum(min_count=1)
    d["week_end"] = [iso_week_end(y, w) for y, w in zip(d.iso_year, d.iso_week)]
    d["season"] = np.where(d.iso_week >= 27, d.iso_year, d.iso_year - 1)
    return d


def weekly_series(d: pd.DataFrame, country: str, origin: str | None) -> pd.DataFrame:
    """origin='SENTINEL' -> sentinel rows; None -> all origins summed ('total'). Complete weekly index."""
    x = d[d.country == country]
    if origin:
        x = x[x.origin == origin]
    x = x.groupby("week_end")[["specimens", "flu_pos", "rsv_pos"]].sum(min_count=1)
    if x.empty:
        return pd.DataFrame()
    idx = pd.date_range(x.index.min(), x.index.max(), freq="7D")
    x = x.reindex(idx)
    x.index.name = "week_end"
    x = x.reset_index()
    iso = [t.isocalendar() for t in x.week_end]
    x["iso_year"] = [c[0] for c in iso]
    x["iso_week"] = [c[1] for c in iso]
    x["season"] = np.where(x.iso_week >= 27, x.iso_year, x.iso_year - 1)
    return x


def qualifying(s: pd.DataFrame, pos_col="flu_pos") -> dict:
    q = {}
    for season, g in s.groupby("season"):
        n_weeks = 52
        rep = ((g.specimens > 0) & g[pos_col].notna()).sum()
        med = g.specimens.median() if g.specimens.notna().any() else 0
        q[int(season)] = bool(rep >= CONFIG["qualify"]["min_reported_frac"] * n_weeks
                              and med >= CONFIG["qualify"]["min_median_specimens"])
    return q


def choose_series(d, country):
    sen = weekly_series(d, country, "SENTINEL")
    if len(sen):
        q = qualifying(sen)
        if sum(q.get(s, False) for s in CONFIG["eval_seasons"]) >= CONFIG["sentinel_min_qualifying_eval_seasons"]:
            return "SENTINEL", sen
    tot = weekly_series(d, country, None)
    return "TOTAL", tot


def prep(s: pd.DataFrame, key: str, ns: pd.DataFrame | None) -> pd.DataFrame:
    pos = s[SER[key]]
    out = s[["week_end", "iso_year", "iso_week", "season", "specimens"]].copy()
    out["pos"] = pos
    out["y"] = logit((pos + 0.5) / (s.specimens + 1.0))
    out.loc[pos.isna() | s.specimens.isna() | (s.specimens <= 0), "y"] = np.nan
    out["logspec"] = np.log(s.specimens.clip(lower=1))
    if ns is not None and len(ns):
        n = ns.set_index("week_end").reindex(out.week_end)
        out["ns_pos"] = n[SER[key]].values
        out["ns_spec"] = n["specimens"].values
        out["z"] = logit((out.ns_pos + 0.5) / (out.ns_spec + 1.0))
        out.loc[out.ns_pos.isna() | out.ns_spec.isna() | (out.ns_spec <= 0), "z"] = np.nan
    else:
        out["ns_pos"] = np.nan
        out["ns_spec"] = np.nan
        out["z"] = np.nan
    out["school_break"] = 0.0          # UAE-specific signal: unavailable outside the UAE (declared)
    out["ramadan"] = ramadan_weekly(out.week_end).values
    out["season"] = out.season.astype(int)
    return out.reset_index(drop=True)


def run_country(d, country, key):
    origin, s = choose_series(d, country)
    if s.empty:
        return [], dict(country=country, series=key, origin="none", scored_seasons=[], reason="no data")
    ns = weekly_series(d, country, "NONSENTINEL") if origin == "SENTINEL" else None
    q = qualifying(s, SER[key])
    x = prep(s, key, ns)
    rows, scored = [], []
    for S in CONFIG["eval_seasons"]:
        train = [k for k, ok in q.items() if ok and k < S and k not in CONFIG["exclude_training_seasons"]]
        if not q.get(S, False) or len(train) < CONFIG["min_training_seasons"]:
            continue
        scored.append(S)
        hist = x[x.season < S]
        models = [NabdUAE(x, train), Persistence(x, train), Analog(x, train),
                  NabdUAEv2(x, train, name="NABD-UAE-v2-GCC")]
        # models were fitted on training seasons only; .d=x lets predict() see rows <= origin
        for i in x.index[x.season == S]:
            if i + 4 >= len(x) or x.season.iloc[i + 4] != S or np.isnan(x.y.iloc[i]):
                continue
            for m in models:
                pq = m.predict(i)
                for h in H:
                    if pq.get(h) is None:
                        continue
                    yv = x.y.iloc[i + h]
                    if np.isnan(yv):
                        continue
                    obs = x.pos.iloc[i + h] / x.specimens.iloc[i + h] * 100
                    vals = 100 * expit(np.sort(pq[h]))
                    rows.append(dict(country=country, series=key, origin_source=origin, season=S,
                                     origin=str(x.week_end.iloc[i].date()), horizon=h - 2, model=m.name,
                                     obs=obs, median=float(vals[11]), wis=wis(QUANTILES, vals, obs),
                                     cov50=covered(QUANTILES, vals, obs, 0.5), cov95=covered(QUANTILES, vals, obs, 0.95)))
        del hist
    return rows, dict(country=country, series=key, origin=origin, scored_seasons=scored,
                      qualifying={k: v for k, v in q.items() if k >= 2015})


def common(sc):
    k = ["country", "series", "season", "origin", "horizon"]
    n = sc.groupby(k).model.nunique()
    keep = n[n == sc.model.nunique()].index
    return sc.set_index(k).loc[keep].reset_index()


def rel_boot(sc, a, b, B=2000, seed=0):
    k = ["country", "series", "season", "origin", "horizon"]
    m = sc[sc.model == a].merge(sc[sc.model == b], on=k, suffixes=("_a", "_b"))
    if m.empty:
        return None
    g = m.groupby(["country", "season"])[["wis_a", "wis_b"]].sum().reset_index()
    r = g.wis_a.sum() / g.wis_b.sum()
    rng = np.random.default_rng(seed)
    bs = [g.wis_a.values[kk].sum() / g.wis_b.values[kk].sum()
          for kk in (rng.integers(0, len(g), len(g)) for _ in range(B))]
    return dict(rel_wis=round(float(r), 3), ci95=[round(float(np.quantile(bs, .025)), 3),
                                                  round(float(np.quantile(bs, .975)), 3)],
                n_cells=int(len(m)), n_country_seasons=int(len(g)))


def score(d, countries, out_dir: Path, label: str):
    rows, meta = [], []
    for c in countries:
        for key in SER:
            r, m = run_country(d, c, key)
            rows += r
            meta.append(m)
    sc = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tables").mkdir(exist_ok=True)
    meta_df = pd.DataFrame(meta)
    meta_df.to_csv(out_dir / "tables" / "inclusion.csv", index=False)
    if sc.empty:
        return sc, meta_df, {}
    included = [c for c in countries if len(set(sc[(sc.country == c) & (sc.series == "flu")].season)) >=
                CONFIG["min_scored_eval_seasons"]]
    sc = sc[sc.country.isin(included)]
    cc = pd.concat([common(g) for _, g in sc.groupby("series")], ignore_index=True)
    cc.to_csv(out_dir / "tables" / "scores_long.csv", index=False)
    res = {}
    flu = cc[cc.series == "flu"]
    res["PRIMARY_flu_v1_vs_persistence"] = rel_boot(flu, "NABD-UAE-v1", "persistence")
    if res["PRIMARY_flu_v1_vs_persistence"]:
        p = res["PRIMARY_flu_v1_vs_persistence"]
        res["PRIMARY_verdict"] = "MET" if (p["rel_wis"] < 1 and p["ci95"][1] < 1) else "NOT MET"
    for key in SER:
        x = cc[cc.series == key]
        for a, b in [("NABD-UAE-v1", "seasonal-analog"), ("NABD-UAE-v2-GCC", "persistence"),
                     ("NABD-UAE-v2-GCC", "NABD-UAE-v1"), ("NABD-UAE-v1", "persistence")]:
            res[f"{key}_{a}_vs_{b}"] = rel_boot(x, a, b)
    per = cc.groupby(["series", "country", "model"]).wis.mean().unstack().reset_index()
    per["v1/persistence"] = per["NABD-UAE-v1"] / per["persistence"]
    per["v1/analog"] = per["NABD-UAE-v1"] / per["seasonal-analog"]
    per.round(4).to_csv(out_dir / "tables" / "per_country.csv", index=False)
    ps = cc.groupby(["series", "country", "season", "model"]).wis.mean().unstack().reset_index()
    ps["v1_beats_persistence"] = ps["NABD-UAE-v1"] < ps["persistence"]
    ps.round(4).to_csv(out_dir / "tables" / "per_country_season.csv", index=False)
    cov = cc.groupby(["series", "model"])[["cov50", "cov95"]].mean().round(3).reset_index()
    cov.to_csv(out_dir / "tables" / "coverage.csv", index=False)
    summ = dict(label=label, included_countries=included, results=res,
                coverage=cov.to_dict(orient="records"),
                season_wins_v1_vs_persistence={k: f"{int(g.v1_beats_persistence.sum())}/{len(g)}"
                                               for k, g in ps.groupby("series")})
    (out_dir / "summary.json").write_text(json.dumps(summ, indent=2, default=str))
    return cc, meta_df, summ


def figure(cc, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    per = cc.groupby(["series", "country", "model"]).wis.mean().unstack()
    fig, ax = plt.subplots(figsize=(8, 4))
    labs, vals, cols = [], [], []
    for (series, country), r in per.iterrows():
        labs.append(f"{country} {series.upper()}")
        vals.append(r["NABD-UAE-v1"] / r["persistence"])
        cols.append("#2b7a78" if vals[-1] < 1 else "#c0392b")
    ax.barh(labs, vals, color=cols)
    ax.axvline(1, color="grey", lw=1)
    ax.set_xlabel("mean WIS, frozen UAE method (v1) / persistence  (< 1 = better)")
    ax.set_title("GCC out-of-sample test (forward-in-time, 2022/23–2025/26)")
    fig.tight_layout()
    fig.savefig(out_dir / "gcc_v1_vs_persistence.png", dpi=130)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        raw = pd.read_csv(ROOT / "data" / "raw" / "flunet_are.csv")
        raw["COUNTRY_CODE"] = "ARE"
        d = tidy(raw)
        cc, meta, summ = score(d, ["ARE"], Path("/tmp/gcc_selftest"), "SELFTEST on UAE (already-seen) data")
        print("selftest rows:", len(cc), "inclusion:", meta[["country", "series", "origin", "scored_seasons"]]
              .to_dict(orient="records"))
        return
    if a.score:
        root = assert_locked(LOCK, PLAN, CODE, CONFIG, None)
        print("GCC lock verified, merkle root", root)
        d = tidy(pd.read_csv(ROOT / "data" / "raw" / "flunet_gcc.csv"))
        cc, meta, summ = score(d, CONFIG["countries"], OUT,
                               "GCC out-of-sample, forward-in-time, revised FluNet data; locked before download")
        if len(cc):
            figure(cc, OUT)
        print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main()
