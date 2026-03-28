"""
This module defines the schema with constraints for input data validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List

class Constraints(BaseModel):
  """ Defines the constraints for educational content generation """
  max_duration_sec: int = Field(..., ge=30, le=1200,description="Maximum duration of the content in seconds")

  examples: Optional[int] = Field(None, ge=1, le=10, description="Number of examples to include (1-10)")

  visual_style: Optional[Literal["minimal", "detailed", "animated"]] = Field(
        default="detailed",
        description="Visual complexity level for diagrams and visualizations"
    )
  
  # Rendering format preferences
  render_formats: Optional[List[Literal["slides", "diagrams", "audio", "video"]]] = Field(
        default=None,
        description="Target output formats - LLM will optimize content structure for these formats"
    )
  
  slide_format: Optional[Literal["html", "svg", "ppt"]] = Field(
        default="html",
        description="Preferred slide format if slides are being rendered"
    )
  
  audio_engine: Optional[Literal["pyttsx3", "gtts", "edge-tts"]] = Field(
        default="pyttsx3",
        description="Text-to-speech engine for audio narration"
    )
  
  optimize_for_format: Optional[bool] = Field(
        default=True,
        description="If True, LLM generates content optimized for specified render_formats"
    )
  
class ContentInput(BaseModel):
  """Input schema for educational content generation."""
  topic: str = Field(
        ..., 
        min_length=3,
        max_length=100,
        description="Educational topic to explain"
    )
  audience: Literal["beginner", "intermediate", "advanced"] = Field(
        ...,
        description="Target audience knowledge level"
    )
  
  constraints: Constraints = Field(
    ...,
    description="Constraints for content generation"
  )

  # Topic field validators
  @field_validator("topic")
  @classmethod
  def topic_not_empty(cls, v: str) -> str:
        """Ensure topic is not just whitespace."""
        if not v.strip():
            raise ValueError("Topic cannot be empty or whitespace")
        return v.strip()
  
# Example usage:
if __name__ == "__main__":
    # Valid input
    valid_input = {
        "topic": "Gradient Descent",
        "audience": "beginner",
        "constraints": {
            "max_duration_sec": 120,
            "examples": 1
        }
    }
    
    content = ContentInput.model_validate(valid_input)
    print("✓ Valid input:")
    print(content.model_dump_json(indent=2))
    
    # Invalid input (will raise validation error)
    try:
        invalid_input = {
            "topic": "GD",
            "audience": "expert",  # Not in allowed values
            "constraints": {
                "max_duration_sec": 10,  # Too short
                "examples": 1
            }
        }
        ContentInput.model_validate(invalid_input)
    except Exception as e:
        print("\n✗ Invalid input caught:")
        print(f"  {e}")