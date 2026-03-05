from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.routes import router   # ← changed from relative to absolute import

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://your-frontend.onrender.com",   # ← add your Render frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)