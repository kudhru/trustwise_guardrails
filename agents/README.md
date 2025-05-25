# Agent Scripts

This directory contains the core agent implementations for the TrustWise Guardrails system.

## Scripts

- **`agent.py`** - AWS Bedrock LangGraph agent implementation
- **`agent_openai.py`** - OpenAI LangGraph agent implementation

## Usage

Run these scripts from the project root directory:

```bash
# Run OpenAI agent (recommended for testing)
python agents/agent_openai.py

# Run AWS Bedrock agent
python agents/agent.py
```

## Features

Both agents provide:
- **Interactive Chat Interface**: Command-line conversation interface
- **Memory Management**: Maintains conversation context using LangGraph
- **State-based Execution**: Uses LangGraph's graph execution for reliable flow
- **Configurable Models**: Easy to switch between different models
- **Error Handling**: Robust error handling and user feedback

## Prerequisites

### For OpenAI Agent (`agent_openai.py`)
1. OpenAI API key configured in `.env` file
2. Run setup verification: `python setup_scripts/check_openai_setup.py`

### For AWS Bedrock Agent (`agent.py`)
1. AWS credentials configured
2. Bedrock model access requested and approved
3. Run setup verification: `python setup_scripts/check_aws_setup.py`

## Available Commands

When running either agent interactively:
- `quit` or `exit`: Stop the conversation
- `clear`: Start a new conversation thread (clears memory)
- Any other text: Send a message to the agent

## Integration with Guardrails

These agents can be wrapped with the guardrails framework for enhanced safety:

```python
from guardrails import GuardrailsEngine
from agents.agent_openai import SimpleOpenAIAgent

# Create and wrap agent
agent = SimpleOpenAIAgent()
engine = GuardrailsEngine()
guarded_agent = engine.wrap_agent(agent)

# Use with guardrails protection
response = guarded_agent.chat("Hello!")
``` 