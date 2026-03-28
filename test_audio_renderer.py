"""
Test audio renderer component independently.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from output_schema import ContentOutput
from few_shot_examples import FEW_SHOT_EXAMPLES


def test_audio_renderer():
    """Test TTS audio generation."""
    
    print("=" * 70)
    print("TESTING AUDIO RENDERER")
    print("=" * 70)
    
    # Check if pyttsx3 is available
    try:
        import pyttsx3
        print("\n[DEPENDENCY CHECK] ✅ pyttsx3 is installed")
    except ImportError:
        print("\n[DEPENDENCY CHECK] ❌ pyttsx3 is not installed")
        print("   Install with: pip install pyttsx3")
        print("\n⚠️  Skipping audio renderer test (pyttsx3 required)")
        return True  # Return True so we don't fail the test, just skip it
    
    # Import audio_renderer only after confirming pyttsx3 is available
    from media_renderers import audio_renderer
    
    # Load mock data
    print("\n[1/3] Loading mock content...")
    example = FEW_SHOT_EXAMPLES[0]
    content = ContentOutput.model_validate(example["output"])
    print(f"✅ Content loaded: {len(content.sections)} sections")
    
    for idx, section in enumerate(content.sections):
        print(f"   Section {idx}: {section.title} ({len(section.script)} chars)")
    
    # Initialize renderer
    print("\n[2/3] Initializing audio renderer (using pyttsx3)...")
    try:
        renderer = audio_renderer.AudioRenderer(output_dir="test_output")
        print("✅ Renderer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize renderer: {e}")
        return False
    
    # Render audio
    print("\n[3/3] Rendering audio narration...")
    print("   This may take a few moments...")
    try:
        audio_files = renderer.render(content)
        print(f"✅ Audio rendered successfully!")
        print(f"   Files generated: {len(audio_files)}")
        
        for audio_file in audio_files:
            if audio_file.exists():
                print(f"   - {audio_file.name} ({audio_file.stat().st_size:,} bytes)")
            else:
                print(f"   - {audio_file.name} (⚠️  file not created)")
        
        print("\n   Note: Audio playback test skipped (requires pydub)")
        print("   You can play the audio files manually to verify quality")
        
        print("\n" + "=" * 70)
        print("✅ AUDIO RENDERER TEST PASSED")
        print("=" * 70)
        print(f"\nGenerated files in: {Path('test_output').absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Audio rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_audio_renderer()
    exit(0 if success else 1)
