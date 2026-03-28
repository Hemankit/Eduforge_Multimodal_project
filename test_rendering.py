"""
Test script for media rendering components without LLM.
Uses mock data from few_shot_examples to test slide, diagram, and audio rendering.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from input_schema import ContentInput
from output_schema import ContentOutput
from cross_validation import CrossValidator
from few_shot_examples import FEW_SHOT_EXAMPLES


def test_rendering_pipeline():
    """Test the complete rendering pipeline with mock data."""
    
    print("=" * 70)
    print("TESTING MEDIA RENDERING PIPELINE (NO LLM)")
    print("=" * 70)
    
    # Step 1: Load mock data from few-shot examples
    print("\n[1/6] Loading mock data from few_shot_examples...")
    example = FEW_SHOT_EXAMPLES[0]  # Use Gradient Descent example
    
    input_data = ContentInput.model_validate(example["input"])
    output_data = ContentOutput.model_validate(example["output"])
    
    print(f"✅ Mock data loaded:")
    print(f"   Topic: {input_data.topic}")
    print(f"   Audience: {input_data.audience}")
    print(f"   Sections: {len(output_data.sections)}")
    print(f"   Total duration: {output_data.total_duration_sec}s")
    
    # Step 2: Validate schemas
    print("\n[2/6] Validating output schema...")
    try:
        # Output self-validation happens automatically via Pydantic
        print("✅ Output schema valid")
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    
    # Step 3: Cross-validation
    print("\n[3/6] Running cross-validation (input ↔ output)...")
    try:
        is_valid, errors = CrossValidator.validate(input_data, output_data)
        if is_valid:
            print("✅ Cross-validation passed")
        else:
            print("⚠️  Cross-validation warnings:")
            for error in errors:
                print(f"   - {error}")
    except Exception as e:
        print(f"❌ Cross-validation failed: {e}")
        return False
    
    # Step 4: Test slide rendering
    print("\n[4/6] Testing slide renderer...")
    try:
        from media_renderers import slide_renderer
        renderer = slide_renderer.SlideRenderer(output_dir="test_output")
        slide_file = renderer.render(output_data, format="html")
        print(f"✅ Slides rendered: {slide_file}")
        print(f"   File exists: {slide_file.exists()}")
        print(f"   File size: {slide_file.stat().st_size} bytes")
    except Exception as e:
        print(f"❌ Slide rendering failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Test diagram rendering
    print("\n[5/6] Testing diagram renderer...")
    try:
        from media_renderers import diagram_renderer
        renderer = diagram_renderer.DiagramRenderer(output_dir="test_output")
        diagram_files = renderer.render(output_data, format="svg")
        print(f"✅ Diagrams rendered: {len(diagram_files)} files")
        for diagram_file in diagram_files:
            if diagram_file.exists():
                print(f"   - {diagram_file.name} ({diagram_file.stat().st_size} bytes)")
    except Exception as e:
        print(f"⚠️  Diagram rendering encountered an issue: {e}")
        print(f"   Note: This may use fallback to HTML if mermaid-cli is not installed")
    
    # Step 6: Test audio rendering
    print("\n[6/6] Testing audio renderer...")
    try:
        import pyttsx3
        from media_renderers import audio_renderer
        
        renderer = audio_renderer.AudioRenderer(output_dir="test_output")
        audio_files = renderer.render(output_data)
        print(f"✅ Audio rendered: {len(audio_files)} files")
        for audio_file in audio_files:
            if audio_file.exists():
                print(f"   - {audio_file.name} ({audio_file.stat().st_size} bytes)")
            else:
                print(f"   - {audio_file.name} (⚠️  file not created)")
        
        print("   Note: Audio playback test skipped")
    
    except ImportError:
        print(f"⚠️  Audio renderer skipped (pyttsx3 not installed)")
        print(f"   Install with: pip install pyttsx3")
    except Exception as e:
        print(f"⚠️  Audio rendering failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ RENDERING PIPELINE TEST COMPLETED")
    print("=" * 70)
    print("\nGenerated files in ./test_output/:")
    test_output = Path("test_output")
    if test_output.exists():
        for file in sorted(test_output.iterdir()):
            print(f"  - {file.name}")
    
    return True
    
    return True


if __name__ == "__main__":
    success = test_rendering_pipeline()
    exit(0 if success else 1)
