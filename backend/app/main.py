from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.routes import router

app = FastAPI(title="AI Surgical Tool API")

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
