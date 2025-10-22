"""
API Integration Examples
Replace the mock functions in reporting_agent.py with these real API implementations
"""

import requests
from typing import List, Dict, Optional
import os
from datetime import datetime, timedelta


class ReportingAPIClient:
    """
    Client for interacting with your reporting backend API
    Replace base_url and authentication with your actual values
    """
    
    def __init__(self, base_url: str = None, api_token: str = None):
        self.base_url = base_url or os.getenv("REPORTING_API_BASE_URL", "https://your-api.com")
        self.api_token = api_token or os.getenv("REPORTING_API_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get_available_templates(self) -> List[Dict]:
        """
        Fetch available report templates from your backend
        
        GET /api/v1/templates
        
        Returns:
            List of template objects
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/templates",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("templates", [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching templates: {e}")
            # Fallback to default templates
            return self._get_default_templates()
    
    def get_template_parameters(self, template_id: str) -> Dict:
        """
        Get parameter requirements for a specific template
        
        GET /api/v1/templates/{template_id}/parameters
        
        Args:
            template_id: The template identifier
            
        Returns:
            Dictionary of parameter definitions
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/templates/{template_id}/parameters",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("parameters", {})
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching template parameters: {e}")
            return {}
    
    def validate_parameters(self, template_id: str, parameters: Dict) -> Dict:
        """
        Validate parameters against template requirements
        
        POST /api/v1/templates/{template_id}/validate
        
        Args:
            template_id: The template identifier
            parameters: Dictionary of parameters to validate
            
        Returns:
            Validation result with valid flag and errors list
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/templates/{template_id}/validate",
                headers=self.headers,
                json={"parameters": parameters},
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error validating parameters: {e}")
            return {"valid": False, "errors": [f"Validation service error: {str(e)}"]}
    
    def schedule_report(
        self,
        template_id: str,
        parameters: Dict,
        user_id: str,
        priority: str = "normal",
        notification_email: Optional[str] = None
    ) -> Dict:
        """
        Schedule a report for generation
        
        POST /api/v1/reports/schedule
        
        Args:
            template_id: The template identifier
            parameters: Report parameters
            user_id: User requesting the report
            priority: Report priority (low, normal, high)
            notification_email: Email for completion notification
            
        Returns:
            Report scheduling result with report_id and status
        """
        try:
            payload = {
                "template_id": template_id,
                "parameters": parameters,
                "user_id": user_id,
                "priority": priority,
                "requested_at": datetime.utcnow().isoformat()
            }
            
            if notification_email:
                payload["notification_email"] = notification_email
            
            response = requests.post(
                f"{self.base_url}/api/v1/reports/schedule",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "report_id": data.get("report_id"),
                "scheduled_at": data.get("scheduled_at"),
                "estimated_completion": data.get("estimated_completion"),
                "status": data.get("status", "scheduled"),
                "queue_position": data.get("queue_position")
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error scheduling report: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_report_status(self, report_id: str) -> Dict:
        """
        Check the status of a scheduled report
        
        GET /api/v1/reports/{report_id}/status
        
        Args:
            report_id: The report identifier
            
        Returns:
            Report status information
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/reports/{report_id}/status",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching report status: {e}")
            return {"status": "unknown", "error": str(e)}
    
    def get_report_navigation_path(self, report_id: str) -> str:
        """
        Generate navigation instructions for accessing the report
        
        Args:
            report_id: The report identifier
            
        Returns:
            Formatted navigation instructions
        """
        # This could also be an API call if navigation is dynamic
        base_url = self.base_url.replace("/api", "")
        
        return f"""
📊 **Your Report is Being Generated**

**Report ID**: {report_id}

**How to Access Your Report:**

**Option 1: Direct Link**
🔗 {base_url}/reports/{report_id}

**Option 2: Navigate via Dashboard**
1. Go to your Dashboard
2. Click on "Reports" in the left sidebar
3. Select "My Reports" tab
4. Look for Report ID: {report_id}

**Estimated Time**: 10-15 minutes
**Notification**: You'll receive an email when the report is ready

**Need Help?**
- Check report status: {base_url}/reports/{report_id}/status
- Contact support: support@your-company.com
"""
    
    def _get_default_templates(self) -> List[Dict]:
        """Fallback templates if API is unavailable"""
        return [
            {
                "id": "sales_report",
                "name": "Sales Performance Report",
                "description": "Comprehensive sales analysis",
                "category": "sales"
            },
            {
                "id": "customer_report",
                "name": "Customer Analytics Report",
                "description": "Customer behavior analysis",
                "category": "customer"
            }
        ]


# ============================================================================
# Integration with LangGraph Agent
# ============================================================================

