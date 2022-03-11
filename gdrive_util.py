"""
這篇說明最詳細
https://learn.markteaching.com/%E3%80%90google-api-%E6%95%99%E5%AD%B8%E3%80%91google-drive-api-upload-%E4%BD%BF%E7%94%A8-python-%E4%B8%8A%E5%82%B3%E5%96%AE%E4%B8%80%E6%AA%94%E6%A1%88-%E5%9F%BA%E6%9C%AC%E6%95%99%E5%AD%B8/
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
安裝好後先下載oauth2 installed key json檔案, 名稱改成credentials.json 
然後跑一次
python quickstart.py
此時需要互動, 就可以取得帶有refresh token 的token.json了
credentials.json and token.json 可以一起copy到server上讓他自己執行, 
否則就需要在server上跑一次, console會提供網址和回傳輸入代碼的方式
輸入代碼後還是可以取得token.json with rtefresh token
token.json若過期,程式會自行refresh token.json

google drive api 原生API docs
https://developers.google.com/drive/api/v3/quickstart/python
https://developers.google.com/drive/api/v3/manage-downloads
x pydrive操作google drive檔案, client.secrets.json 取得方式
https://pythonhosted.org/PyDrive/quickstart.html

x 不要採用service account, 因為會上傳到service account的帳號中, 不好找
https://stackoverflow.com/questions/55527829/what-is-the-role-which-allows-to-use-gcp-apis-such-as-drive-sheets-etc/55527982

"""
import time, os
from pathlib import Path
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
# from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from confs import PATH_PRJ,KEY_FILE_LOCATION,TOKEN_FILE_LOCATION
from pathlib import Path
# 如果更換scope, token也要換
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# KEY_FILE_LOCATION =PATH_PRJ.joinpath('credentials.json')
# TOKEN_FILE_LOCATION=PATH_PRJ.joinpath('token.json')
# Credentials.from_service_account_file(key_file_location)
# ref: pydrive with service account


import loggingsys
try:
    from confs import GLOBAL_LOG_LEVEL
except:
    GLOBAL_LOG_LEVEL = 'DEBUG'

log = loggingsys.generate_general_my_log(log_name="gdrive_util",log_level=GLOBAL_LOG_LEVEL)

# https://www.projectpro.io/recipes/upload-files-to-google-drive-using-python

def get_mimetype(fname:str)->str:

    if '.gz' in  fname:
        str_mimetype = 'application/gzip'
    elif '.py' in fname:
        str_mimetype = 'text/x-python'
    elif '.json' in fname:
        str_mimetype = 'application/json'
    elif '.bz2' in fname:
        str_mimetype = 'application/x-bzip2'
    elif '.zip' in fname:
        str_mimetype = 'application/zip'
    elif '.jpg' in fname:
        str_mimetype = 'image/jpeg'
    elif '.png' in fname:
        str_mimetype = 'image/png'
    elif '.csv' in fname:
        str_mimetype = 'text/csv'
    elif '.xlsx' in fname:
        str_mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif '.xls' in fname:
        str_mimetype = 'application/vnd.ms-excel'
    elif '.gsheet' in fname:
        str_mimetype = 'application/vnd.google-apps.spreadsheet'
    elif '.gdoc' in fname:
        str_mimetype = 'application/vnd.google-apps.document'
    elif '.doc' in fname:
        str_mimetype = 'application/msword'
    elif '.docx' in fname:
        str_mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif '.pptx' in fname:
        str_mimetype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif '.ppt' in fname:
        str_mimetype = 'application/vnd.ms-powerpoint'    
    elif '.txt' in fname:
        str_mimetype = 'text/plain'
    elif '.pdf' in fname:
        str_mimetype = 'application/pdf'    
    else:
        str_mimetype = 'application/octet-stream'

    return str_mimetype

def google_client_api_creds(scopes:list, 
                            key_file_location:str, 
                            token_file_location:str)->Credentials:
    
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

    
# TODO
# def get_list_files_from_gdrive(backup_folder_id:str=GDRIVE_BACKUP_FOLDER_ID,drive=None)->list:
#     # gauth = GoogleAuth()           
#     # drive = GoogleDrive(gauth) 
#     # if drive is None:
#     #     drive = connect_pydrive_gauth_drive()
#     #取得目錄中的檔案清單
#     # file_list = drive.ListFile({'q': f"{backup_folder_id} in parents and trashed=false"}).GetList()
#     # for file in file_list:
#     #     print('title: %s, id: %s' % (file['title'], file['id']))
    
#     return file_list

def get_lst_fname(file_list):
    lst_fname = []
    for dic_file in file_list:
        lst_fname.append(dic_file['title'])
    return lst_fname

def delete_drive_service_file(service, file_id):
    service.files().delete(fileId=file_id).execute()

