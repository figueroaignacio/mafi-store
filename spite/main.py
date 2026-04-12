from contextlib import asynccontextmanager

from fastapi import FastAPI

from spite import __version__
from spite.api.jobs import router as jobs_router
from spite.api.search import router as search_router
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

app.include_router(jobs_router)
app.include_router(search_router)


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "operational", "message": "Unfortunately, still running."}
