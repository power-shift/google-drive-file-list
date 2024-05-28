import os
import csv
import pickle
import time
from tabulate import tabulate
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set up credentials and build Drive API client
def get_drive_api_client():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


# List files in the root directory
def list_root_files(service):
    results = []
    query = "mimeType != 'application/vnd.google-apps.folder' and trashed = false and 'root' in parents"
    files = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, owners, permissions, sharedWithMeTime)").execute()

    for item in files.get('files', []):
        shared_with = []
        for permission in item.get('permissions', []):
            if permission['type'] == 'user':
                shared_with.append(permission['emailAddress'])

        owner_email = item['owners'][0]['emailAddress']
        shared_with_me = bool(item.get('sharedWithMeTime'))
        results.append((item['name'], "", owner_email, ', '.join(shared_with), shared_with_me))

    return results


# Recursively list files and folders
def list_files_recursively(service, folder_id=None, path=""):
    results = []
    query = f"'{folder_id}' in parents" if folder_id else "mimeType='application/vnd.google-apps.folder' and trashed = false and 'root' in parents"
    files = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, owners, permissions, sharedWithMeTime)").execute()

    for item in files.get('files', []):
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            results.extend(list_files_recursively(service, item['id'], path + item['name'] + "/"))
        else:
            shared_with = []
            for permission in item.get('permissions', []):
                if permission['type'] == 'user':
                    shared_with.append(permission['emailAddress'])

            owner_email = item['owners'][0]['emailAddress']
            shared_with_me = bool(item.get('sharedWithMeTime'))
            results.append((item['name'], path, owner_email, ', '.join(shared_with), shared_with_me))

    return results


# List files and folders from "Shared with me" location
def list_shared_with_me_files_recursively(service, folder_id=None, path=""):
    results = []

    if folder_id:
        query = f"'{folder_id}' in parents"
    else:
        query = "sharedWithMe"

    files = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, owners, permissions, sharedWithMeTime)").execute()

    for item in files.get('files', []):
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            results.extend(list_shared_with_me_files_recursively(service, item['id'], path + item['name'] + "/"))
        else:
            shared_with = []
            for permission in item.get('permissions', []):
                if permission['type'] == 'user':
                    shared_with.append(permission['emailAddress'])

            owner_email = item['owners'][0]['emailAddress']
            shared_with_me = bool(item.get('sharedWithMeTime'))
            results.append((item['name'], path, owner_email, ', '.join(shared_with), shared_with_me))

    return results


def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Path', 'Owner', 'Shared With', 'Shared With Me'])
        writer.writerows(data)


def print_duration(start_time):
    duration = time.time() - start_time
    print(f"\rElapsed time: {duration:.2f} seconds", end='')


def run():
    # Print the start time
    start_time = time.time()
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    # Get the Drive API client
    drive_service = get_drive_api_client()

    # List files in the root directory
    root_files = list_root_files(drive_service)

    # Recursively list files and folders
    file_data = list_files_recursively(drive_service)

    # Recursively list files and folders from "Shared with me" location
    shared_with_me_data = list_shared_with_me_files_recursively(drive_service)

    # Combine root files and other file data
    combined_data = root_files + file_data + shared_with_me_data

    # Save the data to a CSV file
    save_to_csv(combined_data, 'google_drive_files.csv')

    # Print the results in a table
    print(tabulate(combined_data, headers=['Name', 'Path', 'Owner', 'Shared With', 'Shared With Me']))

    # Print the end time and duration
    end_time = time.time()
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Duration: {end_time - start_time:.2f} seconds")

if __name__ == "__main__": 
    run()