def search_file(service, update_drive_service_name, is_delete_search_file=False):
    """
    本地端
    取得到雲端名稱，可透過下載時，取得file id 下載
    :param service: 認證用
    :param update_drive_service_name: 要上傳到雲端的名稱
    :param is_delete_search_file: 判斷是否需要刪除這個檔案名稱
    """

    # Call the Drive v3 API
    results = service.files().list(fields="nextPageToken, files(id, name)", 
                                    spaces='drive',
                                   q="name = '" + update_drive_service_name + "' and trashed = false",
                                   ).execute()

    items = results.get('files', [])
    if not items:
        # print('沒有發現你要找尋的 ' + update_drive_service_name + ' 檔案.')
        pass
    else:
        # print('搜尋的檔案: ')
        for item in items:
            times = 1
            # print(u'{0} ({1})'.format(item['name'], item['id']))
            if is_delete_search_file is True:
                
                delete_drive_service_file(service, file_id=item['id'])
                # print("刪除檔案為:" + u'{0} ({1})'.format(item['name'], item['id']))

            if times == len(items):
                return item['id']
            else:
                times += 1

def create_gdrive_folder(
                        service:object,
                        folder_name:str,
                        parent_folder_id:str="", 
                        )->str:
    """
    在指定目錄下建立目錄
    :param drive_service: google drive service
    :param folder_name: folder name
    :return: folder id
    """
    file_metadata = {
        'name': folder_name,
        # 'parents' : [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id != "":
        file_metadata['parents'] = [parent_folder_id]

    try:
        file = service.files().create(body=file_metadata,
                                        fields='id').execute()
        # print(f"Folder ID: {file.get('id')}")
        return file.get('id')

    except Exception as e:
        log.error(e)
        return ""
        

def update_file(parent_folder_id:str,                 
                service:object, 
                path_upload_file:Path, 
                fname:str
                ):
    str_mimetype = get_mimetype(fname)            

    file_metadata = {
                'name': fname,
                'parents': [parent_folder_id],
                'mimeType': str_mimetype
            }

    media = MediaFileUpload(
                            path_upload_file, 
                            mimetype=str_mimetype,                                    
                            resumable=True
                        )
                                
    service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id,name').execute()

def upload_files_to_gdrive_folder(upload_file_list:list,
                                # lst_not_log_files:list,
                                backup_folder_id:str,
                                backup_log_folder_id:str="",
                                backup_ragic_folder_id:str="",
                                backup_ragic_media_folder_id:str=""
                                ):
    """上傳檔案到google drive資料夾
    需要先取得google drive api 的client_secrets.json
    :param upload_file_list: 上傳檔案路徑清單, pathlib.Path
    :param backup_folder: 備份目錄id
    """
    
    # drive = connect_pydrive_gauth_drive()
    #取得目錄中的檔案清單 pydrive
    # lst_files = get_list_files_from_gdrive(backup_folder_id,drive=drive)
    # lst_fname = get_lst_fname(lst_files)
    creds = google_client_api_creds(DRIVE_SCOPES, KEY_FILE_LOCATION, TOKEN_FILE_LOCATION)
    service = build('drive', 'v3', credentials=creds)
    # 取得今天的datestring作為強制上傳的判斷
    str_today = time.strftime("%Y-%m-%d")
    str_this_month = time.strftime("%Y%m")
    for path_upload_file in upload_file_list:
        try:
            fname = path_upload_file.name                                    
            # 檢查是否需要覆蓋            
            
            # 一律覆蓋, 因為清理任務在建立log時就會處理
            is_delete_search_file = True
            # 如果是本日/本月/非log檔案,就強制上傳
            # if str_today in fname:
            #     is_delete_search_file=True
            # elif str_this_month:
            #     is_delete_search_file=True
            # elif fname or fname in lst_not_log_files:
            #     is_delete_search_file=True
            # else:
            #     is_delete_search_file=False
                     
            # 搜尋要上傳的檔案名稱是否有在雲端上並且刪除
            if is_delete_search_file:
                search_file(service=service, update_drive_service_name=fname,
                            is_delete_search_file=is_delete_search_file)
            
            #上傳檔案
            # file = update_file_wrapper(backup_folder_id, backup_log_folder_id, service, path_upload_file, fname)
            if "log" in str(path_upload_file):     
                parent_folder_id = backup_log_folder_id
            elif "ragic_media" in str(path_upload_file):
                parent_folder_id = backup_ragic_media_folder_id
            elif "ragic" in str(path_upload_file):
                parent_folder_id = backup_ragic_folder_id
                # parent_folder_id = create_gdrive_folder(service, 
                #                                     str_today, 
                #                                     parent_folder_id=backup_ragic_folder_id)                 

            else:
                parent_folder_id = backup_folder_id  

            update_file(parent_folder_id,                 
                        service, 
                        path_upload_file, 
                        fname)

        
        # method 1: with pydrive

    #         if alreadyUploaded:
    #             continue
    #         else:
    #             if "log" in fname:     
    #                 this_backup_folder_id = backup_log_folder_id
    #             else:
    #                 this_backup_folder_id = backup_folder_id       

    #             gfile = drive.CreateFile({
    #                 'title': fname,
    #                 'parents': [{'id': this_backup_folder_id}]
    #             })

    #             # Read file and set it as the content of this instance.
    #             gfile.SetContentFile(str(path_upload_file))
    #             gfile.Upload() # Upload the file.

        except Exception as e:
            # print(e)
            log.error(e)
            continue

    log.info('Upload finished.')


if __name__ == "__main__":
    # upload_files_to_gdrive_folder(['1.jpg', '2.jpg'])
    # lst_files = get_list_files_from_gdrive()
    # print(lst_files)
    pass
