"""
Human-in-the-Loop Decorator Module
Provides decorators for requiring human confirmation before critical operations
"""

from typing import Callable, Any, Dict, Optional
from functools import wraps
from langchain_core.messages import HumanMessage, AIMessage
import time


class HumanConfirmationRequired(Exception):
    """Exception raised when human confirmation is required"""
    pass


class HumanConfirmationRejected(Exception):
    """Exception raised when human rejects the action"""
    pass


def require_human_confirmation(
    confirmation_message: str = None,
    custom_prompt: str = None,
    allow_details: bool = True,
    timeout: Optional[int] = None
):
    """
    Decorator that requires human confirmation before executing a function.
    
    This decorator is designed to work with LangGraph agent nodes that operate
    on state dictionaries containing a 'messages' key.
    
    Args:
        confirmation_message: Custom message to show when asking for confirmation
        custom_prompt: Custom prompt text (default: "Type 'yes' to confirm or 'no' to cancel")
        allow_details: If True, shows function details and parameters
        timeout: Optional timeout in seconds for user response
        
    Usage:
        @require_human_confirmation(
            confirmation_message="About to schedule your report",
            allow_details=True
        )
        def schedule_report_node(state):
            # ... scheduling logic
            return state
    
    The decorator expects the state to have:
        - state['messages']: List of conversation messages
        - state['human_confirmation_pending']: Boolean flag (added by decorator)
        - state['human_confirmation_response']: User's response (yes/no)
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # Check if we're waiting for confirmation
            if state.get('human_confirmation_pending'):
                # Get the last human message
                human_messages = [msg for msg in state.get('messages', []) 
                                if isinstance(msg, HumanMessage)]
                
                if human_messages:
                    last_response = human_messages[-1].content.lower().strip()
                    
                    # Parse response
                    if 'yes' in last_response or last_response == 'y':
                        # User confirmed - proceed with function
                        state['human_confirmation_pending'] = False
                        state['human_confirmation_response'] = 'yes'
                        state['messages'].append(
                            AIMessage(content="✅ Confirmed! Proceeding with the operation...")
                        )
                        # Execute the actual function
                        return func(state)
                    
                    elif 'no' in last_response or last_response == 'n':
                        # User rejected - cancel operation
                        state['human_confirmation_pending'] = False
                        state['human_confirmation_response'] = 'no'
                        state['current_step'] = 'cancelled'
                        state['messages'].append(
                            AIMessage(content="❌ Operation cancelled. How else can I help you?")
                        )
                        return state
                    
                    else:
                        # Invalid response - ask again
                        prompt_text = custom_prompt or "Please type 'yes' to confirm or 'no' to cancel:"
                        state['messages'].append(
                            AIMessage(content=f"Invalid response. {prompt_text}")
                        )
                        return state
            
            # First time - request confirmation
            state['human_confirmation_pending'] = True
            
            # Build confirmation message
            if confirmation_message:
                message = confirmation_message
            else:
                message = f"⚠️  **Confirmation Required**\n\nYou are about to execute: `{func.__name__}`"
            
            # Add function details if requested
            if allow_details:
                details = _extract_function_details(state, func)
                if details:
                    message += f"\n\n**Details:**\n{details}"
            
            # Add prompt
            prompt_text = custom_prompt or "**Type 'yes' to confirm or 'no' to cancel:**"
            message += f"\n\n{prompt_text}"
            
            state['messages'].append(AIMessage(content=message))
            state['current_step'] = 'awaiting_human_confirmation'
            
            return state
        
        return wrapper
    return decorator


def _extract_function_details(state: Dict[str, Any], func: Callable) -> str:
    """Extract relevant details from state for confirmation message"""
    details = []
    
    # Add template information
    if state.get('selected_template'):
        template = state['selected_template']
        details.append(f"- **Template**: {template.get('name', 'Unknown')}")
    
    # Add parameters
    if state.get('collected_parameters'):
        params = state['collected_parameters']
        details.append(f"- **Parameters**:")
        for key, value in params.items():
            details.append(f"  - {key.replace('_', ' ').title()}: {value}")
    
    # Add report ID if available
    if state.get('report_id'):
        details.append(f"- **Report ID**: {state['report_id']}")
    
    return "\n".join(details) if details else ""


def create_confirmation_prompt(
    action: str,
    details: Dict[str, Any],
    warning: Optional[str] = None
) -> str:
    """
    Helper function to create a formatted confirmation prompt
    
    Args:
        action: Description of the action to confirm
        details: Dictionary of details to display
        warning: Optional warning message
        
    Returns:
        Formatted confirmation message
    """
    message = f"⚠️  **Confirmation Required**\n\n**Action**: {action}\n\n"
    
    if details:
        message += "**Details**:\n"
        for key, value in details.items():
            message += f"- **{key}**: {value}\n"
        message += "\n"
    
    if warning:
        message += f"⚠️  **Warning**: {warning}\n\n"
    
    message += "**Type 'yes' to confirm or 'no' to cancel:**"
    
    return message


def simple_human_confirmation(prompt: str = "Do you want to proceed?") -> bool:
    """
    Simple synchronous human confirmation (for non-agent use)
    
    Args:
        prompt: Question to ask the user
        
    Returns:
        True if user confirms, False otherwise
    """
    while True:
        response = input(f"\n{prompt} (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Invalid response. Please type 'yes' or 'no'.")


# ============================================================================
# Enhanced Decorator with Additional Options
# ============================================================================

class HumanInTheLoopConfirmation:
    """
    Advanced human-in-the-loop confirmation handler with additional features
    """
    
    def __init__(
        self,
        confirmation_message: str = None,
        require_reason_on_reject: bool = False,
        allow_modification: bool = False,
        critical_operation: bool = False,
        auto_timeout_seconds: Optional[int] = None
    ):
        """
        Initialize the confirmation handler
        
        Args:
            confirmation_message: Custom confirmation message
            require_reason_on_reject: If True, ask for reason when user rejects
            allow_modification: If True, allow user to modify before confirming
            critical_operation: If True, show additional warnings
            auto_timeout_seconds: Auto-reject after timeout (None = no timeout)
        """
        self.confirmation_message = confirmation_message
        self.require_reason_on_reject = require_reason_on_reject
        self.allow_modification = allow_modification
        self.critical_operation = critical_operation
        self.auto_timeout_seconds = auto_timeout_seconds
    
    def __call__(self, func: Callable) -> Callable:
        """Make the class instance callable as a decorator"""
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # Check if we're waiting for confirmation
            if state.get('human_confirmation_pending'):
                return self._handle_confirmation_response(state, func)
            
            # First time - request confirmation
            return self._request_confirmation(state, func)
        
        return wrapper
    
    def _request_confirmation(self, state: Dict[str, Any], func: Callable) -> Dict[str, Any]:
        """Request confirmation from human"""
        state['human_confirmation_pending'] = True
        state['human_confirmation_timestamp'] = time.time()
        
        # Build message
        message = self.confirmation_message or f"⚠️  **Confirmation Required for: {func.__name__}**"
        
        if self.critical_operation:
            message = "🚨 " + message
            message += "\n\n**⚠️  This is a CRITICAL operation. Please review carefully.**"
        
        # Add details
        details = _extract_function_details(state, func)
        if details:
            message += f"\n\n{details}"
        
        # Add options
        message += "\n\n**Options**:"
        message += "\n- Type **'yes'** or **'y'** to confirm and proceed"
        message += "\n- Type **'no'** or **'n'** to cancel"
        
        if self.allow_modification:
            message += "\n- Type **'modify'** or **'change'** to make changes"
        
        if self.auto_timeout_seconds:
            message += f"\n\n⏱️  *Auto-cancel in {self.auto_timeout_seconds} seconds if no response*"
        
        state['messages'].append(AIMessage(content=message))
        state['current_step'] = 'awaiting_human_confirmation'
        
        return state
    
    def _handle_confirmation_response(self, state: Dict[str, Any], func: Callable) -> Dict[str, Any]:
        """Handle user's confirmation response"""
        
        # Check for timeout
        if self.auto_timeout_seconds:
            timestamp = state.get('human_confirmation_timestamp', 0)
            if time.time() - timestamp > self.auto_timeout_seconds:
                state['human_confirmation_pending'] = False
                state['current_step'] = 'cancelled'
                state['messages'].append(
                    AIMessage(content="⏱️ Operation cancelled due to timeout.")
                )
                return state
        
        # Get last human message
        human_messages = [msg for msg in state.get('messages', []) 
                        if isinstance(msg, HumanMessage)]
        
        if not human_messages:
            return state
        
        last_response = human_messages[-1].content.lower().strip()
        
        # Handle YES
        if last_response in ['yes', 'y', 'confirm', 'proceed']:
            state['human_confirmation_pending'] = False
            state['human_confirmation_response'] = 'yes'
            state['messages'].append(
                AIMessage(content="✅ Confirmed! Proceeding with the operation...")
            )
            # Execute the actual function
            return func(state)
        
        # Handle NO
        elif last_response in ['no', 'n', 'cancel', 'abort']:
            state['human_confirmation_pending'] = False
            state['human_confirmation_response'] = 'no'
            
            if self.require_reason_on_reject:
                if not state.get('rejection_reason_requested'):
                    state['rejection_reason_requested'] = True
                    state['messages'].append(
                        AIMessage(content="Could you please provide a reason for cancellation?")
                    )
                    return state
                else:
                    # Save rejection reason
                    state['rejection_reason'] = last_response
                    state['rejection_reason_requested'] = False
            
            state['current_step'] = 'cancelled'
            state['messages'].append(
                AIMessage(content="❌ Operation cancelled. How else can I help you?")
            )
            return state
        
        # Handle MODIFY
        elif self.allow_modification and last_response in ['modify', 'change', 'edit']:
            state['human_confirmation_pending'] = False
            state['current_step'] = 'verify_inputs'  # Go back to verification
            state['messages'].append(
                AIMessage(content="Which parameter would you like to modify?")
            )
            return state
        
        # Invalid response
        else:
            state['messages'].append(
                AIMessage(content="Invalid response. Please type 'yes', 'no'" + 
                                (" or 'modify'" if self.allow_modification else "") + ".")
            )
            return state


