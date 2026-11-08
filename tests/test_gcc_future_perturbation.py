"""Future-perturbation leak test for the GCC scorer's model path (audit R3 #16).

Ported from the R3 auditor's adversarial script. Runs on the committed UAE FluNet file (relabelled as a
pseudo-country) so CI does not depend on GCC data. For random forecast origins i, every value after i
is scrambled; forecasts made at i by v1, v2, persistence and the analog must not change.
A positive control (perturbing data AT the origin) must change the v1 forecast, proving the test can fail.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))

from uae import gcc  # noqa: E402
from uae.models import H, Analog, NabdUAE, Persistence  # noqa: E402
from uae.models_v2 import NabdUAEv2  # noqa: E402

COLS = ["y", "z", "pos", "logspec", "specimens", "ns_pos", "ns_spec"]


def _series():
    raw = pd.read_csv(ROOT / "data" / "raw" / "flunet_are.csv")
    raw.insert(0, "COUNTRY_CODE", "ARE")
    d = gcc.tidy(raw)
    s = gcc.weekly_series(d, "ARE", "SENTINEL")
    ns = gcc.weekly_series(d, "ARE", "NONSENTINEL")
    return s, ns


def _same(a, b):
    for h in H:
        if (a[h] is None) != (b[h] is None):
            return False
        if a[h] is not None and not np.allclose(a[h], b[h]):
            return False
    return True


def _cases(x, train_seasons, S, rng, k=4):
    idx = [i for i in x.index[x.season == S]
           if i + 4 < len(x) and x.season.iloc[i + 4] == S and not np.isnan(x.y.iloc[i])]
    if not idx:
        return []
    return list(rng.choice(idx, size=min(k, len(idx)), replace=False))


@pytest.mark.parametrize("key", list(gcc.SER))
def test_future_values_do_not_change_forecasts(key):
    s, ns = _series()
    x = gcc.prep(s, key, ns)
    rng = np.random.default_rng(1)
    seasons = sorted(set(x.season.dropna().astype(int)))
    n = changed = 0
    for S in seasons[2:]:
        train = [k for k in seasons if k < S and k != 2020]
        if len(train) < 2:
            continue
        for i in _cases(x, train, S, rng):
            xp = x.copy()
            fut = xp.index > i
            for col in [c for c in COLS if c in xp.columns]:
                xp.loc[fut, col] = xp.loc[fut, col] * rng.uniform(0.2, 3, fut.sum()) + rng.normal(0, 2, fut.sum())
            for M in [NabdUAE, Persistence, Analog, lambda a, b: NabdUAEv2(a, b, name="v2")]:
                n += 1
                if not _same(M(x, train).predict(i), M(xp, train).predict(i)):
                    changed += 1
    assert n > 0, "no perturbation cases were generated"
    assert changed == 0, f"{changed}/{n} forecasts changed when only future data were perturbed"


def test_positive_control_detects_present_perturbation():
    s, ns = _series()
    x = gcc.prep(s, "flu", ns)
    seasons = sorted(set(x.season.dropna().astype(int)))
    S = seasons[-1]
    train = [k for k in seasons if k < S and k != 2020]
    rng = np.random.default_rng(2)
    i = _cases(x, train, S, rng, k=1)[0]
    xp = x.copy()
    for col in [c for c in ["y", "z", "pos"] if c in xp.columns]:
        xp.loc[i, col] = xp.loc[i, col] * 3 + 5
    assert not _same(NabdUAE(x, train).predict(i), NabdUAE(xp, train).predict(i)), \
        "positive control failed: perturbing the origin week should change the forecast"
