import request_util

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



import requests
import base64

# token='ya29.a0AfH6SMCa0aRk0P_....
# url='https://gmail.googleapis.com/gmail/v1/users/me/messages?q=from%3Aabcd%40gmail.com'


# def get_query_string(token,userid,query):

#Email list from url generated from search query
def list_emails(token,url):
    headers = {
      'Authorization': 'Bearer {}'.format(token),
      'Content-Type': 'application/json'
    }
    r=requests.get(url, headers=headers)
    id_list=[]
    for i in r.json().get('messages'):
        id_list.append(i.get('id'))
    return(id_list)
    

#Delete Email list from abcd@gmail.com
def delete_emails(token,r):
    headers = {
          'Authorization': 'Bearer {}'.format(token),
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
    payload="""{}""".format({"ids":r})
    m=requests.post('https://gmail.googleapis.com/gmail/v1/users/me/messages/batchDelete', headers=headers,data=payload)


while True:
    try:
        r=list_emails(token,url)
        delete_emails(token,r)
    except:
        print("No more mails")
        break
