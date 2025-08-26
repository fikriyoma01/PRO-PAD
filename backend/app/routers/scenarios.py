from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json
from ..db import get_db
from ..models import Scenario
from ..schemas import ScenarioCreate

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

@router.post("/")
def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
    if db.get(Scenario, payload.scenario_id):
        raise HTTPException(400, "scenario exists")
    s = Scenario(
        scenario_id=payload.scenario_id,
        name=payload.name,
        description=payload.description,
        overrides_json=json.dumps(payload.overrides),
        created_by="api",
        created_at=datetime.utcnow(),
        active=True,
    )
    db.add(s); db.commit()
    return {"ok": True}

@router.get("/")
def list_scenarios(db: Session = Depends(get_db)):
    return db.query(Scenario).all()
