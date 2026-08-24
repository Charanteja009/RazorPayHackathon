from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.router import api_router

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
        from backend.seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"Startup database connection skipped or failed: {e}")

@app.get("/")
def root():
    return {
        "message": "AI Revenue Recovery Platform API is active.",
        "docs": f"{settings.API_PREFIX}/docs"
    }
