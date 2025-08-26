
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import Parameter
from ..schemas import ParameterSchema

router = APIRouter(prefix="/parameters", tags=["parameters"])

@router.get("/", response_model=list[ParameterSchema])
def list_params(db: Session = Depends(get_db)):
    rows = db.query(Parameter).all()
    return [ParameterSchema(**{c.key: getattr(r, c.key) for c in r.__table__.columns}) for r in rows]

@router.get("/{param_key}", response_model=ParameterSchema)
def get_param(param_key: str, db: Session = Depends(get_db)):
    r = db.get(Parameter, param_key)
    if not r:
        raise HTTPException(404, "parameter not found")
    return ParameterSchema(**{c.key: getattr(r, c.key) for c in r.__table__.columns})

@router.post("/", response_model=ParameterSchema)
def upsert_param(payload: ParameterSchema, db: Session = Depends(get_db)):
    existing = db.get(Parameter, payload.param_key)
    if existing:
        # update
        for f in ["value_num","value_text","unit","min_val","max_val","source","owner"]:
            v = getattr(payload, f)
            if v is not None:
                setattr(existing, f, v)
        db.add(existing); db.commit(); db.refresh(existing)
        return ParameterSchema(**{c.key: getattr(existing, c.key) for c in existing.__table__.columns})
    else:
        r = Parameter(
            param_key=payload.param_key,
            value_num=payload.value_num,
            value_text=payload.value_text,
            unit=payload.unit,
            min_val=payload.min_val,
            max_val=payload.max_val,
            source=payload.source,
            owner=payload.owner,
        )
        db.add(r); db.commit(); db.refresh(r)
        return ParameterSchema(**{c.key: getattr(r, c.key) for c in r.__table__.columns})

@router.put("/{param_key}", response_model=ParameterSchema)
def update_param(param_key: str, payload: ParameterSchema, db: Session = Depends(get_db)):
    r = db.get(Parameter, param_key)
    if not r:
        raise HTTPException(404, "parameter not found")
    for f in ["value_num","value_text","unit","min_val","max_val","source","owner"]:
        v = getattr(payload, f)
        if v is not None:
            setattr(r, f, v)
    db.add(r); db.commit(); db.refresh(r)
    return ParameterSchema(**{c.key: getattr(r, c.key) for c in r.__table__.columns})

@router.delete("/{param_key}")
def delete_param(param_key: str, db: Session = Depends(get_db)):
    r = db.get(Parameter, param_key)
    if not r:
        raise HTTPException(404, "parameter not found")
    db.delete(r); db.commit()
    return {"ok": True}
