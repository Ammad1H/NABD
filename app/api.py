"""NABD forecast API. Run:  uvicorn app.api:app --port 8000   (OpenAPI docs at /docs)"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from app import data_io  # noqa: E402

app = FastAPI(title="NABD forecast API", version="0.1.0",
              description="Calibrated RSV and influenza positivity forecasts for the UAE (WHO FluNet sentinel). "
                          "Aggregate data only. `demo=true` means placeholder data, not NABD model output.")


class QuantileValue(BaseModel):
    quantile: float = Field(ge=0, le=1)
    value: float


class HorizonForecast(BaseModel):
    target_end_date: str
    horizon: int
    horizon_label: str = Field(description="Relative to issue date: 'nowcast' or '+X wk'")
    quantiles: list[QuantileValue]
    median: float


class ForecastResponse(BaseModel):
    location: str
    target: str
    unit: Literal["percent"] = "percent"
    model: str
    reference_date: str
    demo: bool
    data_last_week: str
    data_lag_days: int
    forecasts: list[HorizonForecast]


class Health(BaseModel):
    status: Literal["ok"]
    observed_last_week: str
    forecast_source: Literal["results", "demo"]


@app.get("/health", response_model=Health)
def health() -> Health:
    obs = data_io.load_uae_observed()
    _, _, _, demo = data_io.load_uae_forecasts(obs)
    return Health(status="ok", observed_last_week=data_io.freshness(obs)["last_week"],
                  forecast_source="demo" if demo else "results")


@app.get("/forecast", response_model=ForecastResponse)
def forecast(location: str = Query("ARE", description="Only ARE is served"),
             target: str = Query(data_io.UAE_TARGETS["rsv"], description="; ".join(data_io.UAE_TARGETS.values())),
             model: Literal["primary", "persistence"] = "primary") -> ForecastResponse:
    if location != "ARE":
        raise HTTPException(404, "only location=ARE is served")
    if target not in data_io.UAE_TARGETS.values():
        raise HTTPException(422, f"target must be one of {list(data_io.UAE_TARGETS.values())}")
    obs = data_io.load_uae_observed()
    prim, pers, meta, demo = data_io.load_uae_forecasts(obs)
    df = prim if model == "primary" else pers
    df = df[df.target == target]
    if df.empty:
        raise HTTPException(404, "no forecast for that target")
    import datetime as dt
    issue = dt.date.fromisoformat(str(meta["reference_date"]))
    out = []
    for ted, g in df.sort_values("q").groupby("target_end_date"):
        qs = [QuantileValue(quantile=float(q), value=float(v)) for q, v in zip(g.q, g.value)]
        med = float(g.loc[(g.q - 0.5).abs().idxmin(), "value"])
        out.append(HorizonForecast(target_end_date=str(ted), horizon=int(g.horizon.iloc[0]),
                                   horizon_label=data_io.horizon_label(ted, issue), quantiles=qs, median=med))
    fr = data_io.freshness(obs)
    name = meta.get("model", "unknown") if model == "primary" else str(df.model.iloc[0])
    return ForecastResponse(location=location, target=target, model=name, reference_date=issue.isoformat(),
                            demo=demo, data_last_week=fr["last_week"], data_lag_days=fr["lag_days"], forecasts=out)
