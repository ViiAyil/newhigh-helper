import os
import requests
import hashlib
from notify import send

# 接口
USER_INFO_URL = "http://api.newhigh.net/user/info"
SIGNIN_URL = "https://api.newhigh.net/user/signin"
VIDEO_URL = "https://api.newhigh.net/monetizing/fishcoin/obtain/v2"
LUCKYDRAW_URL = "https://api.newhigh.net/monetizing/luckydraw/v2"
LOGIN_URL = "http://api.newhigh.net/authorization/login"

# MD5加密
def md5_hash(data):
    return hashlib.md5(data.encode("utf-8")).hexdigest()

# 发送请求
def send_request(session, url, method="GET", headers=None, json=None):
    try:
        if method == "POST":
            response = session.post(url, headers=headers, json=json)
        else:
            response = session.get(url, headers=headers)
        response.raise_for_status()  # 如果HTTP响应有错误，抛出异常
        return response.json()
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return {}

# 登录
def login(session, cellphone, password):
    print("🔑 正在登录")
    headers = {"Content-Type": "application/json"}
    payload = {
        "logintype": "local",
        "cellphone": cellphone,
        "password": md5_hash(password),
        "rememberstate": 0,
        "front_channel": "WEB",
    }
    res = send_request(session, LOGIN_URL, method="POST", headers=headers, json=payload)
    if res.get("result") == 1:
        print("✔️ 登录成功")
        return True
    else:
        print(f"❌ 登录失败: {res.get('message')}")
        return False

# 获取用户信息
def get_user_info(session):
    print("\n🔍 正在获取用户信息")
    headers = {"Content-Type": "text/html"}
    res = send_request(session, USER_INFO_URL, headers=headers)
    if res.get("result") == 1:
        print("✔️ 用户信息获取成功")
        return res.get("body")
    else:
        print(f"❌ 用户信息获取失败: {res.get('message')}")
        return None

# 签到
def sign_in(session):
    print("\n📅 正在执行签到任务")
    headers = {"Content-Type": "application/json"}
    payload = {"front_channel_name": "WECHAT_APPLET"}
    res = send_request(session, SIGNIN_URL, method="POST", headers=headers, json=payload)
    if res.get('result') == 1:
        points = res.get("body", {}).get("points", 0)
        continuous_sign = res.get("body", {}).get("continuoussign", 0)
        print(f"✔️ 签到成功: +{points} 鱼籽, 连续签到 {continuous_sign} 天")
        return points, continuous_sign
    else:
        print(f"❌ 签到失败: {res.get('message')}")
        return 0, 0

# 视频激励
def video_reward(session, school_id):
    print("\n🎥 正在执行视频激励任务")
    headers = {"Content-Type": "application/json"}
    payload = {
        "task_id": "2",
        "school_id": school_id,
        "front_channel_name": "WECHAT_APPLET",
    }
    video_points = 0
    for i in range(2):
        res = send_request(session, VIDEO_URL, method="POST", headers=headers, json=payload)
        if res.get("result") == 1:
            video_points += res.get("body", {}).get("total_obtained_points", 0)
        else:
            print(f"❌ 第 {i + 1} 次视频激励任务执行失败: {res.get('message')}")  # 显示 第 1 次 和 第 2 次
    print(f"✔️ 视频激励任务已完成，获得 {video_points} 鱼籽")
    return video_points

# 抽奖
def lucky_draw(session, school_id):
    print("\n🎉 正在执行每日抽奖")
    pre_url = f"https://api.newhigh.net/monetizing/luckydraw/v2?front_channel_name=WECHAT_APPLET&school_id={school_id}"
    send_request(session, pre_url)
    payload = {
        "front_channel_name": "WECHAT_APPLET",
        "school_id": school_id,
        "lucky_draw_id": 37,
    }
    res = send_request(session, LUCKYDRAW_URL, method="POST", headers={"Content-Type": "application/json"}, json=payload)
    if res.get('result') == 1:
        prize = res.get("body", {}).get("prize", {}).get("name", "无")
        print(f"✔️ 抽奖成功，获得: {prize}")
        return prize
    else:
        print(f"❌ 抽奖失败: {res.get('message')}")
        return "无"

# 每日任务
def daily_tasks(cellphone, password):
    print(f"\n⚡ 开始处理账户: {cellphone}")

    # 使用会话来保持登录状态
    session = requests.Session()

    if login(session, cellphone, password):
        user_info = get_user_info(session)
        if user_info:
            school_id = user_info["school"]["school_id"]
            nickname = user_info["nickname"]
            signin_points, signin_continuoussign = sign_in(session)
            video_points = video_reward(session, school_id)
            lucky_draw_message = lucky_draw(session, school_id)
            user_info = get_user_info(session)
            total_points = user_info["points"]
            result_text = [
                f"🎧 用户: {nickname}",
                f"✅ 签到成功: +{signin_points} 鱼籽",
                f"🗓️ 连续签到 {signin_continuoussign} 天",
                f"🎉 抽奖获得 {lucky_draw_message}",
                f"🎥 视频奖励 {video_points} 鱼籽",
                f"💰 现有鱼籽： {total_points}",
            ]
            result_message = '\n'.join(result_text)
            print(f"{result_message}\n")
            return result_message
        else:
            return "❌ 获取用户信息失败。"
    else:
        return "❌ 登录失败，请检查手机号和密码。"


if __name__ == "__main__":
    print(f"{'='*20}")
    print("🔍 正在读取环境变量")
    cellphones_list = os.getenv("NH_CELLPHONES")
    passwords_list = os.getenv("NH_PASSWORDS")

    if not cellphones_list or not passwords_list:
        print("❌ 环境变量 NH_CELLPHONES 或 NH_PASSWORDS 未设置。")
        print(f"{'='*20}\n")
        exit(1)
    else:
        cellphone_list = cellphones_list.split(';')
        password_list = passwords_list.split(';')

        if len(cellphone_list) != len(password_list):
            print("❌ 手机号和密码的数量不匹配。")
            print(f"{'='*20}\n")
        else:
            all_results = []  # 存储所有账户的结果
            user_num = len(cellphone_list)
            print("✅ 环境变量读取成功")
            print(f"👥 账号数量: {user_num}")
            print(f"{'='*20}\n")
            for cellphone, password in zip(cellphone_list, password_list):
                result_message = daily_tasks(cellphone, password)
                all_results.append(result_message)

            print("\n✅ 所有账户处理完毕 ✅")
            final_message = '\n\n'.join(all_results)
            send('流海云印每日任务', final_message)
            print("\n✅ 结果推送已完成 ✅")
