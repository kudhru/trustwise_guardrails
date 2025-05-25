# Simple LangGraph Agent with AWS Bedrock

A simple yet powerful conversational AI agent built with LangGraph and AWS Bedrock. This agent takes user text input, processes it through AWS Bedrock foundation models, and provides intelligent responses.

## 🛡️ NEW: Trustwise Guardrails Framework

This project now includes a **universal guardrails framework** that can add safety, compliance, and monitoring capabilities to **any agent** without modifying the agent code!

### ✨ Universal Agent Support

The guardrails framework now works with **ANY agent interface**:

- **`chat()` method** (default): Standard chat interface
- **`invoke()` method** (LangChain style): `agent.invoke({"input": "message"})`
- **`run()` method** (older LangChain): `agent.run("message")`
- **Callable agents**: Function-like agents `agent("message")`
- **Custom methods**: Any method name with configurable input/output transforms
- **OpenAI clients**: Direct OpenAI API client integration
- **Auto-detection**: Automatically detects agent interface type

### Quick Guardrails Demo

```python
from guardrails import GuardrailsEngine
from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail

# Create guardrails engine
engine = GuardrailsEngine()
engine.add_input_guardrail(LengthValidatorGuardrail("length_check"))
engine.add_output_guardrail(PIIFilterGuardrail("pii_filter"))

# Wrap ANY agent with guardrails (works with ANY interface!)
guarded_agent = engine.wrap_agent(your_existing_agent)

# Use exactly like before - guardrails work transparently
response = guarded_agent.chat("Your message here")
```

### Try the Demonstrations

```bash
# Universal agent compatibility demo
python demo_scripts/demo_universal_agents.py

# Original guardrails demo
python demo_scripts/demo_guardrails.py

# Run all tests
python run_tests.py

# Run individual tests
python tests/test_guardrails.py
python tests/test_adapters.py
python tests/test_agent_openai.py
python tests/test_agent.py
```

## Features

- 🤖 **LangGraph Integration**: Uses state-based graph execution for reliable conversation flow
- ☁️ **AWS Bedrock**: Leverages AWS Bedrock foundation models (default: Amazon Titan Text Express)
- 🔌 **OpenAI Support**: Alternative OpenAI integration for easy testing
- 🛡️ **Universal Guardrails**: Add safety and compliance to any agent without code changes
- 🌍 **Universal Compatibility**: Works with ANY agent interface (chat, invoke, run, callable, custom)
- 🔍 **Auto-Detection**: Automatically detects and adapts to agent interfaces
- 💾 **Memory**: Maintains conversation context using LangGraph's built-in memory system
- 🔄 **Interactive Chat**: Simple command-line interface for real-time conversations
- ⚙️ **Configurable**: Easy to switch between different Bedrock models and regions

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions (for Bedrock version)
2. **OpenAI API Key**: For the OpenAI version (easier to get started)
3. **AWS Bedrock Access**: Request access to the foundation models you want to use
4. **Python 3.8+**: Required for running the application

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
# Navigate to the project directory
cd trustwise_guardrails

# Install required packages
pip install -r requirements.txt
```

### 2. Choose Your Model Provider

#### Option A: OpenAI (Easiest to Start)
Create a `.env` file (copy from `env.example`):

```bash
cp env.example .env
```

Edit `.env` with your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

#### Option B: AWS Bedrock
Follow the AWS setup instructions in the [AWS Configuration](#aws-configuration) section below.

### 3. Test Your Setup

```bash
# For OpenAI
python setup_scripts/check_openai_setup.py
python agents/agent_openai.py

