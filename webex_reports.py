#!/usr/bin/env python3
"""
Webex Meeting Reports Generator

This script authenticates with Webex using OAuth, retrieves available report templates,
allows you to select a report, generates it, and displays the download information.

Author: Taylor Hanson, Cisco Collab SE
Purpose: Teaching tool and example for Webex API integration
"""

import sys
import time
import requests
import zipfile
import io
from datetime import datetime, timedelta
from typing import Dict, Any

# Python dependencies, Install with:
# pip install requests>=2.31.0
# Note: zipfile, io, time, datetime are part of Python standard library (no install needed)

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

# Webex site URL (e.g., "yourcompany.webex.com")
SITE_LIST = ""
# Number of days back to generate reports for (30 means report data will range from today to 30 days ago)
DAYS_BACK = 30
# Services to filter reports by (only show templates for these services)
SERVICES = ["Webex Meetings"]
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


def list_report_templates(access_token: str) -> list:
    """
    Retrieve all available report templates from Webex.
    Args:
        access_token: Valid Webex access token
    Returns:
        List of report template dictionaries
    Raises:
        SystemExit: If API call fails
    """
    print("📋 Fetching available report templates...")
    url = f"{WEBEX_API_BASE}/report/templates"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        templates = data.get("items", [])
        print(f"✓ Found {len(templates)} report templates\n")
        return templates 
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch templates: {e}")
        sys.exit(1)


def display_templates_and_select(templates: list) -> int:
    """
    Display available report templates and prompt user to select one.
    Only shows templates whose service matches the SERVICES list.
    Args:
        templates: List of report template dictionaries
    Returns:
        The selected template ID (integer)
    """
    # Filter templates to only include services in the SERVICES list
    filtered_templates = [t for t in templates if t.get("service") in SERVICES]
    
    print("=" * 70)
    print("AVAILABLE REPORTS")
    print("=" * 70)
    # Display each template with its details
    for template in filtered_templates:
        template_id = template.get("Id")
        title = template.get("title")
        service = template.get("service", "N/A")
        max_days = template.get("maxDays", "N/A")
        print(f"\n[{template_id}] {title}")
        print(f"    Service: {service} | Max Days: {max_days}")
    print("\n" + "=" * 70)
    # Prompt user for selection
    while True:
        try:
            selection = input("\nEnter the report number to generate: ").strip()
            selected_id = int(selection)
            # Verify the selected ID exists in the filtered templates
            if any(t.get("Id") == selected_id for t in filtered_templates):
                return selected_id
            else:
                print(f"Invalid selection. Please choose from the list above.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def calculate_date_range(days_back: int) -> tuple:
    """
    Calculate start and end dates for the report.
    Args:
        days_back: Number of days to look back from today
    Returns:
        Tuple of (start_date, end_date) as strings in YYYY-MM-DD format
    """
    # End date is yesterday (today minus 1 day)
    end_date = datetime.now() - timedelta(days=1)
    # Start date is 'days_back' days ago
    start_date = end_date - timedelta(days=days_back)
    # Format as YYYY-MM-DD strings
    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )


def create_report(access_token: str, template_id: int, 
                  start_date: str, end_date: str, site_list: str) -> str:
    """
    Request generation of a new report from Webex.
    Args:
        access_token: Valid Webex access token
        template_id: The report template ID to use
        start_date: Report start date (YYYY-MM-DD)
        end_date: Report end date (YYYY-MM-DD)
        site_list: Webex site URL
    Returns:
        The report ID string for the created report
    Raises:
        SystemExit: If report creation fails
    """
    print(f"\n📊 Creating report...")
    print(f"   Template ID: {template_id}")
    print(f"   Date Range: {start_date} to {end_date}")
    print(f"   Site: {site_list}")
    url = f"{WEBEX_API_BASE}/reports"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the request body
    payload = {
        "templateId": template_id,
        "startDate": start_date,
        "endDate": end_date,
        "siteList": site_list
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        report_id = data.get("items", {}).get("Id")
        if not report_id:
            print("ERROR: No report ID in response")
            sys.exit(1)
        print(f"✓ Report created successfully! (ID: {report_id})\n")
        return report_id
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to create report: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)


def get_report_details(access_token: str, report_id: str) -> Dict[str, Any]:
    """
    Retrieve the details and status of a generated report.
    Args:
        access_token: Valid Webex access token
        report_id: The ID of the report to retrieve
    Returns:
        Dictionary containing report details
    Raises:
        SystemExit: If retrieval fails
    """
    print("📥 Fetching report details...")
    url = f"{WEBEX_API_BASE}/reports/{report_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if not items:
            print("ERROR: No report details found")
            sys.exit(1)
        return items[0]  # Return the first (and typically only) item
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch report details: {e}")
        sys.exit(1)