# ============================================================================
# Usage Examples
# ============================================================================

def example_basic_decorator():
    """Example: Basic confirmation decorator"""
    
    from reporting_agent import ReportingAgentState
    
    @require_human_confirmation(
        confirmation_message="🚀 About to schedule your report",
        allow_details=True
    )
    def schedule_report_node(state: ReportingAgentState) -> ReportingAgentState:
        """Schedule the report (with confirmation)"""
        # ... your scheduling logic here
        state['report_id'] = "RPT-12345"
        state['current_step'] = 'show_navigation'
        return state
    
    return schedule_report_node


def example_advanced_decorator():
    """Example: Advanced confirmation with all options"""
    
    from reporting_agent import ReportingAgentState
    
    @HumanInTheLoopConfirmation(
        confirmation_message="⚠️  Schedule Report Confirmation",
        require_reason_on_reject=True,
        allow_modification=True,
        critical_operation=True,
        auto_timeout_seconds=300  # 5 minutes
    )
    def schedule_report_node(state: ReportingAgentState) -> ReportingAgentState:
        """Schedule the report (with advanced confirmation)"""
        # ... your scheduling logic here
        state['report_id'] = "RPT-12345"
        state['current_step'] = 'show_navigation'
        return state
    
    return schedule_report_node


def example_custom_confirmation():
    """Example: Custom confirmation logic"""
    
    def schedule_report_node(state):
        """Schedule report with custom confirmation"""
        
        # Check if already confirmed
        if not state.get('schedule_confirmed'):
            # Create custom confirmation message
            template = state['selected_template']['name']
            params = state['collected_parameters']
            
            message = create_confirmation_prompt(
                action=f"Schedule {template}",
                details={
                    "Template": template,
                    "Date Range": params.get('date_range'),
                    "Region": params.get('region'),
                    "Priority": "High"
                },
                warning="This will consume API quota and cannot be undone."
            )
            
            state['messages'].append(AIMessage(content=message))
            state['schedule_confirmed'] = False
            state['current_step'] = 'awaiting_schedule_confirmation'
            return state
        
        # Confirmation received - proceed
        # ... scheduling logic
        state['report_id'] = "RPT-12345"
        return state
    
    return schedule_report_node


