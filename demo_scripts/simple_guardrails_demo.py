#!/usr/bin/env python3
"""
Simple Guardrails Demo - Minimal Code Example

This demo shows how to add guardrails protection to any existing agent
with just 3-4 lines of code using all the default settings.
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def main():
    """Demonstrate adding guardrails with minimal code."""
    print("🛡️  SIMPLE GUARDRAILS DEMO")
    print("=" * 50)
    print("Adding guardrails protection to an existing agent")
    print("with just 3-4 lines of code!")
    print()
    
    try:
        # Import the existing agent
        from agents.agent_openai import OpenAIAgent
        
        print("📝 Step 1: Import your existing agent")
        print("   from agents.agent_openai import OpenAIAgent")
        print()
        
        # Create the original agent
        print("🤖 Step 2: Create your agent as usual")
        print("   agent = OpenAIAgent()")
        agent = OpenAIAgent()
        print(f"   ✅ Agent created: {agent.model_name}")
        print()
        
        # THIS IS THE MAGIC - Just 4 lines to add guardrails!
        print("🛡️  Step 3: Add guardrails with just 4 lines!")
        print("   from guardrails import GuardrailsEngine")
        print("   from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail")
        print("   from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail")
        print()
        print("   engine = GuardrailsEngine()")
        print("   engine.add_input_guardrail(LengthValidatorGuardrail('length'))  # Default settings")
        print("   engine.add_output_guardrail(PIIFilterGuardrail('pii'))         # Default settings")
        print("   guarded_agent = engine.wrap_agent(agent)")
        print()
        
        from guardrails import GuardrailsEngine
        from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
        from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail
        
        engine = GuardrailsEngine()
        engine.add_input_guardrail(LengthValidatorGuardrail("length"))  # Uses all defaults
        engine.add_output_guardrail(PIIFilterGuardrail("pii"))         # Uses all defaults
        guarded_agent = engine.wrap_agent(agent)
        
        print("✅ That's it! Your agent now has guardrails protection!")
        print(f"   Original agent: {type(agent).__name__}")
        print(f"   Protected agent: {type(guarded_agent).__name__}")
        print()
        
        # Show what guardrails are active by default
        stats = engine.get_stats()
        print("📊 Default guardrails configuration:")
        print(f"   • Enabled: {stats['enabled']}")
        print(f"   • Fail fast: {stats['fail_fast']}")
        print(f"   • Input guardrails: {stats['input_guardrails']}")
        print(f"   • Output guardrails: {stats['output_guardrails']}")
        print()
        
        # Test the protected agent
        print("🧪 Testing the protected agent:")
        print("   (Same interface as before - no code changes needed!)")
        print()
        
        test_inputs = [
            "Hello! How are you today?",
            "Hi",  # Too short - will trigger length guardrail
            "What's your contact email address?"  # May trigger PII in response
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"Test {i}: '{test_input}'")
            try:
                # Use the guarded agent exactly like the original
                response = guarded_agent.chat(test_input)
                print(f"✅ Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            except Exception as e:
                print(f"❌ Blocked: {e}")
            print()
        
        print("🎉 Demo completed successfully!")
        print()
        print("💡 Key takeaways:")
        print("   • Only 4 lines of code needed to add guardrails")
        print("   • No changes to your existing agent code")
        print("   • Same interface - just call .chat() as before")
        print("   • Automatic protection with sensible defaults")
        print("   • Easy to customize later if needed")
        
    except ImportError as e:
        print(f"⚠️  OpenAI agent not available: {e}")
        print("📝 No problem! Let's use a mock agent to show the concept...")
        print()
        
        # Create a simple mock agent for demonstration
        class MockAgent:
            def __init__(self):
                self.model_name = "mock-gpt-3.5-turbo"
            
            def chat(self, user_input: str) -> str:
                if "email" in user_input.lower():
                    return "You can contact us at support@example.com or call 555-123-4567"
                return f"Mock response to: '{user_input}'"
        
        print("🤖 Step 2: Create your agent as usual")
        print("   agent = MockAgent()  # Using mock for demo")
        agent = MockAgent()
        print(f"   ✅ Agent created: {agent.model_name}")
        print()
        
        # Add guardrails
        print("🛡️  Step 3: Add guardrails with just 4 lines!")
        print("   from guardrails import GuardrailsEngine")
        print("   from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail")
        print("   from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail")
        print()
        print("   engine = GuardrailsEngine()")
        print("   engine.add_input_guardrail(LengthValidatorGuardrail('length'))  # Default settings")
        print("   engine.add_output_guardrail(PIIFilterGuardrail('pii'))         # Default settings")
        print("   guarded_agent = engine.wrap_agent(agent)")
        print()
        
        from guardrails import GuardrailsEngine
        from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
        from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail
        
        engine = GuardrailsEngine()
        engine.add_input_guardrail(LengthValidatorGuardrail("length", config={"min_length": 3}))  # Require at least 3 chars
        engine.add_output_guardrail(PIIFilterGuardrail("pii"))         # Uses all defaults
        guarded_agent = engine.wrap_agent(agent)
        
        print("✅ That's it! Your agent now has guardrails protection!")
        print(f"   Original agent: {type(agent).__name__}")
        print(f"   Protected agent: {type(guarded_agent).__name__}")
        print()
        
        # Show what guardrails are active
        stats = engine.get_stats()
        print("📊 Guardrails configuration:")
        print(f"   • Input guardrails: {stats['input_guardrails']} (length validation)")
        print(f"   • Output guardrails: {stats['output_guardrails']} (PII filtering)")
        print()
        
        # Test the protected agent
        print("🧪 Testing the protected agent:")
        print()
        
        test_inputs = [
            "Hello! How are you today?",
            "Hi",  # Too short - will trigger length guardrail
            "What's your contact email address?"  # Will trigger PII in response
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"Test {i}: '{test_input}'")
            try:
                response = guarded_agent.chat(test_input)
                print(f"✅ Response: {response}")
            except Exception as e:
                print(f"❌ Blocked: {e}")
            print()
        
        print("🎉 Demo completed successfully!")
        print()
        print("💡 Key takeaways:")
        print("   • Only 4 lines of code needed to add guardrails")
        print("   • No changes to your existing agent code")
        print("   • Same interface - just call .chat() as before")
        print("   • Automatic protection with sensible defaults")
        print("   • Works with ANY agent (OpenAI, Bedrock, custom, etc.)")
        print()
        print("🔧 To use with OpenAI:")
        print("   1. Set up your OpenAI API key in .env file")
        print("   2. Run: python setup_scripts/check_openai_setup.py")
        print("   3. Replace MockAgent() with OpenAIAgent()")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 This might be due to missing dependencies or configuration.")
        print("   Check the setup scripts in setup_scripts/ directory.")


if __name__ == "__main__":
    main() 