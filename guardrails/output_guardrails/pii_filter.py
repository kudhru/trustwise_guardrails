"""
PII Filter Guardrail - Detects and masks personally identifiable information.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from ..core.base import OutputGuardrail
from ..utils.result import GuardrailResult, GuardrailStatus


class PIIFilterGuardrail(OutputGuardrail):
    """
    Detects and masks personally identifiable information (PII) in agent responses.
    
    This guardrail uses regex patterns to detect common PII types like email addresses,
    phone numbers, and credit card numbers, and replaces them with masked versions.
    """
    
    def __init__(self, name: str = "pii_filter", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PII filter guardrail.
        
        Args:
            name: Name of the guardrail
            config: Configuration dictionary with options:
                - mask_emails: Whether to mask email addresses (default: True)
                - mask_phones: Whether to mask phone numbers (default: True)
                - mask_credit_cards: Whether to mask credit card numbers (default: True)
                - mask_ssn: Whether to mask social security numbers (default: True)
                - replacement: Replacement text for PII (default: "[REDACTED]")
                - strict_mode: If True, block responses with PII instead of masking (default: False)
        """
        super().__init__(name, config)
        
        # Configuration
        self.mask_emails = self.config.get("mask_emails", True)
        self.mask_phones = self.config.get("mask_phones", True)
        self.mask_credit_cards = self.config.get("mask_credit_cards", True)
        self.mask_ssn = self.config.get("mask_ssn", True)
        self.replacement = self.config.get("replacement", "[REDACTED]")
        self.strict_mode = self.config.get("strict_mode", False)
        
        # Regex patterns for PII detection
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[Tuple[str, re.Pattern, str]]:
        """
        Build regex patterns for PII detection.
        
        Returns:
            List of tuples: (pii_type, compiled_pattern, description)
        """
        patterns = []
        
        if self.mask_emails:
            # Email pattern
            email_pattern = re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                re.IGNORECASE
            )
            patterns.append(("email", email_pattern, "Email address"))
        
        if self.mask_phones:
            # Phone number patterns (US format)
            phone_patterns = [
                re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),  # 123-456-7890
                re.compile(r'\b\(\d{3}\)\s*\d{3}-\d{4}\b'),  # (123) 456-7890
                re.compile(r'\b\d{3}\.\d{3}\.\d{4}\b'),  # 123.456.7890
                re.compile(r'\b\d{10}\b'),  # 1234567890
            ]
            for i, pattern in enumerate(phone_patterns):
                patterns.append(("phone", pattern, f"Phone number (format {i+1})"))
        
        if self.mask_credit_cards:
            # Credit card pattern (basic)
            cc_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
            patterns.append(("credit_card", cc_pattern, "Credit card number"))
        
        if self.mask_ssn:
            # Social Security Number patterns
            ssn_patterns = [
                re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # 123-45-6789
                re.compile(r'\b\d{9}\b'),  # 123456789 (only if isolated)
            ]
            for i, pattern in enumerate(ssn_patterns):
                patterns.append(("ssn", pattern, f"Social Security Number (format {i+1})"))
        
        return patterns
    
    def _detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII instances in the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dictionaries with PII detection information
        """
        detections = []
        
        for pii_type, pattern, description in self.patterns:
            matches = pattern.finditer(text)
            for match in matches:
                detections.append({
                    "type": pii_type,
                    "description": description,
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return detections
    
    def _mask_pii(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """
        Mask PII in the text.
        
        Args:
            text: Original text
            detections: List of PII detections
            
        Returns:
            Text with PII masked
        """
        # Sort detections by position (reverse order to maintain indices)
        sorted_detections = sorted(detections, key=lambda x: x["start"], reverse=True)
        
        masked_text = text
        for detection in sorted_detections:
            start, end = detection["start"], detection["end"]
            masked_text = masked_text[:start] + self.replacement + masked_text[end:]
        
        return masked_text
    
    def filter(self, output_text: str, input_text: str = "", metadata: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Filter PII from the output text.
        
        Args:
            output_text: The agent's response text to filter
            input_text: The original user input (for context)
            metadata: Optional metadata about the request
            
        Returns:
            GuardrailResult: Result of the filtering
        """
        if output_text is None:
            return GuardrailResult(
                status=GuardrailStatus.FAILED,
                message="Output text is None"
            )
        
        # Detect PII in the output
        detections = self._detect_pii(output_text)
        
        if not detections:
            # No PII detected
            return GuardrailResult(
                status=GuardrailStatus.PASSED,
                message="No PII detected in output",
                modified_content=output_text,
                metadata={"pii_detected": False, "pii_count": 0}
            )
        
        # PII detected
        pii_types = list(set(d["type"] for d in detections))
        pii_summary = {pii_type: len([d for d in detections if d["type"] == pii_type]) 
                      for pii_type in pii_types}
        
        if self.strict_mode:
            # Block the response entirely
            return GuardrailResult(
                status=GuardrailStatus.BLOCKED,
                message=f"Response blocked due to PII detection: {', '.join(pii_types)}",
                metadata={
                    "pii_detected": True,
                    "pii_count": len(detections),
                    "pii_types": pii_types,
                    "pii_summary": pii_summary,
                    "detections": detections
                }
            )
        else:
            # Mask the PII
            masked_text = self._mask_pii(output_text, detections)
            
            return GuardrailResult(
                status=GuardrailStatus.WARNING,
                message=f"PII masked in output: {len(detections)} instances of {', '.join(pii_types)}",
                modified_content=masked_text,
                metadata={
                    "pii_detected": True,
                    "pii_count": len(detections),
                    "pii_types": pii_types,
                    "pii_summary": pii_summary,
                    "detections": detections,
                    "masked": True
                }
            ) 