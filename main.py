import requests
import hashlib
import random
import os

# 颜色
class Colors:
    HEADER = '\033[32m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKRED = '\033[31m'
    WARNING = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

session = requests.Session()

# 接口
USER_INFO_URL = "http://api.newhigh.net/user/info"
SIGNIN_URL = "https://api.newhigh.net/user/signin"
VIDEO_URL = "https://api.newhigh.net/monetizing/fishcoin/obtain/v2"
LUCKYDRAW_URL = "https://api.newhigh.net/monetizing/luckydraw/v2"
PUSHPLUS_URL = "https://www.pushplus.plus/send"
LOGIN_URL = "http://api.newhigh.net/authorization/login"
RESET_PWD_URL = "http://api.newhigh.net/user/info/retrievepassword"
SMS_URL = "https://api.newhigh.net/common/sms"

# 清除控制台
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# 生成随机值
def gen_random(n):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(n))

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
        data = res["body"]
        # user_id = data["user_id"]
        cellphone = data["cellphone"]
        # sex = data["sex"]
        nickname = data["nickname"]
        points = data["points"]
        # filecount = data["filecount"]
        # school_id = data["school"]["school_id"]
        school_name = data["school"]["school_name"]
        college_name = data["school"]["college_name"]
        major_name = data["school"]["major_name"]
        class_name = data["school"]["class_name"]
        # avatar = data["headportrait_addr"]
        print(
            f"\n{Colors.OKGREEN}{nickname}{Colors.ENDC}\n{Colors.OKBLUE}{cellphone}{Colors.ENDC}\n{Colors.WARNING}鱼籽数: {points}{Colors.ENDC}\n{school_name} {college_name} {major_name} {class_name}\n"
        )
        return data
    return res

def signIn():
    headers = {"Content-Type": "application/json"}
    payload = {"front_channel_name": "WECHAT_APPLET"}
    res = session.post(SIGNIN_URL, headers=headers, json=payload).json()
    if res['result'] == 1:
        signin_points = res.get("body", {}).get("points")
        signin_continuoussign = res.get("body", {}).get("continuoussign")
        print(f"{Colors.OKGREEN}签到成功，获得{signin_points}鱼籽，连续签到{signin_continuoussign}天{Colors.ENDC}")
        return signin_points, signin_continuoussign
    return 0, 0

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
        if res["result"] == 1:
            print(f"{Colors.OKGREEN}完成激励视频，获得{videon_points}鱼籽{Colors.ENDC}")
    return videon_points

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
    print(f"{Colors.OKGREEN}抽奖获得: {luckydraw_message}{Colors.ENDC}")
    return luckydraw_message

def resetPwd():
    cellphone = input(f"{Colors.UNDERLINE}请输入手机号 (输入exit返回上一级): {Colors.ENDC}")
    if cellphone.lower() == 'exit':
        return None, None
    random_string = gen_random(9) + '3' + gen_random(6)
    random_code_string = gen_random(4) + '6' + gen_random(11)
    verification_url = f"https://api.newhigh.net/public/{random_string}?front_channel_name=web"
    response = session.get(verification_url, headers={
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "zh-Hans-US;q=1, en-US;q=0.9, zh-Hant-US;q=0.8"
    })
    verification_data = response.json()
    verification_code = verification_data["body"]["data"]
    sms_url = f"https://api.newhigh.net/{verification_code}?cellphone={cellphone}&code={random_code_string}&front_channel_name=web&sms_type=1&type=reset_password"
    response = session.get(sms_url, headers={
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "zh-Hans-US;q=1, en-US;q=0.9, zh-Hant-US;q=0.8"
    })
    sms_code = input(f"{Colors.UNDERLINE}请输入收到的验证码 (输入exit返回上一级): {Colors.ENDC}")
    if sms_code.lower() == 'exit':
        return None, None
    post_data = {
        "cellphone": cellphone,
        "verificationcode": sms_code
    }
    response = session.post(SMS_URL, json=post_data, headers={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "zh-Hans-US;q=1, en-US;q=0.9, zh-Hant-US;q=0.8"
    })
    new_password = input(f"{Colors.UNDERLINE}请输入新密码 (输入exit返回上一级): {Colors.ENDC}")
    if new_password.lower() == 'exit':
        return None, None
    rest_pwd_data = {
        "cellphone": cellphone,
        "cellphonecode": sms_code,
        "newpwd": md5_hash(new_password)
    }
    rest_pwd_res = session.post(RESET_PWD_URL, json=rest_pwd_data, headers={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "zh-Hans-US;q=1, en-US;q=0.9, zh-Hant-US;q=0.8"
    }).json()
    if rest_pwd_res["result"] == 1:
        print(f"{Colors.OKGREEN}密码重置成功{Colors.ENDC}")
        return cellphone, new_password
    return None, None

