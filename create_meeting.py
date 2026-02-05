#!/usr/bin/env python3
"""
Webex Meeting Creator

This script authenticates with Webex using OAuth and creates a scheduled meeting
with configurable parameters like title, start/end times, timezone, and host email.

Author: Taylor Hanson, Cisco Collab SE
Purpose: Teaching tool and example for Webex API integration
"""

import sys
import requests
from typing import Dict, Any

# Python dependencies, Install with:
# pip install requests>=2.31.0

# ============================================================================
# CONFIGURATION SECTION - Modify these values as needed
# ============================================================================
# NOTE: In production environments, you should NEVER hardcode credentials.
# Instead, use environment variables or a secure credential manager.
# For learning purposes, we're keeping it simple here.
# ============================================================================
CLIENT_ID = ""
CLIENT_SECRET = ""
REFRESH_TOKEN = ""

# ============================================================================
# MEETING CONFIGURATION - Change these to customize your meeting
# ============================================================================
MEETING_TITLE = "Test"
# Start time in ISO 8601 format with timezone offset (YYYY-MM-DDTHH:MM:SS±HH:MM)
MEETING_START = "2026-03-01T12:30:00+03:00"
# End time in ISO 8601 format with timezone offset (YYYY-MM-DDTHH:MM:SS±HH:MM)
MEETING_END = "2026-03-01T13:00:00+03:00"
# Timezone identifier (e.g., "America/New_York", "Europe/London", "Asia/Tokyo")
MEETING_TIMEZONE = "Asia/Riyadh"
# Email address of the meeting host
HOST_EMAIL = ""
# Webex site URL (e.g., "yourcompany.webex.com")
SITE_URL = ""

# API Base URL - shouldn't need to change this
WEBEX_API_BASE = "https://webexapis.com/v1"


def get_access_token() -> str:
    """
    Exchange a refresh token for a new access token.
    The access token is temporary and used for API calls during this session.
    OAuth flow: refresh_token -> access_token
    Returns:
        A valid access token string
    Raises:
        SystemExit: If token refresh fails
    """
    print("🔐 Authenticating with Webex...")
    # Prepare the token request
    url = f"{WEBEX_API_BASE}/access_token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    # Make the POST request to get a new access token
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)
        # Extract the access token from the response
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            print("ERROR: No access token in response")
            sys.exit(1)
        print("✓ Authentication successful!\n")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to get access token: {e}")
        sys.exit(1)


def create_meeting(access_token: str, title: str, start: str, end: str, 
                   timezone: str, host_email: str, site_url: str) -> Dict[str, Any]:
    """
    Create a new Webex meeting with the specified parameters.
    Args:
        access_token: Valid Webex access token
        title: Meeting title/subject
        start: Meeting start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS±HH:MM)
        end: Meeting end time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS±HH:MM)
        timezone: Timezone identifier (e.g., "America/New_York")
        host_email: Email address of the meeting host
        site_url: Webex site URL (e.g., "company.webex.com")
    Returns:
        Dictionary containing the created meeting details
    Raises:
        SystemExit: If meeting creation fails
    """
    print("📅 Creating Webex meeting...")
    print(f"   Title: {title}")
    print(f"   Start: {start}")
    print(f"   End: {end}")
    print(f"   Timezone: {timezone}")
    print(f"   Host: {host_email}")
    print(f"   Site: {site_url}\n")
    # Prepare the API request
    url = f"{WEBEX_API_BASE}/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # Prepare the request payload
    payload = {
        "title": title,
        "start": start,
        "end": end,
        "timezone": timezone,
        "scheduledType": "meeting",  # This is always "meeting" for scheduled meetings
        "hostEmail": host_email,
        "siteUrl": site_url
    }
    # Make the POST request to create the meeting
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        # Parse the meeting details from the response
        meeting_data = response.json()
        print("✓ Meeting created successfully!\n")
        return meeting_data
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to create meeting: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def display_meeting_details(meeting: Dict[str, Any]) -> None:
    """
    Display meeting details in a user-friendly format.
    Args:
        meeting: Dictionary containing meeting details from Webex API
    """
    print("=" * 70)
    print("MEETING DETAILS")
    print("=" * 70)
    # Extract and display relevant fields
    print(f"\nTitle:         {meeting.get('title', 'N/A')}")
    print(f"Meeting ID:    {meeting.get('id', 'N/A')}")
    print(f"Meeting Number:{meeting.get('meetingNumber', 'N/A')}")
    print(f"Password:      {meeting.get('password', 'N/A')}")
    print(f"Start Time:    {meeting.get('start', 'N/A')}")
    print(f"End Time:      {meeting.get('end', 'N/A')}")
    print(f"Timezone:      {meeting.get('timezone', 'N/A')}")
    print(f"Host Email:    {meeting.get('hostEmail', 'N/A')}")
    print(f"Site URL:      {meeting.get('siteUrl', 'N/A')}")
    print(f"Web Link:      {meeting.get('webLink', 'N/A')}")
    print(f"SIP Address:   {meeting.get('sipAddress', 'N/A')}")
    print("\n" + "=" * 70)


def main():
    """
    Main execution flow of the script.
    """
    print("\n" + "=" * 70)
    print("WEBEX MEETING CREATOR")
    print("=" * 70 + "\n")
    
    # Step 1: Authenticate with Webex
    access_token = get_access_token()
    # Step 2: Create the meeting with configured parameters
    meeting_details = create_meeting(
        access_token=access_token,
        title=MEETING_TITLE,
        start=MEETING_START,
        end=MEETING_END,
        timezone=MEETING_TIMEZONE,
        host_email=HOST_EMAIL,
        site_url=SITE_URL
    )
    # Step 3: Display the meeting details
    display_meeting_details(meeting_details)
    print("\n✓ Script completed successfully!\n")


# Entry point: This runs when the script is executed
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

