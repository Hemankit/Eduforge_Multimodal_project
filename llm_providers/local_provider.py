"""
Local LLM Provider - Uses transformers library for local inference.
Supports models like Mistral-7B, Llama, etc.
"""
import time
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from .base_provider import BaseLLMProvider, LLMResponse


class LocalProvider(BaseLLMProvider):
    """Provider for local model inference using HuggingFace transformers"""
    
    DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
    
    def __init__(self, model: Optional[str] = None, **kwargs):
        """
        Initialize local provider.
        
        Args:
            model: HuggingFace model ID
            **kwargs: Additional config (device_map, torch_dtype, etc.)
        """
        super().__init__(model or self.DEFAULT_MODEL, **kwargs)
        self._model = None
        self._tokenizer = None
        # Don't load model immediately - load on first use for lazy initialization
    
    def _load_model(self):
        """Load model and tokenizer from HuggingFace"""
        if self._model is not None:
            return  # Already loaded
        
        print(f"Loading local model: {self.model}")
        print("This may take 2-3 minutes...")
        
        self._tokenizer = AutoTokenizer.from_pretrained(self.model)
        
        # Handle deprecated torch_dtype parameter
        torch_dtype = self.config.get('torch_dtype', torch.float16)
        if 'torch_dtype' in self.config:
            torch_dtype = self.config.get('dtype', torch_dtype)
        
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model,
            torch_dtype=torch_dtype,
            device_map=self.config.get('device_map', 'auto'),
            **{k: v for k, v in self.config.items() 
               if k not in ['torch_dtype', 'dtype', 'device_map']}
        )
        
        print(f"✅ Model loaded successfully on {self._model.device}")
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 4096, 
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text using local model"""
        # Lazy load model on first use
        if self._model is None:
            self._load_model()
        
        start_time = time.time()
        
        # Tokenize input
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        input_length = inputs['input_ids'].shape[1]
        
        # Generate
        outputs = self._model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=self._tokenizer.eos_token_id,
            **kwargs
        )
        
        # Decode
        full_response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove prompt from response
        response = full_response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        # Calculate metrics
        output_length = outputs.shape[1] - input_length
        latency_ms = (time.time() - start_time) * 1000
        
        return LLMResponse(
            content=response,
            model=self.model,
            provider="local",
            tokens_used=input_length + output_length,
            latency_ms=latency_ms,
            cost_usd=0.0,  # Free!
            metadata={
                "input_tokens": input_length,
                "output_tokens": output_length,
                "device": str(self._model.device)
            }
        )
    
    def is_available(self) -> bool:
        """Check if local inference is available"""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            return True
        except ImportError:
            return False
    
    def get_name(self) -> str:
        """Get provider name"""
        return "local"
    
    def get_max_context_length(self) -> int:
        """Get max context length"""
        # Try to get from model config
        if self._model is not None and hasattr(self._model.config, 'max_position_embeddings'):
            return self._model.config.max_position_embeddings
        return 8192  # Conservative default for modern models
