"""WIS correctness (BUILD-SPEC G6)."""
import numpy as np

from eval.wis import QUANTILES, coverage, wis_interval, wis_pinball


def test_pinball_equals_interval_form():
    rng = np.random.default_rng(0)
    q = np.sort(rng.gamma(2.0, 50.0, size=(500, 23)), axis=1)
    y = rng.gamma(2.0, 50.0, size=500)
    assert np.allclose(wis_pinball(q, y), wis_interval(q, y))


def test_hand_computed_three_quantile_example():
    # Q = {0.25, 0.5, 0.75}: K=1 interval (alpha=0.5) + median.
    taus = np.array([0.25, 0.5, 0.75])
    q = np.array([[8.0, 10.0, 12.0]])
    # y = 15: |y-m| = 5; IS_0.5 = (12-8) + (2/0.5)*(15-12) = 4 + 12 = 16
    # WIS = (0.5*5 + 0.25*16) / 1.5 = (2.5 + 4) / 1.5 = 4.3333...
    assert np.isclose(wis_interval(q, np.array([15.0]), taus)[0], 6.5 / 1.5)
    assert np.isclose(wis_pinball(q, np.array([15.0]), taus)[0], 6.5 / 1.5)


def test_point_mass_reduces_to_absolute_error():
    q = np.full((1, 23), 100.0)
    # all quantiles equal: WIS = (2/23) * sum_tau |tau - 1{y<q}| * |q-y| = |y-q| * (2/23) * sum_tau tau (y>q)
    y = np.array([130.0])
    expected = 2.0 / 23 * np.sum(QUANTILES) * 30.0
    assert np.isclose(wis_pinball(q, y)[0], expected)


def test_coverage_indices():
    q = np.tile(np.arange(23, dtype=float), (1, 1))
    assert coverage(q, np.array([11.0]), 0.5)[0] == 1.0      # median inside 50% interval
    assert coverage(q, np.array([30.0]), 0.95)[0] == 0.0
