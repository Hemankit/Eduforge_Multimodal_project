"""
Media rendering modules for converting educational content into various formats.
"""

# Use lazy imports to avoid dependency errors when only using one renderer
__all__ = ["SlideRenderer", "DiagramRenderer", "AudioRenderer"]

def __getattr__(name):
    """Lazy load renderers to avoid importing all dependencies at once."""
    if name == "SlideRenderer":
        from .slide_renderer import SlideRenderer
        return SlideRenderer
    elif name == "DiagramRenderer":
        from .diagram_renderer import DiagramRenderer
        return DiagramRenderer
    elif name == "AudioRenderer":
        from .audio_renderer import AudioRenderer
        return AudioRenderer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
