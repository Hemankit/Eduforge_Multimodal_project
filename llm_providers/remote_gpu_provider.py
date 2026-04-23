import os
import time
import logging
from typing import Optional

import requests
from requests.exceptions import RequestException

from llm_providers.base_provider import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


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
        max_retries: int = 3,
    ):
        self.model = model or self.DEFAULT_MODEL_NAME
        self.base_url = (base_url or os.getenv("REMOTE_GPU_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("REMOTE_GPU_API_KEY")
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries

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
        last_error = None

        for attempt in range(self.max_retries):
            try:
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

                # Check for HTTP errors with detailed message
                if response.status_code >= 400:
                    error_body = response.text[:500] if response.text else "<empty response>"
                    error_msg = (
                        f"Remote GPU request failed with status {response.status_code}: {error_body}"
                    )
                    
                    # Retry on 5xx errors (server/proxy issues)
                    if response.status_code >= 500 and attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(
                            f"RunPod returned {response.status_code}, retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{self.max_retries})..."
                        )
                        time.sleep(wait_time)
                        last_error = RuntimeError(error_msg)
                        continue
                    
                    raise RuntimeError(error_msg)

                data = response.json()
                text = data.get("text") or data.get("generated_text")
                
                if not text:
                    raise RuntimeError(f"Remote GPU response missing text field: {data}")

                latency_ms = (time.time() - start) * 1000

                return LLMResponse(
                    content=text,
                    provider=self.get_name(),
                    model=self.model,
                    latency_ms=latency_ms,
                    tokens_used=None,
                    cost_usd=None,
                )

            except RequestException as e:
                # Retry on network errors
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Network error: {e}, retrying in {wait_time}s "
                        f"(attempt {attempt + 1}/{self.max_retries})..."
                    )
                    time.sleep(wait_time)
                    last_error = e
                    continue
                raise RuntimeError(f"Remote GPU network error after {self.max_retries} attempts: {e}")

        # If we exhausted retries
        if last_error:
            raise last_error
        raise RuntimeError("Remote GPU request failed after retries")