def integrate_with_agent():
    """
    Example of how to integrate the API client with the agent
    
    Replace the mock functions in reporting_agent.py with these:
    """
    
    # Initialize API client
    api_client = ReportingAPIClient(
        base_url=os.getenv("REPORTING_API_BASE_URL"),
        api_token=os.getenv("REPORTING_API_TOKEN")
    )
    
    # Replace mock functions
    def get_available_templates() -> List[Dict]:
        return api_client.get_available_templates()
    
    def get_template_parameters(template_id: str) -> Dict:
        return api_client.get_template_parameters(template_id)
    
    def validate_parameters(template_id: str, parameters: Dict) -> Dict:
        return api_client.validate_parameters(template_id, parameters)
    
    def schedule_report(template_id: str, parameters: Dict, user_id: str = "user123") -> Dict:
        return api_client.schedule_report(template_id, parameters, user_id)
    
    def get_report_navigation_path(report_id: str) -> str:
        return api_client.get_report_navigation_path(report_id)
    
    return {
        "get_available_templates": get_available_templates,
        "get_template_parameters": get_template_parameters,
        "validate_parameters": validate_parameters,
        "schedule_report": schedule_report,
        "get_report_navigation_path": get_report_navigation_path
    }


# ============================================================================
# Example API Response Formats
# ============================================================================

"""
Expected API Response Formats:

1. GET /api/v1/templates
{
    "templates": [
        {
            "id": "sales_report",
            "name": "Sales Performance Report",
            "description": "Comprehensive sales analysis",
            "category": "sales",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z"
        }
    ]
}

2. GET /api/v1/templates/{template_id}/parameters
{
    "template_id": "sales_report",
    "parameters": {
        "date_range": {
            "type": "date_range",
            "required": true,
            "description": "Start and end date",
            "example": "2024-01-01 to 2024-12-31",
            "validation": {
                "format": "YYYY-MM-DD to YYYY-MM-DD"
            }
        },
        "region": {
            "type": "string",
            "required": true,
            "description": "Geographic region",
            "options": ["North America", "Europe", "Asia", "All"],
            "example": "North America"
        }
    }
}

3. POST /api/v1/templates/{template_id}/validate
Request:
{
    "parameters": {
        "date_range": "2024-01-01 to 2024-12-31",
        "region": "North America"
    }
}

Response:
{
    "valid": true,
    "errors": []
}

OR

{
    "valid": false,
    "errors": [
        "Invalid date format for date_range",
        "Missing required parameter: region"
    ]
}

4. POST /api/v1/reports/schedule
Request:
{
    "template_id": "sales_report",
    "parameters": {
        "date_range": "2024-01-01 to 2024-12-31",
        "region": "North America"
    },
    "user_id": "user123",
    "priority": "normal",
    "requested_at": "2024-10-22T10:30:00Z"
}

Response:
{
    "report_id": "RPT-A1B2C3D4",
    "scheduled_at": "2024-10-22T10:30:00Z",
    "estimated_completion": "2024-10-22T10:45:00Z",
    "status": "scheduled",
    "queue_position": 3
}

5. GET /api/v1/reports/{report_id}/status
{
    "report_id": "RPT-A1B2C3D4",
    "status": "processing",  // or "scheduled", "completed", "failed"
    "progress": 45,  // percentage
    "created_at": "2024-10-22T10:30:00Z",
    "updated_at": "2024-10-22T10:35:00Z",
    "download_url": null  // populated when status is "completed"
}
"""


# ============================================================================
# Error Handling
# ============================================================================

class ReportingAPIError(Exception):
    """Custom exception for API errors"""
    pass


def handle_api_error(error: Exception, operation: str) -> Dict:
    """
    Standardized error handling for API operations
    
    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
        
    Returns:
        Error response dictionary
    """
    error_message = f"Failed to {operation}: {str(error)}"
    
    # Log the error (integrate with your logging system)
    print(f"ERROR: {error_message}")
    
    return {
        "success": False,
        "error": error_message,
        "error_type": type(error).__name__
    }


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the API client
    """
    
    # Set environment variables first:
    # export REPORTING_API_BASE_URL="https://your-api.com"
    # export REPORTING_API_TOKEN="your-api-token"
    
    client = ReportingAPIClient()
    
    # Test getting templates
    print("Fetching templates...")
    templates = client.get_available_templates()
    print(f"Found {len(templates)} templates")
    
    if templates:
        template = templates[0]
        print(f"\nTemplate: {template['name']}")
        
        # Get parameters
        print("\nFetching parameters...")
        params = client.get_template_parameters(template['id'])
        print(f"Parameters: {list(params.keys())}")
        
        # Example validation
        print("\nValidating parameters...")
        test_params = {
            "date_range": "2024-01-01 to 2024-12-31",
            "region": "North America"
        }
        validation = client.validate_parameters(template['id'], test_params)
        print(f"Valid: {validation.get('valid')}")
        
        # Example scheduling
        if validation.get('valid'):
            print("\nScheduling report...")
            result = client.schedule_report(
                template_id=template['id'],
                parameters=test_params,
                user_id="test_user"
            )
            
            if result.get('success'):
                print(f"Report scheduled: {result.get('report_id')}")
                print(f"Status: {result.get('status')}")
                
                # Get navigation
                nav = client.get_report_navigation_path(result.get('report_id'))
                print(nav)
