"""
LangGraph Reporting Agent
A multi-step agent that helps users select templates, collect parameters, and schedule reports.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator
import json


# ============================================================================
# STATE DEFINITION
# ============================================================================

class ReportingAgentState(TypedDict):
    """State object for the reporting agent workflow"""
    messages: Annotated[List, operator.add]
    user_query: str
    available_templates: Optional[List[Dict]]
    selected_template: Optional[Dict]
    required_parameters: Optional[Dict]
    collected_parameters: Optional[Dict]
    validation_result: Optional[Dict]
    report_id: Optional[str]
    navigation_path: Optional[str]
    current_step: str
    user_confirmed: Optional[bool]
    error_message: Optional[str]


# ============================================================================
# MOCK TOOLS (Replace with actual API calls)
# ============================================================================

def get_available_templates() -> List[Dict]:
    """
    Tool: Retrieve all available report templates
    Replace this with actual API call to your backend
    """
    return [
        {
            "id": "sales_report",
            "name": "Sales Performance Report",
            "description": "Comprehensive sales analysis with revenue, trends, and forecasts",
            "category": "sales"
        },
        {
            "id": "customer_report",
            "name": "Customer Analytics Report",
            "description": "Customer behavior, segmentation, and retention analysis",
            "category": "customer"
        },
        {
            "id": "financial_report",
            "name": "Financial Summary Report",
            "description": "P&L, balance sheet, and financial KPIs",
            "category": "finance"
        },
        {
            "id": "inventory_report",
            "name": "Inventory Status Report",
            "description": "Stock levels, turnover rates, and reorder recommendations",
            "category": "operations"
        },
        {
            "id": "marketing_report",
            "name": "Marketing Campaign Report",
            "description": "Campaign performance, ROI, and engagement metrics",
            "category": "marketing"
        }
    ]


def get_template_parameters(template_id: str) -> Dict:
    """
    Tool: Get required parameters for a specific template
    Replace this with actual API call to your backend
    """
    parameter_map = {
        "sales_report": {
            "date_range": {
                "type": "date_range",
                "required": True,
                "description": "Start and end date for the report (e.g., '2024-01-01 to 2024-12-31')",
                "example": "2024-01-01 to 2024-12-31"
            },
            "region": {
                "type": "string",
                "required": True,
                "description": "Geographic region (e.g., 'North America', 'Europe', 'Asia', 'All')",
                "example": "North America"
            },
            "product_category": {
                "type": "string",
                "required": False,
                "description": "Specific product category to filter (optional)",
                "example": "Electronics"
            },
            "include_forecast": {
                "type": "boolean",
                "required": False,
                "description": "Include sales forecast (yes/no)",
                "default": "no"
            }
        },
        "customer_report": {
            "date_range": {
                "type": "date_range",
                "required": True,
                "description": "Analysis period (e.g., '2024-01-01 to 2024-12-31')",
                "example": "2024-01-01 to 2024-12-31"
            },
            "customer_segment": {
                "type": "string",
                "required": False,
                "description": "Customer segment (e.g., 'Enterprise', 'SMB', 'All')",
                "example": "Enterprise"
            },
            "metrics": {
                "type": "list",
                "required": True,
                "description": "Metrics to include (e.g., 'retention', 'churn', 'lifetime_value')",
                "example": "retention, churn, lifetime_value"
            }
        },
        "financial_report": {
            "fiscal_period": {
                "type": "string",
                "required": True,
                "description": "Fiscal period (e.g., 'Q1 2024', '2024', 'January 2024')",
                "example": "Q1 2024"
            },
            "department": {
                "type": "string",
                "required": False,
                "description": "Specific department (optional, default is 'All')",
                "example": "Sales"
            },
            "comparison_period": {
                "type": "string",
                "required": False,
                "description": "Period to compare against (e.g., 'Q1 2023')",
                "example": "Q1 2023"
            }
        },
        "inventory_report": {
            "warehouse": {
                "type": "string",
                "required": True,
                "description": "Warehouse location (e.g., 'Warehouse A', 'All')",
                "example": "Warehouse A"
            },
            "low_stock_threshold": {
                "type": "number",
                "required": False,
                "description": "Threshold for low stock alerts (number of units)",
                "example": "50"
            },
            "category_filter": {
                "type": "string",
                "required": False,
                "description": "Product category filter (optional)",
                "example": "Electronics"
            }
        },
        "marketing_report": {
            "campaign_id": {
                "type": "string",
                "required": True,
                "description": "Campaign ID or name",
                "example": "SPRING2024"
            },
            "date_range": {
                "type": "date_range",
                "required": True,
                "description": "Campaign period",
                "example": "2024-03-01 to 2024-05-31"
            },
            "channels": {
                "type": "list",
                "required": False,
                "description": "Marketing channels (e.g., 'email', 'social', 'ppc')",
                "example": "email, social"
            }
        }
    }
    return parameter_map.get(template_id, {})


def validate_parameters(template_id: str, parameters: Dict) -> Dict:
    """
    Tool: Validate collected parameters against template requirements
    Replace with actual validation logic
    """
    required_params = get_template_parameters(template_id)
    errors = []
    
    # Check required fields
    for param_name, param_info in required_params.items():
        if param_info.get("required") and param_name not in parameters:
            errors.append(f"Missing required parameter: {param_name}")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True, "errors": []}


def schedule_report(template_id: str, parameters: Dict, user_id: str = "user123") -> Dict:
    """
    Tool: Call API to schedule report generation
    Replace with actual API call to your backend
    """
    # Mock API call
    import uuid
    from datetime import datetime, timedelta
    
    report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    scheduled_time = datetime.now()
    estimated_completion = scheduled_time + timedelta(minutes=15)
    
    return {
        "success": True,
        "report_id": report_id,
        "scheduled_at": scheduled_time.isoformat(),
        "estimated_completion": estimated_completion.isoformat(),
        "status": "scheduled"
    }


def get_report_navigation_path(report_id: str) -> str:
    """
    Tool: Generate navigation path for accessing the report
    Replace with actual navigation logic
    """
    return f"""
