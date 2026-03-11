import asyncio
import pytest
from src.utils.llm_client import LLMClient


@pytest.mark.asyncio
async def test_generate_returns_string() -> None:
    """Test LLMClient can generate a response."""
    llm_client = LLMClient()
    prompt = "What is the capital of France?"
    response = await llm_client.generate(prompt)
    assert isinstance(response, str)
    assert len(response) > 0
    print("LLM Response:", response)