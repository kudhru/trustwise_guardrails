"""
Base classes for guardrails implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..utils.result import GuardrailResult


class BaseGuardrail(ABC):
    """Base class for all guardrails."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
    
    def is_enabled(self) -> bool:
        """Check if this guardrail is enabled."""
        return self.enabled
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})"


class InputGuardrail(BaseGuardrail):
    """Base class for input guardrails that validate/filter user input."""
    
    @abstractmethod
    def validate(self, input_text: str, metadata: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Validate and potentially modify input text.
        
        Args:
            input_text: The user's input text to validate
            metadata: Optional metadata about the request (user_id, session_id, etc.)
        
        Returns:
            GuardrailResult: Result of the validation with status and potentially modified content
        """
        pass


class OutputGuardrail(BaseGuardrail):
    """Base class for output guardrails that filter/modify agent responses."""
    
    @abstractmethod
    def filter(self, output_text: str, input_text: str = "", metadata: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Filter and potentially modify output text.
        
        Args:
            output_text: The agent's response text to filter
            input_text: The original user input (for context)
            metadata: Optional metadata about the request
        
        Returns:
            GuardrailResult: Result of the filtering with status and potentially modified content
        """
        pass 