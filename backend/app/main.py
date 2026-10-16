
from fastapi import FastAPI # type: ignore

from app.api.routes.health import router as health_router

from app.api.routes.questions import router as questions_router

from app.api.routes.documents import router as documents_router

app = FastAPI(
    title="Smart RFP Response Assistant",
    description="AI-powered RFP response generation using RAG",
    version="0.1.0"
)

app.include_router(health_router)

app.include_router(questions_router)

app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "message": "Smart RFP Response Assistant API",
        "docs": "/docs"
    }