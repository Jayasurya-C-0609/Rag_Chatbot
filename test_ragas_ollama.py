from openai import OpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextPrecision


# Ollama OpenAI-compatible client
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)


# Ragas LLM
ragas_llm = llm_factory(
    "qwen3.5:9b",
    provider="openai",
    client=client
)


# Test metric
metric = ContextPrecision(
    llm=ragas_llm
)


print("Ragas + Ollama + Context Precision initialized successfully!")