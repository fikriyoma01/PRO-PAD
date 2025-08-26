from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
import json
from typing import Any, Dict, List, Optional

from ..db import get_db
from ..models import Parameter, Scenario, ForecastRun, ForecastResult
from ..schemas import (
    ForecastRequest,
    ForecastResponse,
    ForecastPoint,
    ForecastMeta,
)
from ..services.forecast_engine import run_forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])


def _safe_json_loads(s: str | None) -> Dict[str, Any] | None:
    if not s:
        return None
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return None


def _create_forecast(
    year: int,
    scenario_id: Optional[str],
    horizon_months: int,
    db: Session,
) -> ForecastResponse:
    """
    Core logic to run a forecast, save results, and return the response.
    Refactored to be used by both GET and POST endpoints.
    """
    # 1. Ambil parameter dasar
    params: Dict[str, Any] = {
        p.param_key: p.value_num if p.value_num is not None else p.value_text
        for p in db.query(Parameter).all()
    }

    # 2. Ambil override dari skenario jika ada
    overrides: Optional[Dict[str, Any]] = None
    scenario_name = scenario_id or "baseline"
    if scenario_id:
        sc = db.get(Scenario, scenario_id)
        if sc:
            overrides = _safe_json_loads(sc.overrides_json)
        else:
            raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")

    # 3. Jalankan engine forecast
    # Asumsi engine mengembalikan dict dengan 'annual' dan 'meta'
    computed = run_forecast(year, params, overrides, db)

    annual_rows: List[Dict[str, Any]] = computed.get("annual", [])
    meta_payload: Dict[str, Any] = computed.get("meta", {})

    if not annual_rows:
        raise HTTPException(status_code=500, detail="Forecast engine returned no data.")

    # 4. Simpan hasil dalam satu transaksi
    run_id = str(uuid.uuid4())

    try:
        # Buat record ForecastRun
        forecast_run = ForecastRun(
            run_id=run_id,
            created_at=datetime.utcnow(),
            scenario_id=scenario_name,
            horizon_months=horizon_months,
            meta_json=json.dumps(meta_payload),
        )
        db.add(forecast_run)

        # Buat record ForecastResult
        points: List[ForecastPoint] = []
        for row in annual_rows:
            periode_val = row.get("periode")
            if isinstance(periode_val, str):
                periode_val = date.fromisoformat(periode_val)

            jenis_pajak = row.get("jenis_pajak", "unknown")
            nilai = float(row.get("nilai", 0.0))

            result = ForecastResult(
                run_id=run_id,
                periode=periode_val,
                jenis_pajak=jenis_pajak,
                nilai=nilai,
                p10=row.get("p10"),
                p50=row.get("p50"),
                p90=row.get("p90"),
                model_name=row.get("model", "default"),
                version=int(row.get("version", 1)),
            )
            db.add(result)
            points.append(
                ForecastPoint(periode=periode_val, jenis_pajak=jenis_pajak, nilai=nilai)
            )

        db.commit()

    except Exception as e:
        db.rollback()
        # Sebaiknya log error di sini
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {e}")

    # 5. Bentuk response
    return ForecastResponse(
        run_id=run_id,
        points=points,
        meta=ForecastMeta.model_validate(meta_payload),
    )


@router.post("/run", response_model=ForecastResponse)
def run_forecast_post(
    payload: ForecastRequest, db: Session = Depends(get_db)
):
    """Triggers a new forecast run based on a POST request."""
    return _create_forecast(
        year=payload.year,
        scenario_id=payload.scenario_id,
        horizon_months=payload.horizon_months or 12,
        db=db,
    )


@router.get("/run", response_model=ForecastResponse)
def run_forecast_get(
    year: int,
    scenario_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Triggers a new forecast run based on a GET request."""
    # Menggunakan horizon default 12 bulan untuk GET request
    return _create_forecast(
        year=year,
        scenario_id=scenario_id,
        horizon_months=12,
        db=db,
    )
