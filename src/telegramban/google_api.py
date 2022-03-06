from __future__ import print_function

import csv
import io
import os.path
import re
import sys
import traceback

import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm
from googleapiclient import discovery
from httplib2 import Http


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']


def google_api_search(service, param):
    # search for the file
    results = []
    page_token = None
    while True:
        if page_token:
            param['pageToken'] = page_token
        response = service.files().list(**param).execute()
        # iterate over filtered files
        for file in response.get("files", []):
            results.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more files
            break
    return results


def get_drive_id(service, filename):
    param = {}
    param["q"] = f"name='{filename}'"
    param["spaces"] = "drive"
    param["fields"] = "nextPageToken, files(id, name, mimeType)"
    return google_api_search(service, param)


def get_sheet_id(drive, filename):
    param = {}
    param["q"] = 'mimeType="application/vnd.google-apps.spreadsheet"'
    param["spaces"] = "drive"
    param["fields"] = "nextPageToken, files(id, name, mimeType)"
    results = google_api_search(drive, param)
    return [result for result in results if result[1] == filename]


def get_api_services(credentials_file_path):
    """
    Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    drive = discovery.build('drive', 'v3', credentials=creds)
    sheets = discovery.build('sheets', 'v4', credentials=creds)

    # Return Google Drive API service
    return drive, sheets


def google_drive_download(service, save_path, filename):
    # search for the file by name
    search_result = get_drive_id(service, filename)
    # get the GDrive ID of the file
    file_id = search_result[0][0]
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(f"{save_path}/{filename}", "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def google_sheet_download(drive, sheets, save_path, filename):
    # search for the file by name
    search_result = get_sheet_id(drive, filename)
    # get the GDrive ID of the file
    spreadsheet_id = search_result[0][0]

    result = sheets.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=filename).execute()
    output_file = f'{save_path}/{filename}.csv'

    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(result.get('values'))


def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        # get the file size from Content-length response header
        file_size = int(response.headers.get("Content-Length", 0))
        # extract Content disposition from response headers
        content_disposition = response.headers.get("content-disposition")
        # parse filename
        filename = re.findall("filename=\"(.+)\"", content_disposition)[0]
        print("[+] File size:", file_size)
        print("[+] File name:", filename)
        progress = tqdm(response.iter_content(CHUNK_SIZE), f"Downloading {filename}", total=file_size, unit="Byte", unit_scale=True, unit_divisor=1024)
        with open(destination, "wb") as f:
            for chunk in progress:
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # update the progress bar
                    progress.update(len(chunk))
        progress.close()

    # base URL for download
    URL = "https://docs.google.com/uc?export=download"
    # init a HTTP session
    session = requests.Session()
    # make a request
    response = session.get(URL, params = {'id': id}, stream=True)
    print("[+] Downloading", response.url)
    # get confirmation token
    token = get_confirm_token(response)
    if token:
        params = {'id': id, 'confirm':token}
        response = session.get(URL, params=params, stream=True)
    # download to disk
    save_response_content(response, destination)


def download_drive_file(credentials_file_path, save_path, filename):
    try:
        drive, _ = get_api_services(credentials_file_path)
        google_drive_download(drive, save_path, filename)
    except HttpError as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


def download_sheet_file(credentials_file_path, save_path, filename):
    try:
        drive, sheets = get_api_services(credentials_file_path)
        google_sheet_download(drive, sheets, save_path, filename)
    except HttpError as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
