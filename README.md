# PRO-PAD Monorepo (Pilot → Production)
Komponen: FastAPI API, paket forecasting (Konsep 1), ETL (Airflow+dbt), Frontend React+Tailwind, Reporting PDF/XLSX, Docker Compose, CI.

## Quick start (local dev)
1) Jalankan Postgres:
```
docker compose -f deploy/docker-compose.yml up -d db
```
2) API:
```
cd backend
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```
3) Web:
```
cd web
npm i
npm run dev
```

## Forecast API
```
POST /forecast/run
{ "year": 2026 }
```

Catatan: modul ekonometrik/ML & ETL loaders masih *stub* untuk dilanjutkan.


## Seed Parameter Registry & Skenario
```
export DATABASE_URL=postgresql://propad:propad@localhost:5432/propad
python backend/scripts/seed_params.py
# skenario terbuat: baseline, optimis, pesimis
```

## Unduh Laporan (PDF/XLSX)
- PDF:  `GET /reports/apbd?year=2026&scenario_id=optimis&format=pdf`
- XLSX: `GET /reports/apbd?year=2026&scenario_id=baseline&format=xlsx`

## ETL Mock Loader (data internal)
```
export DATABASE_URL=postgresql://propad:propad@localhost:5432/propad
python etl/loaders/mock_load_internal.py
# Memuat CSV contoh ke schema raw.*
```


## Fitur baru
- **Export CSV** di Dashboard (via `/reports/apbd?format=csv`).
- **Parameter Editor (CRUD)** di tab *Admin* (web).
- **Peta Jatim (dummy)** pada Dashboard — bubble map per kab/kota untuk ilustrasi distribusi.

