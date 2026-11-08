"""NABD member 3: Chronos-2 (amazon/chronos-2) wrapper (PROTOCOL §8).

Runs when the `chronos-forecasting` package and the model weights are available (e.g. on a laptop
or Colab). In environments where they are not (the cloud build sandbox blocks Hugging Face), it
returns None and the run records the member as NOT RUN HERE. It never fabricates output.

Usage on a machine with access:
    pip install "chronos-forecasting>=2.0" torch
    NABD_CHRONOS=1 python -m eval.run_all --cached --with-chronos
"""
from __future__ import annotations

import os

import numpy as np

from .data import QUANTILES

STATUS = "NOT RUN HERE"
_pipeline = None


def available() -> bool:
    global _pipeline, STATUS
    if os.environ.get("NABD_CHRONOS") != "1":
        STATUS = "NOT RUN HERE (NABD_CHRONOS!=1)"
        return False
    try:
        from chronos import BaseChronosPipeline  # type: ignore
        _pipeline = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cpu")
        STATUS = "RUN"
        return True
    except Exception as e:  # noqa: BLE001
        STATUS = f"NOT RUN HERE ({type(e).__name__}: {str(e)[:80]})"
        return False


def chronos_quantiles(Y: np.ndarray, steps: int = 4) -> np.ndarray | None:
    """Y: (L, T) counts up to t0. Returns (L, steps, 23) quantiles, or None if unavailable."""
    if _pipeline is None:
        return None
    import torch  # type: ignore
    ctx = torch.tensor(np.log1p(Y), dtype=torch.float32)
    q, _ = _pipeline.predict_quantiles(ctx, prediction_length=steps, quantile_levels=QUANTILES.tolist())
    q = np.expm1(np.asarray(q)).clip(min=0)            # (L, steps, 23)
    return np.maximum.accumulate(q, axis=2)
