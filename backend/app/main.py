# backend/app/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .routers import parameters, forecast, scenarios, reports
from .config import settings
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title=settings.APP_NAME)

# ---- CORS: izinkan semua origin (untuk development) ----
# Di production, sebaiknya diganti dengan origin spesifik dari env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router tanpa prefix + juga di /api (kompatibel keduanya)
app.include_router(parameters.router)
app.include_router(scenarios.router)
app.include_router(forecast.router)
app.include_router(reports.router)

api = APIRouter()
api.include_router(parameters.router)
api.include_router(scenarios.router)
api.include_router(forecast.router)
api.include_router(reports.router)
app.include_router(api, prefix="/api")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"ok": True}

if settings.ENABLE_METRICS:
    Instrumentator().instrument(app).expose(app)
