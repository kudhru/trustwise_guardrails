"""
Setup script for LangGraph + AWS Bedrock Agent

This script helps with initial setup and dependency installation.
"""

import os
import subprocess
import sys

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment file if it doesn't exist."""
    env_file = ".env"
    example_file = "env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(example_file):
            print(f"📝 Creating {env_file} from {example_file}...")
            with open(example_file, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print(f"✅ Created {env_file}")
            print(f"⚠️  Please edit {env_file} with your AWS credentials!")
        else:
            print(f"❌ {example_file} not found!")
            return False
    else:
        print(f"✅ {env_file} already exists")
    
    return True

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Please use Python 3.8 or higher")
        return False

def print_aws_setup_instructions():
    """Print detailed AWS setup instructions."""
    print("\n" + "="*60)
    print("🔑 AWS ACCESS KEY SETUP INSTRUCTIONS")
    print("="*60)
    print("Since you have AWS console access, follow these steps:")
    print()
    print("1. Go to AWS IAM Console:")
    print("   https://console.aws.amazon.com/iam/")
    print()
    print("2. Click 'Users' in the left sidebar")
    print()
    print("3. Find your username and click on it")
    print("   (or create a new user for this project)")
    print()
    print("4. Go to 'Security credentials' tab")
    print()
    print("5. Scroll to 'Access keys' section")
    print()
    print("6. Click 'Create access key'")
    print()
    print("7. Choose 'Command Line Interface (CLI)'")
    print()
    print("8. Copy both Access Key ID and Secret Access Key")
    print("   ⚠️  This is the only time you'll see the secret key!")
    print()
    print("9. Paste them into your .env file")
    print()
    print("Alternative: Use AWS CLI profiles instead of access keys")
    print("Run: aws configure --profile your-profile-name")
    print("Then set AWS_PROFILE=your-profile-name in .env")
    print("="*60)

def main():
    """Main setup function."""
    print("🚀 LangGraph + AWS Bedrock Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Print AWS setup instructions
    print_aws_setup_instructions()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Follow the AWS setup instructions above")
    print("2. Edit .env file with your AWS credentials")
    print("3. Run: python tests/test_agent.py (for a quick test)")
    print("4. Run: python agents/agent.py (for interactive chat)")

if __name__ == "__main__":
    main() 