def print_main_menu():
    clear_console()
    print(Colors.HEADER + Colors.BOLD + "==================== 主菜单 ====================" + Colors.ENDC)
    print(Colors.OKBLUE + "1. 登录" + Colors.ENDC)
    print(Colors.OKGREEN + "2. 重置密码" + Colors.ENDC)
    print(Colors.WARNING + "3. 退出" + Colors.ENDC)
    print(Colors.HEADER + "=============================================" + Colors.ENDC)

def print_sub_menu():
    print("\n" + Colors.HEADER + Colors.BOLD + "==================== 子菜单 ====================" + Colors.ENDC)
    print(Colors.OKBLUE + "1. 执行每日任务" + Colors.ENDC)
    print(Colors.WARNING + "2. 退出" + Colors.ENDC)
    print(Colors.HEADER + "=============================================" + Colors.ENDC)

def main_menu():
    while True:
        print_main_menu()
        choice = input("请选择操作 (输入exit返回上一级): ")
        if choice.lower() == "exit":
            break
        if choice == "1":
            cellphone = input(f"{Colors.UNDERLINE}请输入手机号 (输入exit返回上一级): {Colors.ENDC}")
            if cellphone.lower() == 'exit':
                continue
            password = input(f"{Colors.UNDERLINE}请输入密码 (输入exit返回上一级): {Colors.ENDC}")
            if password.lower() == 'exit':
                continue
            if login(cellphone, password):
                user_info = getUserInfo()
                school_id = user_info["school"]["school_id"]
                nickname = user_info["nickname"]
                while True:
                    print_sub_menu()
                    sub_choice = input("请选择操作 (输入exit返回上一级): ")
                    if sub_choice.lower() == "exit":
                        break
                    if sub_choice == "1":
                        signin_points, signin_continuoussign = signIn()
                        videon_points = videoReward(school_id)
                        luckydraw_message = luckydraw(school_id)
                        user_info = getUserInfo()
                        total_points = user_info["points"]
                        print(f'{Colors.OKGREEN}流海用户：{nickname}\n 签到成功 +{signin_points} 鱼籽\n 已连续签到 {signin_continuoussign} 天\n '
                              f'抽奖获得 {luckydraw_message}\n 视频奖励 {videon_points} 鱼籽\n 现有鱼籽： {total_points}{Colors.ENDC}')
                    elif sub_choice == "2":
                        break
                    else:
                        print(f"{Colors.FAIL}无效选择，请重新选择。{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}登录失败，请检查用户名和密码。{Colors.ENDC}")
        elif choice == "2":
            cellphone, new_password = resetPwd()
            if cellphone and new_password:
                next_action = input("按回车键自动登录，输入其他任意字符退出: ")
                if next_action == "":
                    if login(cellphone, new_password):
                        user_info = getUserInfo()
                        school_id = user_info["school"]["school_id"]
                        nickname = user_info["nickname"]
                        while True:
                            print_sub_menu()
                            sub_choice = input("请选择操作 (输入exit返回上一级): ")
                            if sub_choice.lower() == "exit":
                                break
                            if sub_choice == "1":
                                signin_points, signin_continuoussign = signIn()
                                videon_points = videoReward(school_id)
                                luckydraw_message = luckydraw(school_id)
                                user_info = getUserInfo()
                                total_points = user_info["points"]
                                print(f'{Colors.OKGREEN}流海用户：{nickname}\n 签到成功 +{signin_points} 鱼籽\n 已连续签到 {signin_continuoussign} 天\n '
                                      f'抽奖获得 {luckydraw_message}\n 视频奖励 {videon_points} 鱼籽\n 现有鱼籽： {total_points}{Colors.ENDC}')
                            elif sub_choice == "2":
                                break
                            else:
                                print(f"{Colors.FAIL}无效选择，请重新选择。{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}登录失败，请检查用户名和密码。{Colors.ENDC}")
                else:
                    break
        elif choice == "3":
            break
        else:
            print(f"{Colors.FAIL}无效选择，请重新选择。{Colors.ENDC}")

if __name__ == "__main__":
    main_menu()