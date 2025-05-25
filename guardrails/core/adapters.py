"""
Agent Adapters - Normalize different agent interfaces for guardrails compatibility.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Union
import logging

logger = logging.getLogger(__name__)


class AgentAdapter(ABC):
    """Base class for agent adapters that normalize different agent interfaces."""
    
    def __init__(self, agent: Any, config: Optional[Dict[str, Any]] = None):
        self.agent = agent
        self.config = config or {}
    
    @abstractmethod
    def chat(self, user_input: str, **kwargs) -> str:
        """
        Normalize the agent interaction to a chat interface.
        
        Args:
            user_input: The user's input text
            **kwargs: Additional arguments
            
        Returns:
            str: The agent's response
        """
        pass
    
    def __getattr__(self, name: str) -> Any:
        """Delegate other method calls to the wrapped agent."""
        return getattr(self.agent, name)


class ChatMethodAdapter(AgentAdapter):
    """Adapter for agents with a 'chat' method (default behavior)."""
    
    def chat(self, user_input: str, **kwargs) -> str:
        return self.agent.chat(user_input, **kwargs)


class InvokeMethodAdapter(AgentAdapter):
    """Adapter for agents with an 'invoke' method (common in LangChain)."""
    
    def __init__(self, agent: Any, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent, config)
        self.input_key = self.config.get("input_key", "input")
        self.output_key = self.config.get("output_key", None)
    
    def chat(self, user_input: str, **kwargs) -> str:
        # Prepare input based on configuration
        if self.input_key:
            input_data = {self.input_key: user_input}
            input_data.update(kwargs)
        else:
            input_data = user_input
        
        # Call the agent
        result = self.agent.invoke(input_data)
        
        # Extract output based on configuration
        if self.output_key and isinstance(result, dict):
            return str(result.get(self.output_key, result))
        else:
            return str(result)


class RunMethodAdapter(AgentAdapter):
    """Adapter for agents with a 'run' method."""
    
    def chat(self, user_input: str, **kwargs) -> str:
        return str(self.agent.run(user_input, **kwargs))


class CallableAdapter(AgentAdapter):
    """Adapter for callable agents (functions, callable objects)."""
    
    def chat(self, user_input: str, **kwargs) -> str:
        return str(self.agent(user_input, **kwargs))


class CustomMethodAdapter(AgentAdapter):
    """Adapter for agents with custom method names."""
    
    def __init__(self, agent: Any, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent, config)
        self.method_name = self.config.get("method_name")
        if not self.method_name:
            raise ValueError("method_name must be specified in config for CustomMethodAdapter")
        
        self.input_transform = self.config.get("input_transform", lambda x, **kwargs: (x,), {})
        self.output_transform = self.config.get("output_transform", str)
    
    def chat(self, user_input: str, **kwargs) -> str:
        method = getattr(self.agent, self.method_name)
        
        # Transform input
        if callable(self.input_transform):
            args, method_kwargs = self.input_transform(user_input, **kwargs)
        else:
            args, method_kwargs = (user_input,), kwargs
        
        # Call the method
        result = method(*args, **method_kwargs)
        
        # Transform output
        if callable(self.output_transform):
            return self.output_transform(result)
        else:
            return str(result)


class OpenAIClientAdapter(AgentAdapter):
    """Adapter for direct OpenAI client usage."""
    
    def __init__(self, agent: Any, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent, config)
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.system_prompt = self.config.get("system_prompt", None)
    
    def chat(self, user_input: str, **kwargs) -> str:
        messages = []
        
        # Add system message if configured
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Call OpenAI API
        response = self.agent.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        
        return response.choices[0].message.content


class LangChainAgentAdapter(AgentAdapter):
    """Adapter for LangChain agents."""
    
    def chat(self, user_input: str, **kwargs) -> str:
        # Try different LangChain interfaces
        if hasattr(self.agent, 'invoke'):
            result = self.agent.invoke({"input": user_input})
            # Handle different return types
            if isinstance(result, dict):
                return str(result.get("output", result.get("text", str(result))))
            return str(result)
        elif hasattr(self.agent, 'run'):
            return str(self.agent.run(user_input))
        else:
            raise ValueError("Unsupported LangChain agent interface")


def detect_agent_interface(agent: Any) -> str:
    """
    Automatically detect the agent interface type.
    
    Args:
        agent: The agent to analyze
        
    Returns:
        str: The detected interface type
    """
    # Check for common method names in order of preference
    if hasattr(agent, 'chat'):
        return 'chat'
    elif hasattr(agent, 'invoke'):
        return 'invoke'
    elif hasattr(agent, 'run'):
        return 'run'
    elif callable(agent):
        return 'callable'
    elif hasattr(agent, 'chat') and hasattr(agent.chat, 'completions'):
        # Looks like OpenAI client
        return 'openai_client'
    else:
        # Check for common agent types
        agent_type = type(agent).__name__
        if 'langchain' in agent_type.lower() or 'chain' in agent_type.lower():
            return 'langchain'
        
        # List available methods for debugging
        methods = [method for method in dir(agent) if not method.startswith('_') and callable(getattr(agent, method))]
        raise ValueError(f"Unable to detect agent interface. Agent type: {agent_type}, Available methods: {methods}")


def create_adapter(agent: Any, adapter_type: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> AgentAdapter:
    """
    Create an appropriate adapter for the agent.
    
    Args:
        agent: The agent to wrap
        adapter_type: Explicit adapter type, or None for auto-detection
        config: Configuration for the adapter
        
    Returns:
        AgentAdapter: An adapter that normalizes the agent interface
    """
    if adapter_type is None:
        adapter_type = detect_agent_interface(agent)
    
    adapter_map = {
        'chat': ChatMethodAdapter,
        'invoke': InvokeMethodAdapter,
        'run': RunMethodAdapter,
        'callable': CallableAdapter,
        'openai_client': OpenAIClientAdapter,
        'langchain': LangChainAgentAdapter,
        'custom': CustomMethodAdapter,
    }
    
    if adapter_type not in adapter_map:
        raise ValueError(f"Unsupported adapter type: {adapter_type}. Available types: {list(adapter_map.keys())}")
    
    adapter_class = adapter_map[adapter_type]
    logger.info(f"Creating {adapter_class.__name__} for agent type: {type(agent).__name__}")
    
    return adapter_class(agent, config) 