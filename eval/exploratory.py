"""EXPLORATORY (post hoc, not pre-registered): where does NABD lose to the FluSight-ensemble?
Does NOT change any model or endpoint. Output: results/tables/exploratory_phase.csv
"""
from pathlib import Path
import numpy as np, pandas as pd
from models.data import final_truth, season_dates, series_as_of
from eval.score import load_model, attach_truth, SEASONS, boot_ratio
from eval.wis import wis

ROOT = Path(__file__).resolve().parents[1]
dates = [d for s in SEASONS for d in season_dates(s)]
M = {m: load_model(m, dates) for m in ["NABD-ensemble", "NABD-EEQ", "FluSight-ensemble"]}
idx = M["NABD-ensemble"].index.intersection(M["FluSight-ensemble"].index)
y = attach_truth(idx, final_truth()); ok = np.isfinite(y); idx, y = idx[ok], y[ok]
last = {R: series_as_of(R)[0].iloc[:, -1] for R in dates}
lo = np.array([last[r][l] for r, l, _ in idx])
ratio = (y + 1) / (lo + 1)
phase = np.where(ratio > 1.25, "rising (truth >1.25x last obs)", np.where(ratio < 0.8, "falling (<0.8x)", "flat (0.8-1.25x)"))
rows = []
for ph in np.unique(phase):
    m = phase == ph
    wa = wis(M["NABD-ensemble"].loc[idx[m]].to_numpy(float), y[m]).sum()
    we = wis(M["NABD-EEQ"].loc[idx[m]].to_numpy(float), y[m]).sum()
    wb = wis(M["FluSight-ensemble"].loc[idx[m]].to_numpy(float), y[m]).sum()
    med_a = M["NABD-ensemble"].loc[idx[m]][0.5].to_numpy(); med_b = M["FluSight-ensemble"].loc[idx[m]][0.5].to_numpy()
    wa_c = wis(M["NABD-ensemble"].loc[idx[m]].to_numpy(float), y[m]); wb_c = wis(M["FluSight-ensemble"].loc[idx[m]].to_numpy(float), y[m])
    _, lo_ci, hi_ci = boot_ratio(wa_c, wb_c, np.array([r for r, _, _ in idx[m]]), np.random.default_rng(99))
    rows.append({"phase": ph, "cells": int(m.sum()), "share_of_FS_WIS": wb, "rel_wis_nabd": wa / wb, "ci_lo": lo_ci, "ci_hi": hi_ci, "rel_wis_eeq_only": we / wb,
                 "nabd_median_bias_log": float(np.mean(np.log1p(med_a) - np.log1p(y[m]))),
                 "fs_median_bias_log": float(np.mean(np.log1p(med_b) - np.log1p(y[m])))})
t = pd.DataFrame(rows); t["share_of_FS_WIS"] = t.share_of_FS_WIS / t.share_of_FS_WIS.sum()
t.to_csv(ROOT / "results" / "tables" / "exploratory_phase.csv", index=False)
print(t.round(3).to_string())
