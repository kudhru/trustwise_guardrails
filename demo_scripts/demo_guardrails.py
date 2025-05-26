"""
Demonstration of the Guardrails Framework

This script shows how to wrap existing agents with guardrails protection
without modifying the agent code.
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from guardrails import GuardrailsEngine
from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail

# Try to import an agent (will work if OpenAI is set up)
try:
    from agents.agent_openai import OpenAIAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  OpenAI agent not available: {e}")
    AGENT_AVAILABLE = False


# Mock agent for demonstration if real agent is not available
class MockAgent:
    """A simple mock agent for demonstration purposes."""
    
    def __init__(self):
        self.model_name = "mock-model"
    
    def chat(self, user_input: str, **kwargs) -> str:
        """Mock chat method that returns a response with potential PII."""
        if "email" in user_input.lower():
            return f"Sure! You can contact us at support@example.com or call 123-456-7890."
        elif "long" in user_input.lower():
            return "This is a long response " * 100  # Very long response
        elif "short" in user_input.lower():
            return "Ok."
        else:
            return f"You said: '{user_input}'. This is a mock response for demonstration."


def demonstrate_basic_usage():
    """Demonstrate basic guardrails usage."""
    print("🛡️  Basic Guardrails Demonstration")
    print("=" * 50)
    
    # # Choose agent
    # if AGENT_AVAILABLE:
    #     try:
    #         agent = OpenAIAgent()
    #         print("✅ Using OpenAI agent")
    #     except Exception as e:
    #         print(f"⚠️  OpenAI agent failed, using mock: {e}")
    #         agent = MockAgent()
    # else:
    #     agent = MockAgent()
    #     print("📝 Using mock agent for demonstration")
    
    # Initialize the agent
    agent = OpenAIAgent()
    
    # Create guardrails engine
    engine = GuardrailsEngine()
    
    # Wrap the agent with guardrails
    guarded_agent = engine.wrap_agent(agent)
    
    # Add input guardrail (length validation)
    length_guard = LengthValidatorGuardrail()
    engine.add_input_guardrail(length_guard)
    
    # Add output guardrail (PII filtering)
    pii_guard = PIIFilterGuardrail()
    engine.add_output_guardrail(pii_guard)
    
    
    print(f"\n📊 Guardrails Stats: {engine.get_stats()}")
    print(f"🤖 Wrapped Agent: {guarded_agent}")
    
    return guarded_agent


def test_scenarios(guarded_agent):
    """Test various scenarios with the guarded agent."""
    print("\n🧪 Testing Different Scenarios")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Normal Input",
            "input": "Hello, how are you today?",
            "description": "Normal input that should pass all guardrails"
        },
        {
            "name": "Too Short Input",
            "input": "Hi",
            "description": "Input that's too short (less than 3 chars)"
        },
        {
            "name": "Long Input (with truncation)",
            "input": "This is a very long input that exceeds the maximum length limit and should be truncated by the length validator guardrail to demonstrate the truncation feature working properly in the guardrails system.",
            "description": "Input that's too long but will be truncated"
        },
        {
            "name": "Request with PII Response",
            "input": "What's your contact email?",
            "description": "Request that might trigger PII in response"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Input: '{test_case['input']}'")
        
        try:
            response = guarded_agent.chat(test_case['input'])
            print(f"✅ Response: '{response}'")
        except Exception as e:
            print(f"❌ Blocked: {e}")


def demonstrate_configuration():
    """Demonstrate different guardrail configurations."""
    print("\n⚙️  Configuration Demonstration")
    print("=" * 50)
    
    # Strict mode PII filter
    print("\n🔒 Strict Mode PII Filter (blocks instead of masking)")
    
    agent = MockAgent()
    engine = GuardrailsEngine()
    
    # Add strict PII filter
    strict_pii_guard = PIIFilterGuardrail(
        "strict_pii_filter",
        config={
            "strict_mode": True,  # Block instead of mask
            "mask_emails": True,
            "mask_phones": True
        }
    )
    engine.add_output_guardrail(strict_pii_guard)
    
    strict_agent = engine.wrap_agent(agent)
    
    try:
        response = strict_agent.chat("What's your contact email?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"🚫 Blocked by strict mode: {e}")


def interactive_demo():
    """Interactive demonstration where user can try inputs."""
    print("\n🎮 Interactive Demonstration")
    print("=" * 50)
    print("You can now chat with the guarded agent!")
    print("Try these test cases:")
    print("- 'Hi' (too short)")
    print("- Very long messages (will be truncated)")
    print("- 'What's your email?' (may trigger PII masking)")
    print("- Type 'quit' to exit")
    
    guarded_agent = demonstrate_basic_usage()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'stop']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("🛡️  Processing through guardrails...")
            response = guarded_agent.chat(user_input)
            print(f"🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main demonstration function."""
    print("🛡️  TRUSTWISE GUARDRAILS FRAMEWORK DEMO")
    print("=" * 60)
    print("This demo shows how to add guardrails to any agent")
    print("without modifying the agent code!")
    print()
    
    # Basic demonstration
    guarded_agent = demonstrate_basic_usage()
    
    # Test scenarios
    test_scenarios(guarded_agent)
    
    # Configuration demo
    demonstrate_configuration()
    
    # Ask if user wants interactive demo
    print("\n" + "=" * 60)
    try:
        choice = input("Would you like to try the interactive demo? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_demo()
        else:
            print("👋 Demo completed!")
            print("\n💡 Next steps:")
            print("  • Run universal agent demo: python demo_universal_agents.py")
            print("  • Run all tests: python run_tests.py")
            print("  • Individual tests: python tests/test_guardrails.py")
    except KeyboardInterrupt:
        print("\n👋 Demo completed!")
        print("\n💡 Next steps:")
        print("  • Run universal agent demo: python demo_universal_agents.py")
        print("  • Run all tests: python run_tests.py")

    print("\n🎉 All adapter tests completed!")
    print("\nTo see a full demonstration, run: python demo_universal_agents.py")
    print("To run all tests, use: python run_tests.py")


if __name__ == "__main__":
    main() 