To view your report:

1. Go to Dashboard → Reports
2. Click on "My Reports" tab
3. Look for Report ID: {report_id}
4. Or use this direct link: https://your-app.com/reports/{report_id}

The report will be available in approximately 15 minutes.
You'll receive an email notification when it's ready.
"""


# ============================================================================
# AGENT NODE FUNCTIONS
# ============================================================================

def understand_query_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 1: Understand user query and retrieve available templates
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Get available templates
    templates = get_available_templates()
    state["available_templates"] = templates
    
    # Create system message for template selection
    system_message = f"""You are a helpful reporting assistant. The user wants to generate a report.
Available templates:
{json.dumps(templates, indent=2)}

Based on the user's query, identify which template(s) would be most appropriate.
Analyze the query and respond with your recommendation."""
    
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=state["user_query"])
    ]
    
    response = llm.invoke(messages)
    state["messages"].append(AIMessage(content=response.content))
    state["current_step"] = "select_template"
    
    return state


def select_template_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 2: Select the most appropriate template based on user query
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    templates_json = json.dumps(state["available_templates"], indent=2)
    
    system_message = f"""Based on the conversation, select the SINGLE most appropriate template.
Available templates:
{templates_json}

Respond with ONLY a valid JSON object in this format:
{{"template_id": "selected_template_id", "reasoning": "brief explanation"}}"""
    
    messages = state["messages"] + [SystemMessage(content=system_message)]
    response = llm.invoke(messages)
    
    # Parse the response to extract template selection
    try:
        # Extract JSON from response
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        selection = json.loads(content)
        template_id = selection["template_id"]
        
        # Find the selected template
        selected = next((t for t in state["available_templates"] if t["id"] == template_id), None)
        
        if selected:
            state["selected_template"] = selected
            state["current_step"] = "confirm_template"
        else:
            state["error_message"] = "Could not find the selected template"
            state["current_step"] = "error"
    except Exception as e:
        state["error_message"] = f"Error parsing template selection: {str(e)}"
        state["current_step"] = "error"
    
    return state


def confirm_template_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 3: Ask user to confirm template selection
    """
    template = state["selected_template"]
    
    confirmation_message = f"""I recommend the **{template['name']}** template for your request.

Description: {template['description']}

Is this the correct template for your needs? Please reply with 'yes' to proceed or 'no' to select a different template."""
    
    state["messages"].append(AIMessage(content=confirmation_message))
    state["current_step"] = "wait_for_confirmation"
    
    return state


def collect_parameters_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 4: Collect required parameters from user
    """
    template_id = state["selected_template"]["id"]
    required_params = get_template_parameters(template_id)
    state["required_parameters"] = required_params
    
    if state.get("collected_parameters") is None:
        state["collected_parameters"] = {}
    
    # Find next missing parameter
    missing_params = [
        (name, info) for name, info in required_params.items()
        if info.get("required") and name not in state["collected_parameters"]
    ]
    
    if missing_params:
        # Ask for the next missing parameter
        param_name, param_info = missing_params[0]
        
        question = f"""Please provide the **{param_name.replace('_', ' ').title()}**:

