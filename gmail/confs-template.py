
from pathlib import Path
# 要搜尋的gmail郵件條件
# ref: https://support.google.com/mail/answer/7190
REFRESH_SLEEP_SECONDS = 120

DIC_QUERY = {
    "joyboy@gmail.com":[ #條件名稱, 方便自己維護
        "from:joyboy@gmail.com",
        "subject:(晚餐 電影 錢)"
        "is:unread",
        "newer_than:1d"]
}

SCOPES = [
    # 'https://www.googleapis.com/auth/gmail.readonly',
    'https://mail.google.com/',
    ]
    
PATH_PRJ = Path(__file__).resolve().parents[1]

TOKEN_FILE_LOCATION = PATH_PRJ.joinpath('gmail','token.json')
KEY_FILE_LOCATION = PATH_PRJ.joinpath('gmail','credentials.json')
