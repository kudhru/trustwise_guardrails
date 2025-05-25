"""
OpenAI Setup Verification Script

This script helps verify that your OpenAI API key and configuration are working correctly.
"""

import os
from dotenv import load_dotenv
import openai

def check_openai_credentials():
    """Check if OpenAI API key is configured."""
    print("🔑 Checking OpenAI credentials...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    model_name = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    if api_key:
        print(f"✅ OpenAI API key found (Key: {api_key[:8]}...{api_key[-4:]})")
        print(f"✅ Model: {model_name}")
        return True
    else:
        print("❌ No OpenAI API key found!")
        print("Please check your .env file.")
        return False

def check_openai_connection():
    """Test OpenAI API connection."""
    print("\n🌐 Testing OpenAI API connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[{"role": "user", "content": "Say 'Hello!' if you can hear me."}],
            max_tokens=10
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API connection successful!")
        print(f"✅ Test response: {response_text}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to OpenAI API: {e}")
        if "invalid api key" in str(e).lower():
            print("💡 Your API key appears to be invalid")
            print("   Get a new one from: https://platform.openai.com/api-keys")
        elif "quota" in str(e).lower():
            print("💡 You may have exceeded your API quota")
            print("   Check your usage at: https://platform.openai.com/usage")
        return False

def check_model_availability():
    """Check if the specified model is available."""
    print("\n🤖 Checking model availability...")
    
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        model_name = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # List available models
        models = client.models.list()
        available_models = [model.id for model in models.data]
        
        if model_name in available_models:
            print(f"✅ Model '{model_name}' is available")
        else:
            print(f"⚠️  Model '{model_name}' not found in your available models")
            print("Available models include:")
            chat_models = [m for m in available_models if 'gpt' in m][:5]
            for model in chat_models:
                print(f"   - {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check model availability: {e}")
        return False

def main():
    """Run all checks."""
    print("🔍 OpenAI Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check credentials
    if not check_openai_credentials():
        all_good = False
        print("\n💡 To fix credentials:")
        print("1. Create .env file: cp env.example .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Get API key from: https://platform.openai.com/api-keys")
        return
    
    # Check connection
    if not check_openai_connection():
        all_good = False
    
    # Check model availability
    if not check_model_availability():
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! You're ready to use the OpenAI agent!")
        print("\nNext steps:")
        print("- Run: python tests/test_agent_openai.py (quick test)")
        print("- Run: python agents/agent_openai.py (interactive chat)")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nFor help with OpenAI setup:")
        print("- Check the env.example file")
        print("- Visit: https://platform.openai.com/api-keys")

if __name__ == "__main__":
    main() 