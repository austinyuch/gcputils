import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

def google_client_api_creds(scopes:list, 
                            key_file_location:str, 
                            token_file_location:str
                        )->Credentials:
    
    # method 1: pyDrive, 但是不相容Drive API (V3)
    # gauth = GoogleAuth()
    # below is the old oauth2client
    # gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
    # below is the new one for google-auth with service account
    # gauth.credentials = Credentials.from_service_account_file(GDRIVE_JSON_FILE)
    # drive = GoogleDrive(gauth)
    # return drive
    # method 2: 原生Drive API
    creds = None
    if os.path.exists(token_file_location):
        # creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        creds = Credentials.from_authorized_user_file(token_file_location, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                key_file_location, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file_location, 'w') as token:
            token.write(creds.to_json())

    print("google api creds got successfully")
    # service = build('drive', 'v3', credentials=creds)
    return creds

def google_client_api_service(service_name:str, 
                            version:str, 
                            creds:Credentials
                        )->object:
    """
    :param service_name:
    :param version: e.g. 'v3
    """
    # service = build('drive', 'v3', credentials=creds)
    service = build(service_name, version, credentials=creds)
    return service