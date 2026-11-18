# GCC test: robustness checks (committed reproduction of the R3 review's scratch reruns)

_Recomputed from `results/gcc/tables/scores_long.csv` by `eval/gcc_robustness.py`. No refit. These are sensitivity checks on a locked result, not new endpoints._

**Influenza** (frozen v1 method vs last week carried forward): pooled 0.914.
- Leave one country out: 0.904–0.929 (without OMN 0.904, without QAT 0.907, without SAU 0.929).
- Two-stage bootstrap (countries, then seasons; B = 2000, seed 0): 95% CI 0.842–0.984.
- By horizon: -1: 0.999, 0: 0.958, 1: 0.898, 2: 0.855.

**RSV** (secondary): pooled 0.798; two-stage bootstrap 95% CI 0.711–1.088; leave one country out without OMN 0.800, without QAT 0.862, without SAU 0.759.

With three countries, a country-level bootstrap is coarse; read the intervals as a stress test.
