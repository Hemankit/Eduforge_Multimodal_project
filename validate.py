"""
Validation utilities for input and output schemas
"""
from typing import Dict, Any, Tuple
from pydantic import ValidationError
from input_schema import ContentInput
from output_schema import ContentOutput
import json


class ValidationResult:
  """Result of a validation operation"""
  def __init__(self, is_valid: bool, data: Any = None, errors: list = None):
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or []

  def __repr__(self) -> str:
    """string representation of the validation result"""
    if self.is_valid:
        return f"ValidationResult(valid=True)"
    return f"ValidationResult(valid=False, errors={len(self.errors)})"


class SchemaValidator:
  """Validator for input and output schemas"""
  
  @staticmethod
  def validate_input(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate input data against ContentInput schema.
    
    Args:
        data: Dictionary containing input data
        
    Returns:
        ValidationResult with validated ContentInput or errors
    """
    try:
        validated = ContentInput.model_validate(data)
        return ValidationResult(is_valid=True, data=validated)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return ValidationResult(is_valid=False, errors=errors)

  def validate_output(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate output data against ContentOutput schema.
    
    Args:
        data: Dictionary containing output data
        
    Returns:
        ValidationResult with validated ContentOutput or errors
    """
    try:
        validated = ContentOutput.model_validate(data)
        return ValidationResult(is_valid=True, data=validated)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return ValidationResult(is_valid=False, errors=errors)
  
  def validate_duration_constraint(
    output: ContentOutput, 
    max_duration: int
) -> Tuple[bool, str]:
    """
    Check if output respects the duration constraint.
    
    Args:
        output: Validated ContentOutput
        max_duration: Maximum allowed duration in seconds
        
    Returns:
        Tuple of (is_valid, message)
    """
    total = output.total_duration_sec
    if total <= max_duration:
        return True, f"Duration {total}s is within limit of {max_duration}s"
    else:
        overage = total - max_duration
        return False, f"Duration {total}s exceeds limit by {overage}s"
    
  # Load JSON file consisting of data from input or output and validate against schema
  def load_and_validate_json(filepath: str, schema_type: str) -> ValidationResult:
    """
    Load JSON file and validate against specified schema.
    
    Args:
        filepath: Path to JSON file
        schema_type: Either 'input' or 'output'
        
    Returns:
        ValidationResult with validated data or errors
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if schema_type == 'input':
            return validate_input(data)
        elif schema_type == 'output':
            return validate_output(data)
        else:
            return ValidationResult(
                is_valid=False, 
                errors=[f"Unknown schema_type: {schema_type}"]
            )
    except FileNotFoundError:
        return ValidationResult(
            is_valid=False,
            errors=[f"File not found: {filepath}"]
        )
    except json.JSONDecodeError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Invalid JSON: {e}"]
        )
    
  # Example usage:
if __name__ == "__main__":
    print("=== Testing Input Validation ===")
    
    # Valid input
    valid_input = {
        "topic": "Neural Networks",
        "audience": "intermediate",
        "constraints": {
            "max_duration_sec": 180,
            "examples": 2
        }
    }
    result = validate_input(valid_input)
    print(f"Valid input: {result}")
    
    # Invalid input
    invalid_input = {
        "topic": "",  # Empty topic
        "audience": "expert",  # Invalid audience
        "constraints": {
            "max_duration_sec": 5,  # Too short
            "examples": 10  # Too many
        }
    }
    result = validate_input(invalid_input)
    print(f"\nInvalid input: {result}")
    if not result.is_valid:
        for error in result.errors:
            print(f"  - {error}")
    
    print("\n=== Testing Output Validation ===")
    
    # Valid output
    valid_output = {
        "learning_objectives": [
            "Understand the architecture of neural networks",
            "Implement forward propagation"
        ],
        "sections": [
            {
                "title": "Introduction to Neural Networks",
                "script": "Neural networks are computational models inspired by biological neurons. They consist of interconnected layers that transform input data into predictions.",
                "visual_plan": "Diagram showing input layer, hidden layers, and output layer",
                "duration_sec": 60
            }
        ]
    }
    result = validate_output(valid_output)
    print(f"Valid output: {result}")
    if result.is_valid:
        print(f"  Total duration: {result.data.total_duration_sec}s")
        
        # Test duration constraint
        is_valid, msg = validate_duration_constraint(result.data, max_duration=120)
        print(f"  Duration check: {msg}")

    # Invalid output (will raise validation error)
    try:
        invalid_output = {
            "learning_objectives": ["Too short"],  # Objective too short
            "sections": []  # Empty sections
        }
        ContentOutput.model_validate(invalid_output)
    except Exception as e:
        print("\n✗ Invalid output caught:")
        print(f"  {e}")