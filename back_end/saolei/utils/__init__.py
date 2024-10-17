from userprofile.models import EmailVerifyRecord
from django.core.mail import send_mail
import uuid, base64, random, json
from datetime import date, datetime
from decimal import Decimal
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
import requests
from config.flags import BAIDU_VERIFY_SKIP, EMAIL_SKIP

def generate_code(code_len):
    """
    生成指定长度的验证码
    :param code_len: 验证码长度（4-6位）
    :return: 生成的验证码
    """
    all_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for _ in range(code_len):
        index = random.randint(0, len(all_chars)-1)
        code += all_chars[index]
    return code


# 发送邮件，根据send_type不同发送不同的邮件内容
def send_email(email, send_type='register'):
    email_record = EmailVerifyRecord()
    code = generate_code(6)
    email_record.code = code
    # email_record.email = email
    hashkey = uuid.uuid4()
    email_record.hashkey = hashkey
    email_record.email = email
    # email_record.send_type = send_type
    email_record.save()
 
    # 验证码保存之后，我们就要把带有验证码的链接发送到注册时的邮箱！
    if EMAIL_SKIP:
        return code, hashkey
    if send_type == 'register':
        email_title = '元扫雷网邮箱注册验证码'
        email_body = f'欢迎您注册元扫雷网，您的邮箱验证码为：{code}（一小时内有效）。'
    elif send_type == 'retrieve':
        email_title = '元扫雷网找回密码验证码'
        email_body = f'您正在找回密码。您的邮箱验证码为：{code}（一小时内有效）。请勿与任何人分享此代码，我们的管理员永远不会向您索要此代码。'
    else:
        return None
    send_status = send_mail(email_title, email_body, 'wangjianing@88.com', [email])
    if send_status:
        return hashkey
    else:
        return None

# https://zhuanlan.zhihu.com/p/429228350
# def active_user(request, active_code):
#     """查询验证码"""
#     print(active_code)
#     all_records = EmailVerifyRecord.objects.filter(code=active_code)
#     print(all_records)
#     if all_records:
#         for record in all_records:
#             email = record.email
#             print(email)
#             user = User.objects.get(email=email)
#             print(user)
#             user.is_staff = True
#             user.save()
#     else:
#         return HttpResponse('链接有误！')
#     return redirect('users:login')


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, bytes):
            return str(obj, encoding="utf-8")
        else:
            return json.JSONEncoder.default(self, obj)



"""
使用 AK，SK 生成鉴权签名（Access Token）。不能调用太多次。
:return: access_token，或是None(如果错误)
"""
def get_access_token() -> str:
    try:
        with open("secrets.json",'r') as f:
            API_KEY = json.load(f)["client_id"]
    except:
        API_KEY = input("请输入client_id：")
    try:
        with open("secrets.json",'r') as f:
            SECRET_KEY = json.load(f)["client_secret"]
    except:
        SECRET_KEY = input("请输入client_secret：")
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    token = str(requests.post(url, params=params).json().get("access_token"))
    with open('secrets.json', 'r') as file:
        data = json.load(file)
    data['token'] = token
    with open('secrets.json', 'w') as file:
        json.dump(data, file)

    if token == "None":
        print("**********************************************\n\n**  警告！内容审核的鉴权签名获取失败！！！  **\n\n**********************************************")
    return token

def get_ACCESS_TOKEN() -> str:
    try:
        with open("secrets.json",'r') as f:
            ACCESS_TOKEN = json.load(f)["token"]
    except KeyError:
        ACCESS_TOKEN = get_access_token()
    except json.JSONDecodeError as e:
        # print(f"JSON解析错误: {e}")
        ...
    except Exception as e:
        # print(f"发生其他错误: {e}")
        ...
    return ACCESS_TOKEN


# 百度大脑鉴别文本合规性
def verify_text(text: str, user_id: int = 0, user_ip: str = '192.168.0.1') -> bool:
    if BAIDU_VERIFY_SKIP:
        return True
    if len(text) < 2:
        return True
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token=" + get_ACCESS_TOKEN()
    payload={
        "text": text,
        "user_id": user_id,
        "user_ip": user_ip
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.json().get("error_code") == 111:
        # token过期了
        url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token=" + get_access_token()
        response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("conclusion") == "合规"


# 百度大脑鉴别图片合规性
# 百度api对图片的尺寸、大小都有要求，后期再测试、适配
def verify_image(image_binary, user_id: int, user_ip: str) -> bool:
    if not image_binary:
        return True
    image_base64 = base64.b64encode(image_binary).decode()
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + get_ACCESS_TOKEN()
    payload={
        "image": image_base64,
        "user_id": user_id,
        "user_ip": user_ip
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.json().get("error_code") == 111:
        # token过期了
        url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + get_access_token()
        response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("conclusion") == "合规"


def ratelimited(request, exception):
    if "/video/download/" in request.path:
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if "/login/" in request.path:
        return JsonResponse({"status": 120, "msg": "请稍后再试！"})
    if "/register/" in request.path:
        return JsonResponse({"status": 120, "msg": "请稍后再试！"})
    if "/retrieve/" in request.path:
        return JsonResponse({"status": 120, "msg": "请稍后再试！"})
    if "/get_email_captcha/" in request.path:
        return JsonResponse({"status": 120, "msg": "请稍后再试！"})
    if "/captcha/" in request.path:
        return JsonResponse({"status": 120, "msg": "请稍后再试！"})
    if "/refresh_captcha/" in request.path:
        return JsonResponse({"status": 120, "msg": "请稍后再试！"})



