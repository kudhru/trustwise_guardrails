"""
Trustwise Guardrails Framework

A universal guardrails system that can wrap any agent to add safety, 
compliance, and monitoring capabilities without modifying the agent code.
"""

from .core.engine import GuardrailsEngine
from .core.wrapper import GuardedAgent
from .core.base import InputGuardrail, OutputGuardrail, GuardrailResult
from .core.adapters import (
    AgentAdapter, 
    ChatMethodAdapter, 
    InvokeMethodAdapter, 
    RunMethodAdapter, 
    CallableAdapter,
    CustomMethodAdapter,
    OpenAIClientAdapter,
    LangChainAgentAdapter,
    create_adapter,
    detect_agent_interface
)
from .utils.result import GuardrailStatus

__version__ = "0.1.0"
__author__ = "Trustwise Team"

# Main exports
__all__ = [
    "GuardrailsEngine",
    "GuardedAgent", 
    "InputGuardrail",
    "OutputGuardrail",
    "GuardrailResult",
    "GuardrailStatus",
    # Adapter system
    "AgentAdapter",
    "ChatMethodAdapter",
    "InvokeMethodAdapter", 
    "RunMethodAdapter",
    "CallableAdapter",
    "CustomMethodAdapter",
    "OpenAIClientAdapter",
    "LangChainAgentAdapter",
    "create_adapter",
    "detect_agent_interface"
] 