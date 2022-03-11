"""
讀取Ragic資料表網址清單
將指定的Ragic網址爬下來
將json格式檔案, 依照指定檔案名稱格式存成文字檔, 並儲存到指定目錄
壓縮打包
（選擇性）, 上傳到google drive
"""
import requests
import asyncio
import os
import json
import time
import shutil
import gzip
from pathlib import Path
from confs import RAGIC_TAB_URL,RAGIC_FILE_API,GLOBAL_LOG_LEVEL,dic_api

from confs import DIC_RAGIC_TABLE_ID, DIC_RAGIC_TABLE_CONF, \
    PATH_BACKUP_FOLDER,PATH_BACKUP_RAGIC_FOLDER, PATH_BACKUP_RAGIC_MEDIA_FOLDER
# from cred_conf import RagicAPIKey

import loggingsys
log = loggingsys.generate_general_my_log(log_name=__name__,log_level=GLOBAL_LOG_LEVEL)

verifySSL=dic_api['verifySSL']

# def get_file_url(str_fname:str,withRagicAPIKey:bool=True)->str:
#     # str_fname = str_fname.encode('utf-8') # 會變成b'xxxx'
#     if str_fname != "":    
#         str_file_api = RAGIC_FILE_API
#         str_url = f"{str_file_api}{str_fname}"
#         if withRagicAPIKey:
#             str_url = f"{str_url}&APIKey={RagicAPIKey}"
#         # log.debug(f"get_file_url {str_url=}")
#         return str_url
#     else:
#         return str_fname

# def get_dic_ragic_api_urls(dic_ragic_table_id:dict=DIC_RAGIC_TABLE_ID, 
#                             use_value:bool=True,
#                             max_row_value=9999999)->dict:
#     """
#     取得Ragic網址清單
#     設定檔範例
#     DIC_RAGIC_TABLE_ID = {
#     "page":"4",#"1",
#     "section":"5",#"2",
#     "chart":"3"
#     }
#     -->    {"id1":"url1","id2":"url2"}
    
#     """
#     dic_urls = {}
#     args=f'api&APIKey={RagicAPIKey}&limit=0,{max_row_value}'
    
#     for k,v in dic_ragic_table_id.items():
#         if use_value:
#             _url = f"{RAGIC_TAB_URL}/{v}?{args}"
#             dic_urls[v] = _url
#         else:
#             _url = f"{RAGIC_TAB_URL}/{k}?{args}"
#             dic_urls[k] = _url            

#     return dic_urls



def requests_get_n_times(
                        str_url:str,
                        max_trial:int=3,
                        verifySSL:bool=True 
                    )->dict:
    # 有時候ragic回應會是空的, 多試2次
    _trial = 0
    # max_trial = 5
    isFail = True
    
    while _trial < max_trial and isFail == True:
        try:
            _r = requests.get(str_url,verify=verifySSL)
            dic_r = _r.json()   
            if dic_r == {}: # TODO or dic_r['status'] != 'SUCCESS'
                isFail = True                
            else:
                isFail = False                    
        except:
            dic_r = {}
            isFail = True
            time.sleep(1)
        finally:
            _trial += 1

    return dic_r


def get_path_gz(tableId:str,
                path_dest_folder:Path=PATH_BACKUP_RAGIC_FOLDER,
                with_str_date:bool=True
            )->Path:
    tableId = str(tableId)
    if with_str_date:
        fname = f"{time.strftime('%Y-%m-%d')}_{tableId}.json.gz"
        path_gz = path_dest_folder.joinpath(fname)
    else:
        path_gz = path_dest_folder.joinpath(f"{tableId}.json.gz")
    return path_gz


