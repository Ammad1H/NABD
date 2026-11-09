"""Coherent weekly card + consistency gate (BUILD-SPEC G14).

Every card shown in the app is built here and re-checked before it can render:

1. Direction facts come from the forecast distribution only (vendor kit `nabd_kit.card`):
   P(rise), P(fall), P(stable) at the level horizon, and a direction key.
2. The playbook band is selected from the EFFECTIVE LEVEL (the highest tier threshold whose
   exceedance probability reaches p_act = 30% at any future target week, from the issued quantiles via
   the vendor kit `quantiles.exceedance_prob`) and TRAJECTORY (median at the furthest horizon vs the last
   observed value; playbook.validate.classify_trend). Playbook v0.3, BUILD-SPEC v1.5 R3-1.
3. `card_problems` re-derives everything and lists contradictions. The app refuses to render
   an action or the approval form for a card with any problem.

Observed change (last week vs the week before) and the observed as-of trend (kit
`phase.asof_log_slope` over the last 3 published weeks) are SEPARATE context fields and never drive
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
from nabd_kit.phase import asof_log_slope, classify  # noqa: E402
from nabd_kit.quantiles import FLUSIGHT_LEVELS, exceedance_prob  # noqa: E402
from app.data_io import horizon_weeks  # noqa: E402
from playbook.validate import (_trend_set, classify_trend, effective_level, p_act,  # noqa: E402
                               select_band, tier_thresholds)

# Card parameters (fixed; documented on the About page).
BAND_REL = 0.10      # +/-10% relative change counts as "stable" (min 1 percentage point)
MIN_ABS = 1.0
P_LABEL = 0.6        # a direction label needs >= 60% probability, otherwise "uncertain"
OBS_WINDOW, OBS_OFFSET, OBS_BAND = 3, 1.0, 0.1   # observed as-of trend (context only)



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
    exceed: pd.DataFrame | None = None        # rows: future horizons; columns: thresholds; P(Y > T)
    max_p: dict = field(default_factory=dict)  # threshold -> max over future horizons
    level: float = 0.0                         # effective level (threshold) used to pick the band
    p_act: float = 0.30
    observed_trend: str = "unknown"
    observed_slope: float = float("nan")
    exceed_dates: list = field(default_factory=list)   # target_end_date per row of `exceed`
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
                     p_high: float | None, max_p: dict | None = None, p_threshold: float = 0.30) -> list[str]:
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
    if band["tier"] == 3 and p_high is not None and p_high < p_threshold:
        problems.append(f"tier-3 surge band {band['id']} but P(above high threshold) = {p_high:.0%} "
                        f"< {p_threshold:.0%}")
    if max_p:
        lower = float(band["lower"])
        if lower > 0 and lower in max_p and max_p[lower] < p_threshold:
            problems.append(f"band {band['id']} starts at {lower:g}% but the chance of exceeding it is only "
                            f"{max_p[lower]:.0%} (< {p_threshold:.0%})")
        missed = [T for T, p in max_p.items() if p >= p_threshold and T > lower]
        if missed:
            problems.append(f"band {band['id']} under-calls: P(> {max(missed):g}%) = {max_p[max(missed)]:.0%} "
                            f">= {p_threshold:.0%} but the band starts at {lower:g}%")
    return problems


def card_problems(res: CardResult, q_level: np.ndarray) -> list[str]:
    """Re-derive the card from the forecast and list every contradiction (empty = OK)."""
    probs = kitcard.check_card(res.kit, q_level, FLUSIGHT_LEVELS, band=BAND_REL, min_abs=MIN_ABS,
                               p_label=P_LABEL)
    probs += band_consistency(res.band, res.kit, res.path_medians, res.last_value, res.p_high,
                              res.max_p, res.p_act)
    return probs


def exceedance_table(path: pd.DataFrame, thresholds: list[float]) -> pd.DataFrame:
    """P(Y > T) for every future horizon (rows, indexed by h_wk) and threshold (columns)."""
    out = {}
    for T in thresholds:
        q = np.vstack([_qvec(r) for _, r in path.iterrows()])
        out[T] = exceedance_prob(q, FLUSIGHT_LEVELS, T)
    return pd.DataFrame(out, index=path.h_wk.to_numpy())


def observed_trend(obs: pd.Series) -> tuple[str, float]:
    s = asof_log_slope(obs.to_numpy(float), window=OBS_WINDOW, offset=OBS_OFFSET)
    slope = float(s[-1]) if len(s) else float("nan")
    return str(classify(np.array([slope]), band=OBS_BAND)[0]), slope


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
    pa = p_act(pb)
    thresholds = tier_thresholds(pb, target, location)
    exceed = exceedance_table(path, thresholds) if thresholds else None
    max_p = {float(T): float(exceed[T].max()) for T in thresholds} if exceed is not None else {}
    level = effective_level(max_p, pa)
    band = select_band(pb, target, location, level, trend)
    q_level = _qvec(level_row)
    kit = kitcard.make_card(prev, last, q_level, FLUSIGHT_LEVELS, horizon=1, band=BAND_REL,
                            min_abs=MIN_ABS, p_label=P_LABEL)
    thr = high_threshold(pb, target, location)
    p_high = max_p.get(thr) if thr is not None else None
    o_trend, o_slope = observed_trend(obs)
    res = CardResult(target=target, issue=issue, last_value=last, prev_value=prev, observed_key=kit.observed_key,
                     level_row=level_row, level_horizon_wk=float(level_row.h_wk), path_medians=path_medians,
                     trend=trend, trend_ratio=ratio, band=band, kit=kit, high_threshold=thr, p_high=p_high,
                     exceed=exceed, max_p=max_p, level=level, p_act=pa, observed_trend=o_trend,
                     observed_slope=o_slope, exceed_dates=list(path.target_end_date))
    res.problems = card_problems(res, q_level)
    return res


def fmt_p(p: float) -> str:
    """Exceedance probabilities at the clip of the forecast are never shown as exact numbers."""
    if p is None or not np.isfinite(p):
        return "n/a"
    if p <= 0.01 + 1e-9:
        return "<1%"
    if p >= 0.99 - 1e-9:
        return ">99%"
    return f"{p:.0%}"


# Plain-language strings for card keys (EN/AR).
OBS_TXT = {"up": {"en": "rose", "ar": "ارتفعت"}, "down": {"en": "fell", "ar": "انخفضت"},
           "flat": {"en": "held steady", "ar": "استقرت"}}
FC_TXT = {"likely_up": {"en": "likely to rise", "ar": "يُرجَّح أن ترتفع"},
          "likely_down": {"en": "likely to fall", "ar": "يُرجَّح أن تنخفض"},
          "likely_stable": {"en": "likely to stay near this level", "ar": "يُرجَّح أن تبقى قرب هذا المستوى"},
          "uncertain": {"en": "uncertain in direction", "ar": "غير مؤكدة الاتجاه"}}
TREND_TXT = {"rising": {"en": "rising", "ar": "صاعد"}, "plateau": {"en": "plateau", "ar": "مستقر"},
             "falling": {"en": "falling", "ar": "هابط"}, "flat": {"en": "flat", "ar": "ثابت"},
             "unknown": {"en": "unknown", "ar": "غير معروف"}}


def card_sentence(res: CardResult, lang: str, hlabel: str | None = None) -> str:
    """One plain sentence. `hlabel` is the display label of the level horizon (ledger round's own label when live)."""
    k = res.kit
    h = hlabel or f"+{res.level_horizon_wk:g} wk"
    if lang == "ar":
        h_ar = h.replace("nowcast", "التقدير الآني").replace(" wk", " أسبوع")
        return (f"آخر أسبوع منشور: {OBS_TXT[k.observed_key]['ar']} ({res.prev_value:.1f}% ← {res.last_value:.1f}%). "
                f"التوقع عند {h_ar}: {FC_TXT[k.forecast_key]['ar']} "
                f"(ارتفاع {k.p_up:.0%}، انخفاض {k.p_down:.0%}). مسار التوقع: {TREND_TXT[res.trend]['ar']}.")
    return (f"Last published week {OBS_TXT[k.observed_key]['en']} ({res.prev_value:.1f}% → {res.last_value:.1f}%). "
            f"Forecast at {h}: {FC_TXT[k.forecast_key]['en']} "
            f"(rise {k.p_up:.0%}, fall {k.p_down:.0%}). Forecast path: {TREND_TXT[res.trend]['en']}.")


def band_label(band: dict | None, lang: str) -> str:
    """Plain-language band name (playbook v0.4 `label`); never the internal id."""
    if not band:
        return ""
    lab = band.get("label") or {}
    return str(lab.get(lang) or lab.get("en") or "")
