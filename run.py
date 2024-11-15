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
                f"🎁 抽奖获得 {lucky_draw_message}",
                f"🎬 视频奖励 {video_points} 鱼籽",
                f"💰 现有鱼籽： {total_points}",
            ]
            result_message = '\n'.join(result_text)
            print(f"{result_message}\n")
            return result_message
        else:
            return "❌ 获取用户信息失败。"
    else:
        return "❌ 登录失败，请检查手机号和密码。"

# 读取配置文件
def read_env(file_path="newhigh.env"):
    config = {}

    # 从环境变量读取
    print("🔍 正在读取环境变量")
    cellphones_env = os.getenv("NH_CELLPHONES")
    passwords_env = os.getenv("NH_PASSWORDS")

    if cellphones_env and passwords_env:
        # 分割环境变量内容
        cellphones = cellphones_env.split(";")
        passwords = passwords_env.split(";")

        if len(cellphones) == len(passwords):
            config = dict(zip(cellphones, passwords))
            print(f"✔️ 从环境变量读取到 {len(config)} 个账户")
        else:
            print("❌ 环境变量中的手机号和密码数量不一致")
            return {}

    # 如果环境变量没有配置，则从文件读取
    if not config and os.path.exists(file_path):
        print("❌ 环境变量未设置")
        with open(file_path, "r", encoding="utf-8") as f:
            print("🔧 正在读取配置文件")
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        cellphone, password = line.strip().split(":", 1)
                        config[cellphone] = password
                    except ValueError:
                        print(f"❌ 配置项格式错误: {line.strip()}")
                        continue
    elif not config:
        print(f"❌ 配置文件 {file_path} 不存在")

    return config


if __name__ == "__main__":
    print(f"{'='*20}")

    config = read_env()

    if not config:
        print("❌ 配置为空或格式错误")
        exit(1)
    else:
        print(f"✔️ 配置文件读取成功，找到 {len(config)} 个账户")
        for phone, pwd in config.items():
            print(f"账号: {phone}, 密码: {pwd}")

    # 获取配置中的所有手机号和密码
    cellphones = list(config.keys())
    passwords = list(config.values())

    # 检查手机号和密码数量是否一致
    if len(cellphones) != len(passwords):
        print("❌ 手机号和密码数量不一致，请检查配置文件。")
        exit(1)

    print(f"🔐 账号数量: {len(cellphones)}")
    print(f"{'='*20}\n")

    all_results = []  # 存储所有账户的结果
    for cellphone, password in zip(cellphones, passwords):
        result_message = daily_tasks(cellphone, password)
        all_results.append(result_message)

    print("\n🌈 所有账户处理完毕")
    final_message = '\n\n'.join(all_results)
    print("\n🔔 正在推送任务结果")
    send('流海云印每日任务', final_message)
    print("\✔️ 结果推送已完成")
