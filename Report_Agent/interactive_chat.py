"""
Interactive Chat Interface for Reporting Agent
Run this to interact with the agent in a conversation flow
"""

from reporting_agent import create_reporting_agent, ReportingAgentState
from langchain_core.messages import HumanMessage, AIMessage
import os


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def print_message(message, is_user=False):
    """Pretty print messages"""
    if is_user:
        print(f"\n👤 You: {message}")
    else:
        print(f"\n🤖 Assistant: {message}")


def run_interactive_agent():
    """Run the agent in interactive mode"""
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("Please set it using: export OPENAI_API_KEY='your-api-key'")
        return
    
    print_separator()
    print("🤖 REPORTING AGENT - Interactive Mode")
    print_separator()
    print("\nWelcome! I'll help you create a report.")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    print_separator()
    
    # Get initial query
    user_query = input("\n👤 You: What report would you like to create?\n> ").strip()
    
    if user_query.lower() in ['quit', 'exit']:
        print("\nGoodbye!")
        return
    
    # Initialize agent and state
    agent = create_reporting_agent()
    
    state: ReportingAgentState = {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "available_templates": None,
        "selected_template": None,
        "required_parameters": None,
        "collected_parameters": None,
        "validation_result": None,
        "report_id": None,
        "navigation_path": None,
        "current_step": "start",
        "user_confirmed": None,
        "error_message": None
    }
    
    # Main conversation loop
    while state.get("current_step") != "complete":
        try:
            # Run the agent
            result = agent.invoke(state)
            
            # Get the last AI message
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                # Check if this message was already printed
                if not state.get("messages") or last_ai_message not in state.get("messages", []):
                    print_message(last_ai_message.content, is_user=False)
            
            # Update state
            state = result
            
            # Check if we're done
            if state.get("current_step") == "complete":
                print("\n✅ Report process completed successfully!")
                break
            
            # Check for errors
            if state.get("current_step") == "error":
                print(f"\n❌ Error: {state.get('error_message')}")
                break
            
            # Check if we need user input
            needs_input = state.get("current_step") in [
                "wait_for_confirmation",
                "waiting_for_parameter",
                "waiting_for_optional_parameter",
                "wait_for_verification",
                "waiting_for_parameter_update"
            ]
            
            if needs_input:
                # Get user input
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye!")
                    break
                
                # Add user message to state
                state["messages"].append(HumanMessage(content=user_input))
            else:
                # Agent is processing, continue
                continue
                
        except KeyboardInterrupt:
            print("\n\nProcess interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again or type 'quit' to exit.")
            break
    
    print_separator()


def run_example_scenarios():
    """Run pre-defined example scenarios"""
    
    print_separator()
    print("🤖 REPORTING AGENT - Example Scenarios")
    print_separator()
    
    scenarios = [
        {
            "name": "Sales Report",
            "query": "I need a sales report for Q1 2024 in North America",
            "responses": [
                "yes",  # Confirm template
                "2024-01-01 to 2024-03-31",  # Date range
                "North America",  # Region
                "skip",  # Optional parameters
                "yes"  # Confirm inputs
            ]
        },
        {
            "name": "Customer Analytics",
            "query": "Show me customer retention metrics",
            "responses": [
                "yes",
                "2024-01-01 to 2024-12-31",
                "Enterprise",
                "retention, churn, lifetime_value",
                "yes"
            ]
        }
    ]
    
    print("\nAvailable scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}: {scenario['query']}")
    
    choice = input("\nSelect a scenario (1-2) or press Enter to skip: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(scenarios):
        scenario = scenarios[int(choice) - 1]
        print(f"\n▶️  Running scenario: {scenario['name']}")
        print(f"Query: {scenario['query']}\n")
        print("(This is a simulation - in production, run the interactive mode)\n")
    else:
        print("\nSkipping scenarios. Run interactive mode for full experience.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        run_example_scenarios()
    else:
        run_interactive_agent()
