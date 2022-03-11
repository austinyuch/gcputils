import requests
import time

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
