import time
from datetime import datetime
from gmail_util import get_token, convert_query_list_str,get_api_url_from_query,\
        list_emails, delete_emails
from confs import DIC_QUERY,REFRESH_SLEEP_SECONDS
import threading

def gmail_batch_search_delete():
    str_token = get_token()
    for key, lst_query in DIC_QUERY.items():
        str_query = convert_query_list_str(lst_query)
        str_url = get_api_url_from_query(str_query)
        lst_r = list_emails(str_url, str_token)
        print(lst_r)
        if len(lst_r) > 0:
            try:
                delete_emails(lst_r, "me", token=str_token)
            except Exception as e:
                print(e)
    dt_now = datetime.now()
    str_dt_now = dt_now.strftime("%Y%m%d%H%M%S")
    print(f"gmail_batch_search_delete done at {str_dt_now}")


# if __name__ == '__main__':
while True:
    t = threading.Thread(target=gmail_batch_search_delete, args=())
    t.start()
    # gmail_batch_search_delete()
    time.sleep(REFRESH_SLEEP_SECONDS)