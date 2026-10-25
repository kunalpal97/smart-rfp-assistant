
from fastapi import FastAPI # type: ignore

from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router

from app.api.routes.questions import router as questions_router

from app.api.routes.documents import router as documents_router

from app.api.routes.users import router as users_router

from app.api.routes.history import router as history_router

from app.api.routes.dashboard import router as dashboard_router

# Later we will use this feature to extract questions from customer RFPs.
# from app.api.routes.rfps import router as rfps_router

from contextlib import asynccontextmanager
from app.storage.history_repository import initialize_history_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_history_table()
    yield

app = FastAPI(
    title="Smart RFP Response Assistant",
    description="AI-powered RFP response generation using RAG",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router)

app.include_router(questions_router)

app.include_router(documents_router)

app.include_router(users_router)

app.include_router(history_router)

app.include_router(dashboard_router)

# Later we will use this feature to extract questions from customer RFPs.

# app.include_router(rfps_router)


@app.get("/")
def root():
    return {
        "message": "Smart RFP Response Assistant API",
        "docs": "/docs"
    }