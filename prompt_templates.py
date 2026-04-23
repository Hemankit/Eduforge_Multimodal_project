"""
Stores prompt templates for different audiences and content types. These templates can be used to generate content that is tailored to specific needs and preferences.
"""
import json
from pathlib import Path
from typing import Optional
from input_schema import ContentInput
from output_schema import ContentOutput


def load_system_prompt() -> str:
    """Load the system prompt from system_prompt.txt"""
    system_prompt_file = Path(__file__).parent / "system_prompt.txt"
    return system_prompt_file.read_text(encoding="utf-8")


def build_prompt(
    content_input: ContentInput,
    include_schema: bool = True,
    include_few_shot: bool = False,
    num_examples: int = 3
) -> str:
    prompt_parts = []
    
    system_prompt = load_system_prompt()
    prompt_parts.append(system_prompt)
    prompt_parts.append("\n\n")
    
    if include_schema:
        schema = ContentOutput.model_json_schema()
        schema_json = json.dumps(schema, indent=2)
        prompt_parts.append("You must output JSON that exactly matches this schema:\n\n")
        prompt_parts.append("```json\n")
        prompt_parts.append(schema_json)
        prompt_parts.append("\n```\n\n")
    
    audience_instructions = {
        "beginner": "Use simple language, relatable examples, and avoid technical jargon. Define any necessary terms immediately.",
        "intermediate": "Use clear language with relevant examples. Introduce technical terms with brief explanations. Balance intuition with light formalism.",
        "advanced": "Use precise technical language and formal notation where appropriate. Include detailed explanations of complex concepts."
    }
    
    prompt_parts.append(f"AUDIENCE LEVEL: {content_input.audience}\n")
    prompt_parts.append(f"Style guidance: {audience_instructions.get(content_input.audience, '')}\n\n")
    
    prompt_parts.append("Now generate educational content for this input:\n\n")
    prompt_parts.append(json.dumps(content_input.model_dump(), indent=2))
    
    prompt_parts.append("""

CRITICAL OUTPUT REQUIREMENTS:

- You MUST return ONLY valid JSON.
- DO NOT include any explanations, comments, or text outside the JSON.
- DO NOT wrap the JSON in markdown (no ```).
- DO NOT omit any required fields.
- If a field is required in the schema, you MUST include it.
- If unsure about a value, provide a reasonable placeholder — NEVER omit fields.

FAILURE TO FOLLOW THESE RULES WILL BREAK THE SYSTEM.

Return ONLY JSON.
""")
    
    return "".join(prompt_parts)
