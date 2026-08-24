import pytest
from backend.app.services.llm.gateway import llm_gateway

def test_openai_simulated_failure_groq_fallback():
    llm_gateway.set_simulation(openai_fail=True, all_llm_fail=False)
    
    res, provider, latency = llm_gateway.generate(
        "Diagnose failed payment with insufficient funds",
        "Return JSON with diagnosis and confidence"
    )
    
    assert res is not None
    assert provider in ["Groq", "Ollama", "Deterministic Policy Rules"]
    
    # Reset simulation
    llm_gateway.set_simulation(openai_fail=False, all_llm_fail=False)

def test_all_llm_simulated_failure_deterministic_fallback():
    llm_gateway.set_simulation(openai_fail=True, all_llm_fail=True)
    
    res, provider, latency = llm_gateway.generate(
        "Select recovery strategy for low score transaction",
        "Return JSON with action and reason"
    )
    
    assert res is not None
    assert provider == "Deterministic Policy Rules"
    assert "action" in res
    
    # Reset simulation
    llm_gateway.set_simulation(openai_fail=False, all_llm_fail=False)
