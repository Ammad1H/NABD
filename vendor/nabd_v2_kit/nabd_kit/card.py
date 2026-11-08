"""Weekly decision card that cannot contradict its own forecast.

The RSV card bug ("RSV rising, prepare surge roster" while the forecast falls)
comes from mixing last week's OBSERVED change with the FORECAST direction. Here
they are separate fields, every label and action is derived from the forecast
distribution, and `check_card` re-derives them to catch any contradiction,
including in text written by hand or by an LLM from these facts.

Labels are keys (e.g. "likely_down"), not prose: the app maps keys to its own
English and Arabic strings.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .quantiles import cdf_at, check_levels, exceedance_prob


@dataclass
class Card:
    horizon: int
    last_value: float
    prev_value: float
    observed_key: str          # "up" | "down" | "flat"
    forecast_key: str          # "likely_up" | "likely_down" | "likely_stable" | "uncertain"
    p_up: float
    p_down: float
    p_stable: float
    median: float
    p_exceed: float | None     # P(value > capacity threshold) at this horizon
    action_key: str            # "prepare_surge" | "watch_closely" | "review_stand_down" | "routine"
    text_en: str

    def as_dict(self) -> dict:
        return asdict(self)


def _bands(last: float, band: float, min_abs: float):
    delta = max(band * last, min_abs)
    return last + delta, max(last - delta, 0.0)


def derive(q_h, levels, last: float, band: float = 0.1, min_abs: float = 1.0,
           p_label: float = 0.6, capacity: float | None = None, p_act: float = 0.3) -> dict:
    """Forecast facts for one horizon: direction probabilities, label, action."""
    lv = check_levels(levels)
    q = np.asarray(q_h, dtype=float).reshape(1, -1)
    up_thr, down_thr = _bands(last, band, min_abs)
    p_up = float(exceedance_prob(q, lv, up_thr)[0])
    p_down = float(cdf_at(q, lv, down_thr)[0]) if down_thr > 0 else 0.0
    p_stable = max(0.0, 1.0 - p_up - p_down)
    if p_up >= p_label:
        key = "likely_up"
    elif p_down >= p_label:
        key = "likely_down"
    elif p_stable >= p_label:
        key = "likely_stable"
    else:
        key = "uncertain"
    p_exc = float(exceedance_prob(q, lv, capacity)[0]) if capacity is not None else None
    if p_exc is not None and p_exc >= p_act:
        action = "prepare_surge"
    elif key == "likely_up":
        action = "watch_closely"
    elif key == "likely_down":
        action = "review_stand_down"
    else:
        action = "routine"
    return {"p_up": p_up, "p_down": p_down, "p_stable": p_stable, "forecast_key": key,
            "median": float(np.sort(q[0])[lv.size // 2]), "p_exceed": p_exc, "action_key": action}


OBS_EN = {"up": "rose", "down": "fell", "flat": "held steady"}
FC_EN = {"likely_up": "likely to rise", "likely_down": "likely to fall",
         "likely_stable": "likely to stay near this level", "uncertain": "uncertain in direction"}
ACT_EN = {"prepare_surge": "Prepare the surge roster: the chance of exceeding capacity is {p:.0%}.",
          "watch_closely": "Watch closely and check surge readiness.",
          "review_stand_down": "Review whether extra capacity can be stood down.",
          "routine": "No change to routine staffing."}


def make_card(prev_value: float, last_value: float, q_h, levels, horizon: int,
              band: float = 0.1, min_abs: float = 1.0, p_label: float = 0.6,
              capacity: float | None = None, p_act: float = 0.3) -> Card:
    obs_rel = (last_value - prev_value) / max(prev_value, min_abs)
    observed = "up" if obs_rel > band else "down" if obs_rel < -band else "flat"
    f = derive(q_h, levels, last_value, band, min_abs, p_label, capacity, p_act)
    p_exc = f["p_exceed"]
    text = (f"Observed last week: {OBS_EN[observed]} ({prev_value:,.0f} to {last_value:,.0f}). "
            f"Forecast for {horizon} week(s) ahead: {FC_EN[f['forecast_key']]} "
            f"(rise {f['p_up']:.0%}, fall {f['p_down']:.0%}). "
            + ACT_EN[f["action_key"]].format(p=p_exc if p_exc is not None else 0.0))
    return Card(horizon, float(last_value), float(prev_value), observed, f["forecast_key"],
                f["p_up"], f["p_down"], f["p_stable"], f["median"], p_exc, f["action_key"], text)


def check_card(card: Card, q_h, levels, band: float = 0.1, min_abs: float = 1.0,
               p_label: float = 0.6, capacity: float | None = None, p_act: float = 0.3) -> list[str]:
    """Re-derive the card from the forecast; return a list of contradictions (empty = OK)."""
    f = derive(q_h, levels, card.last_value, band, min_abs, p_label, capacity, p_act)
    problems = []
    if card.forecast_key != f["forecast_key"]:
        problems.append(f"forecast_key {card.forecast_key!r} but forecast says {f['forecast_key']!r}")
    if card.action_key != f["action_key"]:
        problems.append(f"action_key {card.action_key!r} but forecast implies {f['action_key']!r}")
    if card.action_key == "prepare_surge" and (f["p_exceed"] is None or f["p_exceed"] < p_act):
        problems.append("surge action without exceedance risk above the pre-set level")
    if card.forecast_key == "likely_up" and f["median"] <= card.last_value:
        problems.append("labelled rising but the forecast median is not above the last value")
    if card.forecast_key == "likely_down" and f["median"] >= card.last_value:
        problems.append("labelled falling but the forecast median is not below the last value")
    return problems
