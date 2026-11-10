"""Model-agnostic decision replay (DEVIATIONS V1b-V1f).

Inputs: forecast frames in the contract format (reference_date, target, horizon, target_end_date, location,
output_type='quantile', output_type_id, value, model [, season]) and a truth frame (location, target,
target_end_date, value). Any model's forecast file in that format can be replayed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
from nabd_kit.quantiles import exceedance_prob  # noqa: E402

KEYS = ["location", "target", "season", "reference_date", "horizon", "target_end_date"]
PLAYBOOK_T = {"wk flu pos pct": 15.0, "wk rsv pos pct": 10.0}   # playbook tier-2 lower bounds (V1c primary)
P_STAR = 0.30                                                     # playbook p_act (V1b)
PRIMARY_H = 2                                                     # "+2 wk after issue" = target week L+3


def season_of(date) -> int:
    iso = pd.Timestamp(date).isocalendar()
    return int(iso[0] if iso[1] >= 27 else iso[0] - 1)


def load_forecasts(paths) -> pd.DataFrame:
    F = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    F = F[F.output_type == "quantile"].copy()
    if "season" not in F.columns:
        F["season"] = [season_of(t) for t in F.target_end_date]
    return F


def exceedance(F: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    """One row per forecast: P(Y > T). thresholds: location, target, season, T."""
    W = F.pivot_table(index=KEYS + ["model"], columns="output_type_id", values="value").reset_index()
    levels = sorted(c for c in W.columns if isinstance(c, float))
    W = W.merge(thresholds[["location", "target", "season", "T"]], on=["location", "target", "season"])
    W["p_exceed"] = exceedance_prob(W[levels].values, levels, W["T"].values)
    W["median"] = W[0.5]
    lo, hi = min(levels, key=lambda x: abs(x - 0.1)), min(levels, key=lambda x: abs(x - 0.9))
    W["q10"], W["q90"] = W[lo], W[hi]
    return W[KEYS + ["model", "T", "p_exceed", "median", "q10", "q90"]]


def decisions(E: pd.DataFrame, truth: pd.DataFrame, p_star: float = P_STAR) -> pd.DataFrame:
    """Apply the roster rule and label each decision against what happened. Common cells only."""
    D = E.merge(truth.rename(columns={"value": "obs"})[["location", "target", "target_end_date", "obs"]],
                on=["location", "target", "target_end_date"])
    n = D.groupby(KEYS).model.nunique()
    D = D.set_index(KEYS).loc[n[n == D.model.nunique()].index].reset_index()
    D["roster"] = D.p_exceed >= p_star
    D["surge"] = D.obs > D["T"]
    D["missed"] = D.surge & ~D.roster
    D["wasted"] = ~D.surge & D.roster
    D["mismatch"] = D.missed | D.wasted
    D["brier"] = (D.p_exceed - D.surge.astype(float)) ** 2
    return D


def add_references(D: pd.DataFrame) -> pd.DataFrame:
    """always-roster, never-roster and perfect-foresight rows on the same cells."""
    base = D[D.model == D.model.iloc[0]].copy()
    out = [D]
    for name, r in [("always-roster", True), ("never-roster", False), ("perfect-foresight", None)]:
        b = base.copy()
        b["model"] = name
        b["roster"] = b.surge if r is None else r
        b["p_exceed"] = b.roster.astype(float)
        b["missed"], b["wasted"] = b.surge & ~b.roster, ~b.surge & b.roster
        b["mismatch"] = b.missed | b.wasted
        b["brier"] = (b.p_exceed - b.surge.astype(float)) ** 2
        b[["median", "q10", "q90"]] = np.nan
        out.append(b)
    return pd.concat(out, ignore_index=True)


def per_season(D: pd.DataFrame) -> pd.DataFrame:
    g = D.groupby(["location", "target", "season", "horizon", "model"])
    return g.agg(weeks=("surge", "size"), surge_weeks=("surge", "sum"), rostered=("roster", "sum"),
                 missed=("missed", "sum"), wasted=("wasted", "sum"), mismatch=("mismatch", "sum"),
                 brier=("brier", "mean")).reset_index()


def paired_diff(S: pd.DataFrame, a: str, b: str, col: str = "mismatch", B: int = 2000, seed: int = 0) -> dict:
    """Mean per-season difference a - b in `col`, with a bootstrap CI over country-seasons (V1f)."""
    k = ["location", "target", "season", "horizon"]
    m = S[S.model == a].merge(S[S.model == b], on=k, suffixes=("_a", "_b"))
    if m.empty:
        return {}
    d = (m[f"{col}_a"] - m[f"{col}_b"]).values.astype(float)
    rng = np.random.default_rng(seed)
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(B)]
    return dict(a=a, b=b, metric=col, n_country_seasons=int(len(d)), mean_a=round(float(m[f"{col}_a"].mean()), 3),
                mean_b=round(float(m[f"{col}_b"].mean()), 3), diff_per_season=round(float(d.mean()), 3),
                ci95=[round(float(np.quantile(bs, .025)), 3), round(float(np.quantile(bs, .975)), 3)],
                a_better=int((d < 0).sum()), ties=int((d == 0).sum()), a_worse=int((d > 0).sum()))
