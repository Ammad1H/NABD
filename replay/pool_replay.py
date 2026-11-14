"""Decision replay of the S1 held-out forecasts (DEVIATIONS V2; POST HOC, EXPLORATORY).

  python3 -m replay.pool_replay

Reads the forecasts written by the locked pool.score run (results/pool/tables/forecasts_heldout.csv.gz), applies the
V1b roster rule through the model-agnostic replay.engine, and writes results/replay/pool/. Nothing is refitted.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pool import config as C
from pool.features import load, own_train_seasons
from replay import engine as E

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "results" / "pool" / "tables"
OUT = ROOT / "results" / "replay" / "pool"
TARGET = "wk flu pos pct"
MAIN, LOCAL = "NABD-Pool", "NABD-UAE-v1"
COMPARATORS = [LOCAL, "persistence", "seasonal-analog"]
LABEL = {MAIN: "pooled model (NABD-Pool)", LOCAL: "own-record model (local v1)", "persistence": "last week carried forward",
         "seasonal-analog": "past-season pattern"}
REFS = ["always-roster", "never-roster", "perfect-foresight"]


def contract_forecasts() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Wide held-out file -> replay contract format (horizon = h - 1, as in replay.regen) + truth frame."""
    W = pd.read_csv(POOL / "forecasts_heldout.csv.gz")
    qcols = [c for c in W.columns if c.startswith("q")]
    W = W.dropna(subset=qcols + ["obs"])
    W["target_end_date"] = (pd.to_datetime(W.origin) + pd.to_timedelta(7 * W.h, unit="D")).dt.strftime("%Y-%m-%d")
    W["reference_date"] = (pd.to_datetime(W.origin) + pd.Timedelta(days=7)).dt.strftime("%Y-%m-%d")
    F = W.melt(id_vars=["country", "season", "h", "model", "reference_date", "target_end_date"], value_vars=qcols,
               var_name="output_type_id", value_name="value")
    F["output_type_id"] = F.output_type_id.str[1:].astype(float)
    F = F.rename(columns={"country": "location"})
    F["horizon"], F["target"], F["output_type"] = F.h - 1, TARGET, "quantile"
    truth = (W[["country", "target_end_date", "obs", "season"]].drop_duplicates(["country", "target_end_date"])
             .rename(columns={"country": "location", "obs": "value"}))
    truth["target"] = TARGET
    return F.drop(columns="h"), truth


def check_against_scores() -> dict:
    """V2a: stored median == scores_long median on every common cell (to the file's 3-decimal rounding; V2a-note)."""
    W = pd.read_csv(POOL / "forecasts_heldout.csv.gz", usecols=["country", "season", "i", "h", "model", "q0.5"])
    S = pd.read_csv(POOL / "scores_long.csv", usecols=["country", "season", "i", "h", "model", "median"])
    m = W.dropna().merge(S, on=["country", "season", "i", "h", "model"])
    d = float((m["q0.5"] - m["median"]).abs().max())
    assert len(m) == len(S) and d <= 5.0001e-4, f"forecast file does not match scores_long ({len(m)} vs {len(S)}, max diff {d})"
    return dict(cells=int(len(m)), max_abs_diff=d, tolerance="3-decimal rounding of the stored file (5e-4 pp)")


def country_thresholds(F: pd.DataFrame) -> pd.DataFrame:
    """V2c primary: q75 of the country's weekly positivity over its own training seasons (no evaluation-season data)."""
    D = load(ROOT / "data" / "raw" / "flunet_pool_held.csv", C.HELD)
    rows = []
    for (c, S), _ in F.groupby(["location", "season"]):
        x, q = D[c]["x"], D[c]["q"]
        tr = x[x.season.isin(own_train_seasons(q, int(S))) & x.y.notna()]
        rows.append(dict(location=c, target=TARGET, season=int(S), n_train_seasons=int(tr.season.nunique()),
                         T=float(np.quantile(tr.pos / tr.specimens * 100, 0.75))))
    return pd.DataFrame(rows)


def cluster_diff(S: pd.DataFrame, a: str, b: str, col="mismatch", B=2000, seed=0) -> list[float]:
    """V2e sensitivity: CI of the mean per-season difference, resampling countries."""
    k = ["location", "target", "season", "horizon"]
    m = S[S.model == a].merge(S[S.model == b], on=k, suffixes=("_a", "_b"))
    m["d"] = (m[f"{col}_a"] - m[f"{col}_b"]).astype(float)
    groups = [g.d.values for _, g in m.groupby("location")]
    rng = np.random.default_rng(seed)
    bs = [np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))]).mean() for _ in range(B)]
    return [round(float(np.quantile(bs, .025)), 3), round(float(np.quantile(bs, .975)), 3)]


