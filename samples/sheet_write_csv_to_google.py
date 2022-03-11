#!/usr/bin/python
# -*- coding: utf-8 -*-
import pickle
import argparse
import os.path
import time
import pandas as pd
from datetime import datetime as dt
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint


def get_google_service():
    creds = None
    # The file sheet_token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    file_name_token = 'sheet_token.pickle'
    if os.path.exists(file_name_token):
        with open(file_name_token, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            flow = InstalledAppFlow.from_client_secrets_file(
                './bot_util/sheet_credentials_google_sheet.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(file_name_token, 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service


def update_sheet(service, str_csv_path, str_google_sheet_id, str_sheet_name):
    str_range_name = str_sheet_name + '!1:99999999'
    df = pd.read_csv(str_csv_path)
    df = df.applymap(str)
    lst_values = []
    lst_values.insert(0, list(df))  # row 0, column name
    lst_values.extend(df.values.tolist())
    body = {'values': lst_values}
    result = service.spreadsheets().values().update(
        spreadsheetId=str_google_sheet_id, range=str_range_name,
        valueInputOption='USER_ENTERED', body=body).execute()  # valueInputOption='USER_ENTERED' or 'RAW'
    print('sheet_write_csv_to_google.py, {0} cells updated.'.format(
        result.get('updatedCells')))


def clear_sheet(service, str_google_sheet_id, str_sheet_name):
    str_range_name = str_sheet_name + '!1:99999999'
    clear_values_request_body = {  # TODO: Add desired entries to the request body.
    }
    request = service.spreadsheets().values().clear(spreadsheetId=str_google_sheet_id, range=str_range_name,
                                                    body=clear_values_request_body)
    response = request.execute()
    pprint(response)


def main(str_csv_path, str_google_sheet_id='1JdpdRksNnLgurFeseAMk8d0lKSXwMbPnjWPP8fzJy28', str_sheet_name='3M'):
    try:
        service = get_google_service()
    except Exception as e:
        # RefreshError('deleted_client: The OAuth client was deleted.', {'error': 'deleted_client', 'error_description': 'The OAuth client was deleted.'})
        print(e)
    try:
        clear_sheet(service, str_google_sheet_id, str_sheet_name)
        update_sheet(service, str_csv_path, str_google_sheet_id, str_sheet_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    str_default_google_sheet_id = '1JdpdRksNnLgurFeseAMk8d0lKSXwMbPnjWPP8fzJy28'
    str_default_sheet_name = '3M'
    str_default_csv_path = 'Results/result.csv'
    a = argparse.ArgumentParser()
    a.add_argument("-i", "--google_sheet_id",
                   help=str_default_google_sheet_id, default=str_default_google_sheet_id)
    a.add_argument("-s", "--sheet_name",
                   help=str_default_sheet_name, default=str_default_sheet_name)
    a.add_argument("-c", "--csv_path", help=str_default_csv_path,
                   default=str_default_csv_path)

    t = time.time()
    main(a.parse_args().google_sheet_id,
         a.parse_args().sheet_name, a.parse_args().csv_path)
    print('%s, sheet_write_csv_to_google.py, duration: %s secs' %
          (str(dt.now())[5:19], round(time.time() - t, 2)))
