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
    """
    Build a complete prompt for the LLM with optional schema and few-shot examples.
    
    Args:
        content_input: Validated ContentInput
        include_schema: Whether to include explicit JSON schema
        include_few_shot: Whether to include few-shot examples
        num_examples: Number of few-shot examples to include
        
    Returns:
        Complete prompt string
    """
    prompt_parts = []
    
    # Load system prompt
    system_prompt = load_system_prompt()
    prompt_parts.append(system_prompt)
    prompt_parts.append("\n\n")
    
    # Add explicit JSON schema (helps with structured output)
    if include_schema:
        schema = ContentOutput.model_json_schema()
        schema_json = json.dumps(schema, indent=2)
        prompt_parts.append("You must output JSON that exactly matches this schema:\n\n")
        prompt_parts.append("```json\n")
        prompt_parts.append(schema_json)
        prompt_parts.append("\n```\n\n")
    
    # Add few-shot examples
    if include_few_shot:
        from few_shot_examples import FEW_SHOT_EXAMPLES
        prompt_parts.append("Here are example inputs and expected outputs:\n\n")
        
        for i, example in enumerate(FEW_SHOT_EXAMPLES[:num_examples], 1):
            prompt_parts.append(f"Example {i}:\n")
            prompt_parts.append("INPUT:\n")
            prompt_parts.append(json.dumps(example["input"], indent=2))
            prompt_parts.append("\n\nOUTPUT:\n")
            prompt_parts.append(json.dumps(example["output"], indent=2))
            prompt_parts.append("\n\n---\n\n")
    
    # Add audience-specific instructions
    audience_instructions = {
        "beginner": "Use simple language, relatable examples, and avoid technical jargon. Define any necessary terms immediately.",
        "intermediate": "Use clear language with relevant examples. Introduce technical terms with brief explanations. Balance intuition with light formalism.",
        "advanced": "Use precise technical language and formal notation where appropriate. Include detailed explanations of complex concepts."
    }
    
    prompt_parts.append(f"AUDIENCE LEVEL: {content_input.audience}\n")
    prompt_parts.append(f"Style guidance: {audience_instructions.get(content_input.audience, '')}\n\n")
    
    # Add format-specific optimization instructions
    if content_input.constraints.render_formats and content_input.constraints.optimize_for_format:
        prompt_parts.append("TARGET OUTPUT FORMATS:\n")
        for fmt in content_input.constraints.render_formats:
            prompt_parts.append(f"  - {fmt}\n")
        
        format_guidance = {
            "slides": "Structure content as distinct slide-worthy chunks. Keep each section's script concise (2-3 key points). Make titles punchy and descriptive. Ensure visual_plan gives clear, specific rendering instructions.",
            "diagrams": "Provide highly detailed visual_plan descriptions AND generate Mermaid syntax in mermaid_source field. Set diagram_type to match the Mermaid diagram type. Include specific node labels, relationships, and structure.",
            "audio": "Write scripts that work standalone without visual aids. Include verbal transitions, emphasize key points through repetition, and describe concepts verbally rather than pointing to visuals.",
            "video": "Balance narration with visual descriptions. Scripts should complement visuals, not duplicate them. visual_plan should describe animations, transitions, and on-screen text."
        }
        
        prompt_parts.append("\nFORMAT-SPECIFIC GUIDANCE:\n")
        for fmt in content_input.constraints.render_formats:
            if fmt in format_guidance:
                prompt_parts.append(f"  {fmt.upper()}: {format_guidance[fmt]}\n")
        prompt_parts.append("\n")
    
    # Add Mermaid syntax examples if diagrams are requested
    if content_input.constraints.render_formats and "diagrams" in content_input.constraints.render_formats:
        prompt_parts.append("MERMAID DIAGRAM SYNTAX EXAMPLES:\n\n")
        prompt_parts.append("Flowchart example:\n")
        prompt_parts.append("```mermaid\n")
        prompt_parts.append("flowchart TD\n")
        prompt_parts.append("    A[Start] --> B{Is it?}\n")
        prompt_parts.append("    B -->|Yes| C[OK]\n")
        prompt_parts.append("    B -->|No| D[End]\n")
        prompt_parts.append("```\n\n")
        
        prompt_parts.append("Graph example:\n")
        prompt_parts.append("```mermaid\n")
        prompt_parts.append("graph LR\n")
        prompt_parts.append("    A[Input Layer] --> B[Hidden Layer]\n")
        prompt_parts.append("    B --> C[Output Layer]\n")
        prompt_parts.append("```\n\n")
        
        prompt_parts.append("Timeline example:\n")
        prompt_parts.append("```mermaid\n")
        prompt_parts.append("timeline\n")
        prompt_parts.append("    title History of Computing\n")
        prompt_parts.append("    1945 : ENIAC\n")
        prompt_parts.append("    1971 : First Microprocessor\n")
        prompt_parts.append("    2007 : iPhone Released\n")
        prompt_parts.append("```\n\n")
        
        prompt_parts.append("Use the appropriate Mermaid syntax for your diagram_type in the mermaid_source field.\n\n")
    
    # Add the actual user request
    prompt_parts.append("Now generate educational content for this input:\n\n")
    prompt_parts.append(json.dumps(content_input.model_dump(), indent=2))
    prompt_parts.append("\n\nReturn ONLY valid JSON matching the schema above. No additional commentary.\n")
    
    return "".join(prompt_parts)