def block(S: pd.DataFrame) -> dict:
    tot = S.groupby("model")[["weeks", "surge_weeks", "rostered", "missed", "wasted", "mismatch"]].sum()
    n = int(S[S.model == MAIN].shape[0])
    r = dict(n_country_seasons=n, n_countries=int(S.location.nunique()), totals=tot.to_dict("index"),
             per_season_mean={m: {c: round(float(v) / n, 2) for c, v in row.items()} for m, row in tot.to_dict("index").items()},
             brier=S.groupby("model").brier.mean().round(4).to_dict())
    for c in COMPARATORS:
        for col in ["mismatch", "missed", "wasted"]:
            d = E.paired_diff(S, MAIN, c, col)
            if d and col == "mismatch":
                d["ci95_country_cluster"] = cluster_diff(S, MAIN, c, col)
            r[f"{MAIN}_minus_{c}_{col}"] = d
    return r


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chk = check_against_scores()
    F, truth = contract_forecasts()
    TH = {"country_q75": country_thresholds(F)}
    TH["playbook"] = TH["country_q75"].assign(T=E.PLAYBOOK_T[TARGET])
    TH["country_q75"].round(4).to_csv(OUT / "thresholds_country_q75.csv", index=False)
    n_own = (pd.read_csv(POOL / "scores_long.csv", usecols=["country", "season", "n_own"]).drop_duplicates()
             .rename(columns={"country": "location"}))
    summ = dict(status="POST HOC, EXPLORATORY (DEVIATIONS V2). Not a confirmatory result.",
                forecasts="results/pool/tables/forecasts_heldout.csv.gz (locked run, unchanged)", check_v2a=chk,
                rule=dict(p_star=E.P_STAR, primary_horizon="+2 wk after issue (target week L+3)",
                          primary_threshold="country_q75", secondary_threshold="playbook 15%"), results={})
    for kind, th in TH.items():
        Ex = E.exceedance(F, th)
        for p in ([0.30, 0.20, 0.50] if kind == "country_q75" else [0.30]):
            D = E.add_references(E.decisions(Ex, truth, p))
            S = E.per_season(D).merge(n_own, on=["location", "season"], how="left")
            S.to_csv(OUT / f"per_season_{kind}_p{int(p * 100)}.csv", index=False)
            if kind == "country_q75" and p == 0.30:
                D.round(4).to_csv(OUT / "weekly_decisions.csv.gz", index=False)
            for h in sorted(S.horizon.unique()):
                s = S[S.horizon == h]
                summ["results"][f"{kind}|p{int(p * 100)}|h{h}"] = block(s)
                if p == 0.30:
                    summ["results"][f"{kind}|p{int(p * 100)}|h{h}|short_history"] = block(s[s.n_own <= C.SHORT_HISTORY_MAX_OWN_SEASONS])
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    write_summary(summ)
    figure()
    print((OUT / "SUMMARY.md").read_text())


def _line(r: dict, comp: str) -> str:
    d = r[f"{MAIN}_minus_{comp}_mismatch"]
    return (f"- vs {LABEL[comp]}: **{d['mean_a']:.1f} vs {d['mean_b']:.1f}** mismatch weeks a season "
            f"(difference {d['diff_per_season']:+.2f}; 95% CI {d['ci95'][0]:+.2f} to {d['ci95'][1]:+.2f} resampling "
            f"country-seasons, {d['ci95_country_cluster'][0]:+.2f} to {d['ci95_country_cluster'][1]:+.2f} resampling countries; "
            f"pooled better in {d['a_better']}, tied in {d['ties']}, worse in {d['a_worse']} of {d['n_country_seasons']}).")


def _split(r: dict, comp: str) -> str:
    a, b = r[f"{MAIN}_minus_{comp}_missed"], r[f"{MAIN}_minus_{comp}_wasted"]
    return (f"  Missed surge weeks a season: {a['mean_a']:.1f} vs {a['mean_b']:.1f}; "
            f"wasted surge weeks: {b['mean_a']:.1f} vs {b['mean_b']:.1f}.")