# For AWS Bedrock
python setup_scripts/check_aws_setup.py
python agents/agent.py
```

## 🛡️ Guardrails Framework

### Architecture

The guardrails framework uses a **wrapper/decorator pattern** that can protect any agent:

```
User Input → Input Guardrails → Agent → Output Guardrails → Response
```

### Built-in Guardrails

#### Input Guardrails
- **LengthValidatorGuardrail**: Validates input length, with optional truncation
- More coming soon: Content moderation, injection detection, rate limiting

#### Output Guardrails  
- **PIIFilterGuardrail**: Detects and masks PII (emails, phones, credit cards, SSN)
- More coming soon: Toxicity filtering, bias detection, factual accuracy

### Usage Examples

#### Basic Usage
```python
from guardrails import GuardrailsEngine
from guardrails.input_guardrails.length_validator import LengthValidatorGuardrail
from guardrails.output_guardrails.pii_filter import PIIFilterGuardrail

# Create engine and add guardrails
engine = GuardrailsEngine()
engine.add_input_guardrail(LengthValidatorGuardrail(
    "length_check",
    config={"min_length": 3, "max_length": 1000, "truncate": True}
))
engine.add_output_guardrail(PIIFilterGuardrail(
    "pii_filter", 
    config={"mask_emails": True, "replacement": "[REDACTED]"}
))

# Wrap your agent
guarded_agent = engine.wrap_agent(your_agent)

# Use normally - guardrails work transparently!
response = guarded_agent.chat("Hello there!")
```

#### Universal Agent Compatibility

The framework works with ANY agent interface through automatic detection:

```python
# Standard chat interface
class ChatAgent:
    def chat(self, user_input: str) -> str:
        return f"Response to: {user_input}"

# LangChain invoke interface  
class LangChainAgent:
    def invoke(self, input_data: dict) -> dict:
        return {"output": f"Processed: {input_data['input']}"}

# Older LangChain run interface
class OldLangChainAgent:
    def run(self, user_input: str) -> str:
        return f"Result: {user_input}"

# Callable agent (function-like)
class CallableAgent:
    def __call__(self, user_input: str) -> str:
        return f"Called with: {user_input}"

# Simple function agent
def function_agent(user_input: str) -> str:
    return f"Function result: {user_input}"

# ALL of these work automatically!
engine = GuardrailsEngine()
guarded_chat = engine.wrap_agent(ChatAgent())
guarded_langchain = engine.wrap_agent(LangChainAgent())  
guarded_old = engine.wrap_agent(OldLangChainAgent())
guarded_callable = engine.wrap_agent(CallableAgent())
guarded_function = engine.wrap_agent(function_agent)

# Same interface for all!
response1 = guarded_chat.chat("Hello")
response2 = guarded_langchain.chat("Hello")  # Automatically adapts invoke() to chat()
response3 = guarded_old.chat("Hello")        # Automatically adapts run() to chat()
response4 = guarded_callable.chat("Hello")   # Automatically adapts __call__() to chat()
response5 = guarded_function.chat("Hello")   # Automatically adapts function to chat()
```

#### Custom Agent Interfaces

For agents with custom method names, use explicit configuration:

```python
class CustomAgent:
    def process_message(self, text: str, priority: str = "normal") -> str:
        return f"Processed '{text}' with {priority} priority"

# Configure custom adapter
guarded_agent = engine.wrap_agent(
    CustomAgent(),
    adapter_type="custom",
    adapter_config={
        "method_name": "process_message",
        "input_transform": lambda text, **kwargs: ([text], {"priority": "high"}),
        "output_transform": lambda result: result
    }
)

response = guarded_agent.chat("Hello")  # Calls process_message internally
```

#### OpenAI Client Integration

Direct integration with OpenAI clients:

```python
import openai

client = openai.OpenAI(api_key="your-key")

# Wrap OpenAI client directly
guarded_openai = engine.wrap_agent(
    client,
    adapter_type="openai_client",
    adapter_config={
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful assistant."
    }
)

response = guarded_openai.chat("What is AI?")
```

#### Advanced Configuration
```python
# Strict mode - block instead of mask
strict_pii = PIIFilterGuardrail("strict_pii", config={
    "strict_mode": True,  # Block responses with PII
    "mask_emails": True,
    "mask_phones": True
})

