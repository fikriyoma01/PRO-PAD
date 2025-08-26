from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid, json
from typing import Any, Dict, List

from ..db import get_db
from ..models import Parameter, Scenario, ForecastRun, ForecastResult
from ..schemas import ForecastRequest, ForecastResponse, ForecastPoint
from ..services.forecast_engine import run_forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])

def _safe_json(s: str | None) -> Dict[str, Any] | None:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None

@router.post("/run", response_model=ForecastResponse)
def run(payload: ForecastRequest, db: Session = Depends(get_db)):
    # 1) ambil registry parameter
    params: Dict[str, Any] = {
        p.param_key: (p.value_num if p.value_num is not None else p.value_text)
        for p in db.query(Parameter).all()
    }

    # 2) baca overrides skenario (optional)
    overrides = None
    if payload.scenario_id:
        sc = db.get(Scenario, payload.scenario_id)
        if sc:
            overrides = _safe_json(sc.overrides_json)

    # 3) jalankan engine
    computed = run_forecast(payload.year, params, overrides)

    # 4) kompatibilitas bentuk hasil:
    #    - baru: {"annual":[{periode, jenis_pajak, nilai, model, version}], "monthly":{...}}
    #    - lama: [{periode, jenis_pajak, nilai, model}]
    if isinstance(computed, dict):
        annual_rows: List[Dict[str, Any]] = list(computed.get("annual", []))
        # monthly_rows = computed.get("monthly")  # kalau suatu saat mau dipakai
    else:
        annual_rows = list(computed)  # type: ignore[assignment]

    # 5) buat run_id, simpan parent dulu supaya FK aman
    run_id = str(uuid.uuid4())
    fr = ForecastRun(
        run_id=run_id,
        created_at=datetime.utcnow(),
        scenario_id=payload.scenario_id or "baseline",
        horizon_months=payload.horizon_months,
    )
    db.add(fr)
    db.commit()  # penting: parent ada dulu

    # 6) simpan hasil + bentuk response points
    points: List[ForecastPoint] = []
    for row in annual_rows:
        # robust ke key hilang / tipe numeric Decimal
        periode = row.get("periode")
        if isinstance(periode, str):
            # fallback: jika engine mengirim "2026-12-31"
            periode = date.fromisoformat(periode)
        jenis = row.get("jenis_pajak")
        nilai = float(row.get("nilai", 0) or 0)
        model_name = row.get("model", "Model")
        version = int(row.get("version", 1))

        db.add(
            ForecastResult(
                run_id=run_id,
                periode=periode,
                jenis_pajak=jenis,
                nilai=nilai,
                model_name=model_name,
                version=version,
            )
        )
        points.append(
            ForecastPoint(periode=periode, jenis_pajak=jenis, nilai=nilai)
        )

    db.commit()
    return ForecastResponse(run_id=run_id, points=points)
