"""End-to-end MECHANICS demo on synthetic data.

Every number printed here comes from simulated seasons and a deliberately
flawed toy model. It shows that the kit's pieces run together and move in the
expected direction. It is NOT evidence about NABD, influenza or RSV, and must
not be quoted in the registration, deck, Q&A or app.

Run: python examples/demo_synthetic.py
"""
from __future__ import annotations

import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nabd_kit import card, decision, ledger, phase, prereg, quantiles, recalibrate, scoring, synth  # noqa: E402
from nabd_kit.baselines import flat_baseline  # noqa: E402
from nabd_kit.ensemble import quantile_average  # noqa: E402
from nabd_kit.gbm_global import GlobalQuantileGBM, qcols  # noqa: E402

LV = quantiles.FLUSIGHT_LEVELS
H = (1, 2, 3, 4)
IN_SEASON = (4, 34)  # weeks within a synthetic season that count as "forecast season"
TRAIN_SEASONS, TEST_SEASONS = range(0, 5), range(5, 8)
BANNER = "SYNTHETIC DATA: checks that the code works. Says nothing about NABD or real influenza/RSV."


def rel(a, b):
    return float(np.mean(a) / np.mean(b))


def build_forecasts(world: pd.DataFrame):
    rows, qm, qb = [], [], []
    for loc, g in world.groupby("location", sort=True):
        g = g.sort_values("date")
        y, dates = g["value"].to_numpy(), g["date"].to_numpy()
        seas, wk = g["season"].to_numpy(), g["week_in_season"].to_numpy()
        ph = phase.classify(phase.asof_log_slope(y, window=3), band=0.1)
        for t in range(10, len(y) - max(H)):
            if not (IN_SEASON[0] <= wk[t] <= IN_SEASON[1]):
                continue
            m = synth.momentum_forecast(y[: t + 1], LV, H)
            b = flat_baseline(y[: t + 1], LV, H)
            for i, h in enumerate(H):
                rows.append((loc, dates[t], seas[t], h, y[t], y[t + h], ph[t]))
                qm.append(m[i])
                qb.append(b[i])
    meta = pd.DataFrame(rows, columns=["location", "ref_date", "season", "horizon", "y_ref", "y", "phase"])
    return meta, np.array(qm), np.array(qb)


def tracked(meta: pd.DataFrame, q: np.ndarray, lr: float = 0.1) -> np.ndarray:
    """Issue forecasts in time order; apply each truth only once it would exist."""
    trk = recalibrate.QuantileTracker(LV, lr=lr)
    out = np.empty_like(q)
    pending = defaultdict(list)
    order = meta.sort_values("ref_date").index.to_numpy()
    for ref_date, idx in meta.loc[order].groupby("ref_date", sort=True).groups.items():
        for avail in sorted(d for d in list(pending) if d <= ref_date):
            for grp, iss, yy in pending.pop(avail):
                trk.update(iss, yy, grp)
        idx = np.asarray(idx)
        for h in H:
            sel = idx[meta.loc[idx, "horizon"].to_numpy() == h]
            if sel.size == 0:
                continue
            out[sel] = trk.adjust(q[sel], f"h{h}")
            avail = ref_date + pd.Timedelta(weeks=h)
            pending[avail].append((f"h{h}", out[sel], meta.loc[sel, "y"].to_numpy()))
    return out