# ============================================================================
# Integration Helper
# ============================================================================

def add_confirmation_to_graph(workflow, node_name: str, confirmation_config: Dict = None):
    """
    Helper to add confirmation step to an existing LangGraph workflow
    
    Args:
        workflow: The StateGraph instance
        node_name: Name of the node to add confirmation before
        confirmation_config: Configuration for the confirmation
        
    Example:
        workflow = StateGraph(ReportingAgentState)
        workflow.add_node("schedule_report", schedule_report_node)
        
        add_confirmation_to_graph(
            workflow, 
            "schedule_report",
            {"critical_operation": True}
        )
    """
    confirmation_config = confirmation_config or {}
    
    # Create a confirmation wrapper
    original_node = workflow._nodes.get(node_name)
    
    if original_node:
        # Apply decorator
        if confirmation_config:
            decorated_node = HumanInTheLoopConfirmation(**confirmation_config)(original_node)
        else:
            decorated_node = require_human_confirmation()(original_node)
        
        # Replace the node
        workflow._nodes[node_name] = decorated_node


if __name__ == "__main__":
    """
    Test the decorator functionality
    """
    
    print("=" * 70)
    print("HUMAN-IN-THE-LOOP CONFIRMATION DECORATOR - Test")
    print("=" * 70)
    
    # Example 1: Basic decorator
    print("\n1. Basic Decorator Example:")
    print("-" * 70)
    
    @require_human_confirmation(confirmation_message="Test operation")
    def test_function(state):
        state['executed'] = True
        return state
    
    print("✓ Decorator applied successfully")
    
    # Example 2: Advanced decorator
    print("\n2. Advanced Decorator Example:")
    print("-" * 70)
    
    @HumanInTheLoopConfirmation(
        confirmation_message="Advanced test",
        critical_operation=True,
        allow_modification=True
    )
    def advanced_test_function(state):
        state['executed'] = True
        return state
    
    print("✓ Advanced decorator applied successfully")
    
    # Example 3: Custom prompt
    print("\n3. Custom Confirmation Prompt:")
    print("-" * 70)
    
    prompt = create_confirmation_prompt(
        action="Delete all data",
        details={
            "Records": "1,234",
            "Tables": "5",
            "Size": "10GB"
        },
        warning="This action cannot be undone!"
    )
    print(prompt)
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
