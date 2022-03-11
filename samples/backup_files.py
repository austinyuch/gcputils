"""
將需要備份的檔案複製到backup目錄
"""

import time,os,sys
import tarfile
from pathlib import Path
from shutil import copyfile
from confs import PATH_LOG_FOLDER, PATH_BACKUP_FOLDER,LST_BACKUP_SETTING,\
    GLOBAL_LOG_LEVEL

from confs import GDRIVE_BACKUP_FOLDER_ID, GDRIVE_JSON_FILE
from confs import LOG_PRESERVE_DAYS, GDRIVE_BACKUP_LOG_FOLDER_ID
from confs import RAGIC_PRESERVE_DAYS, GDRIVE_BACKUP_RAGIC_FOLDER_ID,GDRIVE_BACKUP_RAGIC_MEDIA_FOLDER_ID
from confs import PATH_BACKUP_RAGIC_FOLDER, PATH_BACKUP_RAGIC_MEDIA_FOLDER, PATH_BACKUP_LOG_FOLDER

from glob import glob, iglob
from io import StringIO, BytesIO
from gdrive.gdrive_util import upload_files_to_gdrive_folder

from backup_ragic import backup_ragic

import loggingsys

log = loggingsys.generate_general_my_log(log_name="backup_files",log_level=GLOBAL_LOG_LEVEL)


# tarfile example
# def tar_dir(path,prefix):
#     tarfname=f'{prefix}.tar.gz'
#     tar = tarfile.open(tarfname, 'w:gz')
   
#     for root, dirs, files in os.walk(path):
#         for file_name in files:
#             tar.add(os.path.join(root, file_name))

#     tar.close()

def backup_settings():
    """
    apiServer/cred_conf.py, confs.py -> backup/
    """
    for path in LST_BACKUP_SETTING:
        try:
            copyfile(path,PATH_BACKUP_FOLDER.joinpath(path.name))
        except Exception as e:
            log.error(e)
    

def targz_lst_files_in_dir(path_dir=PATH_LOG_FOLDER):
    """
    backup_logs
    logs/* -> backup/logs/<logfilename>.tar.gz"
    """
    lst_str_paths = glob(f"{path_dir}/*")
    # print(backup_logs)
    for str_path in lst_str_paths:
        try:
            # print(path)
            path_file = Path(str_path)
            original_fname=path_file.name
            tarfname=f'{original_fname}.tar.gz'
            # prefix = path_file.stem
            # tarfname=f'{prefix}.tar.gz'
            path_tar = PATH_BACKUP_FOLDER.joinpath('logs',tarfname)
            tar_file = tarfile.TarInfo(name=original_fname)
            """
            ref: https://programtalk.com/python-examples/tarfile.TarInfo/
            """
            try:
                # Python 3 (StringIO gets converted to io module)
                MemFile = BytesIO
            except AttributeError:
                MemFile = StringIO

            with open(path_file, 'r') as file:
                file_data = file.read().rstrip()

            path_file_bytes = MemFile(file_data.encode('utf-8'))
            tar_file.size = len(path_file_bytes.getvalue())
            tar_file.mtime=os.path.getmtime(path_file) 
            dist = tarfile.open(path_tar, 'w:gz')
            try:
                dist.addfile(tar_file, fileobj=path_file_bytes)
            finally:
                dist.close()   

        except Exception as e:
            log.error(e)               

def get_file_path_in_dir(path_dir:Path=PATH_BACKUP_FOLDER)->list:
    lst_file_paths = []
    
    for file_name in glob(f"{str(path_dir)}/**/*", recursive=True):
        if Path(file_name).is_file():
            lst_file_paths.append(Path(file_name))
    
    return lst_file_paths

def cleanup_local_files(
                days_to_keep:int,
                path_dir:Path
            ):
    """
    刪除超過天數的檔案
    """
    lst_fpath = get_file_path_in_dir(path_dir=path_dir)
    for fpath in lst_fpath:
        try:
            if (time.time() - fpath.stat().st_mtime) > (days_to_keep * 24 * 60 * 60):
                # fpath.unlink()
                os.remove(fpath)
            log.info(f"cleanup file {fpath.name} done")

        except Exception as e:
            log.error(e)


def upload_backup_gdrive():
    """
    將檔案備份並且上傳至google drive
    """    
    try:
        lst_backup_files = get_file_path_in_dir()

        upload_files_to_gdrive_folder(lst_backup_files, 
                                    # lst_not_log_files=LST_BACKUP_SETTING,
                                    backup_folder_id=GDRIVE_BACKUP_FOLDER_ID,
                                    backup_log_folder_id=GDRIVE_BACKUP_LOG_FOLDER_ID,
                                    backup_ragic_folder_id=GDRIVE_BACKUP_RAGIC_FOLDER_ID,
                                    backup_ragic_media_folder_id = GDRIVE_BACKUP_RAGIC_MEDIA_FOLDER_ID
                                    )      

    except Exception as e:
        # print(e)
        log.error(e)
    
    
def backup_files(
                # to_backup_setting:bool=True,
                # to_backup_logs:bool=True,
                # to_upload_backup_gdrive:bool=True,
                # to_cleanup_logs:bool=True,
                isTest:bool=False):
    """
    備份設定檔到backup目錄
    打包log目錄backup/logs目錄
    清理log目錄
    """
    if isTest==False:
        to_backup_setting=True
        to_backup_logs=True
        to_backup_ragic=True
        to_backup_ragic_media=True
        to_upload_backup_gdrive=True
        to_cleanup_logs=True
        to_cleanup_ragic=True
        to_cleanup_ragic_media=True
        str_msg_success="備份完成。"

    elif isTest==True:
        to_backup_setting=False
        to_backup_logs=False
        to_backup_ragic=False
        to_backup_ragic_media=False
        to_upload_backup_gdrive=False
        to_cleanup_logs=False
        to_cleanup_ragic=False
        to_cleanup_ragic_media=False
        str_msg_success="備份測試完成。"

    if to_backup_setting:
        backup_settings()

    if to_backup_logs:
        targz_lst_files_in_dir()

    if to_backup_ragic:        
        backup_ragic(to_backup_media=to_backup_ragic_media)

    if to_upload_backup_gdrive:
        upload_backup_gdrive()

    if to_cleanup_logs:     
        # original log files   
        cleanup_local_files(
                        days_to_keep=32,
                        path_dir=PATH_LOG_FOLDER,
                        )
        # gzipped log files
        cleanup_local_files(
            days_to_keep=LOG_PRESERVE_DAYS,
            path_dir=PATH_BACKUP_LOG_FOLDER
            )

    if to_cleanup_ragic:
        cleanup_local_files(
            days_to_keep=RAGIC_PRESERVE_DAYS,
            path_dir=PATH_BACKUP_RAGIC_FOLDER
        )
    
    if to_cleanup_ragic_media:
        cleanup_local_files(
            days_to_keep=RAGIC_PRESERVE_DAYS,
            path_dir=PATH_BACKUP_RAGIC_MEDIA_FOLDER
        )
    log.info(str_msg_success)
    

if __name__ == "__main__":
    backup_files()
    # ret = get_file_path_in_dir(PATH_BACKUP_FOLDER)
    # print(ret)
    # backup_settings()
    # targz_lst_files_in_dir()
    pass
