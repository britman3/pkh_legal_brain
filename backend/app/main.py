from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyze
from app.database import init_db

app = FastAPI(title="PKH Legal Brain API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized")

app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])

@app.get("/health")
def health():
    return {"status": "ok"}
