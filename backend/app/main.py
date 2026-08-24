import sys
from pathlib import Path

# Ensure repository root and backend directory are in sys.path
app_dir = Path(__file__).resolve().parent
backend_dir = app_dir.parent
repo_root = backend_dir.parent

for p in [str(repo_root), str(backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.app.core.config import settings
    from backend.app.api.router import api_router
except ModuleNotFoundError:
    from app.core.config import settings
    from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def on_startup():
    try:
        try:
            from backend.seed_data import seed_database
        except ModuleNotFoundError:
            from seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"Startup database connection skipped or failed: {e}")

@app.get("/")
def root():
    return {
        "message": "AI Revenue Recovery Platform API is active.",
        "docs": f"{settings.API_PREFIX}/docs"
    }
