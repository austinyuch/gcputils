#!/usr/bin/python3
# -*- coding: utf-8 -*-
import smtplib

from email.message import EmailMessage
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

from email.utils import make_msgid

import glob
import os
from pathlib import Path
import time
# from pathlib import Path

from cred_conf import DIC_SMTP

        
from confs import dic_api,PATH_LOG_FOLDER,GLOBAL_LOG_LEVEL

SMTP_URL = DIC_SMTP["smtp_url"]
SMTP_PORT = DIC_SMTP["smtp_port"]
SENDER = DIC_SMTP["sender"]
SENDER_PWD = DIC_SMTP["sender_pwd"]

RECEIVERS = DIC_SMTP["receivers"]
RECEIVERS_DEV_TEAM = DIC_SMTP["receivers_dev_team"]
SITE_NAME = dic_api["site_name"]
if "receivers_customer_service" in DIC_SMTP:
    RECEIVERS_CUSTOMER_SERVICE = DIC_SMTP["receivers_customer_service" ]
else:
    RECEIVERS_CUSTOMER_SERVICE = RECEIVERS

import loggingsys

log = loggingsys.generate_general_my_log(log_name=__name__,log_level=GLOBAL_LOG_LEVEL)


# CLOUD_FOLDER = "G:\\我的雲端硬碟\\test_data_report\\"
# ref: https://www.roytuts.com/how-to-send-attachments-with-email-using-python/
# https://www.lightblue.asia/send-gmail-by-python/
# 要開啟安全性設定中"比較不安全app"的設定 https://myaccount.google.com/lesssecureapps

DEFAULT_RESULT_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'report_results')
# if not os.path.isdir(DEFAULT_RESULT_FOLDER):


def get_lst_files_in_directory(str_abs_folder_path, str_endswith):
    lst_files_in_directory = glob.glob(
        f'{str_abs_folder_path}/*{str_endswith}')
    return lst_files_in_directory


def compose_mail(
    lst_receivers,
    msg_subject,
    msg_body,
    lst_files,
    # file_extention='xlsx',
    smtp_url=SMTP_URL,
    smtp_port=SMTP_PORT,
    sender=SENDER,
    sender_pwd=SENDER_PWD
):
    '''
    compose_mail(
        lst_receivers=lst_receivers,
        msg_subject=msg_subject,
        msg_body=msg_body,
        lst_files=lst_files,
        file_extention=file_extention,
        smtp_url=SMTP_URL,
        smtp_port=SMTP_PORT,
        sender=SENDER,
        sender_pwd=SENDER_PWD
        )
    '''
    # lst_receivers = lst_receivers  # 'epaservice@cameo.tw'
    timestr = time.strftime("%Y-%m-%dT%H:%M:%S")  # %H%M%S
    msg_subject = f'{msg_subject} {timestr}'
    # msg_body = f'''
    #             {msg_subject}
    #             {msg_body}
    #             '''

    dic_mail = {
        'lst_receivers': lst_receivers,
        'Subject': msg_subject,
        'msg_body': msg_body,
        'lst_files': lst_files,
        # 'file_extention': file_extention,
        'smtp_url': smtp_url,
        'smtp_port': smtp_port,
        'sender': sender,
        'sender_pwd': sender_pwd,
    }
    return dic_mail


def determine_ctype(file_extention):
    dic_mime = {
        'html': 'text/html',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'xml': 'text/xml',
        'xlsx': 'application/vnd.ms-excel',
        'xls': 'application/vnd.ms-excel',
        'zip': 'application/x-zip-compressed',
        'misc': 'application/octet-stream'
    }

    try:
        if file_extention in ('zip', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'xml', 'html'):
            ctype = dic_mime[file_extention]
        else:
            ctype = 'application/octet-stream'
    except:
        ctype = 'application/octet-stream'

    return ctype

# def attach_files_to_msg(msg, lst_file_extention, str_abs_folder_path):


def attach_files_to_msg(msg, lst_files):
    '''
    :param msg: mail message物件
    :param lst_files: 檔案名稱字串構成的list

    '''

    # extention to be attached

    # attach each file
    for str_filepath in lst_files:
        basefilename = str(Path(str_filepath).name)
        file_extention = str(Path(str_filepath).suffix).lower()
        ctype = determine_ctype(file_extention)
        # basefilename = os.path.basename(str_filepath)
        # print(f'Now open {str_filepath}')
        with open(str_filepath, 'rb') as fp:

            file_attached = fp.read()

            # print(f'ctype: {ctype}')
            maintype, subtype = ctype.split('/', 1)
            # print(f'maintype: {maintype}; subtype: {subtype}')

            # print(f'basefilename: {basefilename}')
            msg.add_attachment(file_attached, maintype=maintype,
                               subtype=subtype, filename=basefilename)

    return msg


def get_lst_receivers(str_receivers):

    lst_receivers = []
    if len(str_receivers) >= 1:
        # lst_receivers = str_receivers.split(',')
        lst_receivers = [str_receiver.strip() for str_receiver in str_receivers.split(',')]
    # for i in range(len(lst_receivers)):
    #     lst_receivers[i] = lst_receivers[i].strip()
    return lst_receivers


