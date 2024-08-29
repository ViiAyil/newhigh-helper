import os
import requests
import hashlib
from notifier import pushNotification

session = requests.Session()

# 接口
USER_INFO_URL = "http://api.newhigh.net/user/info"
SIGNIN_URL = "https://api.newhigh.net/user/signin"
VIDEO_URL = "https://api.newhigh.net/monetizing/fishcoin/obtain/v2"
LUCKYDRAW_URL = "https://api.newhigh.net/monetizing/luckydraw/v2"
LOGIN_URL = "http://api.newhigh.net/authorization/login"

# MD5加密
def md5_hash(data):
    m = hashlib.md5()
    m.update(data.encode("utf-8"))
    return m.hexdigest()

# 登录
def login(cellphone, password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "logintype": "local",
        "cellphone": cellphone,
        "password": md5_hash(password),
        "rememberstate": 0,
        "front_channel": "WEB",
    }
    res = session.post(LOGIN_URL, headers=headers, json=payload).json()
    print(res["message"])
    return res["result"] == 1

# 获取用户信息
def getUserInfo():
    headers = {"Content-Type": "text/html"}
    res = session.get(USER_INFO_URL, headers=headers).json()
    if res["result"] == 1:
        return res["body"]
    return None

# 签到
def signIn():
    headers = {"Content-Type": "application/json"}
    payload = {"front_channel_name": "WECHAT_APPLET"}
    res = session.post(SIGNIN_URL, headers=headers, json=payload).json()
    if res['result'] == 1:
        signin_points = res.get("body", {}).get("points")
        signin_continuoussign = res.get("body", {}).get("continuoussign")
        return signin_points, signin_continuoussign
    return 0, 0

# 视频激励
def videoReward(school_id):
    headers = {"Content-Type": "application/json"}
    payload = {
        "task_id": "2",
        "school_id": school_id,
        "front_channel_name": "WECHAT_APPLET",
    }
    count = 0
    videon_points = 0
    while count < 2:
        res = session.post(VIDEO_URL, headers=headers, json=payload).json()
        videon_points += res.get("body", {}).get("total_obtained_points", 0)
        count += 1
    return videon_points

# 抽奖
def luckydraw(school_id):
    headers = {"Content-Type": "text/html"}
    pre_url = f"https://api.newhigh.net/monetizing/luckydraw/v2?front_channel_name=WECHAT_APPLET&school_id={school_id}"
    session.get(pre_url, headers=headers).json()
    payload = {
        "front_channel_name": "WECHAT_APPLET",
        "school_id": school_id,
        "lucky_draw_id": 37,
    }
    res = session.post(LUCKYDRAW_URL, headers=headers, json=payload).json()
    luckydraw_message = res.get("body", {}).get("prize", {}).get("name")
    print(f"抽奖获得: {luckydraw_message}")
    return luckydraw_message


# 每日任务
def daily_tasks(cellphone, password, wechat_bot_url=None):
    if login(cellphone, password):
        user_info = getUserInfo()
        if user_info:
            school_id = user_info["school"]["school_id"]
            nickname = user_info["nickname"]
            signin_points, signin_continuoussign = signIn()
            videon_points = videoReward(school_id)
            luckydraw_message = luckydraw(school_id)
            user_info = getUserInfo()
            total_points = user_info["points"]
            result_text = [
                f'流海用户：{nickname}',
                f'签到成功 +{signin_points} 鱼籽',
                f'已连续签到 {signin_continuoussign} 天',
                f'抽奖获得 {luckydraw_message}',
                f'视频奖励 {videon_points} 鱼籽',
                f'现有鱼籽： {total_points}'
            ]
            max_length = max(len(line) for line in result_text)
            border = '=' * (max_length + 4)

            result_message = '\n'.join(result_text)
            print(border)
            for line in result_text:
                print(f'{line.ljust(max_length)}')
            print(border)

            if wechat_bot_url:
                pushNotification(wechat_bot_url, result_message)
        else:
            print("获取用户信息失败。")
    else:
        print("登录失败，请检查手机号和密码。")

if __name__ == "__main__":
    cellphones = os.getenv("CELLPHONES")
    passwords = os.getenv("PASSWORDS")
    wechat_bot_url = os.getenv("WECHAT_BOT_URL")

    if not cellphones or not passwords:
        print("环境变量 CELLPHONES 或 PASSWORDS 未设置。")
    else:
        cellphone_list = cellphones.split(';')
        password_list = passwords.split(';')

        if len(cellphone_list) != len(password_list):
            print("手机号和密码的数量不匹配。")
        else:
            for cellphone, password in zip(cellphone_list, password_list):
                print(f"正在处理账户：{cellphone}")
                daily_tasks(cellphone, password, wechat_bot_url)