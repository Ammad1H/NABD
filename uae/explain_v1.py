"""Exact per-signal explanation of the frozen HEADLINE model NABD-UAE-v1 (G11).

The weekly card shows NABD-UAE-v1, so its "Why this forecast" panel must explain v1, not the v2 challenger.
v1 is linear on the logit scale (uae/models.py):

    median_logit(t+h) = y[t] + b0 + b1*dy1 + b2*anom + b3*dclim + b4*dlogspec + median(nested-LOSO residuals)

so the decomposition below is EXACT: the contributions sum to the median logit that NabdUAE.predict()
returns (tested in tests/test_explain_v1.py). This module only READS the fitted coefficients of a
NabdUAE instance; it does not change the frozen model (uae/models.py is untouched).
"""
import numpy as np
import pandas as pd

from uae.models import H, QUANTILES, SERIES, _features, expit

FEATURES = ["dy1", "anom", "dclim", "dlogspec"]
PLAIN = {
    "last_observed_logit": "Latest published week (starting point)",
    "intercept": "Average week-to-week drift",
    "dy1": "Momentum: change over the last week",
    "anom": "Distance from the usual level for this week of the year",
    "dclim": "Usual seasonal change between now and the target week",
    "dlogspec": "Change in testing volume last week",
    "residual_median_offset": "Typical past forecast error (median correction)",
}


def explain_v1(model, i: int) -> dict:
    """{h: DataFrame(feature, value, beta, contribution) or None} for the forecast issued at row i."""
    d = model.d.iloc[: i + 1]
    y0 = float(d.y.iloc[i])
    out = {}
    for h in H:
        F = _features(pd.concat([d, model.d.iloc[i + 1:i + 1 + h][["week_end", "iso_year", "iso_week", "season"]]],
                                ignore_index=True), model.clim, h)
        row = F.iloc[i]
        if np.isnan(y0) or row[FEATURES].isna().any():
            out[h] = None
            continue
        b = model.beta[h]
        x = row[FEATURES].values.astype(float)
        med_off = float(np.quantile(model.resid[h], QUANTILES)[QUANTILES.index(0.5)])
        ex = [("last_observed_logit", y0, 1.0, y0), ("intercept", 1.0, float(b[0]), float(b[0]))]
        ex += [(c, float(v), float(bb), float(v * bb)) for c, v, bb in zip(FEATURES, x, b[1:])]
        ex += [("residual_median_offset", 1.0, med_off, med_off)]
        out[h] = pd.DataFrame(ex, columns=["feature", "value", "beta", "contribution"])
    return out


def explain_frame(model, i: int, key: str, issue_date: str, design: str, target_end_dates: dict) -> pd.DataFrame:
    """Contract format (BUILD-SPEC v1.3): horizon, feature, value, contribution, unit (+ extras)."""
    parts = []
    for h, e in explain_v1(model, i).items():
        if e is None:
            continue
        e = e.copy()
        tot = e.contribution.sum()
        e["pp_effect_loo"] = [np.nan if f == "last_observed_logit" else 100 * expit(tot) - 100 * expit(tot - c)
                              for f, c in zip(e.feature, e.contribution)]
        e.insert(0, "horizon", h - 2)
        e["label"] = e.feature.map(PLAIN)
        e["unit"] = "logit"
        e["series"] = key
        e["target"] = SERIES[key][1]
        e["model"] = model.name
        e["submodel"] = "v1 (dy1+anom+dclim+dlogspec)"
        e["median_pct"] = 100 * expit(tot)
        e["issue_date"] = issue_date
        e["target_end_date"] = target_end_dates[h]
        e["design"] = design
        parts.append(e)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
