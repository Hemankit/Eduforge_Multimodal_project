"""
Cross-model validation between ContentInput and ContentOutput.
Validates that generated output respects input constraints and maintains logical consistency.
"""
from input_schema import ContentInput
from output_schema import ContentOutput
from typing import List, Tuple
import warnings


class CrossValidator:
    """Validates ContentOutput against ContentInput constraints."""
    
    @staticmethod
    def validate(input_data: ContentInput, output_data: ContentOutput) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive cross-model validation.
        
        Args:
            input_data: Validated ContentInput with constraints
            output_data: Generated ContentOutput
            
        Returns:
            Tuple of (is_valid, list of error/warning messages)
        """
        errors = []
        warnings_list = []
        
        # 1. Check total duration constraint
        max_duration = input_data.constraints.max_duration_sec
        if output_data.total_duration_sec > max_duration:
            errors.append(
                f"Total duration {output_data.total_duration_sec}s exceeds "
                f"max_duration_sec constraint of {max_duration}s"
            )
        elif output_data.total_duration_sec < max_duration * 0.5:
            warnings_list.append(
                f"Total duration {output_data.total_duration_sec}s is significantly "
                f"under the max_duration_sec constraint of {max_duration}s. Consider adding more content."
            )
        
        # 2. Check individual section durations (no single section should be > 50% of total)
        section_limit = max_duration * 0.5
        for idx, section in enumerate(output_data.sections):
            if section.duration_sec > section_limit:
                warnings_list.append(
                    f"Section {idx} '{section.title}' duration ({section.duration_sec}s) is very long. "
                    f"Consider splitting into multiple sections."
                )
        
        # 3. Validate example count if specified
        if input_data.constraints.examples:
            requested_examples = input_data.constraints.examples
            # Count mentions of "example" or "for example" in scripts (rough heuristic)
            example_count = sum(
                script.lower().count("example") + script.lower().count("for instance")
                for script in [s.script for s in output_data.sections]
            )
            
            if example_count < requested_examples:
                warnings_list.append(
                    f"Requested {requested_examples} examples but only found ~{example_count} "
                    f"example mentions in scripts. Content may lack sufficient examples."
                )
        
        # 4. Check visual style alignment
        visual_style = input_data.constraints.visual_style
        if visual_style == "minimal":
            # Expect shorter visual plans
            for section in output_data.sections:
                if len(section.visual_plan) > 200:
                    warnings_list.append(
                        f"Section '{section.title}' has detailed visual_plan ({len(section.visual_plan)} chars) "
                        f"but 'minimal' visual_style was requested."
                    )
        elif visual_style == "detailed":
            # Expect longer, detailed visual plans
            for section in output_data.sections:
                if len(section.visual_plan) < 50:
                    warnings_list.append(
                        f"Section '{section.title}' has brief visual_plan ({len(section.visual_plan)} chars) "
                        f"but 'detailed' visual_style was requested."
                    )
        
        # 5. Check diagram requirements for diagram format
        if input_data.constraints.render_formats and "diagrams" in input_data.constraints.render_formats:
            sections_with_diagrams = sum(1 for s in output_data.sections if s.mermaid_source)
            if sections_with_diagrams == 0:
                errors.append(
                    "Diagrams format was requested but no sections have mermaid_source defined."
                )
            elif sections_with_diagrams < len(output_data.sections) * 0.5:
                warnings_list.append(
                    f"Only {sections_with_diagrams}/{len(output_data.sections)} sections have diagrams. "
                    f"Consider adding more visual diagrams."
                )
        
        # 6. Validate learning objectives coverage (basic keyword matching)
        objective_keywords = set()
        for obj in output_data.learning_objectives:
            # Extract key terms (rough heuristic: words > 4 chars)
            keywords = [word.lower() for word in obj.split() if len(word) > 4]
            objective_keywords.update(keywords)
        
        all_scripts = " ".join(s.script.lower() for s in output_data.sections)
        uncovered_keywords = [kw for kw in objective_keywords if kw not in all_scripts]
        
        if uncovered_keywords:
            warnings_list.append(
                f"Learning objective keywords not found in content: {', '.join(uncovered_keywords[:5])}. "
                f"Ensure all objectives are addressed."
            )
        
        # 7. Check audience alignment (basic check)
        audience = input_data.audience
        all_content = " ".join(s.script for s in output_data.sections).lower()
        
        if audience == "beginner":
            # Check for overly complex terms (rough heuristic)
            complex_terms = ["algorithm", "optimization", "asymptotic", "polynomial", "exponential"]
            found_complex = [term for term in complex_terms if term in all_content]
            if found_complex and len(found_complex) > 3:
                warnings_list.append(
                    f"Content for 'beginner' audience contains many advanced terms: {', '.join(found_complex[:3])}. "
                    f"Ensure they are properly explained."
                )
        
        # Print warnings
        for warning in warnings_list:
            warnings.warn(warning, UserWarning)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def validate_and_raise(input_data: ContentInput, output_data: ContentOutput):
        """
        Perform validation and raise exception if errors found.
        
        Args:
            input_data: Validated ContentInput
            output_data: Generated ContentOutput
            
        Raises:
            ValueError: If validation fails
        """
        is_valid, errors = CrossValidator.validate(input_data, output_data)
        if not is_valid:
            error_msg = "Cross-validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            raise ValueError(error_msg)


# Example usage
if __name__ == "__main__":
    from input_schema import ContentInput
    from output_schema import ContentOutput
    
    # Create sample input
    input_data = ContentInput.model_validate({
        "topic": "Binary Search",
        "audience": "beginner",
        "constraints": {
            "max_duration_sec": 120,
            "examples": 2,
            "visual_style": "detailed",
            "render_formats": ["diagrams"]
        }
    })
    
    # Create sample output
    output_data = ContentOutput.model_validate({
        "learning_objectives": [
            "Understand how binary search works",
            "Implement binary search algorithm"
        ],
        "sections": [
            {
                "title": "Introduction to Binary Search",
                "script": "Binary search is an efficient algorithm for finding an item in a sorted list. For example, imagine looking up a word in a dictionary. You don't start from page 1; you open somewhere in the middle and decide whether to look left or right based on alphabetical order.",
                "visual_plan": "Show a sorted array with pointers indicating left, middle, and right positions. Animate the search process step by step.",
                "duration_sec": 60,
                "diagram_type": "flowchart",
                "mermaid_source": "flowchart TD\nA[Start] --> B[Find middle]\nB --> C{Target found?}\nC -->|Yes| D[Return]\nC -->|No| E{Target < middle?}"
            }
        ]
    })
    
    # Validate
    is_valid, errors = CrossValidator.validate(input_data, output_data)
    print(f"Validation result: {'✓ Valid' if is_valid else '✗ Invalid'}")
    if errors:
        for error in errors:
            print(f"  ERROR: {error}")