Description: {param_info['description']}
Example: {param_info.get('example', 'N/A')}"""
        
        state["messages"].append(AIMessage(content=question))
        state["current_step"] = "waiting_for_parameter"
    else:
        # All required parameters collected, ask about optional ones
        optional_params = [
            (name, info) for name, info in required_params.items()
            if not info.get("required") and name not in state["collected_parameters"]
        ]
        
        if optional_params:
            param_list = "\n".join([f"- {name.replace('_', ' ').title()}: {info['description']}" 
                                   for name, info in optional_params])
            
            question = f"""All required parameters collected! Would you like to provide optional parameters?

Optional parameters:
{param_list}

Reply with the parameter name and value, or 'skip' to proceed with defaults."""
            
            state["messages"].append(AIMessage(content=question))
            state["current_step"] = "waiting_for_optional_parameter"
        else:
            state["current_step"] = "verify_inputs"
    
    return state


def verify_inputs_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 5: Show all collected parameters and ask for confirmation
    """
    params = state["collected_parameters"]
    template_name = state["selected_template"]["name"]
    
    # Format parameters nicely
    param_list = "\n".join([f"- **{key.replace('_', ' ').title()}**: {value}" 
                           for key, value in params.items()])
    
    verification_message = f"""Please review the report configuration:

**Template**: {template_name}

**Parameters**:
{param_list}

Is this correct? Reply 'yes' to schedule the report, 'no' to make changes, or specify which parameter you'd like to update."""
    
    state["messages"].append(AIMessage(content=verification_message))
    state["current_step"] = "wait_for_verification"
    
    return state


def schedule_report_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 6: Schedule the report via API
    """
    template_id = state["selected_template"]["id"]
    parameters = state["collected_parameters"]
    
    # Validate parameters first
    validation = validate_parameters(template_id, parameters)
    state["validation_result"] = validation
    
    if not validation["valid"]:
        error_msg = f"""There are validation errors:
{chr(10).join(['- ' + err for err in validation['errors']])}

Please provide the missing information."""
        state["messages"].append(AIMessage(content=error_msg))
        state["current_step"] = "collect_parameters"
        return state
    
    # Schedule the report
    try:
        result = schedule_report(template_id, parameters)
        
        if result["success"]:
            state["report_id"] = result["report_id"]
            state["current_step"] = "show_navigation"
            
            success_msg = f"""✅ Report scheduled successfully!

