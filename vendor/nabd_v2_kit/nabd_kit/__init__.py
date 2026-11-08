"""nabd_kit: drop-in v2 utilities for NABD.

Scoring cross-checks, phase-aware recalibration, online calibration, small
ensembles, a global gradient-boosted quantile model, decision/value analysis,
card consistency checks, a calibration guardrail, a forecast ledger with
outside-timestamp support, and pre-registration locks.

This package contains method code only. It holds no evidence about NABD's
real-world accuracy: the synthetic data in `synth` exists to test that the
code does what it says, never to support a performance claim.
"""

__version__ = "0.1.0"
