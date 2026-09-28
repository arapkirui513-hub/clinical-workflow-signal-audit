from fastapi import FastAPI

from app.fhir.routes import router as fhir_router

app = FastAPI(
    title="Clinical Workflow Signal Audit API",
    version="0.1.0",
    description="FHIR-enabled clinical workflow signal audit backend.",
)

app.include_router(fhir_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}