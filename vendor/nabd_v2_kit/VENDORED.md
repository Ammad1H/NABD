# Vendored: nabd_v2_kit (second-opinion kit)

Source: the user's Project docs `nabd_v2_kit/` (an independent agent's companion kit, 8 Nov 2026). Vendored as-is; treat it as third-party code and review it before relying on it. Contains method code and synthetic-data tests only, so it is NOT evidence of accuracy.

Copied by the coordinator: `nabd_kit/__init__, quantiles, scoring, phase, prereg, ledger`.
Each workstream fetches the remaining modules it needs, verbatim, with the Projects tool (`project_read nabd_v2_kit/<path>`):
- modelling: nabd_kit/{baselines,ensemble,recalibrate,gbm_global,decision,monitor,synth}.py, tests/*, examples/*, requirements.txt
- data-UAE: nabd_kit/calendar_features.py, templates/*, scripts/anchor.sh
- app: nabd_kit/card.py
Use it via `sys.path.insert(0, "vendor/nabd_v2_kit")`, then `import nabd_kit`.
