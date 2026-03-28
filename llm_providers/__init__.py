"""
LLM Provider System - Simple switching between local and API-based inference.

Supports:
- Local inference (Mistral 7B via Transformers) - Free, runs on GPU
- Together AI (Llama 3.3 70B via API) - Paid, cloud-hosted
"""
from .base_provider import BaseLLMProvider
from .local_provider import LocalProvider
from .together_provider import TogetherProvider

__all__ = [
    'BaseLLMProvider',
    'LocalProvider',
    'TogetherProvider',
]