# def send_mail(lst_receivers, msg_subject, msg_body, file_extention, lst_files):
def send_mail(lst_receivers, 
            msg_subject, 
            msg_body, 
            lst_files=[],
            is_html=True,
            is_test=False):
            
    dic_mail = compose_mail(
        lst_receivers=lst_receivers,
        msg_subject=msg_subject,
        msg_body=msg_body,
        lst_files=lst_files,
        # file_extention=file_extention,
        smtp_url=SMTP_URL,
        smtp_port=SMTP_PORT,
        sender=SENDER,
        sender_pwd=SENDER_PWD
    )
    '''
    
    dic_mail = {
        'lst_receivers': lst_receivers,
        'Subject': msg_subject,
        'msg_body': msg_body,
        'lst_files':'lst_files',
        # 'file_extention': file_extention,
        'smtp_url': smtp_url,
        'smtp_port': smtp_port,
        'sender': sender,
        'sender_pwd': sender_pwd,
    }
    '''
    msg = EmailMessage()
    # msg = MIMEMultipart('alternative')

    asparagus_cid = make_msgid()
    # print(dic_mail)
    if is_html:
        # https://stackoverflow.com/questions/882712/sending-html-email-using-python
        msg.set_content(dic_mail['msg_body'], subtype='html')
    else:
        msg.set_content(dic_mail['msg_body'])
    # msg_body = MIMEText(dic_mail['msg_body'], 'html')
    # msg.attach(msg_body)

    msg['Subject'] = dic_mail['Subject']
    msg['From'] = dic_mail['sender']
    msg['To'] = ','.join(dic_mail['lst_receivers'])
    

    # lst_files = dic_mail['lst_files']
    # print(f'lst_files in send_mail func:{lst_files}')
    if len(lst_files) > 0:
        # msg = attach_files_to_msg(msg, file_extention, lst_files)
        msg = attach_files_to_msg(msg, lst_files)

    # s = smtplib.SMTP('smtp.gmail.com', 587) # qq.com 只支援SMTP_SSL

    # s.login(sender, sender_pwd)
    try:
        try:
            str_msg_method = 'method1 SMTP_SSL qq sent success'
            # qq smtp ref:https://zhuanlan.zhihu.com/p/147285001
            # qq.com 需要取得授權碼才能用smtp在第三方程式裡面發信
            # https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256%27)
            print(str_msg_method)
            with smtplib.SMTP_SSL(dic_mail['smtp_url'],  dic_mail['smtp_port']) as s:
            # s = smtplib.SMTP_SSL(dic_mail['smtp_url'],  dic_mail['smtp_port'])
                s.login(dic_mail['sender'], dic_mail['sender_pwd'])
                s.send_message(msg)
                # s.quit()
                # print('method2 qq sent success')
                log.info(str_msg_method)
            isSuccess = True             

        except smtplib.SMTPException as e:
            # print(e)
            log.warning(f"{str_msg_method} {e}")
            isSuccess = False            
    except:
        try:
            str_msg_method = 'method2 SMTP gmail,outlook'
            # https://medium.com/@neonforge/how-to-send-emails-with-attachments-with-python-by-using-microsoft-outlook-or-office365-smtp-b20405c9e63a
            print(str_msg_method)
            with smtplib.SMTP(dic_mail['smtp_url'], dic_mail['smtp_port']) as s:
            # s = smtplib.SMTP(dic_mail['smtp_url'], dic_mail['smtp_port'])
    #         s.ser_debuglevel(1)
                s.ehlo()
                s.starttls()  # qq.com不支援這個
                s.login(dic_mail['sender'], dic_mail['sender_pwd'])
                s.send_message(msg)
                # s.quit()
                # print('method1 sent success')
                log.info("method1 sent success")            
            isSuccess = True            

        except smtplib.SMTPException as e:
            # print(e)
            log.warning(f"{str_msg_method} {e}")
            isSuccess = False
    
    return isSuccess

def main(sender_pwd):

    # str_abs_folder_path = os.path.join(
    #     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Results')
    # toEmail = 'epaservice@cameo.tw'
    # sender_pwd = {PWD}
    dic_mail = compose_mail(sender_pwd=sender_pwd)
    send_mail(dic_mail)


if __name__ == "__main__":
    dic_customer_request = {
            "requirementTypes":"資金需求,辦公室需求,輔導需求,媒合需求",
            "requirementRightTypes":"申請新創會員,申請登入平台,系統問題,其他",
            "requirementComment":"測試內容信件內容改版測試 requirementCommentrequirementCommentrequirementComment",
            "fullname":"Mark Thatborg",
            "phone":"0912345678",
            "email":"ycchang.pmp@gmail.com",
            "companyName":"後設 Inc.",
            "companyTaxId":"12345678"
    }

    pass
    # main()
    """
    2021-06-24 08:23:19,642 - method1 gmail,outlook 
    (534, b'5.7.14 <https://accounts.google.com/signin/continue?sarp=1&scc=1&plt=AKgnsbt\n5.7.14 
    PS4lkZZxZ9k1qVebX5S36uzgCbnXdUDl0IgMqGaa2b1cbbIn8l4AFsyQvrjG2S-ZVd4xC\n5.7.14 2NxWqWAd4KXYBLbs6K3d4E3U9NPrpJe8T9YVrg33lFdEsuhd57Cl-pxFFAYiAptG>\n
    5.7.14 Please log in via your web browser and then try again.\n5.7.14  Learn more at\n5.7.14  
    https://support.google.com/mail/answer/78754 s10sm1268917ilv.81 - gsmtp')
    """
