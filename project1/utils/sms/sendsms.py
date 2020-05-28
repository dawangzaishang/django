import requests
import json

def send_sms(mobile_num, code):
    data = {
        "sid": "74341298e9e030b5d5faf634eb8adc05",
        "token": "747a2b2322c27d80f2fe882e5cb9fd0c",
        "appid": "a5812db19adb40fb99d162c7965477aa",
        "templateid": "545734",
        "param": code,
        "mobile": mobile_num,
    }
    data = json.dumps(data)
    # 将验证码存入redis，过期时间设置为5分钟
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8',
    }
    response = requests.post('https://open.ucpaas.com/ol/sms/sendsms', data=data,headers=headers)
    result = json.loads(response.text)
    return result


if __name__=='__main__':
    send_sms('15621008081','123456')


        