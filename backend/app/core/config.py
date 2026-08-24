import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Revenue Recovery Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database - Strictly PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/revenue_recovery"
    )
    
    # LLM Keys & Endpoints
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Razorpay Gateway Keys
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    USE_MOCK_GATEWAY: bool = os.getenv("USE_MOCK_GATEWAY", "true").lower() == "true"
    
    # Business Logic Defaults
    MAX_RETRY_COUNT: int = 3
    HIGH_VALUE_THRESHOLD: float = 50000.0
    COST_PER_RECOVERY_ATTEMPT: float = 50.0
    AVERAGE_RECOVERY_RATE: float = 0.80

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
