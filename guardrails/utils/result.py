"""
Result classes for guardrail operations.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class GuardrailStatus(Enum):
    """Status of a guardrail check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class GuardrailResult:
    """Result of a guardrail operation."""
    status: GuardrailStatus
    message: str
    modified_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    
    @property
    def is_success(self) -> bool:
        """Check if the guardrail check was successful."""
        return self.status == GuardrailStatus.PASSED
    
    @property
    def is_failure(self) -> bool:
        """Check if the guardrail check failed."""
        return self.status in [GuardrailStatus.FAILED, GuardrailStatus.BLOCKED]
    
    @property
    def content(self) -> str:
        """Get the content (modified if available, original otherwise)."""
        return self.modified_content if self.modified_content is not None else ""
    
    def __str__(self) -> str:
        return f"GuardrailResult(status={self.status.value}, message='{self.message}')" 