# Length limits with custom messages
length_guard = LengthValidatorGuardrail("length", config={
    "min_length": 10,
    "max_length": 500,
    "truncate": True,
    "truncate_suffix": " [TRUNCATED]"
})

# Custom invoke adapter configuration
invoke_agent = engine.wrap_agent(
    langchain_agent,
    adapter_type="invoke",
    adapter_config={
        "input_key": "input",
        "output_key": "output" 
    }
)
```

#### Multiple Agents with Same Guardrails
```python
# Same guardrails can protect different agent types
agents = [
    ("OpenAI", openai_agent),
    ("Bedrock", bedrock_agent), 
    ("LangChain", langchain_agent),
    ("Custom", custom_agent)
]

guarded_agents = {}
for name, agent in agents:
    guarded_agents[name] = engine.wrap_agent(agent)
    
# All agents now have the same guardrails protection!
for name, guarded in guarded_agents.items():
    response = guarded.chat("Hello")
    print(f"{name}: {response}")
```

### Creating Custom Guardrails

```python
from guardrails.core.base import InputGuardrail
from guardrails.utils.result import GuardrailResult, GuardrailStatus

class CustomInputGuardrail(InputGuardrail):
    def validate(self, input_text: str, metadata=None) -> GuardrailResult:
        if "blocked_word" in input_text.lower():
            return GuardrailResult(
                status=GuardrailStatus.FAILED,
                message="Blocked word detected"
            )
        return GuardrailResult(
            status=GuardrailStatus.PASSED,
            message="Input is clean",
            modified_content=input_text
        )

# Use your custom guardrail
engine.add_input_guardrail(CustomInputGuardrail("custom_filter"))
```

## Usage

### Run the Interactive Agents

```bash
# OpenAI version (recommended for testing)
python agents/agent_openai.py

# AWS Bedrock version
python agents/agent.py

# Guardrails demo (shows protection in action)
python demo_scripts/demo_guardrails.py
```

### Example Conversation

```
🤖 Simple LangGraph + OpenAI Agent
==================================================
Type 'quit' or 'exit' to stop the conversation.
Type 'clear' to start a new conversation thread.

✅ Agent initialized successfully!
📍 Using model: gpt-3.5-turbo

You: Hello, can you explain what machine learning is?
🤔 Thinking...
🤖 Agent: Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and improve from experience without being explicitly programmed...

You: Can you give me a simple example?
🤔 Thinking...
🤖 Agent: Sure! A simple example is email spam detection. Instead of programming specific rules...
```

### Available Commands

- `quit` or `exit`: Stop the conversation
- `clear`: Start a new conversation thread (clears memory)
- Any other text: Send a message to the agent

## AWS Configuration

### Get AWS Access Keys

1. **Go to AWS IAM Console**: [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/)
2. **Click "Users"** in the left sidebar
3. **Find your username** and click on it
4. **Go to "Security credentials"** tab
5. **Click "Create access key"**
6. **Choose "Command Line Interface (CLI)"**
7. **Copy both Access Key ID and Secret Access Key** ⚠️ You won't see the secret key again!
8. **Add to your .env file**:

```bash
AWS_ACCESS_KEY_ID=AKIA1234567890EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
```

### Required AWS IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        }
    ]
}
```

### Request Bedrock Model Access

1. Go to AWS Bedrock Console
2. Navigate to "Model access" in the left sidebar
3. Request access to your desired models (e.g., Amazon Titan Text Express)
4. Wait for approval (usually instant for most models)

## Customization

### Change Models

#### OpenAI Models
Edit your `.env` file:
```bash
# Faster, cheaper (default)
OPENAI_MODEL=gpt-3.5-turbo

# More capable, expensive  
OPENAI_MODEL=gpt-4

# Latest GPT-4 variant
OPENAI_MODEL=gpt-4-turbo
```

