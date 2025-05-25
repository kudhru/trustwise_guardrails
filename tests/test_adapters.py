"""
Test script for the Agent Adapter System

This script tests the adapter system that allows guardrails to work
with agents having different interfaces.
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from guardrails import GuardrailsEngine, detect_agent_interface, create_adapter
from guardrails.core.adapters import (
    ChatMethodAdapter, InvokeMethodAdapter, RunMethodAdapter, 
    CallableAdapter, CustomMethodAdapter, OpenAIClientAdapter
)
from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail


# Test agents with different interfaces
class TestChatAgent:
    def chat(self, user_input: str, **kwargs) -> str:
        return f"Chat: {user_input}"


class TestInvokeAgent:
    def invoke(self, input_data: dict) -> dict:
        return {"output": f"Invoke: {input_data.get('input', str(input_data))}"}


class TestRunAgent:
    def run(self, user_input: str) -> str:
        return f"Run: {user_input}"


class TestCallableAgent:
    def __call__(self, user_input: str, **kwargs) -> str:
        return f"Callable: {user_input}"


class TestCustomAgent:
    def process_text(self, text: str, mode: str = "default") -> str:
        return f"Custom: {text} (mode: {mode})"


def test_function_agent(user_input: str) -> str:
    return f"Function: {user_input}"


class TestMockOpenAI:
    def __init__(self):
        self.chat = self
        self.completions = self.MockCompletions()
    
    class MockCompletions:
        def create(self, model: str, messages: list, **kwargs):
            content = messages[-1]["content"] if messages else "empty"
            return self.MockResponse(f"OpenAI: {content}")
        
        class MockResponse:
            def __init__(self, content: str):
                self.choices = [self.MockChoice(content)]
            
            class MockChoice:
                def __init__(self, content: str):
                    self.message = self.MockMessage(content)
                
                class MockMessage:
                    def __init__(self, content: str):
                        self.content = content


def test_interface_detection():
    """Test automatic interface detection."""
    print("🧪 Testing Interface Detection")
    print("-" * 40)
    
    test_cases = [
        (TestChatAgent(), "chat"),
        (TestInvokeAgent(), "invoke"),
        (TestRunAgent(), "run"),
        (TestCallableAgent(), "callable"),
        (test_function_agent, "callable"),
        (TestMockOpenAI(), "openai_client"),
    ]
    
    for agent, expected in test_cases:
        try:
            detected = detect_agent_interface(agent)
            success = detected == expected
            agent_name = type(agent).__name__ if hasattr(agent, '__class__') else str(agent.__name__)
            print(f"  {'✅' if success else '❌'} {agent_name:20} → {detected} (expected: {expected})")
        except Exception as e:
            print(f"  ❌ {type(agent).__name__:20} → Error: {e}")


def test_adapter_creation():
    """Test adapter creation for different agent types."""
    print("\n🧪 Testing Adapter Creation")
    print("-" * 40)
    
    test_cases = [
        (TestChatAgent(), "chat", ChatMethodAdapter),
        (TestInvokeAgent(), "invoke", InvokeMethodAdapter),
        (TestRunAgent(), "run", RunMethodAdapter),
        (TestCallableAgent(), "callable", CallableAdapter),
        (test_function_agent, "callable", CallableAdapter),
        (TestMockOpenAI(), "openai_client", OpenAIClientAdapter),
    ]
    
    for agent, adapter_type, expected_class in test_cases:
        try:
            adapter = create_adapter(agent, adapter_type)
            success = isinstance(adapter, expected_class)
            agent_name = type(agent).__name__ if hasattr(agent, '__class__') else str(agent.__name__)
            print(f"  {'✅' if success else '❌'} {agent_name:20} → {type(adapter).__name__}")
        except Exception as e:
            agent_name = type(agent).__name__ if hasattr(agent, '__class__') else str(agent.__name__)
            print(f"  ❌ {agent_name:20} → Error: {e}")


def test_adapter_functionality():
    """Test that adapters work correctly."""
    print("\n🧪 Testing Adapter Functionality")
    print("-" * 40)
    
    test_input = "Hello, world!"
    
    test_cases = [
        ("ChatMethodAdapter", TestChatAgent(), "chat"),
        ("InvokeMethodAdapter", TestInvokeAgent(), "invoke"),
        ("RunMethodAdapter", TestRunAgent(), "run"),
        ("CallableAdapter", TestCallableAgent(), "callable"),
        ("CallableAdapter (function)", test_function_agent, "callable"),
        ("OpenAIClientAdapter", TestMockOpenAI(), "openai_client"),
    ]
    
    for name, agent, adapter_type in test_cases:
        try:
            adapter = create_adapter(agent, adapter_type)
            response = adapter.chat(test_input)
            
            # Check that response contains our input
            success = test_input.replace(",", "") in response or "Hello" in response
            print(f"  {'✅' if success else '❌'} {name:25} → '{response}'")
            
        except Exception as e:
            print(f"  ❌ {name:25} → Error: {e}")


def test_custom_adapter():
    """Test custom adapter with configuration."""
    print("\n🧪 Testing Custom Adapter")
    print("-" * 40)
    
    agent = TestCustomAgent()
    
    # Test custom method adapter
    try:
        adapter = create_adapter(
            agent,
            "custom",
            {
                "method_name": "process_text",
                "input_transform": lambda text, **kwargs: ([text], {"mode": "advanced"}),
                "output_transform": lambda result: result
            }
        )
        
        response = adapter.chat("Test message")
        success = "Test message" in response and "advanced" in response
        print(f"  {'✅' if success else '❌'} Custom method adapter → '{response}'")
        
    except Exception as e:
        print(f"  ❌ Custom method adapter → Error: {e}")


def test_guardrails_integration():
    """Test that adapters work with the full guardrails system."""
    print("\n🧪 Testing Guardrails Integration")
    print("-" * 40)
    
    # Create engine with guardrails
    engine = GuardrailsEngine()
    engine.add_input_guardrail(LengthValidatorGuardrail(
        "length", {"min_length": 3, "max_length": 100}
    ))
    
    agents = [
        ("Chat Agent", TestChatAgent()),
        ("Invoke Agent", TestInvokeAgent()),
        ("Run Agent", TestRunAgent()),
        ("Callable Agent", TestCallableAgent()),
        ("Function Agent", test_function_agent),
    ]
    
    test_input = "Hello from guardrails!"
    
    for name, agent in agents:
        try:
            # Wrap with guardrails (should auto-detect interface)
            guarded_agent = engine.wrap_agent(agent)
            
            # Test the wrapped agent
            response = guarded_agent.chat(test_input)
            
            success = "Hello" in response
            print(f"  {'✅' if success else '❌'} {name:15} → '{response}'")
            
        except Exception as e:
            print(f"  ❌ {name:15} → Error: {e}")


def test_error_scenarios():
    """Test error handling for problematic cases."""
    print("\n🧪 Testing Error Scenarios")
    print("-" * 40)
    
    # Agent with no compatible interface
    class IncompatibleAgent:
        def some_method(self):
            return "incompatible"
    
    # Test incompatible agent
    try:
        agent = IncompatibleAgent()
        interface = detect_agent_interface(agent)
        print(f"  ❌ Should have failed but got: {interface}")
    except ValueError:
        print(f"  ✅ Correctly detected incompatible agent")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
    
    # Test invalid adapter type
    try:
        agent = TestChatAgent()
        adapter = create_adapter(agent, "invalid_type")
        print(f"  ❌ Should have failed but got: {adapter}")
    except ValueError:
        print(f"  ✅ Correctly rejected invalid adapter type")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")


def main():
    """Run all adapter tests."""
    print("🧪 AGENT ADAPTER SYSTEM TESTS")
    print("=" * 50)
    
    try:
        # Test interface detection
        test_interface_detection()
        
        # Test adapter creation
        test_adapter_creation()
        
        # Test adapter functionality
        test_adapter_functionality()
        
        # Test custom adapter
        test_custom_adapter()
        
        # Test guardrails integration
        test_guardrails_integration()
        
        # Test error scenarios
        test_error_scenarios()
        
        print("\n🎉 All adapter tests completed!")
        print("\nTo see a full demonstration, run: python demo_universal_agents.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 