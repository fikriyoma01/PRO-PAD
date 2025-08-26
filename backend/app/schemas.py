from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Dict, Any, List

class ParameterSchema(BaseModel):
    param_key: str
    value_num: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    source: Optional[str] = None
    owner: Optional[str] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None

class ScenarioCreate(BaseModel):
    scenario_id: str
    name: str
    description: Optional[str]
    overrides: Dict[str, Any] = Field(default_factory=dict)

class ForecastRequest(BaseModel):
    year: int
    scenario_id: Optional[str] = None
    horizon_months: Optional[int] = 12


class ForecastPoint(BaseModel):
    periode: date
    jenis_pajak: str
    nilai: float


class ForecastMeta(BaseModel):
    assumptions: Dict[str, Any] = Field(default_factory=dict)
    model_weights: Dict[str, float] = Field(default_factory=dict)
    backtest: Dict[str, Any] = Field(default_factory=dict)
    interval: Dict[str, Any] = Field(default_factory=dict)


class ForecastResponse(BaseModel):
    run_id: str
    points: List[ForecastPoint]
    meta: Optional[ForecastMeta] = None
