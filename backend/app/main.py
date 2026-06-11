import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.routes import router

# Vercel mounts this service at /api when using experimentalServices.
root_path = "/api" if os.getenv("VERCEL") else ""

app = FastAPI(title="AI Surgical Tool API", root_path=root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Surgical Tool API is running"}


app.include_router(router)
