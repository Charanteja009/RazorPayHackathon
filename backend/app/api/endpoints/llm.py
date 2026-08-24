from fastapi import APIRouter
from backend.app.services.llm.gateway import llm_gateway
from backend.app.schemas.pydantic_schemas import ProviderHealthResponse, SimulationToggleRequest

router = APIRouter()

@router.get("/providers", response_model=ProviderHealthResponse)
def get_llm_providers_health():
    """
    Returns health status, request counts, and fallback counts for all LLM providers.
    """
    return llm_gateway.get_status()

@router.post("/simulation")
def toggle_llm_simulation(request: SimulationToggleRequest):
    """
    Demo control endpoint: Simulate OpenAI failure or All LLM failure to test fallback.
    """
    llm_gateway.set_simulation(
        openai_fail=request.simulate_openai_failure,
        all_llm_fail=request.simulate_all_llm_failure
    )
    return {
        "message": "LLM simulation state updated successfully.",
        "state": llm_gateway.get_status()
    }
