import os
import requests
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

regist_url = "https://v.ruc.edu.cn/campus/Regist/regist"

regist_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "", # get from ruclogin
    "Origin": "https://v.ruc.edu.cn",
    "Pragma": "no-cache",
    "Referer": "https://v.ruc.edu.cn/campus",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "rucactivity/0.2",
    "X-Requested-With": "XMLHttpRequest",
}

regist_data = {
    "aid": ""
}

def regist_activity(cookies: str, aid: int | str) -> dict:
    print(f"regist_activity({aid}):", datetime.now())

    regist_headers["Cookie"] = cookies
    regist_data["aid"] = str(aid)
    
    regist_response = requests.post(regist_url, headers=regist_headers, data=regist_data)
    print(f"regist_activity({aid}) =>", json.loads(regist_response.text))
    return json.loads(regist_response.text)

# example response:
# {'code': 0, 'msg': '报名成功', 'join': {'code': 3, 'data': '取消报名'}}
# {'code': 1, 'msg': '活动报名名额已满'} # 名额已满
# {'code': 1, 'msg': '报名失败'} # 已报名
