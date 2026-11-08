"""Turning forecast probabilities into decisions and their value.

Cost-loss model: acting costs C; an event that hits without action costs L.
A user who trusts calibrated probabilities acts when P(event) > alpha = C / L.

Relative economic value (Richardson 2000), per case, in units of L, base rate s:
    E_clim    = min(alpha, s)            (always act, or never act)
    E_perfect = s * alpha                (act exactly when the event happens)
    E_fcst    = (hits + false alarms) * alpha + misses
    V         = (E_clim - E_fcst) / (E_clim - E_perfect)
V = 1 is a perfect forecast, V = 0 is no better than base rates, V < 0 is worse.
Compute V for every model on the SAME event definition and the same cases.
"""
from __future__ import annotations

import numpy as np


def expense(p, event, alpha: float, threshold: float | None = None) -> float:
    """Mean expense per case (units of L) when acting on p > threshold (default alpha)."""
    p = np.asarray(p, dtype=float)
    o = np.asarray(event, dtype=bool)
    act = p > (alpha if threshold is None else threshold)
    hits = np.mean(act & o)
    false_alarms = np.mean(act & ~o)
    misses = np.mean(~act & o)
    return float((hits + false_alarms) * alpha + misses)


def relative_economic_value(p, event, alphas, envelope: bool = False,
                            thresholds=None) -> np.ndarray:
    """V(alpha) for each cost-loss ratio in `alphas`.

    envelope=False: the user acts on p > alpha (value of a trusted, calibrated
    forecast). envelope=True: the best probability threshold per alpha (the
    potential value if the user re-tunes their trigger; report it as such).
    """
    o = np.asarray(event, dtype=bool)
    s = float(o.mean())
    thr = np.linspace(0.0, 1.0, 101) if thresholds is None else np.asarray(thresholds, float)
    out = []
    for a in np.asarray(alphas, dtype=float):
        e_clim, e_perf = min(a, s), s * a
        if e_clim - e_perf <= 0:
            out.append(np.nan)
            continue
        if envelope:
            e_f = min(expense(p, o, a, t) for t in thr)
        else:
            e_f = expense(p, o, a)
        out.append((e_clim - e_f) / (e_clim - e_perf))
    return np.array(out)


def contingency(p, event, threshold: float) -> dict:
    """Hits, misses, false alarms, precision and recall for an alert rule."""
    act = np.asarray(p, dtype=float) > threshold
    o = np.asarray(event, dtype=bool)
    hits, fa, miss = int(np.sum(act & o)), int(np.sum(act & ~o)), int(np.sum(~act & o))
    return {"hits": hits, "false_alarms": fa, "misses": miss,
            "precision": hits / (hits + fa) if hits + fa else float("nan"),
            "recall": hits / (hits + miss) if hits + miss else float("nan")}


def alert_lead_times(p_by_week, truth_by_week, threshold: float, p_alert: float,
                     max_lead: int = 4) -> dict:
    """Lead time of the first alert before a season's first threshold crossing.

    p_by_week[t] = P(threshold crossed within the forecast window) issued at
    week t; truth_by_week[t] = observed value at week t. Event week E = first
    t with truth >= threshold. The first alert in [E - max_lead, E] gives
    lead = E - A (0 = alert in the crossing week). Alerts earlier than
    E - max_lead count as false alarms, not as long leads.
    """
    p = np.asarray(p_by_week, dtype=float)
    y = np.asarray(truth_by_week, dtype=float)
    crossed = np.where(y >= threshold)[0]
    if crossed.size == 0:
        early = int(np.sum(p >= p_alert))
        return {"event_week": None, "first_alert_week": None, "lead": None,
                "false_alarms_before": early}
    e = int(crossed[0])
    lo = max(e - max_lead, 0)
    window = np.where(p[lo:e + 1] >= p_alert)[0]
    first = int(lo + window[0]) if window.size else None
    early = int(np.sum(p[:lo] >= p_alert))
    return {"event_week": e, "first_alert_week": first,
            "lead": (e - first) if first is not None else None,
            "false_alarms_before": early}
