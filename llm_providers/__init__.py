"""
LLM Provider System - Simple switching between local, API-based, and remote GPU inference.

Supports:
- Local inference (Mistral 7B / Phi-2 via Transformers)
- Together AI (cloud-hosted API)
- Remote GPU inference (RunPod-hosted Mistral)
"""
from .base_provider import BaseLLMProvider, LLMResponse
from .local_provider import LocalProvider
from .together_provider import TogetherProvider
from .remote_gpu_provider import RemoteGPUProvider

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "LocalProvider",
    "TogetherProvider",
    "RemoteGPUProvider",
]
