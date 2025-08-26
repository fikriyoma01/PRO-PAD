from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io, json
from ..db import get_db
from ..models import Parameter, Scenario
from ..services.forecast_engine import run_forecast
from ..services.reporting import build_pdf_report, build_xlsx_report

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/apbd")
def apbd_report(year: int, format: str = "pdf", scenario_id: str | None = None, db: Session = Depends(get_db)):
    # Load params
    params = {p.param_key: (p.value_num if p.value_num is not None else p.value_text)
              for p in db.query(Parameter).all()}
    overrides = None
    scenario_name = "baseline"
    if scenario_id:
        sc = db.get(Scenario, scenario_id)
        if sc:
            overrides = json.loads(sc.overrides_json)
            scenario_name = sc.name
        else:
            raise HTTPException(404, "Scenario not found")

    rows = run_forecast(year, params, overrides)
    if format.lower() == "pdf":
        pdf_bytes = build_pdf_report({"year": year, "scenario": scenario_name, "rows": rows})
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                                 headers={"Content-Disposition": f"attachment; filename=report_apbd_{year}_{scenario_name}.pdf"})
    elif format.lower() == "xlsx":
        xlsx_bytes = build_xlsx_report(rows)
        return StreamingResponse(io.BytesIO(xlsx_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": f"attachment; filename=report_apbd_{year}_{scenario_name}.xlsx"})
    elif format.lower() == "csv":
        # Build CSV on the fly
        import csv
        import io as _io
        buf = _io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["periode","jenis_pajak","nilai"])
        for r in rows:
            writer.writerow([r["periode"], r["jenis_pajak"], float(r["nilai"])])
        data = buf.getvalue().encode("utf-8")
        return StreamingResponse(_io.BytesIO(data), media_type="text/csv",
                                 headers={"Content-Disposition": f"attachment; filename=report_apbd_{year}_{scenario_name}.csv"})
    else:
        raise HTTPException(400, "format must be pdf or xlsx or csv")

@router.get("/apbd.csv")
def apbd_report_csv(year: int, scenario_id: str | None = None, db: Session = Depends(get_db)):
    # convenience endpoint direct .csv path
    return apbd_report(year=year, format="csv", scenario_id=scenario_id, db=db)
