"""
Comprehensive verification script for deterministic rendering.
Checks that all three rendering types (slides, diagrams, audio) are functioning correctly.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from output_schema import ContentOutput
from few_shot_examples import FEW_SHOT_EXAMPLES
from media_renderers import slide_renderer, diagram_renderer, audio_renderer


def verify_all_renderers():
    """Verify all rendering components are working."""
    
    print("=" * 70)
    print("EDUFORGE MULTIMODAL - RENDERING VERIFICATION")
    print("=" * 70)
    
    # Load test data
    print("\n📋 Loading test data...")
    example = FEW_SHOT_EXAMPLES[0]
    content = ContentOutput.model_validate(example["output"])
    print(f"✅ Loaded: {content.sections[0].title} ({len(content.sections)} sections)")
    
    results = {}
    output_dir = Path("test_output")
    
    # Test 1: Slide Renderer
    print("\n" + "="*70)
    print("1️⃣  TESTING SLIDE RENDERER")
    print("="*70)
    try:
        renderer = slide_renderer.SlideRenderer(output_dir=str(output_dir))
        slide_file = renderer.render(content, format="html")
        
        if slide_file.exists() and slide_file.stat().st_size > 0:
            results['slides'] = '✅ PASS'
            print(f"✅ SUCCESS: {slide_file.name}")
            print(f"   📄 Size: {slide_file.stat().st_size:,} bytes")
            print(f"   📍 Location: {slide_file.absolute()}")
        else:
            results['slides'] = '❌ FAIL'
            print(f"❌ FAIL: File not created or empty")
    except Exception as e:
        results['slides'] = f'❌ ERROR: {e}'
        print(f"❌ ERROR: {e}")
    
    # Test 2: Diagram Renderer
    print("\n" + "="*70)
    print("2️⃣  TESTING DIAGRAM RENDERER")
    print("="*70)
    try:
        renderer = diagram_renderer.DiagramRenderer(output_dir=str(output_dir))
        diagram_files = renderer.render(content, format="svg")
        
        # Count successfully created files (including HTML fallbacks)
        created_files = []
        for df in diagram_files:
            if df.exists():
                created_files.append(df)
            elif df.with_suffix('.html').exists():
                created_files.append(df.with_suffix('.html'))
        
        if created_files:
            results['diagrams'] = '✅ PASS'
            print(f"✅ SUCCESS: {len(created_files)} diagram(s) rendered")
            for df in created_files:
                file_type = "HTML fallback" if df.suffix == '.html' else df.suffix.upper()
                print(f"   📊 {df.name} ({df.stat().st_size:,} bytes) [{file_type}]")
            if any(f.suffix == '.html' for f in created_files):
                print(f"   💡 Note: HTML fallback used (mermaid-cli not installed)")
        else:
            results['diagrams'] = '⚠️  WARN: No files created'
            print(f"⚠️  WARNING: No diagram files created")
    except Exception as e:
        results['diagrams'] = f'❌ ERROR: {e}'
        print(f"❌ ERROR: {e}")
    
    # Test 3: Audio Renderer
    print("\n" + "="*70)
    print("3️⃣  TESTING AUDIO RENDERER")
    print("="*70)
    try:
        import pyttsx3
        renderer = audio_renderer.AudioRenderer(output_dir=str(output_dir))
        audio_files = renderer.render(content)
        
        existing_files = [f for f in audio_files if f.exists() and f.stat().st_size > 0]
        
        if len(existing_files) == len(audio_files):
            results['audio'] = '✅ PASS'
            print(f"✅ SUCCESS: {len(existing_files)} audio file(s) rendered")
            for af in existing_files:
                duration_estimate = af.stat().st_size / 88200  # Rough estimate at 44.1kHz 16-bit mono
                print(f"   🔊 {af.name} ({af.stat().st_size:,} bytes, ~{duration_estimate:.1f}s)")
        elif existing_files:
            results['audio'] = '⚠️  PARTIAL'
            print(f"⚠️  PARTIAL: {len(existing_files)}/{len(audio_files)} files created")
        else:
            results['audio'] = '❌ FAIL'
            print(f"❌ FAIL: No audio files created")
    except ImportError:
        results['audio'] = '⚠️  SKIPPED: pyttsx3 not installed'
        print(f"⚠️  SKIPPED: pyttsx3 not installed")
        print(f"   Install with: pip install pyttsx3")
    except Exception as e:
        results['audio'] = f'❌ ERROR: {e}'
        print(f"❌ ERROR: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    for component, status in results.items():
        print(f"  {component.capitalize():12} : {status}")
    
    # Overall status
    print("\n" + "="*70)
    passes = sum(1 for s in results.values() if '✅' in s)
    total = len(results)
    
    if passes == total:
        print("🎉 ALL RENDERING COMPONENTS WORKING!")
        print("="*70)
        print("\n✅ Your deterministic rendering pipeline is fully operational.")
        print("   You can now proceed to test with LLM integration.")
        return True
    else:
        print(f"⚠️  SOME ISSUES DETECTED ({passes}/{total} passing)")
        print("="*70)
        print("\n💡 Check the errors above and ensure all dependencies are installed.")
        return False


if __name__ == "__main__":
    success = verify_all_renderers()
    sys.exit(0 if success else 1)
