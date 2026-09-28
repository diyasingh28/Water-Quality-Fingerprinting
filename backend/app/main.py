from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_reports
from app.api import routes_action_center


from app.core.config import settings
from app.db.database import init_db
from app.api import (
    routes_predict,
    routes_explain,
    routes_stations,
    routes_history,
    routes_upload,
    routes_stream,
)

app = FastAPI(
    title="Water Quality Fingerprinting API",
    description="Pollution source attribution using ML + Explainable AI (SHAP).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "water-quality-fingerprinting-api"}


app.include_router(routes_predict.router)
app.include_router(routes_explain.router)
app.include_router(routes_stations.router)
app.include_router(routes_history.router)
app.include_router(routes_upload.router)
app.include_router(routes_stream.router)  # Phase 2 stub
app.include_router(routes_reports.router)
app.include_router(routes_action_center.router)
