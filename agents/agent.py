"""
Simple LangGraph Agent with AWS Bedrock Integration

This agent takes user input, processes it through AWS Bedrock model,
and returns the response.
"""

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Define the state schema
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

class BedrockAgent:
    def __init__(self):
        """Initialize the Bedrock agent with AWS configuration."""
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        # Initialize the Bedrock model
        self.llm = ChatBedrock(
            model_id=self.model_id,
            region_name=self.region,
            model_kwargs={
                # "max_tokens": 1000,
                # "temperature": 0.7,
            }
        )
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create the LangGraph state graph."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add the agent node
        workflow.add_node("agent", self._call_model)
        
        # Set entry point
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        
        # Compile the graph with memory
        memory = MemorySaver()
        graph = workflow.compile(checkpointer=memory)
        
        return graph
    
    def _call_model(self, state: AgentState):
        """Call the Bedrock model with the current state."""
        try:
            # Get the last message from the state
            messages = state["messages"]
            
            # Call the model
            response = self.llm.invoke(messages)
            
            # Return the response
            return {"messages": [response]}
            
        except Exception as e:
            error_message = AIMessage(content=f"Error calling Bedrock model: {str(e)}")
            return {"messages": [error_message]}
    
    def chat(self, user_input: str, thread_id: str = "default"):
        """
        Process user input and return model response.
        
        Args:
            user_input: The user's text input
            thread_id: Conversation thread ID for memory
            
        Returns:
            str: The model's response
        """
        try:
            # Create the input message
            input_message = HumanMessage(content=user_input)
            
            # Create the config with thread ID for memory
            config = {"configurable": {"thread_id": thread_id}}
            
            # Invoke the graph
            result = self.graph.invoke(
                {"messages": [input_message]}, 
                config=config
            )
            
            # Extract and return the response
            if result["messages"]:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            else:
                return "No response generated."
                
        except Exception as e:
            return f"Error processing request: {str(e)}"

def main():
    """Main function to run the interactive chat."""
    print("🤖 Simple LangGraph + AWS Bedrock Agent")
    print("=" * 50)
    print("Type 'quit' or 'exit' to stop the conversation.")
    print("Type 'clear' to start a new conversation thread.")
    print()
    
    # Initialize the agent
    try:
        agent = BedrockAgent()
        print("✅ Agent initialized successfully!")
        print(f"📍 Using model: {agent.model_id}")
        print(f"🌍 Region: {agent.region}")
        print()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("Please check your AWS configuration and try again.")
        return
    
    thread_id = "main_conversation"
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            # Check for clear command
            if user_input.lower() == 'clear':
                thread_id = f"conversation_{hash(str(os.urandom(8)))}"
                print("🗑️ Conversation history cleared.")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Get agent response
            print("🤔 Thinking...")
            response = agent.chat(user_input, thread_id)
            
            # Print the response
            print(f"🤖 Agent: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    main() 