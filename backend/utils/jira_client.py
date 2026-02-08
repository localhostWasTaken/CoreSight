import os
import requests
from typing import Optional

def get_jira_auth():
    """Get Jira credentials from environment variables"""
    jira_url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    
    if not all([jira_url, email, token]):
        print("⚠️  Jira credentials not set. Skipping Jira operations.")
        return None
        
    return {
        "url": jira_url.rstrip("/"),
        "auth": (email, token),
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    }

def assign_issue(issue_key_or_id: str, account_id: str) -> bool:
    """
    Assign a Jira issue to a user by accountId.
    
    Args:
        issue_key_or_id: The Jira issue key (e.g., 'PROJ-123') or ID.
        account_id: The Jira accountId of the user to assign.
        
    Returns:
        True if successful, False otherwise.
    """
    creds = get_jira_auth()
    if not creds:
        return False
        
    url = f"{creds['url']}/rest/api/3/issue/{issue_key_or_id}/assignee"
    
    payload = {
        "accountId": account_id
    }
    
    try:
        response = requests.put(
            url,
            json=payload,
            auth=creds["auth"],
            headers=creds["headers"]
        )
        
        if response.status_code == 204:
            print(f"✅ Successfully assigned Jira issue {issue_key_or_id} to {account_id}")
            return True
        else:
            print(f"❌ Failed to assign Jira issue. Status: {response.status_code}, Body: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error assigning Jira issue: {e}")
        return False
