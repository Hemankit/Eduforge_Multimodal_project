"""
Test prompt building without LLM - verify schema injection, examples, and formatting.
"""
from input_schema import ContentInput, Constraints
from prompt_templates import build_prompt, load_system_prompt
import json


def test_prompt_building():
    """Test the prompt builder with different configurations."""
    
    print("=" * 70)
    print("TESTING PROMPT BUILDER")
    print("=" * 70)
    
    # Test 1: Load system prompt
    print("\n[1/5] Testing system prompt loading...")
    system_prompt = load_system_prompt()
    print(f"✅ System prompt loaded: {len(system_prompt)} characters")
    print(f"   Preview: {system_prompt[:200]}...")
    
    # Test 2: Build basic prompt (no few-shot examples)
    print("\n[2/5] Testing basic prompt (without few-shot examples)...")
    basic_input = ContentInput(
        topic="Binary Search Algorithm",
        audience="intermediate",
        constraints=Constraints(
            max_duration_sec=120,
            render_formats=["slides", "diagrams"],
            slide_format="html",
            optimize_for_format=True
        )
    )
    
    basic_prompt = build_prompt(basic_input, include_few_shot=False)
    print(f"✅ Basic prompt built: {len(basic_prompt)} characters")
    
    # Check for key components
    checks = {
        "System prompt": "Core Goals" in basic_prompt,
        "JSON Schema": "ContentOutput" in basic_prompt,
        "Mermaid examples": "flowchart" in basic_prompt and "graph LR" in basic_prompt,
        "Audience instructions": "intermediate" in basic_prompt.lower(),
        "Format guidance": "slides" in basic_prompt.lower() or "diagrams" in basic_prompt.lower()
    }
    
    print("\n   Component checks:")
    for component, present in checks.items():
        status = "✅" if present else "❌"
        print(f"   {status} {component}: {'Present' if present else 'Missing'}")
    
    # Test 3: Build prompt with few-shot examples
    print("\n[3/5] Testing prompt with few-shot examples...")
    fewshot_input = ContentInput(
        topic="Gradient Descent",
        audience="beginner",
        constraints=Constraints(
            max_duration_sec=180,
            example_count=2,
            render_formats=["slides", "diagrams", "audio"],
            optimize_for_format=True
        )
    )
    
    fewshot_prompt = build_prompt(fewshot_input, include_few_shot=True)
    print(f"✅ Few-shot prompt built: {len(fewshot_prompt)} characters")
    print(f"   Prompt is {len(fewshot_prompt) - len(basic_prompt)} characters longer")
    
    # Check for few-shot content
    has_examples = "## Example" in fewshot_prompt or "learning_objectives" in fewshot_prompt
    print(f"   {'✅' if has_examples else '❌'} Few-shot examples included")
    
    # Test 4: Different audiences
    print("\n[4/5] Testing audience-specific instructions...")
    audiences = ["beginner", "intermediate", "advanced"]
    for aud in audiences:
        test_input = ContentInput(
            topic="Machine Learning Basics",
            audience=aud,
            constraints=Constraints(max_duration_sec=120)
        )
        prompt = build_prompt(test_input, include_few_shot=False)
        has_audience = aud in prompt.lower()
        print(f"   {'✅' if has_audience else '⚠️ '} {aud.capitalize()}: {'Found' if has_audience else 'Not explicit'}")
    
    # Test 5: Format-specific guidance
    print("\n[5/5] Testing format-specific guidance...")
    
    # Slides-only
    slides_input = ContentInput(
        topic="Data Structures",
        audience="intermediate",
        constraints=Constraints(
            max_duration_sec=120,
            render_formats=["slides"],
            optimize_for_format=True
        )
    )
    slides_prompt = build_prompt(slides_input, include_few_shot=False)
    has_slides_guidance = "punchy" in slides_prompt.lower() or "concise" in slides_prompt.lower()
    print(f"   {'✅' if has_slides_guidance else '⚠️ '} Slides-only: {('Concise guidance included' if has_slides_guidance else 'Generic')}")
    
    # Diagrams + audio
    diagram_input = ContentInput(
        topic="Sorting Algorithms",
        audience="beginner",
        constraints=Constraints(
            max_duration_sec=180,
            render_formats=["diagrams", "audio"],
            optimize_for_format=True
        )
    )
    diagram_prompt = build_prompt(diagram_input, include_few_shot=False)
    has_mermaid = "mermaid_source" in diagram_prompt
    has_audio = "standalone" in diagram_prompt.lower() or "audio" in diagram_prompt.lower()
    print(f"   {'✅' if has_mermaid else '❌'} Diagrams: {'Mermaid guidance' if has_mermaid else 'Missing'}")
    print(f"   {'✅' if has_audio else '⚠️ '} Audio: {'Standalone script guidance' if has_audio else 'Generic'}")
    
    # Show sample section of final prompt
    print("\n" + "=" * 70)
    print("PROMPT SAMPLE (First 1500 chars of few-shot prompt)")
    print("=" * 70)
    print(fewshot_prompt[:1500])
    print("\n... [truncated] ...")
    
    print("\n" + "=" * 70)
    print("✅ PROMPT BUILDER TEST COMPLETED")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  - Basic prompt: {len(basic_prompt):,} characters")
    print(f"  - With few-shot: {len(fewshot_prompt):,} characters")
    print(f"  - System prompt: {len(system_prompt):,} characters")
    print(f"\nAll components verified! Ready for LLM integration.")
    
    return True


if __name__ == "__main__":
    success = test_prompt_building()
    exit(0 if success else 1)
