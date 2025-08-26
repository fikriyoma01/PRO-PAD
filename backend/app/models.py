# backend/app/models.py
from datetime import date, datetime
from sqlalchemy import String, Integer, Numeric, Date, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Parameter(Base):
    __tablename__ = "param_registry"

    param_key: Mapped[str] = mapped_column(String, primary_key=True)

    # gunakan Python types pada anotasi; SQL types di mapped_column:
    value_num: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(16), nullable=True)
    min_val: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    max_val: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(64), nullable=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class ForecastRun(Base):
    __tablename__ = "forecast_run"

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    scenario_id: Mapped[str] = mapped_column(String, nullable=False)
    horizon_months: Mapped[int] = mapped_column(Integer, nullable=False)
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class ForecastResult(Base):
    __tablename__ = "forecast_result"

    run_id: Mapped[str] = mapped_column(String, ForeignKey("forecast_run.run_id"), primary_key=True)
    periode: Mapped[date] = mapped_column(Date, primary_key=True)
    jenis_pajak: Mapped[str] = mapped_column(String(16), primary_key=True)

    nilai: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    p10: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    p50: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    p90: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)

    model_name: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)

class Scenario(Base):
    __tablename__ = "scenario"

    scenario_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    overrides_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class RealisasiTahunan(Base):
    __tablename__ = "realisasi_tahunan"

    tahun: Mapped[int] = mapped_column(Integer, primary_key=True)
    jenis_pajak: Mapped[str] = mapped_column(String(16), primary_key=True)
    nilai: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    # Catatan: PDRB atau variabel exogen lain bisa ditambahkan di sini
    # oleh skrip ETL untuk dipakai model ekonometrik.
