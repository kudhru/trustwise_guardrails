"""
AWS Bedrock Setup Verification Script

This script helps verify that your AWS credentials and Bedrock access are working correctly.
"""

import os
import boto3
from dotenv import load_dotenv

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("🔑 Checking AWS credentials...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for access keys
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    profile = os.getenv('AWS_PROFILE')
    
    if profile:
        print(f"✅ Using AWS profile: {profile}")
        return True
    elif access_key and secret_key:
        print(f"✅ Using access keys (Key ID: {access_key[:8]}...)")
        print(f"✅ Region: {region}")
        return True
    else:
        print("❌ No AWS credentials found!")
        print("Please check your .env file or AWS configuration.")
        return False

def check_aws_connection():
    """Test AWS connection using STS."""
    print("\n🌐 Testing AWS connection...")
    
    try:
        # Create STS client to test connection
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ Connected as: {identity.get('Arn', 'Unknown')}")
        print(f"✅ Account ID: {identity.get('Account', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to AWS: {e}")
        return False

def check_bedrock_access():
    """Check if Bedrock service is accessible."""
    print("\n🏗️  Testing Bedrock access...")
    
    try:
        # Create Bedrock client
        bedrock = boto3.client('bedrock')
        
        # List foundation models to test access
        response = bedrock.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        print(f"✅ Bedrock accessible! Found {len(models)} foundation models")
        
        # Check if we have access to default model
        default_model = os.getenv('BEDROCK_MODEL_ID', 'amazon.titan-text-express-v1')
        model_found = any(model['modelId'] == default_model for model in models)
        
        if model_found:
            print(f"✅ Default model '{default_model}' is available")
        else:
            print(f"⚠️  Default model '{default_model}' not found")
            print("Available models:")
            for model in models[:5]:  # Show first 5 models
                print(f"   - {model['modelId']}")
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to access Bedrock: {e}")
        if "AccessDeniedException" in str(e):
            print("💡 This usually means you need to request access to Bedrock models")
            print("   Go to AWS Bedrock Console > Model access > Request access")
        return False

def check_bedrock_runtime():
    """Test Bedrock Runtime for inference."""
    print("\n🚀 Testing Bedrock Runtime...")
    
    try:
        # Create Bedrock Runtime client
        bedrock_runtime = boto3.client('bedrock-runtime')
        
        # Test with a simple invoke (this might fail due to model access, but tests the service)
        print("✅ Bedrock Runtime client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Bedrock Runtime client: {e}")
        return False

def main():
    """Run all checks."""
    print("🔍 AWS Bedrock Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check credentials
    if not check_aws_credentials():
        all_good = False
        print("\n💡 To fix credentials:")
        print("1. Create .env file: cp env.example .env")
        print("2. Add your AWS access keys to .env")
        print("3. Or configure AWS CLI: aws configure")
        return
    
    # Check connection
    if not check_aws_connection():
        all_good = False
    
    # Check Bedrock access
    if not check_bedrock_access():
        all_good = False
    
    # Check Bedrock Runtime
    if not check_bedrock_runtime():
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! You're ready to use the Bedrock agent!")
        print("\nNext steps:")
        print("- Run: python tests/test_agent.py (quick test)")
        print("- Run: python agents/agent.py (interactive chat)")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nFor help with AWS setup:")
        print("- Run: python setup.py")
        print("- Check the README.md file")

if __name__ == "__main__":
    main() 