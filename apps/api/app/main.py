from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import user

app = FastAPI(title="UTN Buddy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Hello from UTN Buddy API 🚀"}