def display_report_details(report: Dict[str, Any]) -> None:
    """
    Display report details in a user-friendly format.
    Args:
        report: Dictionary containing report details
    """
    print("\n" + "=" * 70)
    print("REPORT DETAILS")
    print("=" * 70)
    # Extract and display relevant fields
    print(f"\nTitle:       {report.get('title', 'N/A')}")
    print(f"Service:       {report.get('service', 'N/A')}")
    print(f"Status:        {report.get('status', 'N/A')}")
    print(f"Date Range:    {report.get('startDate', 'N/A')} to {report.get('endDate', 'N/A')}")
    print(f"Site:          {report.get('siteList', 'N/A')}")
    print(f"Report ID:     {report.get('Id', 'N/A')}")
    print(f"Download URL:  {report.get('downloadURL', 'N/A')}")
    print("\n" + "=" * 70)


def poll_report_until_ready(access_token: str, report_id: str, poll_interval: int = 5, max_attempts: int = 60) -> Dict[str, Any]:
    """
    Poll the report status until it's ready (status = "done").
    Args:
        access_token: Valid Webex access token
        report_id: The ID of the report to poll
        poll_interval: Seconds to wait between polls (default: 5)
        max_attempts: Maximum number of polling attempts (default: 60)
    Returns:
        Dictionary containing the final report details
    Raises:
        SystemExit: If report fails or timeout reached
    """
    print("⏳ Waiting for report to be generated...")
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        report = get_report_details(access_token, report_id)
        status = report.get("status", "").lower()
        if status == "done":
            print("✓ Report is ready!\n")
            return report
        elif status == "failed":
            print("❌ Report generation failed!")
            sys.exit(1)
        else:
            # Still processing - wait and try again
            print(f"   Status: {status} (attempt {attempt}/{max_attempts})")
            time.sleep(poll_interval)
    # Timeout reached
    print(f"❌ Timeout: Report did not complete after {max_attempts * poll_interval} seconds")
    sys.exit(1)


def download_report(access_token: str, download_url: str, output_filename: str = None) -> str:
    """
    Download the report file from the provided URL.
    Webex typically returns reports as ZIP files containing CSVs.
    This function extracts the CSV from the ZIP automatically.
    Args:
        access_token: Valid Webex access token
        download_url: The URL to download the report from
        output_filename: Optional filename to save as (default: auto-generated)
    Returns:
        The filename of the downloaded report
    Raises:
        SystemExit: If download fails
    """
    print(f"📥 Downloading report from: {download_url}")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
        # Check if the response is a ZIP file
        content = response.content
        if content[:4] == b'PK\x03\x04':  # ZIP file magic number
            print("   Detected ZIP file, extracting CSV...")
            # Open the ZIP file from memory
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                # Get list of files in the ZIP
                file_list = zip_file.namelist()
                # Find the first CSV file
                csv_file = next((f for f in file_list if f.endswith('.csv')), None)
                if csv_file:
                    # Extract the CSV content
                    csv_content = zip_file.read(csv_file)
                    # Generate output filename if not provided
                    if not output_filename:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_filename = f"webex_report_{timestamp}.csv"
                    # Write the CSV to a file
                    with open(output_filename, 'wb') as f:
                        f.write(csv_content)
                    print(f"✓ Report downloaded and extracted: {output_filename}\n")
                    return output_filename
                else:
                    print("ERROR: No CSV file found in ZIP archive")
                    sys.exit(1)
        else:
            # Not a ZIP file, save as-is
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"webex_report_{timestamp}.csv"
            with open(output_filename, 'wb') as f:
                f.write(content)
            print(f"✓ Report downloaded: {output_filename}\n")
            return output_filename
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download report: {e}")
        sys.exit(1)
    except zipfile.BadZipFile as e:
        print(f"ERROR: Failed to extract ZIP file: {e}")
        sys.exit(1)


def main():
    """
    Main execution flow of the script.
    """
    print("\n" + "=" * 70)
    print("WEBEX MEETING REPORTS GENERATOR")
    print("=" * 70 + "\n")
    
    # Step 1: Authenticate
    access_token = get_access_token()
    # Step 2: Get available report templates
    templates = list_report_templates(access_token)
    if not templates:
        print("No report templates available.")
        sys.exit(0)
    # Step 3: Let user select a report
    selected_template_id = display_templates_and_select(templates)
    # Step 4: Calculate date range
    start_date, end_date = calculate_date_range(DAYS_BACK)
    # Step 5: Create the report
    report_id = create_report(
        access_token=access_token,
        template_id=selected_template_id,
        start_date=start_date,
        end_date=end_date,
        site_list=SITE_LIST
    )
    # Step 6: Poll until report is ready
    report_details = poll_report_until_ready(access_token, report_id)
    display_report_details(report_details)
    # Step 7: Download the report
    download_url = report_details.get("downloadURL")
    if download_url:
        downloaded_file = download_report(access_token, download_url)
        print(f"✓ Script completed successfully! Report saved as: {downloaded_file}\n")
    else:
        print("⚠️  No download URL available for this report.\n")


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

