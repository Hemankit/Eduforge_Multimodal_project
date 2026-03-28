"""
Quick test to verify rendered outputs (audio and diagrams).
"""
from pathlib import Path
import webbrowser
import subprocess

def test_outputs():
    """Test viewing the generated outputs."""
    
    output_dir = Path("test_output")
    
    print("=" * 70)
    print("TESTING RENDERED OUTPUTS")
    print("=" * 70)
    
    # 1. Check audio files
    print("\n[1/3] Audio Files:")
    audio_files = list(output_dir.glob("*.wav"))
    for audio_file in audio_files:
        size_mb = audio_file.stat().st_size / (1024 * 1024)
        print(f"   ✅ {audio_file.name} ({size_mb:.2f} MB)")
    
    if audio_files:
        print(f"\n   Playing first audio file: {audio_files[0].name}")
        print("   (Will open in default audio player)")
        try:
            # Open with default system player
            subprocess.run(["start", str(audio_files[0].absolute())], shell=True)
            print("   ✅ Audio file opened")
        except Exception as e:
            print(f"   ⚠️  Could not auto-play: {e}")
            print(f"   Manually open: {audio_files[0].absolute()}")
    
    # 2. Check diagram HTML
    print("\n[2/3] Diagram File:")
    diagram_files = list(output_dir.glob("diagram_*.html"))
    for diagram_file in diagram_files:
        print(f"   ✅ {diagram_file.name}")
    
    if diagram_files:
        print(f"\n   Opening diagram in browser: {diagram_files[0].name}")
        try:
            webbrowser.open(str(diagram_files[0].absolute()))
            print("   ✅ Diagram opened in browser")
            print("   (Check if Mermaid diagram renders correctly)")
        except Exception as e:
            print(f"   ⚠️  Could not auto-open: {e}")
    
    # 3. Check slides HTML
    print("\n[3/3] Slides File:")
    slides_files = list(output_dir.glob("slides.html"))
    for slides_file in slides_files:
        print(f"   ✅ {slides_file.name}")
    
    if slides_files:
        print(f"\n   Opening slides in browser: {slides_files[0].name}")
        try:
            webbrowser.open(str(slides_files[0].absolute()))
            print("   ✅ Slides opened in browser")
        except Exception as e:
            print(f"   ⚠️  Could not auto-open: {e}")
    
    print("\n" + "=" * 70)
    print("OUTPUT VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nManual verification checklist:")
    print("  [ ] Audio narration plays and sounds clear")
    print("  [ ] Mermaid diagram displays correctly in browser")
    print("  [ ] Slides display with proper layout and styling")
    print()

if __name__ == "__main__":
    test_outputs()
