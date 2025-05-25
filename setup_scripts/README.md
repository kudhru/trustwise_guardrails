# Setup Scripts

This directory contains scripts for setting up and configuring the TrustWise Guardrails system.

## Scripts

- **`setup.py`** - Main setup script for installing the package and dependencies
- **`check_openai_setup.py`** - Verifies OpenAI API configuration and connectivity
- **`check_aws_setup.py`** - Verifies AWS configuration and connectivity

## Usage

Run these scripts from the project root directory:

```bash
# Install the package
python setup_scripts/setup.py

# Check OpenAI setup
python setup_scripts/check_openai_setup.py

# Check AWS setup
python setup_scripts/check_aws_setup.py
```

## Prerequisites

Make sure you have the required environment variables and credentials configured before running these scripts. 