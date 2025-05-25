"""
Simple test script for the LangGraph + AWS Bedrock Agent

This script runs a single test query to verify the agent is working correctly.
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.agent import BedrockAgent

def test_agent():
    """Test the agent with a simple query."""
    print("🧪 Testing LangGraph + AWS Bedrock Agent")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("Initializing agent...")
        agent = BedrockAgent()
        print(f"✅ Agent initialized with model: {agent.model_id}")
        
        # Test query
        test_query = "Hello! Can you tell me a short joke?"
        print(f"\n📝 Test query: {test_query}")
        
        # Get response
        print("🤔 Processing...")
        response = agent.chat(test_query)
        
        # Print result
        print(f"\n🤖 Response: {response}")
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_agent() 