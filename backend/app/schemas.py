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


class ExplainItem(BaseModel):
    jenis_pajak: str
    formula: str
    components: Dict[str, float]  # contoh: {"base": ..., "macro": ..., "policy": ...}


class ForecastResponse(BaseModel):
    run_id: str
    scenario_id: Optional[str] = None
    points: List[ForecastPoint]                     # agregat tahunan per jenis
    monthly: List[ForecastPoint] = []              # 12 bulan per jenis
    explain: List[ExplainItem] = []                # transparansi model
    params_snapshot: Dict[str, Any] = {}           # parameter yang dipakai
    overrides_applied: Dict[str, Any] = {}         # overrides skenario
