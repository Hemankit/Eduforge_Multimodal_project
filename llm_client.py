"""
Simple LLM Client - Switch between local, Together AI, and remote GPU inference.

Providers:
- local: Free, runs on local GPU/CPU via Transformers
- together: Paid API, powerful hosted models
- remote_gpu: Self-hosted GPU inference (RunPod)
"""
import json
import logging
from typing import Optional, List, Type, TypeVar

from pydantic import BaseModel, ValidationError

from llm_providers import (
    BaseLLMProvider,
    LocalProvider,
    TogetherProvider,
    RemoteGPUProvider,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, provider: BaseLLMProvider, fallback_providers: Optional[List[BaseLLMProvider]] = None):
        self.provider = provider
        self.fallback_providers = fallback_providers or []
        self.total_cost = 0.0
        self.total_tokens = 0
        self.call_count = 0

    def generate_content(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        providers_to_try = [self.provider] + self.fallback_providers

        for idx, provider in enumerate(providers_to_try):
            try:
                logger.info(f"Attempting generation with {provider.get_name()} ({provider.model})")
                response = provider.generate(prompt, max_tokens, temperature)

                self.call_count += 1
                self.total_cost += response.cost_usd or 0.0
                self.total_tokens += response.tokens_used or 0

                tokens_display = response.tokens_used if response.tokens_used is not None else "n/a"
                latency_display = f"{response.latency_ms:.0f}ms" if response.latency_ms is not None else "n/a"
                cost_display = f"${response.cost_usd:.4f}" if response.cost_usd is not None else "n/a"

                logger.info(
                    f"✅ Generation successful | Provider: {response.provider} | "
                    f"Model: {response.model} | Tokens: {tokens_display} | "
                    f"Latency: {latency_display} | Cost: {cost_display}"
                )

                return response.content

            except Exception as e:
                is_last_provider = idx == len(providers_to_try) - 1

                if is_last_provider:
                    logger.error(f"❌ All providers failed. Last error: {e}")
                    raise RuntimeError(f"All LLM providers failed. Last error: {e}")
                else:
                    logger.warning(
                        f"⚠️ Provider {provider.get_name()} failed: {e}. "
                        f"Trying fallback {providers_to_try[idx + 1].get_name()}..."
                    )
                    continue

    def repair_loop(self, prompt: str, output_model: Type[T], max_retries: int = 3) -> T:
        response = self.generate_content(prompt)

        for attempt in range(max_retries):
            try:
                data = json.loads(response)
                return output_model.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Validation failed (attempt {attempt + 1}/{max_retries}): {e}")

                repair_prompt = f"""
Fix the JSON so it matches the schema and constraints.
Return ONLY corrected JSON.

Invalid JSON:
{response}

Errors:
{str(e)}
"""
                response = self.generate_content(repair_prompt)

        raise RuntimeError(
            f"Failed to produce valid structured output for {output_model.__name__} after repair attempts"
        )

    def get_stats(self) -> dict:
        return {
            "total_calls": self.call_count,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost,
            "avg_tokens_per_call": self.total_tokens / self.call_count if self.call_count > 0 else 0,
            "avg_cost_per_call": self.total_cost / self.call_count if self.call_count > 0 else 0,
        }

    @classmethod
    def create(cls, provider: str = "local", model: Optional[str] = None, fallback_to_local: bool = False, **kwargs) -> "LLMClient":
        provider_classes = {
            "local": LocalProvider,
            "together": TogetherProvider,
            "remote_gpu": RemoteGPUProvider,
        }

        if provider not in provider_classes:
            raise ValueError(
                f"Unknown provider: {provider}. Choose 'local', 'together', or 'remote_gpu'"
            )

        primary_provider = provider_classes[provider](model=model, **kwargs)

        if not primary_provider.is_available():
            if provider == "together":
                raise RuntimeError(
                    "Together AI provider not available. "
                    "Set TOGETHER_API_KEY environment variable or pass api_key parameter."
                )
            elif provider == "remote_gpu":
                raise RuntimeError(
                    "Remote GPU provider not available. "
                    "Set REMOTE_GPU_URL and REMOTE_GPU_API_KEY environment variables."
                )
            else:
                raise RuntimeError(
                    "Local provider not available. "
                    "Install 'transformers', 'torch', and 'accelerate' packages."
                )

        fallback_providers = []

        if provider == "remote_gpu":
            together_provider = TogetherProvider(api_key=kwargs.get("api_key"))
            if together_provider.is_available():
                fallback_providers.append(together_provider)
                logger.info("Added Together fallback provider for remote_gpu")

        elif provider == "together":
            remote_gpu_provider = RemoteGPUProvider()
            if remote_gpu_provider.is_available():
                fallback_providers.append(remote_gpu_provider)
                logger.info("Added remote_gpu fallback provider for together")

        return cls(provider=primary_provider, fallback_providers=fallback_providers)

    @classmethod
    def from_pretrained(cls, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3") -> "LLMClient":
        logger.info("Using legacy from_pretrained() - consider using LLMClient.create()")
        provider = LocalProvider(model=model_id)
        return cls(provider=provider)
