import os
import ruclogin
import requests
import json
import base64
from typing import List
from datetime import datetime
from dotenv import load_dotenv

from json_utils import save_json, load_json
from email_utils import send_email
from regist import regist_activity

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

REGIST_EXCLUDE_PATH = "exclude.json"

search_url = "https://v.ruc.edu.cn/campus/v2/search"

activity_detail_url = "https://v.ruc.edu.cn/campus#/activity/partakedetail/{aid}/show"

search_headers = {
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
    "X-KL-Ajax-Request": "Ajax_Request",
    "X-Requested-With": "XMLHttpRequest",
}

cookie_template = "session={session}; access_token={access_token}; tiup_uid={tiup_uid}"

search_data = {
    "perpage": "15",
    "page": "1",
    "typelevel1": "", # set in .env
    "typelevel2": "", # set in .env
    "typelevel3": "", # set in .env
    "applyscore": "0",
    "begintime": "",
    "location": "",
    "progress": "3", # 活动状态：3 - 未开始
    "owneruid": "",
    "sponsordeptid": "",
    "query": "",
    "canregist": "0"
}

def get_cookies_str() -> str:
    cookies = ruclogin.get_cookies(domain="v")
    if not ruclogin.check_cookies(cookies):
        cookies = ruclogin.get_cookies(cache=False, domain="v")
        if not ruclogin.check_cookies(cookies):
            raise ValueError("Cookies invalid!")
    return cookie_template.format(session=cookies["session"],
                           access_token=cookies["access_token"],
                           tiup_uid=cookies["tiup_uid"])

def embed_image(image_url: str, cookies: str) -> str:
    print(f"downloading image: {image_url}")

    if image_url.endswith(".jpeg") or image_url.endswith(".jpg"):
        tag_template = """<img src="data:image/jpeg;base64,{encoded_img}">\n"""
    elif image_url.endswith(".png"):
        tag_template = """<img src="data:image/png;base64,{encoded_img}">\n"""
    elif image_url.endswith(".gif"):
        tag_template = """<img src="data:image/gif;base64,{encoded_img}">\n"""
    else:
        raise ValueError("Unknown image format!")

    response = requests.get(image_url, headers={"Cookie": cookies})

    encoded_img = base64.b64encode(response.content).decode('utf-8')

    return tag_template.format(encoded_img=encoded_img)

class Activity:
    def __init__(self, activity: dict):
        self.aid = activity["aid"]
        self.aname = activity["aname"] # 活动名称

        self.progressname = activity["progressname"] # 活动状态：报名中/进行中/已结束/...
        self.registname = activity["registname"] # 报名状态：进行中/已满员/已结束/...
        self.registernum = activity["registernum"] # 已报名人数
        self.allowednum = activity["allowednum"] # 允许报名名额

        # 活动起止时间
        self.begintime = activity["begintime"]
        self.endtime = activity["endtime"]
        
        # 报名起止时间
        self.registbegintime = activity["registbegintime"]
        self.registendtime = activity["registendtime"]

        self.abstract = activity["abstract"] # 活动简介
        self.poster = activity["poster"] # 活动海报链接
        self.location = activity["location"] # 活动地点
        self.contacts = activity["contacts"] # 组织单位联系方式
        self.partakemodename = activity["partakemodename"] # 参与方式：签到/...

    def dump_dict(self) -> dict:
        activity_dict = {
            "aid": self.aid,
            "aname": self.aname,
            "progressname": self.progressname,
            "registname": self.registname,
            "registernum": self.registernum,
            "allowednum": self.allowednum,
            "begintime": self.begintime,
            "endtime": self.endtime,
            "registbegintime": self.registbegintime,
            "registendtime": self.registendtime,
            "abstract": self.abstract,
            "poster": self.poster,
            "location": self.location,
            "contacts": self.contacts,
            "partakemodename": self.partakemodename,
        }
        return activity_dict

    def dump_html(self, cookies: str) -> str:
        html = ""

        html += f"""<h2><a href="{activity_detail_url.format(aid=self.aid)}">{self.aname}</a></h2>\n"""
        html += f"""<p>报名<strong>{self.registname}</strong> ({self.registernum}/{self.allowednum}) | 活动<strong>{self.progressname}</strong></p>\n"""
        html += f"""<p>活动起止时间：<strong>{self.begintime} 至 {self.endtime}</strong></p>\n"""
        html += f"""<p>活动地点：{self.location}</p>\n"""
        html += f"""<p>报名起止时间：{self.registbegintime} 至 {self.registendtime}</p>\n"""
        html += embed_image(self.poster, cookies)
        html += f"""<p>{self.abstract}</p>\n"""
        html += f"""<p>组织单位联系方式：{self.contacts}</p>\n"""
        html += f"""<p>参与方式：{self.partakemodename}</p>\n"""

        return html

def export_html(activity_list: List[Activity], file_name: str, cookies: str) -> None:
    html = ""
    for a in activity_list:
        html += a.dump_html(cookies)
    html = "<html>\n<body>\n" + html + "</body>\n</html>\n"

    with open(file_name, "w", encoding='utf-8') as f:
        f.write(html)

    print(f"activities exported to: {file_name}")

def main():
    print("\nmain():", datetime.now()) # logging

    # 0. load env
    load_dotenv()

    search_data["typelevel1"] = os.getenv("TYPELEVEL1")
    search_data["typelevel2"] = os.getenv("TYPELEVEL2")
    search_data["typelevel3"] = os.getenv("TYPELEVEL3")

    # 1. load exclude list
    exclude_aids = load_json(REGIST_EXCLUDE_PATH)
    if exclude_aids is None:
        exclude_aids = []
    assert isinstance(exclude_aids, list)

    # 2. fetch search query
    cookies = get_cookies_str()
    print(f"cookies: {cookies}")
    search_headers["Cookie"] = cookies

    search_response = requests.post(search_url, headers=search_headers, data=search_data)
    search_result = json.loads(search_response.text)
    print(f"response code: {search_result['code']}, total: {search_result['data']['total']}, status: {[str(a["aid"]) + ": " + a["registname"] + "(" + str(a["registernum"]) + "/" + str(a["allowednum"]) + ")" for a in search_result["data"]["data"]]}") # logging
    activity_list = [Activity(a) for a in search_result["data"]["data"]]

    # 3. attempt registering; write and send email
    notify_list = []
    regist_error = False
    for activity in activity_list:
        if activity.aid not in exclude_aids and activity.registname == "进行中":
            status = regist_activity(cookies, activity.aid)
            if status["code"] == 0:
                exclude_aids.append(activity.aid)
            else:
                regist_error = True
            notify_list.append( (status, activity) )
    
    if len(notify_list) > 0:
        anames = []
        html = ""

        for status, activity in notify_list:
            assert isinstance(activity, Activity)
            assert isinstance(status, dict)
            anames.append(activity.aname)
            html += f"""<hr>\n<p>报名请求响应：{status['msg']}</p>\n"""
            html += activity.dump_html(cookies)

        html = "<html>\n<body>\n" + html + "</body>\n</html>\n"
        subject = "报名活动：" + "、".join(anames)
        if regist_error:
            subject = "[错误]" + subject

        send_email(subject, html)
    else:
        print("nothing new")
    
    # export_html(activity_list, "export.html", cookies)

    # 4. save exclude list
    save_json(exclude_aids, REGIST_EXCLUDE_PATH)

if __name__ == "__main__":
    main()
