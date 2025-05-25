"""
Universal Agent Compatibility Demonstration

This script shows how the guardrails framework can protect agents 
with different interfaces (chat, invoke, run, callable, etc.)
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(__file__))

from guardrails import GuardrailsEngine, detect_agent_interface
from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail


# Example agents with different interfaces
class ChatAgent:
    """Agent with chat() method (current standard)."""
    
    def chat(self, user_input: str, **kwargs) -> str:
        return f"ChatAgent response to: '{user_input}'"


class InvokeAgent:
    """Agent with invoke() method (LangChain style)."""
    
    def invoke(self, input_data: dict) -> dict:
        user_input = input_data.get("input", str(input_data))
        return {"output": f"InvokeAgent response to: '{user_input}'"}


class RunAgent:
    """Agent with run() method (older LangChain style)."""
    
    def run(self, user_input: str) -> str:
        return f"RunAgent response to: '{user_input}'"


class CallableAgent:
    """Agent that is callable (function-like)."""
    
    def __call__(self, user_input: str, **kwargs) -> str:
        return f"CallableAgent response to: '{user_input}'"


class CustomMethodAgent:
    """Agent with a custom method name."""
    
    def process(self, text: str, format_type: str = "default") -> str:
        return f"CustomMethodAgent processed '{text}' in {format_type} format"


class MockOpenAIClient:
    """Mock OpenAI client for demonstration."""
    
    def __init__(self):
        self.chat = self
    
    class Completions:
        def create(self, model: str, messages: list, **kwargs) -> 'MockResponse':
            user_message = messages[-1]["content"] if messages else "No message"
            return MockResponse(f"OpenAI mock response to: '{user_message}'")
    
    def __init__(self):
        self.chat = self
        self.completions = self.Completions()


class MockResponse:
    """Mock OpenAI response."""
    
    def __init__(self, content: str):
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock OpenAI choice."""
    
    def __init__(self, content: str):
        self.message = MockMessage(content)


class MockMessage:
    """Mock OpenAI message."""
    
    def __init__(self, content: str):
        self.content = content


def simple_function_agent(user_input: str) -> str:
    """A simple function that acts as an agent."""
    return f"Function agent response to: '{user_input}'"


def demonstrate_interface_detection():
    """Demonstrate automatic interface detection."""
    print("🔍 Interface Detection Demonstration")
    print("=" * 50)
    
    agents = [
        ("ChatAgent", ChatAgent()),
        ("InvokeAgent", InvokeAgent()),
        ("RunAgent", RunAgent()),
        ("CallableAgent", CallableAgent()),
        ("Function", simple_function_agent),
        ("CustomMethodAgent", CustomMethodAgent()),
        ("MockOpenAIClient", MockOpenAIClient()),
    ]
    
    for name, agent in agents:
        try:
            interface = detect_agent_interface(agent)
            print(f"  ✅ {name:18} → {interface}")
        except ValueError as e:
            print(f"  ❌ {name:18} → {e}")


def demonstrate_universal_wrapping():
    """Demonstrate wrapping different agent types with guardrails."""
    print("\n🛡️  Universal Agent Wrapping Demonstration")
    print("=" * 50)
    
    # Create guardrails engine
    engine = GuardrailsEngine()
    engine.add_input_guardrail(LengthValidatorGuardrail(
        "length_check", {"min_length": 3, "max_length": 50}
    ))
    engine.add_output_guardrail(PIIFilterGuardrail(
        "pii_filter", {"mask_emails": True}
    ))
    
    # Test different agent types
    agents = [
        ("chat", ChatAgent()),
        ("invoke", InvokeAgent()),
        ("run", RunAgent()),
        ("callable", CallableAgent()),
        ("callable", simple_function_agent),
    ]
    
    test_input = "Hello, how are you?"
    
    for adapter_type, agent in agents:
        try:
            print(f"\n📝 Testing {type(agent).__name__}:")
            
            # Wrap with guardrails
            guarded_agent = engine.wrap_agent(agent)
            
            # Test the wrapped agent
            response = guarded_agent.chat(test_input)
            print(f"  ✅ Success: {response}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")


