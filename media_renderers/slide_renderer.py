"""
This module contains the slide renderer that takes the structured content output and generates slide decks in HTML format.
"""
from __future__ import annotations
from output_schema import ContentOutput, Section

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class SlideRenderer:
    """Generates slide decks from ContentOutput sections using custom templates."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the slide renderer.
        
        Args:
            output_dir: Directory to save rendered slides
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load templates from templates/ folder
        templates_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(searchpath=str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render(self, content: ContentOutput, format: str = "html") -> Path:
        """
        Render slides deck from content to HTML.
        
        Args:
            content: Validated ContentOutput
            format: Output format (only "html" supported)
            
        Returns:
            Path to generated slide file
        """
        # Convert sections to slide format expected by template
        slides = [self.section_to_slide_model(section) for section in content.sections]
        
        # Build deck context for template
        deck_context = {
            "learning_objectives": content.learning_objectives,
            "total_duration_sec": content.total_duration_sec,
            "slides": slides,
            "prerequisites": getattr(content, "prerequisites", None)
        }
        
        # Render using deck.html.j2 template
        tpl = self.env.get_template("deck.html.j2")
        html = tpl.render(deck=deck_context)
        
        # Save to file
        output_file = self.output_dir / "slides.html"
        output_file.write_text(html, encoding="utf-8")
        
        return output_file
    
    def section_to_slide_model(self, section: Section) -> Dict[str, Any]:
        """
        Convert a Section to slide data model expected by template.
        
        Template expects: layout, title, bullets, visual_plan, diagram_type,
        key_terms, duration_sec, audio_emphasis, visual_priority
        """
        # Convert script to bullets (split by sentences or newlines)
        bullets = []
        if section.script:
            # Split script into bullet points (by periods or newlines)
            sentences = section.script.replace('\n', '. ').split('. ')
            bullets = [s.strip() for s in sentences if s.strip()][:5]  # Max 5 bullets
        
        return {
            "layout": section.slide_layout or "content",
            "title": section.title,
            "bullets": bullets,
            "visual_plan": section.visual_plan,
            "diagram_type": section.diagram_type,
            "key_terms": section.key_terms or [],
            "duration_sec": section.duration_sec,
            "audio_emphasis": section.audio_emphasis or [],
            "visual_priority": section.visual_priority or "medium"
        }
