"""
Test script for the Guardrails Framework

This script tests the individual guardrails and the overall framework.
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from guardrails import GuardrailsEngine
from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail
from guardrails.utils.result import GuardrailStatus


class SimpleTestAgent:
    """Simple test agent for unit testing."""
    
    def chat(self, user_input: str, **kwargs) -> str:
        # Return specific responses for testing
        if "pii" in user_input.lower():
            return "Contact us at john.doe@company.com or call 555-123-4567"
        elif "credit" in user_input.lower():
            return "Your card number is 4532 1234 5678 9012"
        else:
            return f"Echo: {user_input}"


def test_length_validator():
    """Test the LengthValidatorGuardrail."""
    print("🧪 Testing LengthValidatorGuardrail")
    print("-" * 40)
    
    # Test configuration
    guardrail = LengthValidatorGuardrail(
        "test_length",
        config={
            "min_length": 5,
            "max_length": 20,
            "truncate": True
        }
    )
    
    test_cases = [
        ("Valid input", "Hello world", GuardrailStatus.PASSED),
        ("Too short", "Hi", GuardrailStatus.FAILED),
        ("Too long (truncated)", "This is a very long message that should be truncated", GuardrailStatus.WARNING),
        ("Edge case - min length", "Hello", GuardrailStatus.PASSED),
        ("Empty string", "", GuardrailStatus.FAILED),
    ]
    
    for test_name, input_text, expected_status in test_cases:
        result = guardrail.validate(input_text)
        status_match = result.status == expected_status
        
        print(f"  {'✅' if status_match else '❌'} {test_name}")
        print(f"    Input: '{input_text}' (len={len(input_text)})")
        print(f"    Expected: {expected_status.value}, Got: {result.status.value}")
        print(f"    Message: {result.message}")
        if result.modified_content:
            print(f"    Modified: '{result.modified_content}'")
        print()


def test_pii_filter():
    """Test the PIIFilterGuardrail."""
    print("🧪 Testing PIIFilterGuardrail")
    print("-" * 40)
    
    # Test configuration
    guardrail = PIIFilterGuardrail(
        "test_pii",
        config={
            "mask_emails": True,
            "mask_phones": True,
            "mask_credit_cards": True,
            "replacement": "[MASKED]"
        }
    )
    
    test_cases = [
        ("No PII", "Hello, how are you today?", GuardrailStatus.PASSED, False),
        ("Email PII", "Contact john.doe@company.com for help", GuardrailStatus.WARNING, True),
        ("Phone PII", "Call us at 555-123-4567", GuardrailStatus.WARNING, True),
        ("Credit Card PII", "Card: 4532 1234 5678 9012", GuardrailStatus.WARNING, True),
        ("Multiple PII", "Email john@test.com or call 555-123-4567", GuardrailStatus.WARNING, True),
    ]
    
    for test_name, output_text, expected_status, should_mask in test_cases:
        result = guardrail.filter(output_text)
        status_match = result.status == expected_status
        masking_correct = bool(result.modified_content) == should_mask
        
        print(f"  {'✅' if status_match and masking_correct else '❌'} {test_name}")
        print(f"    Output: '{output_text}'")
        print(f"    Expected: {expected_status.value}, Got: {result.status.value}")
        print(f"    Message: {result.message}")
        if result.modified_content:
            print(f"    Masked: '{result.modified_content}'")
        print()


def test_engine_integration():
    """Test the GuardrailsEngine integration."""
    print("🧪 Testing GuardrailsEngine Integration")
    print("-" * 40)
    
    # Create engine with guardrails
    engine = GuardrailsEngine()
    engine.add_input_guardrail(LengthValidatorGuardrail(
        "length", {"min_length": 3, "max_length": 50, "truncate": True}
    ))
    engine.add_output_guardrail(PIIFilterGuardrail(
        "pii", {"mask_emails": True, "replacement": "[REDACTED]"}
    ))
    
    # Test agent
    agent = SimpleTestAgent()
    guarded_agent = engine.wrap_agent(agent)
    
    test_cases = [
        {
            "name": "Normal flow",
            "input": "Hello there",
            "should_work": True
        },
        {
            "name": "Input too short",
            "input": "Hi",
            "should_work": False  # Should be blocked
        },
        {
            "name": "PII in response",
            "input": "Tell me about PII",
            "should_work": True,  # Should work but mask PII
            "check_masking": True
        }
    ]
    
    for test_case in test_cases:
        print(f"  Testing: {test_case['name']}")
        print(f"    Input: '{test_case['input']}'")
        
        try:
            response = guarded_agent.chat(test_case['input'])
            
            if test_case['should_work']:
                print(f"    ✅ Success: '{response}'")
                
                # Check if PII was masked
                if test_case.get('check_masking'):
                    if '[REDACTED]' in response:
                        print(f"    ✅ PII correctly masked")
                    else:
                        print(f"    ⚠️  Expected PII masking")
            else:
                print(f"    ❌ Expected failure but got: '{response}'")
                
        except Exception as e:
            if not test_case['should_work']:
                print(f"    ✅ Correctly blocked: {e}")
            else:
                print(f"    ❌ Unexpected error: {e}")
        
        print()


def test_guardrails_stats():
    """Test guardrails statistics and configuration."""
    print("🧪 Testing Guardrails Stats & Configuration")
    print("-" * 40)
    
    engine = GuardrailsEngine()
    
    # Initially empty
    stats = engine.get_stats()
    print(f"  Initial stats: {stats}")
    assert stats['total_guardrails'] == 0
    
    # Add guardrails
    engine.add_input_guardrail(LengthValidatorGuardrail("test1"))
    engine.add_output_guardrail(PIIFilterGuardrail("test2"))
    
    # Check updated stats
    stats = engine.get_stats()
    print(f"  Updated stats: {stats}")
    assert stats['total_guardrails'] == 2
    assert stats['input_guardrails'] == 1
    assert stats['output_guardrails'] == 1
    
    print("  ✅ Stats test passed")


def main():
    """Run all tests."""
    print("🧪 GUARDRAILS FRAMEWORK TESTS")
    print("=" * 50)
    
    try:
        # Individual guardrail tests
        test_length_validator()
        test_pii_filter()
        
        # Integration tests
        test_engine_integration()
        test_guardrails_stats()
        
        print("🎉 All tests completed!")
        print("\nTo see a full demonstration, run: python demo_guardrails.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 