# POST HOC: UAE v1 vs last year's pattern (seasonal analog), forward-in-time

Declared before computing in docs/DEVIATIONS.md U6. **Exploratory, not confirmatory**: per-fold means were already visible in results/uae/v2/tables/forward_wis_by_season.csv. Relative WIS < 1 means v1 had less error.

| Series | Pooled v1/analog | 95% CI (date cluster) | 95% CI (moving block L=4) | cells |
|---|---|---|---|---|
| flu | 0.824 | 0.726–0.955 | 0.664–1.133 | 470 |
| rsv | 0.855 | 0.773–0.946 | 0.719–1.026 | 564 |

**By training history** (training seasons available to the forward-in-time fit):

| Series | 1 training season | ≥2 training seasons |
|---|---|---|
| flu | 2.562 (2.069–3.259) | 0.607 (0.551–0.677) |
| rsv | 1.387 (1.262–1.561) | 0.675 (0.615–0.739) |

**Per fold:**

| Series | Test season | Training seasons | v1 WIS | analog WIS | ratio | v1 better |
|---|---|---|---|---|---|---|
| flu | 2023 | 1 | 4.746 | 1.852 | 2.562 | no |
| flu | 2024 | 2 | 2.544 | 4.504 | 0.565 | yes |
| flu | 2025 | 3 | 1.938 | 2.884 | 0.672 | yes |
| rsv | 2023 | 1 | 2.502 | 1.804 | 1.387 | no |
| rsv | 2024 | 2 | 1.315 | 1.475 | 0.892 | yes |
| rsv | 2025 | 3 | 2.296 | 3.873 | 0.593 | yes |

v1 beat the analog in 4/6 folds.
Caution: pooling over cells weights seasons by their number of scored cells. The unweighted average of the per-season mean WIS is flu v1 3.08 vs analog 3.08; rsv v1 2.04 vs analog 2.38. The moving-block CIs above include 1.
Reading (post hoc): with one training season the UAE model has almost no history to learn a seasonal shape; the Gulf test countries had flu history from 2015. This is an explanation, not a tested hypothesis.
