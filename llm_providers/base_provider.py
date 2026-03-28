"""
Abstract base class for LLM providers.
All providers must implement this interface for seamless switching.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    cost_usd: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Base class that all LLM providers must implement"""
    
    def __init__(self, model: Optional[str] = None, **kwargs):
        """
        Initialize the provider.
        
        Args:
            model: Model identifier (provider-specific)
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 4096, 
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text completion from the model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with generated content and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider is available and properly configured.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the provider name for logging/debugging.
        
        Returns:
            Provider name (e.g., "local", "openai", "anthropic")
        """
        pass
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost for a generation (optional, provider-specific).
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        return 0.0  # Default: free (local models)
    
    def get_max_context_length(self) -> int:
        """
        Get maximum context length for this model.
        
        Returns:
            Maximum context length in tokens
        """
        return 4096  # Conservative default
