"""
Guarded Agent - Wrapper that adds guardrails to any agent.
"""

import logging
from typing import Any, Dict, Optional
from ..utils.result import GuardrailStatus

logger = logging.getLogger(__name__)


class GuardedAgent:
    """
    A wrapper that adds guardrails protection to any agent.
    
    This class wraps an agent (via an adapter) and applies input/output guardrails
    without requiring any changes to the original agent code.
    """
    
    def __init__(self, agent_or_adapter: Any, guardrails_engine: 'GuardrailsEngine'):
        """
        Initialize the guarded agent.
        
        Args:
            agent_or_adapter: The agent adapter that normalizes the agent interface
            guardrails_engine: The guardrails engine to use for protection
        """
        self.agent = agent_or_adapter
        self.engine = guardrails_engine
        
        # The adapter should always have a chat method
        if not hasattr(self.agent, 'chat'):
            raise ValueError("Agent adapter must have a 'chat' method")
    
    def chat(self, user_input: str, **kwargs) -> str:
        """
        Chat with the agent while applying guardrails.
        
        Args:
            user_input: The user's input text
            **kwargs: Additional arguments passed to the original agent
            
        Returns:
            str: The agent's response (potentially modified by output guardrails)
            
        Raises:
            ValueError: If input is blocked by guardrails
            RuntimeError: If output is blocked by guardrails
        """
        # Extract metadata for guardrails
        metadata = {
            "kwargs": kwargs,
            "agent_type": type(self.agent).__name__,
            "original_agent_type": type(getattr(self.agent, 'agent', self.agent)).__name__
        }
        
        # Apply input guardrails
        logger.info(f"Applying input guardrails to: '{user_input[:50]}...'")
        input_result = self.engine.apply_input_guardrails(user_input, metadata)
        
        if input_result.is_failure:
            error_msg = f"Input blocked by guardrails: {input_result.message}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Use the potentially modified input
        processed_input = input_result.content or user_input
        
        if input_result.modified_content:
            logger.info(f"Input modified by guardrails: '{processed_input[:50]}...'")
        
        try:
            # Call the agent through the adapter
            logger.info(f"Calling agent via adapter: {type(self.agent).__name__}")
            agent_response = self.agent.chat(processed_input, **kwargs)
            
            # Apply output guardrails
            logger.info(f"Applying output guardrails to response: '{agent_response[:50]}...'")
            output_result = self.engine.apply_output_guardrails(
                agent_response, 
                user_input,  # Pass original input for context
                metadata
            )
            
            if output_result.is_failure:
                error_msg = f"Output blocked by guardrails: {output_result.message}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Return the potentially modified output
            final_response = output_result.content or agent_response
            
            if output_result.modified_content:
                logger.info(f"Output modified by guardrails: '{final_response[:50]}...'")
            
            return final_response
            
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                # Re-raise guardrail errors
                raise
            else:
                # Log and re-raise agent errors
                logger.error(f"Agent error: {str(e)}")
                raise RuntimeError(f"Agent execution failed: {str(e)}")
    
    def get_guardrails_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the guardrails protecting this agent.
        
        Returns:
            Dictionary with guardrails statistics
        """
        stats = self.engine.get_stats()
        stats["wrapped_agent_type"] = type(self.agent).__name__
        if hasattr(self.agent, 'agent'):
            stats["original_agent_type"] = type(self.agent.agent).__name__
        return stats
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the wrapped agent for other methods.
        
        This allows the GuardedAgent to act as a transparent proxy for
        methods other than 'chat'.
        """
        if name == 'chat':
            return self.chat
        return getattr(self.agent, name)
    
    def __str__(self) -> str:
        adapter_type = type(self.agent).__name__
        original_type = type(getattr(self.agent, 'agent', self.agent)).__name__
        return f"GuardedAgent(adapter={adapter_type}, original_agent={original_type}, guardrails={self.engine})" 