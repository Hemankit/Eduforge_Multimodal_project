"""
Simple LLM Client - Switch between local (Mistral 7B) and API (Llama 3.3 70B) inference.

Two options:
- Local: Free, runs on GPU via Transformers
- Together AI: Paid API, powerful Llama 3.3 70B
"""
import json
import logging
from typing import Optional, List, Type, TypeVar

from pydantic import BaseModel, ValidationError

from llm_providers import (
    BaseLLMProvider,
    LocalProvider,
    TogetherProvider
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    Unified client for LLM interactions across multiple providers.

    Features:
    - Dynamic provider selection (local, Together)
    - Automatic fallback chains for resilience
    - Cost and latency tracking
    - Backward compatible with existing code
    """

    def __init__(self, provider: BaseLLMProvider, fallback_providers: Optional[List[BaseLLMProvider]] = None):
        """
        Initialize LLM client with a primary provider and optional fallbacks.

        Args:
            provider: Primary LLM provider
            fallback_providers: List of fallback providers (tried in order on failure)
        """
        self.provider = provider
        self.fallback_providers = fallback_providers or []
        self.total_cost = 0.0
        self.total_tokens = 0
        self.call_count = 0

    def generate_content(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """
        Generate content using the configured provider with automatic fallback.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text content
        """
        providers_to_try = [self.provider] + self.fallback_providers

        for idx, provider in enumerate(providers_to_try):
            try:
                logger.info(f"Attempting generation with {provider.get_name()} ({provider.model})")
                response = provider.generate(prompt, max_tokens, temperature)

                # Track metrics
                self.call_count += 1
                self.total_cost += response.cost_usd or 0.0
                self.total_tokens += response.tokens_used or 0

                # Log success
                logger.info(
                    f"✅ Generation successful | Provider: {response.provider} | "
                    f"Model: {response.model} | Tokens: {response.tokens_used} | "
                    f"Latency: {response.latency_ms:.0f}ms | Cost: ${response.cost_usd:.4f}"
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

    def repair_loop(
        self,
        prompt: str,
        output_model: Type[T],
        max_retries: int = 3
    ) -> T:
        """
        Generate content with validation and automatic repair on schema violations.

        Args:
            prompt: Input prompt
            output_model: Pydantic model used to validate the LLM response
            max_retries: Maximum repair attempts

        Returns:
            Validated output_model instance
        """
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
        """Get usage statistics"""
        return {
            "total_calls": self.call_count,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost,
            "avg_tokens_per_call": self.total_tokens / self.call_count if self.call_count > 0 else 0,
            "avg_cost_per_call": self.total_cost / self.call_count if self.call_count > 0 else 0,
        }

    @classmethod
    def create(
        cls,
        provider: str = "local",
        model: Optional[str] = None,
        fallback_to_local: bool = True,
        **kwargs
    ) -> "LLMClient":
        """
        Factory method to create LLMClient with specified provider.

        Args:
            provider: Provider name ("local" or "together")
            model: Model name (provider-specific, uses defaults if not specified)
            fallback_to_local: If True, falls back to local if API provider fails
            **kwargs: Additional provider-specific configuration (api_key, etc.)

        Returns:
            Configured LLMClient instance

        Examples:
            >>> # Local Mistral 7B (free, requires GPU)
            >>> client = LLMClient.create(provider="local")

            >>> # Together AI Llama 3.3 70B (API)
            >>> client = LLMClient.create(provider="together")

            >>> # Together with fallback to local on failure
            >>> client = LLMClient.create(provider="together", fallback_to_local=True)
        """
        provider_classes = {
            "local": LocalProvider,
            "together": TogetherProvider,
        }

        if provider not in provider_classes:
            raise ValueError(f"Unknown provider: {provider}. Choose 'local' or 'together'")

        primary_provider = provider_classes[provider](model=model, **kwargs)

        if not primary_provider.is_available():
            if provider == "together":
                raise RuntimeError(
                    "Together AI provider not available. "
                    "Set TOGETHER_API_KEY environment variable or pass api_key parameter."
                )
            raise RuntimeError(
                "Local provider not available. "
                "Install 'transformers', 'torch', and 'accelerate' packages."
            )

        fallback_providers = []
        if fallback_to_local and provider != "local":
            local_provider = LocalProvider()
            if local_provider.is_available():
                fallback_providers.append(local_provider)
                logger.info("Added local fallback provider")

        return cls(provider=primary_provider, fallback_providers=fallback_providers)

    @classmethod
    def from_pretrained(cls, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3") -> "LLMClient":
        """
        Backward compatibility: Load local model using transformers.

        Args:
            model_id: HuggingFace model ID

        Returns:
            LLMClient configured with LocalProvider
        """
        logger.info("Using legacy from_pretrained() - consider using LLMClient.create() for provider flexibility")
        provider = LocalProvider(model=model_id)
        return cls(provider=provider)
