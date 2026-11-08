"""G11: the v1 explanation is exact, and the live explanation matches the hashed R1 ledger forecast."""
from pathlib import Path

import numpy as np
import pandas as pd

from adapters import flunet
from uae.explain_v1 import explain_v1
from uae.models import NabdUAE, QUANTILES, SERIES, expit, prepare

ROOT = Path(__file__).resolve().parents[1]


def _model(key):
    s = flunet.sentinel_series(flunet.load("cached"))
    d = prepare(s, key)
    seasons = sorted(d.season.dropna().unique().astype(int))
    train = seasons[:-2]
    i = int(d[d.season == seasons[-2]].dropna(subset=["y"]).index[10])
    return NabdUAE(d, train), i


def test_v1_contributions_sum_to_median_logit():
    for key in SERIES:
        m, i = _model(key)
        pq = m.predict(i)
        ex = explain_v1(m, i)
        mid = QUANTILES.index(0.5)
        n = 0
        for h, e in ex.items():
            if e is None or pq[h] is None:
                continue
            assert np.isclose(e.contribution.sum(), pq[h][mid], atol=1e-9)
            n += 1
        assert n > 0


def test_live_v1_explanation_matches_hashed_R1_median():
    led = ROOT / "ledger" / "2026-11-08T1212Z_NABD-UAE-v1.csv"
    f = pd.read_csv(led)
    for slug, target in [("flu_pos_pct_sentinel", "wk flu pos pct sentinel"),
                         ("rsv_pos_pct_sentinel", "wk rsv pos pct sentinel")]:
        ex = pd.read_csv(ROOT / "results" / "uae" / "explain" / f"2026-11-08_{slug}.csv")
        assert set(ex.model) == {"NABD-UAE-v1"}
        for te, g in ex.groupby("target_end_date"):
            med_ex = 100 * expit(g.contribution.sum())
            r = f[(f.target == target) & (f.target_end_date == te) & np.isclose(f.output_type_id, 0.5)]
            assert len(r) == 1
            # ledger values are rounded to 4 dp
            assert abs(med_ex - r.value.iloc[0]) < 1e-3, (te, med_ex, r.value.iloc[0])


def test_challenger_explanations_kept_separate():
    d = ROOT / "results" / "uae" / "explain" / "challenger_v2"
    files = list(d.glob("2026-11-08_*.csv"))
    assert files
    for p in files:
        assert "NABD-UAE-v1" not in set(pd.read_csv(p).get("model", pd.Series(dtype=str)))


def test_weekly_is_idempotent_on_cached_data():
    from ledger.weekly import run
    before = sorted(p.name for p in (ROOT / "ledger").glob("*.csv"))
    a = run("cached")
    b = run("cached")
    after = sorted(p.name for p in (ROOT / "ledger").glob("*.csv"))
    assert a["issued"] is None and b["issued"] is None
    assert before == after
