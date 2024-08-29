import requests
import hashlib
import random

session = requests.Session()

RESET_PWD_URL = "http://api.newhigh.net/user/info/retrievepassword"
SMS_URL = "https://api.newhigh.net/common/sms"

# 生成随机值
def gen_random(n):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(n))

# MD5加密
def md5_hash(data):
    m = hashlib.md5()
    m.update(data.encode("utf-8"))
    return m.hexdigest()

def resetPwd():
    cellphone = input("请输入手机号: ")
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
    sms_code = input("请输入收到的验证码: ")
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
    new_password = input("请输入新密码: ")
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
        print("密码重置成功")
        return cellphone, new_password
    return None, None

if __name__ == "__main__":
    resetPwd()