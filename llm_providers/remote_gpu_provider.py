import os
import time
from typing import Optional

import requests

from llm_providers.base_provider import BaseLLMProvider, LLMResponse


class RemoteGPUProvider(BaseLLMProvider):
    """
    Calls a remote inference API hosted on RunPod.
    Expects:
      POST {base_url}/infer
      headers: x-api-key
      json: {prompt, max_tokens, temperature}
      response: {"text": "..."}
    """

    DEFAULT_MODEL_NAME = "mistral-7b-runpod"

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_sec: int = 180,
    ):
        self.model = model or self.DEFAULT_MODEL_NAME
        self.base_url = (base_url or os.getenv("REMOTE_GPU_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("REMOTE_GPU_API_KEY")
        self.timeout_sec = timeout_sec

    def is_available(self) -> bool:
        return bool(self.base_url and self.api_key)

    def get_name(self) -> str:
        return "remote_gpu"

    def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        if not self.is_available():
            raise RuntimeError(
                "Remote GPU provider not configured. "
                "Set REMOTE_GPU_URL and REMOTE_GPU_API_KEY."
            )

        start = time.time()

        response = requests.post(
            f"{self.base_url}/infer",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            },
            json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=self.timeout_sec,
        )
        response.raise_for_status()

        data = response.json()
        text = data["text"]

        latency_ms = (time.time() - start) * 1000

        return LLMResponse(
            content=text,
            provider=self.get_name(),
            model=self.model,
            latency_ms=latency_ms,
            tokens_used=None,
            cost_usd=None,
        )