"""
Takes validated input and calls llm with structured prompt to generate content. Then validates the output.
"""
from validate import SchemaValidator
import json
from pydantic import ValidationError
from input_schema import ContentInput
from output_schema import ContentOutput
from llm_client import LLMClient

class ContentGenerator:
  def __init__(self, llm_client: LLMClient, valid_input: ContentInput, prompt: str):
    self.llm_client = llm_client
    self.valid_input = valid_input
    self.prompt = prompt

  def generate_content(self) -> ContentOutput:
    """Generate content using the llm client, then validate and parse the output"""
    output_text = self.llm_client.generate_content(self.prompt)
    
    # Try to extract JSON from the output (in case there's extra text)
    json_str = self._extract_json(output_text)
    
    # Parse and validate the output
    try:
        output_data = json.loads(json_str)
        validated_output = ContentOutput.model_validate(output_data)
        return validated_output
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Output validation failed: {e}")

  def generate_with_repair(self) -> ContentOutput:
    """Generate content with automatic repair on validation failure"""
    return self.llm_client.repair_loop(self.prompt)
  
  def _extract_json(self, text: str) -> str:
    """Extract JSON from text that might contain extra content"""
    # Try to find JSON block in markdown code fence
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    
    # Try to find JSON object or array
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
    
    # Return as-is if no JSON markers found
    return text.strip()
    
  