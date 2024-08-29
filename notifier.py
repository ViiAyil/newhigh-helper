import requests
import json

# 企业微信消息推送
def pushNotification(wechat_bot_url, message):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'msgtype': 'markdown',
        'markdown': {
            'content': message
        }
    }
    response = requests.post(wechat_bot_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("推送成功")
    else:
        print(f"推送失败，状态码: {response.status_code}, 响应内容: {response.text}")