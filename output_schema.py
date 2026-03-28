"""
This module defines the schema for the output of educational content generation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Literal

class Section(BaseModel):
  """Individual section of the educational content."""
  title: str = Field(..., min_length=5, max_length=100, description="Title of the section")
  script: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="Narration script for this section"
    )
  
  visual_plan: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Description of visual elements for diagrams and slides"
    )
  
  duration_sec: int = Field(..., ge=10, le=600, description="Duration of this section in seconds")

  key_terms: Optional[List[str]] = Field(default=None, description="Important terminology introduced in this section")
  
  # Format-specific rendering hints
  slide_layout: Optional[Literal["title", "content", "split", "full-visual"]] = Field(
        default="content",
        description="Suggested slide layout for this section"
    )
  
  diagram_type: Optional[Literal["flowchart", "graph", "network", "comparison", "timeline", "concept-map"]] = Field(
        default=None,
        description="Type of diagram to render for visual_plan"
    )
  
  mermaid_source: Optional[str] = Field(
        default=None,
        description="Mermaid diagram syntax to render for this section. Must match diagram_type."
    )
  
  audio_emphasis: Optional[List[str]] = Field(
        default=None,
        description="Words or phrases to emphasize in audio narration"
    )
  
  visual_priority: Optional[Literal["low", "medium", "high"]] = Field(
        default="medium",
        description="How important visuals are for this section (high = visuals carry most meaning)"
    )

  @field_validator("title", "script", "visual_plan")
  @classmethod
  def not_empty(cls, v: str) -> str:
        """Ensure fields are not just whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

class ContentOutput(BaseModel):
    """Output schema for generated educational content."""

    learning_objectives: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="2-5 learning objectives for the educational content"
    )
      
    sections: List[Section] = Field(...,
                                    min_length=1, max_length=10, description="List of sections in the educational content")
    
    total_duration_sec: Optional[int] = Field(default=None, description="Total duration computed from sections in seconds")

    prerequisites: Optional[List[str]] = Field(default=None, description="List of prerequisite topics or knowledge areas")
    
    # Format-specific metadata
    recommended_formats: Optional[List[Literal["slides", "diagrams", "audio", "video"]]] = Field(
        default=None,
        description="Formats this content is best suited for based on structure and visuals"
    )

    # validator for learning objectives
    @field_validator("learning_objectives")
    @classmethod
    def validate_learning_objectives(cls, v: List[str]) -> List[str]:
        for obj in v:
            if len(obj.strip()) < 10:
                raise ValueError("Each learning objective must be at least 10 characters long")
        return [obj.strip() for obj in v]
        
    @model_validator(mode="after")
    def compute_total_duration(self):
        """Automatically compute total duration from sections."""
        if self.total_duration_sec is None:
            self.total_duration_sec = sum(section.duration_sec for section in self.sections)
        return self
    
    @model_validator(mode="after")
    def validate_script_duration_alignment(self):
        """Validate that script length roughly matches stated duration (approx 150 words/min)."""
        WORDS_PER_MINUTE = 150
        
        for idx, section in enumerate(self.sections):
            word_count = len(section.script.split())
            estimated_duration = (word_count / WORDS_PER_MINUTE) * 60  # in seconds
            
            # Allow 50% variance (scripts can have pauses, emphasis, etc.)
            min_duration = estimated_duration * 0.5
            max_duration = estimated_duration * 1.5
            
            if not (min_duration <= section.duration_sec <= max_duration):
                import warnings
                warnings.warn(
                    f"Section {idx} '{section.title}': duration_sec={section.duration_sec}s doesn't align "
                    f"with script length ({word_count} words ≈ {estimated_duration:.0f}s at 150 wpm). "
                    f"Expected range: {min_duration:.0f}-{max_duration:.0f}s"
                )
        return self
    
    @model_validator(mode="after")
    def validate_visual_plan_exists(self):
        """Ensure every section has a visual plan."""
        for idx, section in enumerate(self.sections):
            if not section.visual_plan or len(section.visual_plan.strip()) < 10:
                raise ValueError(f"Section {idx} '{section.title}' has missing or insufficient visual_plan")
        return self
  
  
# Example usage:
if __name__ == "__main__":
    # Valid output
    valid_output = {
        "learning_objectives": [
            "Understand optimization as minimization",
            "Interpret gradients intuitively"
        ],
        "sections": [
            {
                "title": "What is Gradient Descent?",
                "script": "Gradient descent is an optimization method that helps us find the minimum of a function by iteratively moving in the direction of steepest descent.",
                "visual_plan": "2D loss curve with moving point showing descent",
                "duration_sec": 30,
                "key_terms": ["optimization", "gradient", "minimum"]
            },
            {
                "title": "Intuition Example",
                "script": "Imagine standing on a hill blindfolded. To reach the bottom, you would feel the slope around you and take a step in the steepest downward direction. That's exactly what gradient descent does mathematically.",
                "visual_plan": "Hill metaphor with arrows indicating descent direction",
                "duration_sec": 45,
                "key_terms": ["steepest descent", "local minimum"]
            }
        ],
        "prerequisites": ["Basic calculus", "Function notation"]
    }
    
    content = ContentOutput.model_validate(valid_output)
    print("✓ Valid output:")
    print(content.model_dump_json(indent=2))
    print(f"\n  Total duration: {content.total_duration_sec}s")
    
    # Invalid output (will raise validation error)
    try:
        invalid_output = {
            "learning_objectives": ["Too short"],  # Objective too short
            "sections": []  # Empty sections
        }
        ContentOutput.model_validate(invalid_output)
    except Exception as e:
        print("\n✗ Invalid output caught:")
        print(f"  {e}")