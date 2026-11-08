"""Coherent weekly card + consistency gate (BUILD-SPEC G14).

Every card shown in the app is built here and re-checked before it can render:

1. Direction facts come from the forecast distribution only (vendor kit `nabd_kit.card`):
   P(rise), P(fall), P(stable) at the level horizon, and a direction key.
2. The playbook band is selected from LEVEL (median at the level horizon) and TRAJECTORY
   (median at the furthest horizon vs the last observed value; playbook.validate.classify_trend).
3. `card_problems` re-derives everything and lists contradictions. The app refuses to render
   an action or the approval form for a card with any problem.

Observed change (last week vs the week before) is kept as a SEPARATE field and never drives
the band or the action.
"""
from __future__ import annotations

import datetime as dt
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "nabd_v2_kit"
for p in (ROOT, VENDOR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from nabd_kit import card as kitcard  # noqa: E402
from nabd_kit.quantiles import FLUSIGHT_LEVELS, exceedance_prob  # noqa: E402
from app.data_io import horizon_weeks  # noqa: E402
from playbook.validate import _trend_set, classify_trend, select_band  # noqa: E402

# Card parameters (fixed; documented on the About page).
BAND_REL = 0.10      # +/-10% relative change counts as "stable" (min 1 percentage point)
MIN_ABS = 1.0
P_LABEL = 0.6        # a direction label needs >= 60% probability, otherwise "uncertain"



@dataclass
class CardResult:
    target: str
    issue: dt.date
    last_value: float
    prev_value: float
    observed_key: str
    level_row: pd.Series
    level_horizon_wk: float
    path_medians: list
    trend: str
    trend_ratio: float
    band: dict | None
    kit: kitcard.Card
    high_threshold: float | None
    p_high: float | None
    problems: list = field(default_factory=list)

    @property
    def renderable(self) -> bool:
        return not self.problems and self.band is not None


def _qvec(row: pd.Series, levels=FLUSIGHT_LEVELS) -> np.ndarray:
    return np.array([float(row[round(float(q), 3)]) for q in levels])


def high_threshold(pb: dict, target: str, location: str) -> float | None:
    """Lower bound of the tier-3 band for this target (the playbook's 'high pressure' level)."""
    lows = [float(b["lower"]) for b in pb["bands"]
            if b["target"] == target and b["location"] == location and b["tier"] == 3]
    return min(lows) if lows else None


def band_consistency(band: dict | None, kit: kitcard.Card, path_medians, last_value: float,
                     p_high: float | None) -> list[str]:
    """Contradictions between the playbook band and the forecast facts."""
    problems = []
    if band is None:
        return ["no playbook band matches this forecast"]
    trends = _trend_set(band)
    furthest = float(path_medians[-1])
    if trends == {"rising"}:
        if kit.forecast_key == "likely_down":
            problems.append(f"band {band['id']} is for a rising trend but the forecast says likely_down")
        if furthest <= last_value:
            problems.append(f"band {band['id']} is for a rising trend but the furthest median "
                            f"({furthest:.1f}) is not above the last value ({last_value:.1f})")
    if trends == {"falling"}:
        if kit.forecast_key == "likely_up":
            problems.append(f"band {band['id']} is for a falling trend but the forecast says likely_up")
        if furthest >= last_value:
            problems.append(f"band {band['id']} is for a falling trend but the furthest median "
                            f"({furthest:.1f}) is not below the last value ({last_value:.1f})")
    if band["tier"] == 3 and p_high is not None and p_high < 0.3:
        problems.append(f"tier-3 surge band {band['id']} but P(above high threshold) = {p_high:.0%} < 30%")
    return problems


def card_problems(res: CardResult, q_level: np.ndarray) -> list[str]:
    """Re-derive the card from the forecast and list every contradiction (empty = OK)."""
    probs = kitcard.check_card(res.kit, q_level, FLUSIGHT_LEVELS, band=BAND_REL, min_abs=MIN_ABS,
                               p_label=P_LABEL)
    probs += band_consistency(res.band, res.kit, res.path_medians, res.last_value, res.p_high)
    return probs


def build_card(pb: dict, target: str, location: str, fc: pd.DataFrame, observed: pd.Series,
               issue: dt.date) -> CardResult:
    """fc: quantile frame for ONE target (columns target_end_date, q, value).
    observed: observed values for this target, ordered by week (last = latest published)."""
    obs = observed.dropna()
    last, prev = float(obs.iloc[-1]), float(obs.iloc[-2])
    wide = fc.pivot_table(index="target_end_date", columns="q", values="value").sort_index()
    wide.columns = [round(float(c), 3) for c in wide.columns]
    wide = wide.reset_index()
    wide["h_wk"] = [horizon_weeks(d, issue) for d in wide.target_end_date]
    future = wide[wide.h_wk > 0]
    level_row = (future if not future.empty else wide).iloc[0]
    path = future if not future.empty else wide
    path_medians = path[0.5].tolist()
    trend, ratio = classify_trend(path_medians, last, pb)
    band = select_band(pb, target, location, float(level_row[0.5]), trend)
    q_level = _qvec(level_row)
    kit = kitcard.make_card(prev, last, q_level, FLUSIGHT_LEVELS, horizon=1, band=BAND_REL,
                            min_abs=MIN_ABS, p_label=P_LABEL)
    thr = high_threshold(pb, target, location)
    p_high = float(exceedance_prob(q_level.reshape(1, -1), FLUSIGHT_LEVELS, thr)[0]) if thr is not None else None
    res = CardResult(target=target, issue=issue, last_value=last, prev_value=prev, observed_key=kit.observed_key,
                     level_row=level_row, level_horizon_wk=float(level_row.h_wk), path_medians=path_medians,
                     trend=trend, trend_ratio=ratio, band=band, kit=kit, high_threshold=thr, p_high=p_high)
    res.problems = card_problems(res, q_level)
    return res


# Plain-language strings for card keys (EN/AR).
OBS_TXT = {"up": {"en": "rose", "ar": "ارتفعت"}, "down": {"en": "fell", "ar": "انخفضت"},
           "flat": {"en": "held steady", "ar": "استقرت"}}
FC_TXT = {"likely_up": {"en": "likely to rise", "ar": "يُرجَّح أن ترتفع"},
          "likely_down": {"en": "likely to fall", "ar": "يُرجَّح أن تنخفض"},
          "likely_stable": {"en": "likely to stay near this level", "ar": "يُرجَّح أن تبقى قرب هذا المستوى"},
          "uncertain": {"en": "uncertain in direction", "ar": "غير مؤكدة الاتجاه"}}
TREND_TXT = {"rising": {"en": "rising", "ar": "صاعد"}, "plateau": {"en": "plateau", "ar": "مستقر"},
             "falling": {"en": "falling", "ar": "هابط"}}


def card_sentence(res: CardResult, lang: str) -> str:
    k = res.kit
    if lang == "ar":
        return (f"آخر أسبوع منشور: {OBS_TXT[k.observed_key]['ar']} ({res.prev_value:.1f}% ← {res.last_value:.1f}%). "
                f"التوقع عند +{res.level_horizon_wk:g} أسبوع: {FC_TXT[k.forecast_key]['ar']} "
                f"(ارتفاع {k.p_up:.0%}، انخفاض {k.p_down:.0%}). مسار التوقع: {TREND_TXT[res.trend]['ar']}.")
    return (f"Last published week {OBS_TXT[k.observed_key]['en']} ({res.prev_value:.1f}% → {res.last_value:.1f}%). "
            f"Forecast at +{res.level_horizon_wk:g} wk: {FC_TXT[k.forecast_key]['en']} "
            f"(rise {k.p_up:.0%}, fall {k.p_down:.0%}). Forecast path: {TREND_TXT[res.trend]['en']}.")
