
from fastapi import FastAPI # type: ignore

from app.api.routes.health import router as health_router

from app.api.routes.questions import router as questions_router

from app.api.routes.documents import router as documents_router

# Later we will use this feature to extract questions from customer RFPs.
# from app.api.routes.rfps import router as rfps_router

app = FastAPI(
    title="Smart RFP Response Assistant",
    description="AI-powered RFP response generation using RAG",
    version="0.1.0"
)

app.include_router(health_router)

app.include_router(questions_router)

app.include_router(documents_router)

# Later we will use this feature to extract questions from customer RFPs.

# app.include_router(rfps_router)


@app.get("/")
def root():
    return {
        "message": "Smart RFP Response Assistant API",
        "docs": "/docs"
    }