"""
Guardrails Engine - Central controller for managing guardrails.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from .base import InputGuardrail, OutputGuardrail
from .wrapper import GuardedAgent
from .adapters import create_adapter, AgentAdapter
from ..utils.result import GuardrailResult, GuardrailStatus

logger = logging.getLogger(__name__)


class GuardrailsEngine:
    """
    Central engine for managing and executing guardrails.
    
    The engine maintains lists of input and output guardrails and provides
    methods to wrap agents with guardrails protection.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the guardrails engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.input_guardrails: List[InputGuardrail] = []
        self.output_guardrails: List[OutputGuardrail] = []
        self.enabled = self.config.get("enabled", True)
        self.fail_fast = self.config.get("fail_fast", True)
        self.logging_enabled = self.config.get("logging", True)
        
        if self.logging_enabled:
            logging.basicConfig(level=logging.INFO)
    
    def add_input_guardrail(self, guardrail: InputGuardrail) -> 'GuardrailsEngine':
        """
        Add an input guardrail to the engine.
        
        Args:
            guardrail: InputGuardrail instance to add
            
        Returns:
            Self for method chaining
        """
        self.input_guardrails.append(guardrail)
        logger.info(f"Added input guardrail: {guardrail}")
        return self
    
    def add_output_guardrail(self, guardrail: OutputGuardrail) -> 'GuardrailsEngine':
        """
        Add an output guardrail to the engine.
        
        Args:
            guardrail: OutputGuardrail instance to add
            
        Returns:
            Self for method chaining
        """
        self.output_guardrails.append(guardrail)
        logger.info(f"Added output guardrail: {guardrail}")
        return self
    
    def apply_input_guardrails(self, input_text: str, metadata: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Apply all input guardrails to the input text.
        
        Args:
            input_text: The user's input text
            metadata: Optional metadata about the request
            
        Returns:
            GuardrailResult: Combined result of all input guardrails
        """
        if not self.enabled:
            return GuardrailResult(
                status=GuardrailStatus.PASSED,
                message="Guardrails engine disabled",
                modified_content=input_text
            )
        
        current_text = input_text
        combined_metadata = {}
        messages = []
        has_failures = False
        
        for guardrail in self.input_guardrails:
            if not guardrail.is_enabled():
                continue
                
            try:
                result = guardrail.validate(current_text, metadata)
                
                if result.is_failure:
                    has_failures = True
                    logger.warning(f"Input guardrail {guardrail.name} failed: {result.message}")
                    if self.fail_fast:
                        return result
                    messages.append(f"{guardrail.name}: {result.message}")
                else:
                    # Use modified content if available
                    if result.modified_content is not None:
                        current_text = result.modified_content
                    
                    # Collect metadata
                    if result.metadata:
                        combined_metadata.update(result.metadata)
                    
                    messages.append(f"{guardrail.name}: {result.message}")
                    
            except Exception as e:
                has_failures = True
                error_msg = f"Error in input guardrail {guardrail.name}: {str(e)}"
                logger.error(error_msg)
                if self.fail_fast:
                    return GuardrailResult(
                        status=GuardrailStatus.FAILED,
                        message=error_msg
                    )
                messages.append(error_msg)
        
        # Return appropriate status based on whether any guardrails failed
        final_status = GuardrailStatus.FAILED if has_failures else GuardrailStatus.PASSED
        final_message = "; ".join(messages) if messages else "All input guardrails passed"
        
        return GuardrailResult(
            status=final_status,
            message=final_message,
            modified_content=current_text,
            metadata=combined_metadata
        )
    
    def apply_output_guardrails(self, output_text: str, input_text: str = "", metadata: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Apply all output guardrails to the output text.
        
        Args:
            output_text: The agent's response text
            input_text: The original user input
            metadata: Optional metadata about the request
            
        Returns:
            GuardrailResult: Combined result of all output guardrails
        """
        if not self.enabled:
            return GuardrailResult(
                status=GuardrailStatus.PASSED,
                message="Guardrails engine disabled",
                modified_content=output_text
            )
        
        current_text = output_text
        combined_metadata = {}
        messages = []
        has_failures = False
        
        for guardrail in self.output_guardrails:
            if not guardrail.is_enabled():
                continue
                
            try:
                result = guardrail.filter(current_text, input_text, metadata)
                
                if result.is_failure:
                    has_failures = True
                    logger.warning(f"Output guardrail {guardrail.name} failed: {result.message}")
                    if self.fail_fast:
                        return result
                    messages.append(f"{guardrail.name}: {result.message}")
                else:
                    # Use modified content if available
                    if result.modified_content is not None:
                        current_text = result.modified_content
                    
                    # Collect metadata
                    if result.metadata:
                        combined_metadata.update(result.metadata)
                    
                    messages.append(f"{guardrail.name}: {result.message}")
                    
            except Exception as e:
                has_failures = True
                error_msg = f"Error in output guardrail {guardrail.name}: {str(e)}"
                logger.error(error_msg)
                if self.fail_fast:
                    return GuardrailResult(
                        status=GuardrailStatus.FAILED,
                        message=error_msg
                    )
                messages.append(error_msg)
        
        # Return appropriate status based on whether any guardrails failed
        final_status = GuardrailStatus.FAILED if has_failures else GuardrailStatus.PASSED
        final_message = "; ".join(messages) if messages else "All output guardrails passed"
        
        return GuardrailResult(
            status=final_status,
            message=final_message,
            modified_content=current_text,
            metadata=combined_metadata
        )
    
    def wrap_agent(self, agent: Any, adapter_type: Optional[str] = None, adapter_config: Optional[Dict[str, Any]] = None) -> GuardedAgent:
        """
        Wrap an agent with guardrails protection.
        
        Args:
            agent: Any agent object
            adapter_type: Type of adapter to use ('chat', 'invoke', 'run', 'callable', 'custom', etc.)
                         If None, will auto-detect the interface
            adapter_config: Configuration for the adapter
            
        Returns:
            GuardedAgent: Wrapped agent with guardrails
        """
        # Create an adapter to normalize the agent interface
        try:
            adapter = create_adapter(agent, adapter_type, adapter_config)
            logger.info(f"Successfully created adapter for agent: {type(agent).__name__}")
        except Exception as e:
            logger.error(f"Failed to create adapter for agent {type(agent).__name__}: {e}")
            raise ValueError(f"Unable to wrap agent: {e}")
        
        return GuardedAgent(adapter, self)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current guardrails configuration.
        
        Returns:
            Dictionary with guardrails statistics
        """
        return {
            "enabled": self.enabled,
            "input_guardrails": len(self.input_guardrails),
            "output_guardrails": len(self.output_guardrails),
            "total_guardrails": len(self.input_guardrails) + len(self.output_guardrails),
            "fail_fast": self.fail_fast,
            "input_guardrails_list": [str(g) for g in self.input_guardrails],
            "output_guardrails_list": [str(g) for g in self.output_guardrails]
        }
    
    def __str__(self) -> str:
        stats = self.get_stats()
        return f"GuardrailsEngine(enabled={stats['enabled']}, total_guardrails={stats['total_guardrails']})" 