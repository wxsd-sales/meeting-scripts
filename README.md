# Webex Meeting Scripts

A collection of Python scripts for interacting with the Webex Meetings API. This repository contains two main utilities:
- **Meeting Reports Generator** - Authenticates with Webex, retrieves and generates meeting reports with customizable date ranges
- **Meeting Creator** - Creates scheduled Webex meetings with configurable parameters including timezone support

## Demo
<!-- Replace with your video URL -->
[![Demo Video](screenshot-placeholder.png)](https://your-video-url-here)

## Developer Documentation

**Webex Meetings API Documentation:**
- [Webex Meetings API Overview](https://developer.webex.com/docs/api/v1/meetings)
- [Reports API](https://developer.webex.com/docs/api/v1/reports)
- [OAuth Integration Guide](https://developer.webex.com/docs/integrations)

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Webex OAuth integration credentials for webex_reports.py (Client ID, Client Secret, Refresh Token)
- Webex ServiceApp credentials for create_meeting.py (Client ID, Client Secret, Refresh Token)

### Clone the Repository
```bash
git clone <your-repository-url>
cd meeting-scripts
```

## Installation

Install the required Python dependency:
```bash
pip install requests>=2.31.0
```

## Configuration

Both scripts use OAuth authentication with hardcoded credentials for simplicity. **Note: This is for demonstration purposes only. In production, use environment variables or a secure credential manager.**

### 1. Configure Authentication Credentials
Open each script (`webex_reports.py` and `create_meeting.py`) and update the following variables in the CONFIGURATION SECTION:

```python
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REFRESH_TOKEN = "your_refresh_token_here"
```

### 2. Configure Script-Specific Settings

#### For `webex_reports.py`:
- `SITE_LIST` - Your Webex site URL (e.g., "company.webex.com")
- `DAYS_BACK` - Number of days to include in report (default: 30)
- `SERVICES` - Services to filter reports by (default: ["Webex Meetings"])

#### For `create_meeting.py`:
- `MEETING_TITLE` - Title of the meeting
- `MEETING_START` - Start time in ISO 8601 format with timezone offset
- `MEETING_END` - End time in ISO 8601 format with timezone offset
- `MEETING_TIMEZONE` - Timezone identifier (e.g., "America/New_York", "Asia/Riyadh")
- `HOST_EMAIL` - Email address of the meeting host
- `SITE_URL` - Your Webex site URL

## Usage

### Generate Meeting Reports
Run the report generator script:
```bash
python3 webex_reports.py
```

The script will:
1. Authenticate with Webex
2. Display available report templates
3. Prompt you to select a report
4. Generate the report for the configured date range
5. Download and extract the report as a CSV file

### Create a Webex Meeting
Run the meeting creator script:
```bash
python3 create_meeting.py
```

The script will:
1. Authenticate with Webex
2. Create a meeting with your configured parameters
3. Display the meeting details including join link, meeting number, and password

## License

All contents are licensed under the MIT license. Please see [LICENSE](LICENSE) for details.

## Disclaimer

Everything included is for demo and Proof of Concept purposes only. Use of these scripts is solely at your own risk. These demos are for Cisco Webex use cases, but are not Official Cisco Webex Branded demos.

**Security Note:** Never commit your API credentials to version control. Always use environment variables or secure credential management in production environments.

## Support

Please contact the Webex SD team at [wxsd@external.cisco.com](mailto:wxsd@external.cisco.com?subject=WebexMeetingScripts) for questions. Or for Cisco internal, reach out to us on Webex App via our bot globalexpert@webex.bot & choose "Engagement Type: API/SDK Proof of Concept Integration Development". 

For Webex API support, visit the [Webex Developer Portal](https://developer.webex.com/).

