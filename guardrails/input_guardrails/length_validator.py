"""
Length Validator Guardrail - Validates input text length.
"""

from typing import Dict, Any, Optional
from ..core.base import InputGuardrail
from ..utils.result import GuardrailResult, GuardrailStatus


class LengthValidatorGuardrail(InputGuardrail):
    """
    Validates the length of input text.
    
    This guardrail checks if the input text meets minimum and maximum
    length requirements and can optionally truncate text that's too long.
    """
    
    def __init__(self, name: str = "length_validator", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the length validator guardrail.
        
        Args:
            name: Name of the guardrail
            config: Configuration dictionary with options:
                - min_length: Minimum allowed length (default: 1)
                - max_length: Maximum allowed length (default: 10000)
                - truncate: Whether to truncate long text (default: False)
                - truncate_suffix: Suffix to add when truncating (default: "...")
        """
        super().__init__(name, config)
        
        # Configuration
        self.min_length = self.config.get("min_length", 1)
        self.max_length = self.config.get("max_length", 10000)
        self.truncate = self.config.get("truncate", False)
        self.truncate_suffix = self.config.get("truncate_suffix", "...")
        
        # Validation
        if self.min_length < 0:
            raise ValueError("min_length must be >= 0")
        if self.max_length <= 0:
            raise ValueError("max_length must be > 0")
        if self.min_length > self.max_length:
            raise ValueError("min_length must be <= max_length")
    
    def validate(self, input_text: str, metadata: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Validate the length of the input text.
        
        Args:
            input_text: The user's input text to validate
            metadata: Optional metadata about the request
            
        Returns:
            GuardrailResult: Result of the validation
        """
        if input_text is None:
            return GuardrailResult(
                status=GuardrailStatus.FAILED,
                message="Input text is None"
            )
        
        text_length = len(input_text.strip())
        
        # Check minimum length
        if text_length < self.min_length:
            return GuardrailResult(
                status=GuardrailStatus.FAILED,
                message=f"Input too short: {text_length} chars (minimum: {self.min_length})",
                metadata={"original_length": text_length, "min_length": self.min_length}
            )
        
        # Check maximum length
        if text_length > self.max_length:
            if self.truncate:
                # Truncate the text
                max_content_length = self.max_length - len(self.truncate_suffix)
                if max_content_length > 0:
                    truncated_text = input_text[:max_content_length] + self.truncate_suffix
                    return GuardrailResult(
                        status=GuardrailStatus.WARNING,
                        message=f"Input truncated: {text_length} -> {len(truncated_text)} chars",
                        modified_content=truncated_text,
                        metadata={
                            "original_length": text_length,
                            "truncated_length": len(truncated_text),
                            "max_length": self.max_length,
                            "truncated": True
                        }
                    )
                else:
                    return GuardrailResult(
                        status=GuardrailStatus.FAILED,
                        message=f"Input too long and cannot be truncated safely: {text_length} chars"
                    )
            else:
                return GuardrailResult(
                    status=GuardrailStatus.FAILED,
                    message=f"Input too long: {text_length} chars (maximum: {self.max_length})",
                    metadata={"original_length": text_length, "max_length": self.max_length}
                )
        
        # All checks passed
        return GuardrailResult(
            status=GuardrailStatus.PASSED,
            message=f"Length validation passed: {text_length} chars",
            modified_content=input_text,
            metadata={"length": text_length}
        ) 