def save_dict_to_gz(str_id:str, 
                    dic_r:dict, 
                    path_gz:Path,
                    path_dest_folder:Path=PATH_BACKUP_RAGIC_FOLDER,
                    to_clean_json:bool=True,                    
                    
                    ):
    str_id = str(str_id)
    path_fname = path_dest_folder.joinpath(f"{str_id}.json")

    try:
        # 存成json檔
        with open(path_fname, 'w', encoding='utf8') as f:
            json.dump(dic_r, f,ensure_ascii=False)

        # 打包成gz
        with open(path_fname, 'rb') as f_in, gzip.open(path_gz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        if to_clean_json:
            # 清理原本的json文字檔
            os.remove(path_fname)

        print(f'table {str_id} backuped')
        return path_gz

    except Exception as e:
        log.error(e)
        return None

def download_files(lst_file_urls, 
                lst_fpaths,
                verifySSL:bool=dic_api["verifySSL"],
                timeSleep:float=0.5 ):
    """
    批次下載檔案存到目標路徑
    """
    lst_fpath_success = []    
    for i,url in enumerate(lst_file_urls):
        fpath = lst_fpaths[i]
        ext = fpath.suffix
        if ext in [".html", ".csv", ".json", ".xml",".txt",".py",".js",".css",".md"]:
            isText = True
        else:
            isText = False
        try:            
            #ref: https://stackoverflow.com/questions/31126596/saving-response-from-requests-to-file
            if isText:
                r = requests.get(url, verify=verifySSL)
                with open(fpath, 'w', encoding='utf8') as f:
                    # f.write(r.content)
                    f.write(r.text)
            # otherwise:
            else:
                r = requests.get(url, stream=True,verify=verifySSL)
                with open(fpath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

            lst_fpath_success.append(fpath)
            # 休息一下減少Ragic server負擔
            time.sleep(timeSleep)

        except Exception as e:
            log.error(e)
            continue

    return lst_fpath_success

# def backup_ragic_media(tableId:str,
#                         dic_r:dict, 
#                         path_dest_folder:Path=PATH_BACKUP_RAGIC_MEDIA_FOLDER,
#                         dic_ragic_table_conf:dict=DIC_RAGIC_TABLE_CONF,
#                         is_test:bool=False):
#     """
#     將ragic api回傳值中帶有附件的欄位, 存成檔案
#     fname = f"{str_today},{tableId},{_ragicId},{col_id},{fname_src}"
#     (還原時依照檔案名稱中的tableid, ragicid, colid, filename 建立requests.post)
#     str_today = time.strftime('%Y-%m-%d')
#     fpath = path_dest_folder.joinpath(fname)        
#     :param tableId: Table Id
#     :param dic_r: Ragic API回傳值 (dictionary, raw data)
#     :param path_dest_folder: 存檔目錄
#     :param dic_ragic_table_id: Ragic API table config data (table schema etc.)
#     :return: lst_fpaths: 存檔檔案列表
#      fname = fname_dest.split(",")[4]
#     """
#     lst_col_file = dic_ragic_table_conf[tableId]['LST_COL_FILE']
    
#     dic_col_id = dic_ragic_table_conf[tableId]['DIC_COL_ID']

#     lst_file_urls = []
#     lst_fpaths = []

#     # iterate dic_r, get lst_file_urls and lst_fpaths
#     str_today = time.strftime('%Y-%m-%d')
#     for k, dic_row in dic_r.items():
#         _ragicId = str(k)
#         # v: row data in dic
#         for file_col in lst_col_file:
#             # e.g  "htmlfile"
#             if file_col in dic_row:
#                 # e.g  "htmlfile"
#                 str_fid = dic_row[file_col] #"593ctIVZCD@article_20220120_5.html"
#                 str_url = get_file_url(str_fid) #article_20220120_5.html
#                 fname_src = str_fid.split("@")[1]
#                 lst_file_urls.append(str_url)
#                 col_id = dic_col_id[file_col]
#                 fname_dest = f"{str_today},{tableId},{_ragicId},{col_id},{fname_src}"
                
#                 fpath = path_dest_folder.joinpath(fname_dest)   
#                 lst_fpaths.append(fpath)

#     # batch download files
#     if not is_test:
#         lst_fpaths_success = download_files(lst_file_urls, lst_fpaths)
#     else:
#         lst_fpaths_success = lst_fpaths

#     return lst_fpaths_success
        

# def fetch_lst_urls_to_gz(
#                         dic_urls:dict,
#                         to_clean_json=True,
#                         to_backup_media:bool=True,
#                         is_test:bool=False
#                        ):
#     """
#     {"id1":"url1","id2":"url2"}
#     for each return of url: format example:
#         dic_r =  {"26":{
#         "_ragicId": 26,
#         "_star": false,
#         "id": "26",
#         "_index_title_": "26",
#         "filename": "article_20220120_5.html",
#         "title": "Malaysia Smart Cities Outlook",
#         "subTitle": "",
#         "tags": ["Malaysia"],
#         "img": "",
#         "pageView": "6",
#         "author": "Alan Kang",
#         "intro": "",
#         "createDate": "2022/01/20",
#         "_index_calDates_": "d1000111 2022/01/20 d1000112 2022/01/21",
#         "modifiedDate": "2022/01/21",
#         "htmlfile": "593ctIVZCD@article_20220120_5.html",
#         "isPublic": "True",
#         "_index_": "",
#         "_seq": 1
#         },
#     "25":{},...
#     }
#     """
#     lst_gz_paths = []
#     lst_fpaths_success=[]
#     for k,v in dic_urls.items():
#         try:
#             dic_r = requests_get_n_times(dic_urls[k],
#                                     verifySSL=dic_api["verifySSL"]
#                                 )
#             tableId = str(k)
#             path_gz = get_path_gz(tableId,
#                                 path_dest_folder=PATH_BACKUP_RAGIC_FOLDER,
#                                 with_str_date=True)
#             if not is_test:
#                 path_gz = save_dict_to_gz(tableId, 
#                             dic_r,
#                             path_gz,
#                             path_dest_folder=PATH_BACKUP_RAGIC_FOLDER,
#                             to_clean_json=to_clean_json,
#                             # to_save_attached_media=True
#                             )
#             lst_gz_paths.append(path_gz)
#             # 休息一下減少Ragic server負擔
#             time.sleep(1)

#             if to_backup_media:
#                 lst_fpaths_success = backup_ragic_media(tableId, 
#                                         dic_r, 
#                                         path_dest_folder=PATH_BACKUP_RAGIC_MEDIA_FOLDER,
#                                         dic_ragic_table_conf=DIC_RAGIC_TABLE_CONF,
#                                         is_test=is_test)
             
#         except Exception as e:
#             log.error(e)
#             continue

#     return lst_gz_paths,lst_fpaths_success

# def backup_ragic(to_clean_json:bool=True,
#                 to_backup_media:bool=True
#             ):
#     dic_urls = get_dic_ragic_api_urls()
#     lst_gz_paths,lst_fpaths_success = fetch_lst_urls_to_gz(dic_urls,
#                                                 to_clean_json=to_clean_json,
#                                                 to_backup_media=to_backup_media                                                
#                                             )
#     return lst_gz_paths,lst_fpaths_success

if __name__ == "__main__":
    lst_gz_paths,lst_fpaths_success = backup_ragic()
    
    
    # print(lst_urls)
    pass