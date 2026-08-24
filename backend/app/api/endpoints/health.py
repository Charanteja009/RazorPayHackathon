from fastapi import APIRouter
from backend.seed_data import seed_database

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Revenue Recovery API",
        "version": "1.0.0",
        "ml_model_loaded": True
    }

@router.post("/seed/demo-scenarios")
def reseed_demo_scenarios():
    """
    Reseeds the database with default demo scenarios.
    """
    seed_database()
    return {"message": "Demo dataset and 5 deterministic scenarios reseeded successfully."}
