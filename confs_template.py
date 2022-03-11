# import time
from pathlib import Path
import os
dic_api = {    
    "log_level": "info",    
    "verifySSL":True,
    }


    #Log setting
GLOBAL_LOG_LEVEL = "INFO" # CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
LOG_BACKUP_COUNT = 60

PATH_PRJ = Path(__file__).resolve().parents[1]
PATH_LOG_FOLDER = PATH_PRJ.joinpath("logs")
#file cache
PATH_DATA_FOLDER = PATH_PRJ.joinpath("data")
PATH_CACHE_FOLDER = PATH_PRJ.joinpath("data","cache")

PATH_TEST = PATH_PRJ.joinpath("tests")
PATH_TEST_DATA = PATH_TEST.joinpath("data")

PATH_BACKUP_FOLDER = PATH_PRJ.joinpath("backup")
PATH_BACKUP_LOG_FOLDER = PATH_BACKUP_FOLDER.joinpath("logs")
PATH_BACKUP_RAGIC_FOLDER = PATH_BACKUP_FOLDER.joinpath("ragic")
PATH_BACKUP_RAGIC_MEDIA_FOLDER = PATH_BACKUP_FOLDER.joinpath("ragic_media")

PATH_RESTORE_FOLDER = PATH_PRJ.joinpath("restore")
PATH_RESTORE_LOG_FOLDER = PATH_RESTORE_FOLDER.joinpath("logs")
PATH_RESTORE_RAGIC_FOLDER = PATH_RESTORE_FOLDER.joinpath("ragic")
PATH_RESTORE_RAGIC_MEDIA_FOLDER = PATH_RESTORE_FOLDER.joinpath("ragic_media")

LST_BACKUP_SETTING = [
        PATH_PRJ.joinpath('apiServer','confs.py'),
        PATH_PRJ.joinpath('apiServer','cred_conf.py'),
        PATH_PRJ.joinpath('credentials.json'),
        PATH_PRJ.joinpath('token.json')
    ]

# BACKUP Setting
# https://drive.google.com/drive/folders/<folderId>
KEY_FILE_LOCATION =PATH_PRJ.joinpath('credentials.json')
TOKEN_FILE_LOCATION=PATH_PRJ.joinpath('token.json')
GDRIVE_BACKUP_FOLDER_ID = ''
GDRIVE_BACKUP_LOG_FOLDER_ID = ''
GDRIVE_BACKUP_RAGIC_FOLDER_ID=''
GDRIVE_BACKUP_RAGIC_MEDIA_FOLDER_ID = ''

GDRIVE_JSON_FILE = PATH_PRJ.joinpath('service_account_key.json')
LOG_PRESERVE_DAYS = 93
RAGIC_PRESERVE_DAYS = 93

_lst_folder_path = [PATH_LOG_FOLDER, 
                    PATH_DATA_FOLDER,
                    PATH_TEST,
                    PATH_TEST_DATA,
                    PATH_BACKUP_FOLDER,
                    PATH_BACKUP_LOG_FOLDER,
                    PATH_BACKUP_RAGIC_FOLDER,
                    PATH_BACKUP_RAGIC_MEDIA_FOLDER,
                    PATH_RESTORE_FOLDER,
                    PATH_RESTORE_LOG_FOLDER,
                    PATH_RESTORE_RAGIC_FOLDER,
                    PATH_RESTORE_RAGIC_MEDIA_FOLDER,                     
                    PATH_CACHE_FOLDER
                ]
for _path in _lst_folder_path:
    # print(f"{_path=}")
    if not _path.exists():
        try:
            os.mkdir(_path)
        except:
            pass
