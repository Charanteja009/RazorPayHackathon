from fastapi import APIRouter
from backend.app.api.endpoints import recovery, dashboard, audit, agents, llm, health

api_router = APIRouter()

api_router.include_router(recovery.router, prefix="/recovery", tags=["Recovery"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Trail"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents Timeline"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM Gateway"])
api_router.include_router(health.router, tags=["System Health"])
