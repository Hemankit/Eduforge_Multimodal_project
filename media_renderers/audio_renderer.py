"""
This module contains the audio renderer that takes the structured content output and generates audio narration using text-to-speech synthesis.
"""
from output_schema import ContentOutput, Section
from pathlib import Path
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play

class AudioRenderer:
    """Generates audio narration from ContentOutput sections using pyttsx3."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the audio renderer.
        
        Args:
            output_dir: Directory to save rendered audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed (words per minute)
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    def render(self, content: ContentOutput) -> list[Path]:
        """
        Render audio narration for all sections.
        
        Args:
            content: Validated ContentOutput
            
        Returns:
            List of paths to generated audio files
        """
        audio_files = []
        
        # Queue all audio files first
        for idx, section in enumerate(content.sections):
            safe_title = section.title[:20].replace(' ', '_').replace('/', '_')
            output_file = self.output_dir / f"narration_{idx:02d}_{safe_title}.wav"
            script = section.script
            self.engine.save_to_file(script, str(output_file))
            audio_files.append(output_file)
        
        # Process all queued audio in one go
        try:
            self.engine.runAndWait()
            self.engine.stop()
        except Exception as e:
            print(f"Warning: Audio engine issue (files may still be created): {e}")
        
        return audio_files
    
    def render_section(self, section: Section, output_file: Path) -> Path:
        """
        Render a single section's script to an audio file.
        
        Args:
            section: Section with script
            output_file: Path to save the generated audio
            
        Returns:
            Path to the generated audio file
        """
        script = section.script
        
        # Use a fresh engine instance per section to avoid hanging on Windows
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.save_to_file(script, str(output_file))
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            # Fallback to instance engine if fresh init fails
            print(f"Warning: Using fallback engine for {output_file.name}: {e}")
            self.engine.save_to_file(script, str(output_file))
            # Don't call runAndWait here to avoid hanging
        
        return output_file
    
    def play_audio(self, audio_file: Path):
        """
        Play an audio file.
        
        Args:
            audio_file: Path to the audio file to play
        """
        try: 
            audio = AudioSegment.from_file(audio_file)
            play(audio)
        except ImportError:
            print("pydub not installed. Run: pip install pydub")
        except Exception as e:
            print(f"Error playing audio {audio_file}: {e}")
  
    
  
    
  