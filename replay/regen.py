"""Regenerate the frozen GCC forward-in-time forecasts WITH full quantiles (DEVIATIONS V1a).

Calls the locked uae.gcc functions unchanged; refuses to run unless the GCC lock verifies; then checks that
the regenerated median and WIS equal results/gcc/tables/scores_long.csv on every common cell.

  python3 -m replay.regen          # writes results/replay/forecasts/*.csv.gz, truth.csv, thresholds.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))

from nabd_kit.prereg import assert_locked  # noqa: E402

from uae import gcc  # noqa: E402
from uae.models import Analog, H, NabdUAE, Persistence, QUANTILES, expit  # noqa: E402
from uae.scoring import wis  # noqa: E402

OUT = ROOT / "results" / "replay"
TARGET = {"flu": "wk flu pos pct", "rsv": "wk rsv pos pct"}
NAMES = {"NABD-UAE-v1": "NABD", "seasonal-analog": "past-season-pattern", "persistence": "persistence"}


def run_country(d, country, key, eval_seasons):
    """Same loop as uae.gcc.run_country (v1, persistence, analog), keeping every quantile."""
    origin, s = gcc.choose_series(d, country)
    if s.empty:
        return [], [], []
    ns = gcc.weekly_series(d, country, "NONSENTINEL") if origin == "SENTINEL" else None
    q = gcc.qualifying(s, gcc.SER[key])
    x = gcc.prep(s, key, ns)
    fc, truth, thr = [], [], []
    for S in eval_seasons:
        train = [k for k, ok in q.items() if ok and k < S and k not in gcc.CONFIG["exclude_training_seasons"]]
        if not q.get(S, False) or len(train) < gcc.CONFIG["min_training_seasons"]:
            continue
        tr = x[x.season.isin(train) & x.y.notna()]
        thr.append(dict(location=country, series=key, season=S, kind="country_q75",
                        T=float(np.quantile(tr.pos / tr.specimens * 100, 0.75)), n_train_seasons=len(train)))
        models = [NabdUAE(x, train), Persistence(x, train), Analog(x, train)]
        for i in x.index[x.season == S]:
            if i + 4 >= len(x) or x.season.iloc[i + 4] != S or np.isnan(x.y.iloc[i]):
                continue
            L = x.week_end.iloc[i]
            for m in models:
                pq = m.predict(i)
                for h in H:
                    if pq.get(h) is None or np.isnan(x.y.iloc[i + h]):
                        continue
                    vals = 100 * expit(np.sort(pq[h]))
                    obs = x.pos.iloc[i + h] / x.specimens.iloc[i + h] * 100
                    te = x.week_end.iloc[i + h]
                    for ql, v in zip(QUANTILES, vals):
                        fc.append((str((L + pd.Timedelta(days=7)).date()), TARGET[key], h - 1, str(te.date()),
                                   country, "quantile", ql, float(v), NAMES[m.name], S, str(L.date())))
                    truth.append((country, TARGET[key], str(te.date()), float(obs), S))
    return fc, truth, thr


def regen(raw_path: Path, countries, eval_seasons, tag: str, check: bool):
    raw = pd.read_csv(raw_path)
    if "COUNTRY_CODE" not in raw.columns or tag == "uae":
        raw["COUNTRY_CODE"] = "ARE"
    d = gcc.tidy(raw)
    fc, truth, thr = [], [], []
    for c in countries:
        for key in gcc.SER:
            a, b, t = run_country(d, c, key, eval_seasons)
            fc += a
            truth += b
            thr += t
    cols = ["reference_date", "target", "horizon", "target_end_date", "location", "output_type",
            "output_type_id", "value", "model", "season", "last_data_week"]
    F = pd.DataFrame(fc, columns=cols)
    T = pd.DataFrame(truth, columns=["location", "target", "target_end_date", "value", "season"]).drop_duplicates()
    TH = pd.DataFrame(thr)
    if check:
        verify(F, T)
    return F, T, TH


def verify(F, T):
    """Regenerated median and WIS must equal the locked scores_long.csv on every common cell."""
    sl = pd.read_csv(ROOT / "results" / "gcc" / "tables" / "scores_long.csv")
    sl = sl[sl.model.isin(NAMES)].copy()
    sl["model"] = sl.model.map(NAMES)
    sl["target"] = sl.series.map(TARGET)
    W = F.pivot_table(index=["location", "target", "season", "last_data_week", "horizon", "model"],
                      columns="output_type_id", values="value").reset_index()
    qcols = [c for c in W.columns if isinstance(c, float)]
    W["median_re"] = W[0.5]
    W = W.merge(F[["location", "target", "last_data_week", "horizon", "target_end_date"]].drop_duplicates(),
                on=["location", "target", "last_data_week", "horizon"])
    W = W.merge(T.rename(columns={"value": "obs_re"})[["location", "target", "target_end_date", "obs_re"]],
                on=["location", "target", "target_end_date"])
    W["wis_re"] = [wis(qcols, r[qcols].values.astype(float), r.obs_re) for _, r in W.iterrows()]
    sl["h"] = sl.horizon + 1   # scores_long stores h-2; contract stores h-1
    m = sl.merge(W, left_on=["country", "target", "season", "origin", "h", "model"],
                 right_on=["location", "target", "season", "last_data_week", "horizon", "model"], how="left")
    assert m.wis_re.notna().all(), f"{m.wis_re.isna().sum()} locked cells missing from the regeneration"
    dm, dw = (m["median"] - m.median_re).abs().max(), (m.wis - m.wis_re).abs().max()
    assert dm < 1e-9 and dw < 1e-9, f"regeneration differs from the lock: median {dm}, wis {dw}"
    print(f"verified: {len(m)} locked cells; max |median diff| {dm:.2e}, max |WIS diff| {dw:.2e}")
    return len(m), float(dm), float(dw)


def restrict_to_locked(F, T, TH):
    """Keep only the country-seasons that the locked GCC scoring included (scores_long.csv)."""
    sl = pd.read_csv(ROOT / "results" / "gcc" / "tables" / "scores_long.csv")
    keep = set(zip(sl.country, sl.series.map(TARGET), sl.season))
    kf = [k in keep for k in zip(F.location, F.target, F.season)]
    kt = [k in keep for k in zip(T.location, T.target, T.season)]
    kh = [k in keep for k in zip(TH.location, TH.series.map(TARGET), TH.season)]
    return F[kf], T[kt], TH[kh]


def main():
    root = assert_locked(gcc.LOCK, gcc.PLAN, gcc.CODE, gcc.CONFIG, None)
    print("GCC lock verified, merkle root", root)
    F, T, TH = regen(ROOT / "data" / "raw" / "flunet_gcc.csv", gcc.CONFIG["countries"],
                     gcc.CONFIG["eval_seasons"], "gcc", check=True)
    F, T, TH = restrict_to_locked(F, T, TH)
    Fu, Tu, THu = regen(ROOT / "data" / "raw" / "flunet_are.csv", ["ARE"], gcc.CONFIG["eval_seasons"], "uae",
                        check=False)
    (OUT / "forecasts").mkdir(parents=True, exist_ok=True)
    allF = pd.concat([F, Fu], ignore_index=True)
    for m, g in allF.groupby("model"):
        g.to_csv(OUT / "forecasts" / f"{m}.csv.gz", index=False, float_format="%.6g")
    pd.concat([T, Tu], ignore_index=True).to_csv(OUT / "truth.csv", index=False, float_format="%.6g")
    pd.concat([TH, THu], ignore_index=True).round(4).to_csv(OUT / "thresholds_country_q75.csv", index=False)
    print("country-seasons:", allF.groupby(["location", "target"]).season.nunique().to_dict())


if __name__ == "__main__":
    main()