def write_summary(summ: dict):
    R = summ["results"]
    L = ["# Decision replay of the pooled model on the held-out countries (influenza)", "",
         "_POST HOC and EXPLORATORY (DEVIATIONS V2, declared before computing). The forecasts are the locked S1 "
         "held-out forecasts, unchanged; their accuracy had already been seen. Not a confirmatory result._", "",
         "Rule (same as DEVIATIONS V1b): each week, for the week about two weeks after issue, roster surge capacity "
         "if the forecast gives at least a 30% chance that positivity exceeds the threshold T. A *missed* week is a "
         "surge week that was not rostered; a *wasted* week was rostered without a surge; mismatch = missed + wasted.", ""]
    for kind, title in [("country_q75", "Primary threshold: country-relative (75th percentile of the country's own earlier seasons)"),
                        ("playbook", "Secondary threshold: the playbook's 15% (written for UAE levels)")]:
        r = R[f"{kind}|p30|h{E.PRIMARY_H}"]
        L += [f"## {title}", "",
              f"{r['n_country_seasons']} country-seasons in {r['n_countries']} countries; "
              f"{r['totals'][MAIN]['surge_weeks']} surge weeks out of {r['totals'][MAIN]['weeks']} decision weeks.", ""]
        for c in COMPARATORS:
            L += [_line(r, c), _split(r, c)]
        L += ["", "| Rule input | Missed / season | Wasted / season | Mismatch / season | Brier |", "|---|---|---|---|---|"]
        for m in [MAIN, *COMPARATORS, *REFS]:
            pm = r["per_season_mean"][m]
            L.append(f"| {LABEL.get(m, m)} | {pm['missed']:.1f} | {pm['wasted']:.1f} | {pm['mismatch']:.1f} | {r['brier'][m]:.3f} |")
        sh = R[f"{kind}|p30|h{E.PRIMARY_H}|short_history"]
        if sh["n_country_seasons"]:
            d = sh[f"{MAIN}_minus_{LOCAL}_mismatch"]
            L += ["", f"Short-history stratum (≤ {C.SHORT_HISTORY_MAX_OWN_SEASONS} own earlier seasons; {sh['n_country_seasons']} "
                      f"country-seasons): pooled {d['mean_a']:.1f} vs local {d['mean_b']:.1f} mismatch weeks a season "
                      f"(difference {d['diff_per_season']:+.2f}; 95% CI {d['ci95'][0]:+.2f} to {d['ci95'][1]:+.2f})."]
        L.append("")
    L += ["## Other horizons and trigger probabilities (primary threshold; pooled minus local v1, mismatch weeks a season)", "",
          "| Target week | p* | Pooled | Local v1 | Difference (95% CI, country-seasons) |", "|---|---|---|---|---|"]
    for h in sorted({int(k.split("|h")[1].split("|")[0]) for k in R if k.startswith("country_q75|p30")}):
        for p in ([30, 20, 50] if h == E.PRIMARY_H else [30]):
            d = R[f"country_q75|p{p}|h{h}"][f"{MAIN}_minus_{LOCAL}_mismatch"]
            L.append(f"| L+{h + 1} | {p / 100:.2f} | {d['mean_a']:.1f} | {d['mean_b']:.1f} | {d['diff_per_season']:+.2f} "
                     f"({d['ci95'][0]:+.2f} to {d['ci95'][1]:+.2f}) |")
    S = pd.read_csv(OUT / "per_season_country_q75_p30.csv")
    S = S[S.horizon == E.PRIMARY_H].pivot_table(index=["location", "season", "surge_weeks", "weeks"], columns="model",
                                                values="mismatch").reset_index()
    L += ["", "## Every country-season (primary threshold; mismatch weeks)", "",
          "| Country | Season | Decision weeks | Surge weeks | Pooled | Local v1 | Last week | Past-season pattern |", "|---|---|---|---|---|---|---|---|"]
    for _, x in S.sort_values(["location", "season"]).iterrows():
        L.append(f"| {x.location} | {int(x.season)}/{(int(x.season) + 1) % 100:02d} | {int(x.weeks)} | {int(x.surge_weeks)} | "
                 f"{int(x[MAIN])} | {int(x[LOCAL])} | {int(x['persistence'])} | {int(x['seasonal-analog'])} |")
    L += ["", "## Limits",
          "- Post hoc: the accuracy of these forecasts was known before this replay was declared.",
          "- Positivity thresholds, not hospital load; a mismatch week is a rule outcome, not a measured cost.",
          "- Finalised FluNet data; no real-time versions exist. RSV not replayed (quantiles not saved by the locked run).",
          "- The declaration was written before computing but committed together with these results (DEVIATIONS V2 note)."]
    (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n")


def figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S = pd.read_csv(OUT / "per_season_country_q75_p30.csv")
    S = S[S.horizon == E.PRIMARY_H]
    order = [MAIN, LOCAL, "persistence", "seasonal-analog"]
    g = S[S.model.isin(order)].groupby("model")[["missed", "wasted"]].mean().loc[order]
    fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=160)
    y = np.arange(len(order))[::-1]
    ax.barh(y, g.missed, color="#b4505b", label="missed surge weeks")
    ax.barh(y, g.wasted, left=g.missed, color="#1f7a8c", label="wasted surge weeks")
    for yi, tot in zip(y, g.missed + g.wasted):
        ax.text(tot + 0.1, yi, f"{tot:.1f}", va="center", fontsize=8)
    ax.set_yticks(y, [LABEL[m] for m in order], fontsize=8)
    ax.set_xlabel("mismatch weeks per country-season (lower is better)", fontsize=8)
    ax.set_title("Roster rule replayed on 18 held-out countries, influenza (post hoc)", fontsize=9, loc="left")
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "pool_replay_mismatch_weeks.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
