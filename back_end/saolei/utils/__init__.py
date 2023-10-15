from userprofile.models import EmailVerifyRecord
from django.core.mail import send_mail
import random
import string
import uuid
from datetime import date, datetime
import json
from decimal import Decimal

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


def send_register_email(email):
    email_record = EmailVerifyRecord()
    code = generate_code(6)
    email_record.code = code
    # email_record.email = email
    hashkey = uuid.uuid4()
    email_record.hashkey = hashkey
    # email_record.send_type = send_type
    email_record.save()
 
# 验证码保存之后，我们就要把带有验证码的链接发送到注册时的邮箱！
    # if send_type == 'register':
    email_title = '扫雷网邮箱注册验证码'
    email_body = f'您的邮箱验证码为{code}'
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
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, bytes):
            return str(obj, encoding="utf-8")
        else:
            return json.JSONEncoder.default(self, obj)
        




