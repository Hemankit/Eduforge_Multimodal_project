"""
Test to verify Mermaid diagram syntax and provide alternative viewing options.
"""
from few_shot_examples import FEW_SHOT_EXAMPLES
from output_schema import ContentOutput

# Load the example with Mermaid diagram
example = FEW_SHOT_EXAMPLES[0]
content = ContentOutput.model_validate(example["output"])

print("=" * 70)
print("MERMAID DIAGRAM SYNTAX VERIFICATION")
print("=" * 70)

for idx, section in enumerate(content.sections):
    if section.mermaid_source:
        print(f"\n[Section {idx}] {section.title}")
        print(f"Diagram Type: {section.diagram_type}")
        print(f"\nMermaid Syntax ({len(section.mermaid_source)} characters):")
        print("-" * 70)
        print(section.mermaid_source)
        print("-" * 70)
        
        print("\n✅ Alternative viewing options:")
        print(f"   1. Open: test_output/diagram_{idx:02d}_{section.title[:20].replace(' ', '_')}.html")
        print(f"   2. Copy the syntax above and paste into: https://mermaid.live/")
        print(f"   3. Install mermaid-cli: npm install -g @mermaid-js/mermaid-cli")
        print(f"      Then run: mmdc -i diagram.mmd -o diagram.svg")

print("\n" + "=" * 70)