#### Bedrock Models
```bash
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

Popular model options:
- `amazon.titan-text-express-v1` (default)
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `cohere.command-text-v14`

### Modify Model Parameters

Edit the model configuration in the agent files:
```python
self.llm = ChatOpenAI(
    model=self.model_name,
    temperature=0.3,      # Lower for more focused responses
    max_tokens=2000,      # Increase response length
)
```

## Troubleshooting

### Common Issues

1. **"AccessDeniedException"**: 
   - Check if you have requested access to the Bedrock model
   - Verify your IAM permissions

2. **"ValidationException"**: 
   - Ensure the model ID is correct and available in your region
   - Check that the model supports the parameters you're using

3. **"CredentialsNotFound"**: 
   - Verify your AWS credentials are properly configured
   - Check your `.env` file or AWS CLI configuration

4. **Import Errors**: 
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

5. **OpenAI API Errors**:
   - Verify your API key is valid
   - Check your usage quota at [OpenAI Usage](https://platform.openai.com/usage)

### Enable Debug Logging

Add to the beginning of any agent file:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Project Structure

```
├── agents/                    # 🤖 Agent Implementations
│   ├── agent.py               # AWS Bedrock LangGraph agent
│   ├── agent_openai.py        # OpenAI LangGraph agent
│   └── README.md              # Agent documentation
├── guardrails/                # 🛡️ Guardrails Framework
│   ├── __init__.py
│   ├── core/                  # Core engine and wrapper
│   ├── input_guardrails/      # Input validation guardrails
│   ├── output_guardrails/     # Output filtering guardrails
│   └── utils/                 # Utility classes
├── tests/                     # 🧪 Test Suite
│   ├── __init__.py
│   ├── test_guardrails.py     # Core guardrails tests
│   ├── test_adapters.py       # Adapter system tests
│   ├── test_agent_openai.py   # OpenAI agent tests
│   └── test_agent.py          # Bedrock agent tests
├── demo_scripts/              # 🎯 Demo Scripts
│   ├── demo_guardrails.py     # Guardrails demonstration
│   ├── demo_universal_agents.py # Universal compatibility demo
│   └── README.md              # Demo documentation
├── setup_scripts/             # ⚙️ Setup Scripts
│   ├── setup.py               # Setup automation
│   ├── check_openai_setup.py  # OpenAI setup verification
│   ├── check_aws_setup.py     # AWS setup verification
│   └── README.md              # Setup documentation
├── run_tests.py               # Test runner script
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Architecture

### LangGraph Agent Architecture
The agent follows LangGraph's state-based architecture:

1. **User Input**: Text input is received and converted to a `HumanMessage`
2. **State Management**: Messages are stored in the graph's state
3. **Model Invocation**: AWS Bedrock/OpenAI model processes the conversation
4. **Response Generation**: AI response is added to state and returned
5. **Memory**: Conversation history is maintained across interactions

### Guardrails Architecture
The guardrails use a transparent wrapper pattern:

1. **Input Processing**: User input passes through input guardrails
2. **Agent Execution**: Original agent processes the (potentially modified) input
3. **Output Processing**: Agent response passes through output guardrails
4. **Final Response**: User receives the (potentially modified) response

## Contributing

Feel free to submit issues and enhancement requests!

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python tests/test_guardrails.py      # Core guardrails
python tests/test_adapters.py        # Adapter system
python tests/test_agent_openai.py    # OpenAI integration
python tests/test_agent.py           # AWS Bedrock integration
```

### Adding New Guardrails

1. Create a new file in `guardrails/input_guardrails/` or `guardrails/output_guardrails/`
2. Inherit from `InputGuardrail` or `OutputGuardrail`
3. Implement the required `validate()` or `filter()` method
4. Add to the package `__init__.py`
5. Create tests in `tests/test_guardrails.py`

### Adding New Adapters

1. Create a new adapter class in `guardrails/core/adapters.py`
2. Inherit from `AgentAdapter`
3. Implement the required `chat()` method
4. Add to the adapter map in `create_adapter()`
5. Create tests in `tests/test_adapters.py`

## License

This project is provided as-is for educational and development purposes.
