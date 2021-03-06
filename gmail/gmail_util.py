"""
Batch delete gmail emails

References:
Method: users.messages.delete https://developers.google.com/gmail/api/reference/rest/v1/users.messages/delete
DELETE https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{id}
Method: users.messages.batchDelete 
https://developers.google.com/gmail/api/reference/rest/v1/users.messages/batchDelete
Method: users.messages.list
https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list

https://developers.google.com/gmail/api/reference/rest/v1/users.settings.filters


gmail query syntax :
https://support.google.com/mail/answer/7190
https://developers.google.com/gmail/api/guides/filtering

API key  gmail api不能用
https://cloud.google.com/docs/authentication/api-keys
{
  "error": {
    "code": 401,
    "message": "API keys are not supported by this API. Expected OAuth2 access token or other authentication credentials that assert a principal. See https://cloud.google.com/docs/authentication",
    "errors": [
      {
        "message": "Login Required.",
        "domain": "global",
        "reason": "required",
        "location": "Authorization",
        "locationType": "header"
      }
    ],
    "status": "UNAUTHENTICATED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "CREDENTIALS_MISSING",
        "domain": "googleapis.com",
        "metadata": {
          "method": "caribou.api.proto.MailboxService.ListMessages",
          "service": "gmail.googleapis.com"
        }
      }
    ]
  }
}

Code from 
API
https://jyotiskabhattacharjee.medium.com/guide-to-deleting-emails-using-google-gmail-apis-252e4a98572 
https://github.com/jyotiska22/knowledge_base/blob/main/gmail_bulk_delete_using_api.py 

Google Service
https://github.com/qualman/gmail_delete_by_filter/blob/master/deleter.py

"""


   
# https://jyotiskabhattacharjee.medium.com/guide-to-deleting-emails-using-google-gmail-apis-252e4a98572 for context
#!/usr/bin/env python
# coding: utf-8


import json
import requests
import base64
from confs import DIC_QUERY, SCOPES, TOKEN_FILE_LOCATION, KEY_FILE_LOCATION
from cred_conf import apikey
from google_client_api_util import google_client_api_creds, google_client_api_service

# token='ya29.a0AfH6SMCa0aRk0P_....
# url='https://gmail.googleapis.com/gmail/v1/users/me/messages?q=from%3Aabcd%40gmail.com'
API_URL_BASE = 'https://gmail.googleapis.com/gmail/v1/users/'
LST_QUERY = ["from:joyboy@gmail.com",
    "subject:(晚餐 電影 錢)"
    "is:unread",
    "newer_than:1d"]

def convert_query_list_str(
                      lst_query:list=LST_QUERY
                  )->str:
  """
  
  """
  str_query = ""
  for i in lst_query:
      str_query += i + " "
  
  str_query=str_query.rstrip()

  return str_query

def get_api_url_from_query(str_query:dict, 
                          str_userid:str="me",
                          # use_apikey:bool=True
                          )->str:
    """
    Return API URL from query string
    dic_query:dict
    {

    }
    """
    str_url = f"{API_URL_BASE}{str_userid}/messages?q={str_query}"
    # str_query=""
    # if use_apikey:
    #     str_url += f"&key={apikey}"

    return str_url



def get_header(
            # use_apikey:bool=False,
            token:str=None):
    # if use_apikey:
    #     dic_headers = {            
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json'
    #     }
    # else: # user service token
    dic_headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    return dic_headers

#Email list from url generated from search query
# def list_emails(token,url):
def list_emails(str_url:str, 
              # use_apikey:bool=True,
              token:str=None
          )->list:
    dic_headers = get_header(token)

    r=requests.get(str_url, headers=dic_headers)

    lst_id=[]
    if r.json()['resultSizeEstimate'] > 0:
      for i in r.json().get('messages'):
          lst_id.append(i.get('id'))

    return lst_id
    

#Delete Email list from abcd@gmail.com
def delete_emails(r,
              userid,
              use_apikey:bool=True,
              token=None):

    dic_headers = get_header(token)
    str_url = f"https://gmail.googleapis.com/gmail/v1/users/{userid}/messages/batchDelete"
    # 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchDelete'
    payload="""{}""".format({"ids":r})
    try:
      m=requests.post(str_url, 
                    headers=dic_headers,
                    data=payload
                )
      print(m.json())

    except Exception as e:
      print(e)

def get_token()->str:
  # 更新token
    creds = google_client_api_creds(SCOPES, 
                              str(KEY_FILE_LOCATION), 
                              str(TOKEN_FILE_LOCATION)
                            )
    # 讀入token
    dic_token = {}    
    with open(str(TOKEN_FILE_LOCATION), 'r') as f:
        dic_token = json.load(f)

    str_token = dic_token["token"]
    return str_token

# while True:
#     try:
#         r=list_emails(token,url)
#         delete_emails(token,r)
#     except:
#         print("No more mails")
#         break

if __name__ == '__main__':

    str_token=get_token()
    print(str_token)
    str_query = convert_query_list_str(lst_query=DIC_QUERY["asuswebstorage"])
    print(str_query)
    str_url = get_api_url_from_query(str_query)
    print(str_url)
    lst_id=list_emails(str_url, str_token)
    print(lst_id)
