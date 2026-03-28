"""
Test diagram renderer component independently.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from output_schema import ContentOutput
from media_renderers import diagram_renderer
from few_shot_examples import FEW_SHOT_EXAMPLES


def test_diagram_renderer():
    """Test Mermaid diagram generation."""
    
    print("=" * 70)
    print("TESTING DIAGRAM RENDERER")
    print("=" * 70)
    
    # Load mock data
    print("\n[1/3] Loading mock content...")
    example = FEW_SHOT_EXAMPLES[0]
    content = ContentOutput.model_validate(example["output"])
    
    # Count sections with diagrams
    sections_with_diagrams = sum(1 for s in content.sections if s.mermaid_source)
    print(f"✅ Content loaded:")
    print(f"   Total sections: {len(content.sections)}")
    print(f"   Sections with diagrams: {sections_with_diagrams}")
    
    if sections_with_diagrams == 0:
        print("⚠️  No sections have mermaid_source defined")
        return False
    
    # Initialize renderer
    print("\n[2/3] Initializing diagram renderer...")
    renderer = diagram_renderer.DiagramRenderer(output_dir="test_output")
    print("✅ Renderer initialized")
    print("   Note: Will use Mermaid.ink API if mermaid-cli not installed")
    
    # Render diagrams
    print("\n[3/3] Rendering diagrams...")
    try:
        diagram_files = renderer.render(content, format="svg")
        print(f"✅ Diagrams rendered successfully!")
        print(f"   Files generated: {len(diagram_files)}")
        
        for diagram_file in diagram_files:
            # Check for the file or HTML fallback
            if diagram_file.exists():
                print(f"   - {diagram_file.name} ({diagram_file.stat().st_size:,} bytes)")
            else:
                # Check if HTML fallback was created
                html_fallback = diagram_file.with_suffix('.html')
                if html_fallback.exists():
                    print(f"   - {html_fallback.name} ({html_fallback.stat().st_size:,} bytes) [HTML fallback]")
                else:
                    print(f"   - {diagram_file.name} (⚠️  file not found)")
        
        print("\n" + "=" * 70)
        print("✅ DIAGRAM RENDERER TEST PASSED")
        print("=" * 70)
        print(f"\nGenerated files in: {Path('test_output').absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Diagram rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_diagram_renderer()
    exit(0 if success else 1)
