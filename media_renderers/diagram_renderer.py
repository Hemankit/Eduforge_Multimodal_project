"""
This module contains the diagram renderer that takes the structured content output and generates diagrams in SVG or matplotlib based on visual_plan.

Uses Mermaid syntax for diagram generation when mermaid_source is provided.
"""
from output_schema import ContentOutput, Section
from pathlib import Path
from typing import List, Literal
import subprocess
import json


class DiagramRenderer:
    """Generates diagrams from ContentOutput sections using Mermaid syntax."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the diagram renderer.
        
        Args:
            output_dir: Directory to save rendered diagrams
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def render(
        self, 
        content: ContentOutput, 
        format: Literal["svg", "png", "pdf"] = "svg"
    ) -> List[Path]:
        """
        Render diagrams for all sections with mermaid_source.
        
        Args:
            content: Validated ContentOutput
            format: Output format (svg, png, pdf)
            
        Returns:
            List of paths to generated diagram files
        """
        diagram_files = []
        
        for idx, section in enumerate(content.sections):
            if section.mermaid_source:
                output_file = self.output_dir / f"diagram_{idx:02d}_{section.title[:20].replace(' ', '_')}.{format}"
                self.render_mermaid(section.mermaid_source, output_file, format)
                diagram_files.append(output_file)
        
        return diagram_files
    
    def render_mermaid(
        self, 
        mermaid_source: str, 
        output_file: Path, 
        format: str = "svg"
    ) -> Path:
        """
        Render a Mermaid diagram to file using mermaid-cli (mmdc).
        
        Requires: npm install -g @mermaid-js/mermaid-cli
        
        Args:
            mermaid_source: Mermaid syntax string
            output_file: Path to save rendered diagram
            format: Output format (svg, png, pdf)
            
        Returns:
            Path to generated file
        """
        # Create temporary mermaid file
        temp_mmd = self.output_dir / "temp.mmd"
        temp_mmd.write_text(mermaid_source, encoding="utf-8")
        
        try:
            # Call mermaid-cli (mmdc)
            cmd = [
                "mmdc",
                "-i", str(temp_mmd),
                "-o", str(output_file),
                "-b", "transparent"  # Transparent background
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            return output_file
            
        except FileNotFoundError:
            # mermaid-cli not installed, fallback to online API rendering
            print("Warning: mermaid-cli (mmdc) not found. Falling back to Mermaid.ink API.")
            return self._render_mermaid_api(mermaid_source, output_file, format)
            
        except subprocess.CalledProcessError as e:
            print(f"Error rendering Mermaid diagram: {e.stderr}")
            # Fallback to API
            return self._render_mermaid_api(mermaid_source, output_file, format)
            
        finally:
            # Clean up temp file
            if temp_mmd.exists():
                temp_mmd.unlink()
    
    def _render_mermaid_api(self, mermaid_source: str, output_file: Path, format: str = "svg") -> Path:
        """
        Fallback: Use Mermaid.ink API to render diagram to SVG/PNG.
        
        Args:
            mermaid_source: Mermaid syntax string
            output_file: Path to save rendered diagram
            format: Output format (svg or png)
            
        Returns:
            Path to generated file
        """
        import urllib.request
        import urllib.parse
        import base64
        
        # Encode mermaid source for URL
        encoded = base64.urlsafe_b64encode(mermaid_source.encode('utf-8')).decode('ascii')
        
        # Use mermaid.ink API
        if format == "svg":
            url = f"https://mermaid.ink/svg/{encoded}"
        elif format == "png":
            url = f"https://mermaid.ink/img/{encoded}"
        else:
            # Default to SVG for other formats
            url = f"https://mermaid.ink/svg/{encoded}"
            output_file = output_file.with_suffix('.svg')
        
        try:
            # Download rendered diagram
            with urllib.request.urlopen(url) as response:
                content = response.read()
            
            output_file.write_bytes(content)
            print(f"Diagram rendered via API: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error rendering via API: {e}")
            # Last resort: save as HTML
            return self._render_mermaid_html(mermaid_source, output_file)
    
    def _render_mermaid_html(self, mermaid_source: str, output_file: Path) -> Path:
        """
        Last resort fallback: Generate HTML file with Mermaid diagram.
        
        Args:
            mermaid_source: Mermaid syntax string
            output_file: Base path (will save as .html)
            
        Returns:
            Path to generated HTML file
        """
        html_file = output_file.with_suffix('.html')
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .diagram-container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 1200px;
            width: 100%;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 300px;
        }}
        .loading {{
            color: #666;
            font-style: italic;
        }}
        .error {{
            color: #d32f2f;
            padding: 20px;
            background: #ffebee;
            border-radius: 4px;
            margin-top: 20px;
        }}
    </style>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{ 
                useMaxWidth: true,
                htmlLabels: true 
            }}
        }});
        
        window.addEventListener('load', function() {{
            console.log('Page loaded, Mermaid should initialize...');
        }});
        
        // Error handling
        window.addEventListener('error', function(e) {{
            console.error('Error loading diagram:', e);
            document.body.innerHTML += '<div class="error">Error: Could not render diagram. Check browser console for details.</div>';
        }});
    </script>
</head>
<body>
    <h1>Gradient Descent Flowchart</h1>
    <div class="diagram-container">
        <div class="mermaid">
{mermaid_source}
        </div>
    </div>
    <div class="loading" id="loading-msg" style="margin-top: 10px;">
        <small>If diagram doesn't appear, try refreshing the page or check if JavaScript is enabled.</small>
    </div>
</body>
</html>"""
        
        html_file.write_text(html_content, encoding="utf-8")
        print(f"Diagram saved as HTML (last resort): {html_file}")
        return html_file
    
    def validate_mermaid_syntax(self, mermaid_source: str) -> bool:
        """
        Basic validation of Mermaid syntax.
        
        Args:
            mermaid_source: Mermaid syntax to validate
            
        Returns:
            True if syntax appears valid
        """
        # Basic checks
        if not mermaid_source.strip():
            return False
        
        # Check for common diagram types
        valid_prefixes = [
            "flowchart", "graph", "sequenceDiagram", "classDiagram",
            "stateDiagram", "erDiagram", "gantt", "pie", "timeline"
        ]
        
        first_line = mermaid_source.strip().split('\n')[0].strip()
        return any(first_line.startswith(prefix) for prefix in valid_prefixes)
