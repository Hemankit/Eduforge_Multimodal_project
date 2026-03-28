"""
Test script for schemas and validation components only (no rendering, no LLM).
Tests the core data structures and validation logic.
"""
from input_schema import ContentInput
from output_schema import ContentOutput
from cross_validation import CrossValidator
from few_shot_examples import FEW_SHOT_EXAMPLES


def test_schemas_and_validation():
    """Test schemas and cross-validation with mock data."""
    
    print("=" * 70)
    print("TESTING SCHEMAS AND VALIDATION (NO RENDERING, NO LLM)")
    print("=" * 70)
    
    # Step 1: Load mock data
    print("\n[1/4] Loading mock data from few_shot_examples...")
    example = FEW_SHOT_EXAMPLES[0]  # Gradient Descent example
    
    print(f"   Raw input data: {list(example['input'].keys())}")
    print(f"   Raw output data: {list(example['output'].keys())}")
    
    # Step 2: Validate input schema
    print("\n[2/4] Validating input schema...")
    try:
        input_data = ContentInput.model_validate(example["input"])
        print(f"✅ Input schema valid:")
        print(f"   - Topic: {input_data.topic}")
        print(f"   - Audience: {input_data.audience}")
        print(f"   - Max duration: {input_data.constraints.max_duration_sec}s")
        print(f"   - Examples: {input_data.constraints.examples}")
        print(f"   - Visual style: {input_data.constraints.visual_style}")
    except Exception as e:
        print(f"❌ Input validation failed: {e}")
        return False
    
    # Step 3: Validate output schema
    print("\n[3/4] Validating output schema...")
    try:
        output_data = ContentOutput.model_validate(example["output"])
        print(f"✅ Output schema valid:")
        print(f"   - Learning objectives: {len(output_data.learning_objectives)}")
        print(f"   - Sections: {len(output_data.sections)}")
        print(f"   - Total duration: {output_data.total_duration_sec}s")
        
        for idx, section in enumerate(output_data.sections):
            print(f"\n   Section {idx}: {section.title}")
            print(f"     - Script length: {len(section.script)} chars")
            print(f"     - Visual plan: {len(section.visual_plan)} chars")
            print(f"     - Duration: {section.duration_sec}s")
            print(f"     - Key terms: {section.key_terms}")
            if section.mermaid_source:
                print(f"     - Has Mermaid diagram: Yes ({len(section.mermaid_source)} chars)")
            
    except Exception as e:
        print(f"❌ Output validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Cross-validation
    print("\n[4/4] Running cross-validation (input ↔ output)...")
    try:
        is_valid, errors = CrossValidator.validate(input_data, output_data)
        if is_valid:
            print("✅ Cross-validation passed - all constraints satisfied")
        else:
            print("⚠️  Cross-validation found issues:")
            for error in errors:
                print(f"   ERROR: {error}")
    except Exception as e:
        print(f"❌ Cross-validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ SCHEMA & VALIDATION TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\nNext step: Test media renderers (slides, diagrams, audio)")
    
    return True


if __name__ == "__main__":
    success = test_schemas_and_validation()
    exit(0 if success else 1)
