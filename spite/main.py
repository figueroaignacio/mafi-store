from contextlib import asynccontextmanager

from fastapi import FastAPI

from spite import __version__
from spite.db.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="spite",
    description="Job hunting automation API. Cynicism included at no extra charge.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "operational", "message": "Unfortunately, still running."}
