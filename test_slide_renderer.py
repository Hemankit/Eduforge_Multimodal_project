"""
Test slide renderer component independently.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from output_schema import ContentOutput
from media_renderers import slide_renderer
from few_shot_examples import FEW_SHOT_EXAMPLES


def test_slide_renderer():
    """Test HTML slide generation."""
    
    print("=" * 70)
    print("TESTING SLIDE RENDERER")
    print("=" * 70)
    
    # Load mock data
    print("\n[1/3] Loading mock content...")
    example = FEW_SHOT_EXAMPLES[0]
    content = ContentOutput.model_validate(example["output"])
    print(f"✅ Content loaded: {len(content.sections)} sections")
    
    # Initialize renderer
    print("\n[2/3] Initializing slide renderer...")
    renderer = slide_renderer.SlideRenderer(output_dir="test_output")
    print("✅ Renderer initialized")
    
    # Render slides
    print("\n[3/3] Rendering HTML slides...")
    try:
        slide_file = renderer.render(content, format="html")
        print(f"✅ Slides rendered successfully!")
        print(f"   File: {slide_file}")
        print(f"   Exists: {slide_file.exists()}")
        print(f"   Size: {slide_file.stat().st_size:,} bytes")
        
        # Show a preview of the content
        if slide_file.exists():
            content_preview = slide_file.read_text(encoding='utf-8')[:500]
            print(f"\n   Preview (first 500 chars):")
            print(f"   {content_preview}...")
        
        print("\n" + "=" * 70)
        print("✅ SLIDE RENDERER TEST PASSED")
        print("=" * 70)
        print(f"\nOpen the file to view: {slide_file.absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Slide rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_slide_renderer()
    exit(0 if success else 1)
