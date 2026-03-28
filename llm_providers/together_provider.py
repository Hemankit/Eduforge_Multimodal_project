"""
Together AI Provider - Uses Together AI API for open-source models like Llama 70B.
"""
import os
import time
from typing import Optional
from .base_provider import BaseLLMProvider, LLMResponse


class TogetherProvider(BaseLLMProvider):
    """Provider for Together AI API (Llama, Mixtral, etc.)"""
    
    DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    
    # Pricing per 1M tokens (approximate, as of March 2026)
    PRICING = {
        "meta-llama/Llama-3.3-70B-Instruct-Turbo": {"input": 0.88, "output": 0.88},
        "meta-llama/Llama-3.1-70B-Instruct-Turbo": {"input": 0.88, "output": 0.88},
        "meta-llama/Llama-3-70b-chat-hf": {"input": 0.9, "output": 0.9},
        "meta-llama/Llama-3-8b-chat-hf": {"input": 0.2, "output": 0.2},
        "mistralai/Mixtral-8x22B-Instruct-v0.1": {"input": 1.2, "output": 1.2},
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.6, "output": 0.6},
    }
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Together AI provider.
        
        Args:
            model: Together AI model name
            api_key: Together API key (or set TOGETHER_API_KEY env var)
            **kwargs: Additional Together-specific parameters
        """
        super().__init__(model or self.DEFAULT_MODEL, **kwargs)
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self._client = None
        
        if self.is_available():
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Together client"""
        try:
            from together import Together
            self._client = Together(api_key=self.api_key)
        except ImportError:
            raise ImportError("Together package not installed. Run: pip install together")
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 4096, 
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Together AI API"""
        if self._client is None:
            raise RuntimeError("Together client not initialized. Check API key.")
        
        start_time = time.time()
        
        # Call Together API
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract response
        content = response.choices[0].message.content
        
        # Together API doesn't always return token counts, estimate if needed
        input_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else len(prompt.split()) * 1.3
        output_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else len(content.split()) * 1.3
        total_tokens = int(input_tokens + output_tokens)
        
        # Calculate cost
        cost = self.estimate_cost(int(input_tokens), int(output_tokens))
        
        return LLMResponse(
            content=content,
            model=self.model,
            provider="together",
            tokens_used=total_tokens,
            latency_ms=latency_ms,
            cost_usd=cost,
            metadata={
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "finish_reason": response.choices[0].finish_reason if hasattr(response.choices[0], 'finish_reason') else None
            }
        )
    
    def is_available(self) -> bool:
        """Check if Together AI API is available"""
        try:
            import together
            return self.api_key is not None
        except ImportError:
            return False
    
    def get_name(self) -> str:
        """Get provider name"""
        return "together"
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost based on Together AI pricing"""
        pricing = self.PRICING.get(self.model, {"input": 0.9, "output": 0.9})
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def get_max_context_length(self) -> int:
        """Get max context length"""
        context_lengths = {
            "meta-llama/Llama-3.3-70B-Instruct-Turbo": 131072,  # 128K context
            "meta-llama/Llama-3.1-70B-Instruct-Turbo": 131072,  # 128K context
            "meta-llama/Llama-3-70b-chat-hf": 8192,
            "meta-llama/Llama-3-8b-chat-hf": 8192,
            "mistralai/Mixtral-8x22B-Instruct-v0.1": 65536,
            "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
        }
        return context_lengths.get(self.model, 8192)
