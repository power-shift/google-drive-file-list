# Google Drive File Listing Script

This script lists files from a Google Drive account, including files in the root directory, files recursively in all folders, and files shared with you. It saves the collected data to a CSV file.

## Prerequisites

- Python 3.x
- Google API Client Library for Python
- OAuth2 for Google API

## Setup up Google API credentials:
 - Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project (if you don't have one).
- Enable the Google Drive API for your project.
- Create OAuth 2.0 Client IDs credentials.
- Download the `credentials.json` file and place it in the same directory as the script.

## Usage

1. **Run the script**:
    When you run the script for the first time, it will open a browser window asking you to log in to your Google account and authorize the application.

2. **Output**:
    - The script will create a CSV file named `google_drive_files.csv` in the same directory.
    - This CSV file will contain information about all files, including file name, path, owner, shared with, and whether the file is shared with you.


## Notes

- Ensure `credentials.json` and `token.pickle` are kept secure and not exposed to unauthorized users.
- The script saves the OAuth 2.0 token to `token.pickle` for subsequent runs, avoiding the need to reauthorize the application.