**Report ID**: {result['report_id']}
**Status**: {result['status']}
**Estimated Completion**: {result['estimated_completion']}"""
            
            state["messages"].append(AIMessage(content=success_msg))
        else:
            state["error_message"] = "Failed to schedule report"
            state["current_step"] = "error"
    except Exception as e:
        state["error_message"] = f"Error scheduling report: {str(e)}"
        state["current_step"] = "error"
    
    return state


def show_navigation_node(state: ReportingAgentState) -> ReportingAgentState:
    """
    Node 7: Show user how to access the report
    """
    report_id = state["report_id"]
    navigation = get_report_navigation_path(report_id)
    
    state["navigation_path"] = navigation
    state["messages"].append(AIMessage(content=navigation))
    state["current_step"] = "complete"
    
    return state


def handle_user_response(state: ReportingAgentState) -> ReportingAgentState:
    """
    Handle user responses at various stages
    """
    if not state["messages"]:
        return state
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return state
    
    user_input = last_message.content.lower().strip()
    current_step = state["current_step"]
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Handle confirmation responses
    if current_step == "wait_for_confirmation":
        if "yes" in user_input or "correct" in user_input or "proceed" in user_input:
            state["user_confirmed"] = True
            state["current_step"] = "collect_parameters"
        else:
            state["user_confirmed"] = False
            state["current_step"] = "select_template"
            state["messages"].append(AIMessage(content="Let me help you choose a different template. Which type of report are you looking for?"))
    
    # Handle parameter collection
    elif current_step == "waiting_for_parameter":
        # Extract parameter value using LLM
        required_params = state["required_parameters"]
        missing_params = [
            name for name, info in required_params.items()
            if info.get("required") and name not in state["collected_parameters"]
        ]
        
        if missing_params:
            param_name = missing_params[0]
            state["collected_parameters"][param_name] = user_input
            state["current_step"] = "collect_parameters"
    
    # Handle optional parameters
    elif current_step == "waiting_for_optional_parameter":
        if "skip" in user_input or "no" in user_input or "proceed" in user_input:
            state["current_step"] = "verify_inputs"
        else:
            # Try to extract parameter name and value
            # Simple parsing - in production, use LLM to extract structured data
            state["current_step"] = "collect_parameters"
    
    # Handle verification
    elif current_step == "wait_for_verification":
        if "yes" in user_input or "correct" in user_input or "confirm" in user_input:
            state["current_step"] = "schedule_report"
        else:
            state["messages"].append(AIMessage(content="Which parameter would you like to change?"))
            state["current_step"] = "waiting_for_parameter_update"
    
    return state


# ============================================================================
# CONDITIONAL EDGES
# ============================================================================

def should_continue_after_confirmation(state: ReportingAgentState) -> str:
    """Decide next step after template confirmation"""
    if state.get("user_confirmed"):
        return "collect_parameters"
    return "select_template"


def should_continue_parameter_collection(state: ReportingAgentState) -> str:
    """Decide if more parameters need to be collected"""
    current_step = state.get("current_step")
    
    if current_step == "verify_inputs":
        return "verify_inputs"
    elif current_step == "waiting_for_parameter" or current_step == "waiting_for_optional_parameter":
        return "wait_for_user"
    else:
        return "collect_more"


def should_continue_after_verification(state: ReportingAgentState) -> str:
    """Decide next step after input verification"""
    current_step = state.get("current_step")
    
    if current_step == "schedule_report":
        return "schedule"
    else:
        return "wait_for_user"


# ============================================================================
# BUILD THE GRAPH
# ============================================================================

def create_reporting_agent():
    """Create and compile the reporting agent graph"""
    
    workflow = StateGraph(ReportingAgentState)
    
    # Add nodes
    workflow.add_node("understand_query", understand_query_node)
    workflow.add_node("select_template", select_template_node)
    workflow.add_node("confirm_template", confirm_template_node)
    workflow.add_node("handle_response", handle_user_response)
    workflow.add_node("collect_parameters", collect_parameters_node)
    workflow.add_node("verify_inputs", verify_inputs_node)
    workflow.add_node("schedule_report", schedule_report_node)
    workflow.add_node("show_navigation", show_navigation_node)
    
    # Set entry point
    workflow.set_entry_point("understand_query")
    
    # Add edges
    workflow.add_edge("understand_query", "select_template")
    workflow.add_edge("select_template", "confirm_template")
    workflow.add_edge("confirm_template", "handle_response")
    
    # Conditional edge after confirmation
    workflow.add_conditional_edges(
        "handle_response",
        lambda state: state.get("current_step", ""),
        {
            "collect_parameters": "collect_parameters",
            "select_template": "select_template",
            "verify_inputs": "verify_inputs",
            "schedule_report": "schedule_report",
            "waiting_for_parameter": "handle_response",
            "waiting_for_optional_parameter": "handle_response",
            "wait_for_verification": "handle_response",
        }
    )
    
    workflow.add_conditional_edges(
        "collect_parameters",
        lambda state: state.get("current_step", ""),
        {
            "waiting_for_parameter": "handle_response",
            "waiting_for_optional_parameter": "handle_response",
            "verify_inputs": "verify_inputs",
        }
    )
    
    workflow.add_edge("verify_inputs", "handle_response")
    workflow.add_edge("schedule_report", "show_navigation")
    workflow.add_edge("show_navigation", END)
    
    return workflow.compile()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    agent = create_reporting_agent()
    
    # Initial state
    initial_state = {
        "messages": [],
        "user_query": "I need a sales report for Q1 2024",
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
    
    print("=" * 80)
    print("REPORTING AGENT - Example Run")
    print("=" * 80)
    print(f"\nUser Query: {initial_state['user_query']}\n")
    
    # This would be run in an interactive loop in production
    # For now, showing the structure
    result = agent.invoke(initial_state)
    
    print("\nAgent Messages:")
    print("-" * 80)
    for msg in result["messages"]:
        if isinstance(msg, AIMessage):
            print(f"\n🤖 Assistant: {msg.content}")
        elif isinstance(msg, HumanMessage):
            print(f"\n👤 User: {msg.content}")
    
    print("\n" + "=" * 80)
    print(f"Final State: {result['current_step']}")
    print("=" * 80)