def main() -> None:
    t0 = time.time()
    print("=" * 88 + f"\n{BANNER}\n" + "=" * 88)
    world = synth.make_world(n_locations=20, n_seasons=8, seed=7)
    meta, qm, qb = build_forecasts(world)
    tr = meta["season"].isin(TRAIN_SEASONS).to_numpy()
    te = meta["season"].isin(TEST_SEASONS).to_numpy()
    y = meta["y"].to_numpy()
    groups = (meta["phase"] + "|h" + meta["horizon"].astype(str)).to_numpy()
    print(f"forecast rows: {len(meta):,} (train {tr.sum():,}, test {te.sum():,}); built in {time.time() - t0:.1f}s")

    # 1. Diagnose the flawed model: WIS decomposition by as-of phase (test seasons).
    w_m, w_b = scoring.wis(qm, y, LV), scoring.wis(qb, y, LV)
    disp, over, under = scoring.wis_components(qm, y, LV)
    print("\n[1] Toy trend-follower vs flat baseline on test seasons, by AS-OF phase")
    print(f"{'phase':<9}{'n':>7}{'rel WIS':>9}   share of toy WIS: dispersion / over / under")
    for ph in ["rising", "flat", "falling"]:
        s = te & (meta["phase"].to_numpy() == ph)
        tot = w_m[s].sum()
        print(f"{ph:<9}{s.sum():>7}{rel(w_m[s], w_b[s]):>9.2f}   "
              f"{disp[s].sum() / tot:.0%} / {over[s].sum() / tot:.0%} / {under[s].sum() / tot:.0%}")

    # 2. Phase-aware blend + spread, fitted on TRAIN seasons only, applied to TEST.
    rc = recalibrate.GroupedRecalibrator(LV, min_n=200).fit(qm[tr], qb[tr], y[tr], groups[tr])
    q_rc = rc.transform(qm[te], qb[te], groups[te])
    w_rc = scoring.wis(q_rc, y[te], LV)
    print("\n[2] Phase-aware blend toward persistence + spread scale (12 groups, fitted on train only)")
    print(f"{'phase':<9}{'toy':>8}{'blend':>8}   (relative WIS vs flat baseline, test seasons)")
    for ph in ["rising", "flat", "falling"]:
        s = meta.loc[te, "phase"].to_numpy() == ph
        print(f"{ph:<9}{rel(w_m[te][s], w_b[te][s]):>8.2f}{rel(w_rc[s], w_b[te][s]):>8.2f}")
    for g in ["rising|h2", "flat|h2", "falling|h2"]:
        p = rc.params_.get(g, {})
        print(f"   fitted {g:<11} w(toy)={p.get('w', float('nan')):.2f}  spread={p.get('s_lo', float('nan')):.2f}")

    # 3. Online calibration (quantile tracking) on the raw toy model, delayed updates.
    q_tr = tracked(meta.loc[te].reset_index(drop=True), qm[te], lr=0.1)
    print("\n[3] Online calibration by quantile tracking (truth applied only after it would exist)")
    for name, q in [("toy raw", qm[te]), ("toy + tracking", q_tr)]:
        c50 = scoring.interval_hit(q, y[te], LV, 0.5).mean()
        c90 = scoring.interval_hit(q, y[te], LV, 0.9).mean()
        print(f"   {name:<16} 50% PI covers {c50:.0%}, 90% PI covers {c90:.0%}, "
              f"rel WIS {rel(scoring.wis(q, y[te], LV), w_b[te]):.2f}")

    # 4. Global quantile GBM trained across all locations on train seasons.
    t1 = time.time()
    train_rows = world[world["season"].isin(TRAIN_SEASONS)]
    gbm = GlobalQuantileGBM(LV, horizons=H, gbm_params={"max_iter": 150}).fit(train_rows)
    ref_dates = np.sort(meta.loc[te, "ref_date"].unique())
    preds = pd.concat([gbm.predict(world[world["date"] <= d], d) for d in ref_dates], ignore_index=True)
    key = ["location", "reference_date", "horizon"]
    m_te = meta.loc[te].rename(columns={"ref_date": "reference_date"}).reset_index(drop=True)
    merged = m_te.merge(preds[key + qcols(LV)], on=key, how="left", validate="one_to_one")
    q_gbm = merged[qcols(LV)].to_numpy()
    assert not np.isnan(q_gbm).any(), "GBM missing some test forecasts"
    w_g = scoring.wis(q_gbm, y[te], LV)
    print(f"\n[4] Global quantile GBM ({gbm.n_train_rows_:,} training rows, fit+predict {time.time() - t1:.0f}s)")
    q_ens = quantile_average([qm[te], q_gbm, qb[te]])
    w_e = scoring.wis(q_ens, y[te], LV)
    print(f"{'model':<28}{'rel WIS vs flat baseline (test)':>32}")
    for name, w in [("toy trend-follower", w_m[te]), ("phase-aware blend", w_rc),
                    ("global GBM", w_g), ("ensemble: toy+GBM+baseline", w_e)]:
        print(f"{name:<28}{rel(w, w_b[te]):>32.2f}")
    bt = scoring.block_bootstrap_ratio(
        pd.DataFrame({"date": meta.loc[te, "ref_date"].to_numpy(), "season": meta.loc[te, "season"].to_numpy(),
                      "a": w_e, "b": w_b[te]}), "a", "b", "date", block_len=4, n_boot=1000, group_col="season")
    print(f"   ensemble vs baseline, moving-block bootstrap 95% CI: {bt['ratio']:.2f} ({bt['lo']:.2f}-{bt['hi']:.2f})")
    d_series = (pd.DataFrame({"d": w_e - w_b[te], "date": meta.loc[te, "ref_date"].to_numpy()})
                .groupby("date")["d"].mean().to_numpy())
    dm = scoring.dm_test(d_series, h=2)
    print(f"   Diebold-Mariano (per-date mean WIS difference): stat {dm['stat']:.2f}, p {dm['p_value']:.3g}")

    # 5. Decision value: event = value two weeks ahead above 2x the location's training median.
    thr = (world[world["season"].isin(TRAIN_SEASONS)].groupby("location")["value"].median() * 2.0)
    h2 = (meta.loc[te, "horizon"] == 2).to_numpy()
    t_loc = meta.loc[te, "location"].map(thr).to_numpy()[h2]
    event = y[te][h2] > t_loc
    alphas = [0.05, 0.1, 0.2, 0.3, 0.5]
    print(f"\n[5] Relative economic value, event base rate {event.mean():.0%} (1 = perfect, 0 = base rates)")
    print(f"{'model':<28}" + "".join(f"{'C/L=' + str(a):>10}" for a in alphas))
    for name, q in [("toy trend-follower", qm[te][h2]), ("flat baseline", qb[te][h2]),
                    ("global GBM", q_gbm[h2]), ("ensemble", q_ens[h2])]:
        p = np.array([quantiles.exceedance_prob(q[i:i + 1], LV, t_loc[i])[0] for i in range(len(q))])
        v = decision.relative_economic_value(p, event, alphas)
        print(f"{name:<28}" + "".join(f"{x:>10.2f}" for x in v))

    # 6. A card that keeps observed and forecast apart, checked against its numbers.
    i = int(np.argmax((meta.loc[te, "phase"].to_numpy() == "rising") & h2 & (y[te] < meta.loc[te, "y_ref"].to_numpy())))
    row = meta.loc[te].iloc[i]
    c = card.make_card(row["y_ref"] * 0.8, row["y_ref"], q_ens[i], LV, horizon=2, capacity=row["y_ref"] * 1.5)
    print("\n[6] Card:", c.text_en, "| contradictions:", card.check_card(c, q_ens[i], LV, capacity=row["y_ref"] * 1.5))

    # 7. Ledger + lock + goalpost guard.
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        fc = merged[key].assign(**{c: q_ens[:, j] for j, c in enumerate(qcols(LV))})
        (base / "forecasts.csv").write_bytes(ledger.canonical_csv_bytes(fc, key))
        (base / "plan.md").write_text("Primary: relative WIS vs flat baseline; block bootstrap, block 4.\n")
        mj, _ = ledger.write_manifest(ledger.build_manifest([base / "forecasts.csv", base / "plan.md"], base),
                                      base / "lock")
        cfg = {"members": ["toy", "gbm", "baseline"], "weights": "equal", "band": 0.1}
        prereg.lock(base / "LOCK.json", [base / "plan.md"], [Path(__file__)], cfg, data_manifest=mj)
        prereg.assert_locked(base / "LOCK.json", [base / "plan.md"], [Path(__file__)], cfg, data_manifest=mj)
        try:
            prereg.assert_locked(base / "LOCK.json", [base / "plan.md"], [Path(__file__)],
                                 dict(cfg, band=0.15), data_manifest=mj)
            guard = "NOT triggered (bug)"
        except prereg.GoalpostError:
            guard = "refused the changed config, as it should"
        print(f"\n[7] Ledger intact: {ledger.verify_manifest(mj) == []}; goalpost guard {guard}")
    print(f"\ndone in {time.time() - t0:.0f}s\n{BANNER}")


if __name__ == "__main__":
    main()
