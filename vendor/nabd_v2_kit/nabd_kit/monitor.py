"""Calibration guardrail with an automatic fallback.

Each week, feed the forecasts whose truth just arrived (and the reference
forecasts for the same targets). Over the last `window` weeks the monitor
checks interval coverage against binomial tolerance and relative WIS against
the reference. States:
  ok        - within tolerance
  watch     - coverage outside tolerance: show a notice, keep the model
  fallback  - relative WIS above the pre-set limit: serve the reference
              forecast as the headline, show a banner, write an audit entry
Pre-register window, tolerances and limit. The tolerance ignores
autocorrelation between locations and horizons, so treat "watch" as a prompt to
look, not as a test result.
"""
from __future__ import annotations

from collections import deque

import numpy as np

from .scoring import interval_hit, wis


class CalibrationMonitor:
    def __init__(self, levels, window: int = 8, coverages=(0.5, 0.9), tol_z: float = 2.0,
                 fallback_rel_wis: float = 1.25, min_points: int = 20):
        self.levels = np.asarray(levels, dtype=float)
        self.window, self.coverages, self.tol_z = int(window), tuple(coverages), float(tol_z)
        self.fallback_rel_wis, self.min_points = float(fallback_rel_wis), int(min_points)
        self.weeks: deque = deque(maxlen=self.window)

    def add_week(self, week, q, y, q_ref=None) -> None:
        q = np.atleast_2d(np.asarray(q, dtype=float))
        y = np.atleast_1d(np.asarray(y, dtype=float))
        rec = {"week": week, "wis": wis(q, y, self.levels),
               "hits": {c: interval_hit(q, y, self.levels, c) for c in self.coverages}}
        if q_ref is not None:
            rec["wis_ref"] = wis(np.atleast_2d(q_ref), y, self.levels)
        self.weeks.append(rec)

    def status(self) -> dict:
        if not self.weeks:
            return {"state": "ok", "reasons": ["no data yet"], "n": 0}
        n = int(sum(len(r["wis"]) for r in self.weeks))
        reasons, state = [], "ok"
        cov = {}
        for c in self.coverages:
            hits = np.concatenate([r["hits"][c] for r in self.weeks])
            obs = float(hits.mean())
            se = np.sqrt(c * (1 - c) / max(n, 1))
            cov[c] = obs
            if n >= self.min_points and abs(obs - c) > self.tol_z * se:
                state = "watch"
                reasons.append(f"{c:.0%} interval covered {obs:.0%} over {n} forecasts")
        rel = None
        if all("wis_ref" in r for r in self.weeks):
            num = float(sum(r["wis"].sum() for r in self.weeks))
            den = float(sum(r["wis_ref"].sum() for r in self.weeks))
            rel = num / den if den > 0 else None
            if rel is not None and n >= self.min_points and rel > self.fallback_rel_wis:
                state = "fallback"
                reasons.append(f"relative WIS {rel:.2f} over the last {len(self.weeks)} weeks "
                               f"exceeds the pre-set limit {self.fallback_rel_wis:.2f}")
        return {"state": state, "reasons": reasons or ["within tolerance"], "n": n,
                "coverage": cov, "rel_wis": rel, "weeks": [r["week"] for r in self.weeks]}
