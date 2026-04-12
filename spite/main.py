from fastapi import FastAPI

from spite import __version__

app = FastAPI(
    title="spite",
    description="Job hunting automation API. Cynicism included at no extra charge.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "operational", "message": "Unfortunately, still running."}