def demonstrate_custom_configurations():
    """Demonstrate custom adapter configurations."""
    print("\n⚙️  Custom Configuration Demonstration")
    print("=" * 50)
    
    engine = GuardrailsEngine()
    engine.add_input_guardrail(LengthValidatorGuardrail("length", {"min_length": 3}))
    
    # Example 1: Custom method name
    print("\n1. Custom Method Name:")
    custom_agent = CustomMethodAgent()
    
    try:
        guarded_agent = engine.wrap_agent(
            custom_agent,
            adapter_type="custom",
            adapter_config={
                "method_name": "process",
                "input_transform": lambda text, **kwargs: ([text], {"format_type": "advanced"}),
                "output_transform": lambda result: result
            }
        )
        
        response = guarded_agent.chat("Test custom method")
        print(f"  ✅ Custom method success: {response}")
        
    except Exception as e:
        print(f"  ❌ Custom method failed: {e}")
    
    # Example 2: OpenAI client style
    print("\n2. OpenAI Client Style:")
    openai_client = MockOpenAIClient()
    
    try:
        guarded_agent = engine.wrap_agent(
            openai_client,
            adapter_type="openai_client",
            adapter_config={
                "model": "gpt-3.5-turbo",
                "system_prompt": "You are a helpful assistant."
            }
        )
        
        response = guarded_agent.chat("What is AI?")
        print(f"  ✅ OpenAI client success: {response}")
        
    except Exception as e:
        print(f"  ❌ OpenAI client failed: {e}")
    
    # Example 3: Invoke with custom keys
    print("\n3. Invoke with Custom Keys:")
    invoke_agent = InvokeAgent()
    
    try:
        guarded_agent = engine.wrap_agent(
            invoke_agent,
            adapter_type="invoke",
            adapter_config={
                "input_key": "input",
                "output_key": "output"
            }
        )
        
        response = guarded_agent.chat("Test custom keys")
        print(f"  ✅ Custom keys success: {response}")
        
    except Exception as e:
        print(f"  ❌ Custom keys failed: {e}")


def demonstrate_error_scenarios():
    """Demonstrate how the system handles problematic agents."""
    print("\n🚨 Error Handling Demonstration")
    print("=" * 50)
    
    engine = GuardrailsEngine()
    
    # Agent with no compatible interface
    class IncompatibleAgent:
        def some_other_method(self):
            return "This won't work"
    
    print("\n1. Incompatible Agent:")
    try:
        incompatible = IncompatibleAgent()
        guarded_agent = engine.wrap_agent(incompatible)
        print(f"  ❌ Should have failed but didn't")
    except Exception as e:
        print(f"  ✅ Correctly failed: {e}")
    
    # Agent that throws errors
    class ErrorAgent:
        def chat(self, user_input: str) -> str:
            raise RuntimeError("Agent internal error")
    
    print("\n2. Agent That Throws Errors:")
    try:
        error_agent = ErrorAgent()
        guarded_agent = engine.wrap_agent(error_agent)
        response = guarded_agent.chat("This will fail")
        print(f"  ❌ Should have failed: {response}")
    except Exception as e:
        print(f"  ✅ Correctly handled error: {e}")


def main():
    """Main demonstration function."""
    print("🌍 UNIVERSAL AGENT COMPATIBILITY DEMO")
    print("=" * 60)
    print("This demo shows how guardrails can protect ANY agent interface!")
    print()
    
    # Demonstrate interface detection
    demonstrate_interface_detection()
    
    # Demonstrate universal wrapping
    demonstrate_universal_wrapping()
    
    # Demonstrate custom configurations
    demonstrate_custom_configurations()
    
    # Demonstrate error handling
    demonstrate_error_scenarios()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\n💡 Key Benefits:")
    print("  ✅ Works with ANY agent interface")
    print("  ✅ Auto-detects agent types")
    print("  ✅ Configurable adapters")
    print("  ✅ Zero agent code changes")
    print("  ✅ Robust error handling")
    print("\n💡 Next steps:")
    print("  • Run all tests: python run_tests.py")
    print("  • Test adapters: python tests/test_adapters.py")
    print("  • Test guardrails: python tests/test_guardrails.py")


if __name__ == "__main__":
    main() 