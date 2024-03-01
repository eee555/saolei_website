import logging
logger = logging.getLogger(__name__)
# from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from .forms import UserLoginForm, UserRegisterForm, UserRetrieveForm, EmailForm
from captcha.models import CaptchaStore
# from captcha.helpers import captcha_image_url
import json
# from django.views.generic import View
# 引入验证登录的装饰器
# from django.contrib.auth.decorators import login_required
# from django.views.generic.edit import CreateView
from .models import EmailVerifyRecord,UserProfile
# from django.core.mail import send_mail
from utils import send_email
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import get_user_model
from msuser.models import UserMS
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events


User = get_user_model()


# Create your views here.


@ratelimit(key='ip', rate='60/h')
# 此处要分成两个，密码容易碰撞，hash难碰撞
def user_login(request):
    if request.method == 'POST':
        # print(request.session.get("login"))
        # print(request.user)

        # 用cookie登录
        response = {'status': 100, 'msg': None}
        if request.user.is_authenticated:
            # login(request, request.user)
            response['msg'] = response['msg'] = {
                "id": request.user.id, "username": request.user.username,
                  "realname": request.user.realname, "is_banned": request.user.is_banned}
            return JsonResponse(response)
        # if user_id:=request.session.get("_auth_user_id"):
        #     if user:=User.objects.get(id=user_id):
        #         login(request, user)
        #         print(user)
        #         response['msg'] = user.username
        #         return JsonResponse(response)

        # 用账号、密码登录
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data

            capt = data["captcha"]   # 用户提交的验证码
            key = data["hashkey"]    # 验证码hash
            response = {'status': 100, 'msg': None}
            if judge_captcha(capt, key):
                # 检验账号、密码是否正确匹配数据库中的某个用户
                # 如果均匹配则返回这个 user 对象
                user = authenticate(
                    username=data['username'], password=data['password'])
                if user:
                    # 将用户数据保存在 session 中，即实现了登录动作
                    login(request, user)
                    response['msg'] = {
                        "id": user.id, "username": user.username, 
                        "realname": user.realname, "is_banned": user.is_banned}
                    if 'user_id' in data and data['user_id'] != str(user.id):
                        # 检测到小号
                        logger.info(f'{data["user_id"][:50]} is diffrent from {str(user.id)}.')
                    return JsonResponse(response)
                else:
                    return JsonResponse({'status': 105, 'msg': "账号或密码输入有误。请重新输入~"})
            
            else:
                return JsonResponse({'status': 104, 'msg': "验证码错误！"})
            

        
        else:
            response['status'] = 106
            response['msg'] = "账号或密码输入不合法"
            return JsonResponse(response)
    elif request.method == 'GET':
        return HttpResponse("别瞎玩")
        # user_login_form = UserLoginForm()
        # context = {'form': user_login_form}
        # return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("别瞎玩")


def user_logout(request):
    logout(request)
    return JsonResponse({'status': 100, 'msg': None})


# 用户找回密码
@ratelimit(key='ip', rate='60/h')
def user_retrieve(request):
    if request.method == 'POST':
        user_retrieve_form = UserRetrieveForm(data=request.POST)
        if user_retrieve_form.is_valid():
            emailHashkey = request.POST.get("email_key", None)
            email_captcha = request.POST.get("email_captcha", None)
            get_email_captcha = EmailVerifyRecord.objects.filter(
                hashkey=emailHashkey).first()
            # print(emailHashkey)
            # print(email_captcha)
            if get_email_captcha and email_captcha and get_email_captcha.code == email_captcha:
                if (timezone.now() - get_email_captcha.send_time).seconds <= 3600:
                    user = UserProfile.objects.filter(email=user_retrieve_form.cleaned_data['email']).first()
                    if not user:
                        return JsonResponse({'status': 109, 'msg': "该邮箱尚未注册，请先注册！"})
                    # 设置密码(哈希)
                    user.set_password(
                        user_retrieve_form.cleaned_data['password'])
                    user.save()
                    # 保存好数据后立即登录
                    login(request, user)
                    EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
                    return JsonResponse({'status': 100, 'msg': user.realname})
                else:
                    # 顺手把过期的验证码删了
                    EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
                    return JsonResponse({'status': 150, 'msg': "邮箱验证码已过期！" })
            else:
                return JsonResponse({'status': 102, 'msg': "邮箱验证码不正确！"})
        else:
            return JsonResponse({'status': 101, 'msg': user_retrieve_form.errors.\
                                 as_text().split("*")[-1]})
    else:
        return HttpResponse("别瞎玩")


# 用户注册
# @method_decorator(ensure_csrf_cookie)
@ratelimit(key='ip', rate='6/h')
def user_register(request):
    # print(request.POST)
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        # print(request.POST)
        # print(user_register_form.cleaned_data.get('username'))
        # print(user_register_form.cleaned_data)
        if user_register_form.is_valid():
            emailHashkey = request.POST.get("email_key", None)
            email_captcha = request.POST.get("email_captcha", None)
            get_email_captcha = EmailVerifyRecord.objects.filter(hashkey=emailHashkey).first()
            # get_email_captcha = EmailVerifyRecord.objects.filter(hashkey="5f0db744-180b-4d9f-af5a-2986f4a78769").first()
            if get_email_captcha and email_captcha and get_email_captcha.code == email_captcha:
                if (timezone.now() - get_email_captcha.send_time).seconds <= 3600:
                    new_user = user_register_form.save(commit=False)
                    # 设置密码(哈希)
                    new_user.set_password(
                        user_register_form.cleaned_data['password'])
                    new_user.is_active = True # 自动激活
                    user_ms = UserMS.objects.create()
                    new_user.userms = user_ms
                    user_ms.save()
                    new_user.save()
                    # 保存好数据后立即登录
                    login(request, new_user)
                    # 顺手把过期的验证码删了
                    EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
                    return JsonResponse({'status': 100, 'msg': {
                        "id": new_user.id, "username": new_user.username,
                        "realname": new_user.realname, "is_banned": False}
                        })
                else:
                    # 顺手把过期的验证码删了
                    EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
                    return JsonResponse({'status': 150, 'msg': "邮箱验证码已过期！" })
            else:
                return JsonResponse({'status': 102, 'msg': "邮箱验证码不正确！"})
        else:
            if "email" not in user_register_form.cleaned_data:
                # 可能发生前端验证正确，而后端验证不正确（后端更严格），此时clean会直接删除email字段
                return JsonResponse({'status': 105, 'msg': "邮箱格式不正确！"})
            # print(user_register_form.errors.as_json())
            else:
                # print(user_register_form.errors)
                return JsonResponse({'status': 101, 'msg': user_register_form.errors.\
                                    as_text().split("*")[-1]})
    else:
        return HttpResponse("别瞎玩")


# 【站长】任命解除管理员
# http://127.0.0.1:8000/userprofile/set_staff/?id=1&is_staff=True
def set_staff(request):
    if request.user.is_superuser and request.method == 'GET':
        user = UserProfile.objects.get(id=request.GET["id"])
        user.is_staff = request.GET["is_staff"]
        logger.info(f'{request.user.id} set_staff {request.GET["id"]} {request.GET["is_staff"]}')
        if request.GET["is_staff"] == "True":
            user.is_staff = True
            user.save()
            return HttpResponse(f"设置\"{user.realname}\"为管理员成功！")
        elif request.GET["is_staff"] == "False":
            user.is_staff = False
            user.save()
            return HttpResponse(f"解除\"{user.realname}\"的管理员权限！")
        else:
            return HttpResponse("失败！is_staff需要为\"True或\"False")
    else:
        return HttpResponse("别瞎玩")

# 【管理员】封禁用户
# http://127.0.0.1:8000/userprofile/set_banned/?id=1&is_banned=True
def set_banned(request):
    if request.user.is_staff and request.method == 'GET':
        user = UserProfile.objects.get(id=request.GET["id"])
        user.is_banned = request.GET["is_banned"]
        logger.info(f'{request.user.id} set_banned {request.GET["id"]} {request.GET["is_banned"]}')
        if user.is_staff:
            return HttpResponse("没有封禁管理员的权限！")
        if request.GET["is_banned"] == "True":
            user.is_banned = True
            user.save()
            return HttpResponse(f"封禁用户\"{user.realname}\"成功！")
        elif request.GET["is_banned"] == "False":
            user.is_banned = False
            user.save()
            return HttpResponse(f"解封用户\"{user.realname}\"成功！")
        else:
            return HttpResponse("失败！is_banned需要为\"True或\"False")
    else:
        return HttpResponse("别瞎玩")

# 创建验证码
@ratelimit(key='ip', rate='60/h')
def captcha(request):
    hashkey = CaptchaStore.generate_key()  # 验证码答案
    # print(f"?captcha-image={hashkey}")
    # image_url = captcha_image_url(hashkey)  # 验证码地址
    # http://127.0.0.1:8000/userprofile/captcha/image/846d863374767ce04f8949882b05b3b21c697765
    captcha = {'hashkey': hashkey}
    return captcha

# 刷新验证码
@ratelimit(key='ip', rate='60/h')
def refresh_captcha(request):
    c = captcha(request)
    c.update({'status': 100})
    return HttpResponse(json.dumps(c), content_type='application/json')

# 验证验证码，若通过，发送email
@ratelimit(key='ip', rate='20/h')
def get_email_captcha(request):
    if request.method == 'POST':
        email_form = EmailForm(data=request.POST)
        if email_form.is_valid():
            capt = request.POST.get("captcha", None)  # 用户提交的验证码
            key = request.POST.get("hashkey", None)  # 验证码hash
            response = {'status': 100, 'msg': None, "hashkey": None}
            if judge_captcha(capt, key):
                hashkey = send_email(request.POST.get("email", None), request.POST.get("type", None))
                if hashkey:
                    response['hashkey'] = hashkey
                    return JsonResponse(response)
                else:
                    response['status'] = 103
                    response['msg'] = "发送邮件失败"
                    return JsonResponse(response)
            else:
                response['status'] = 104
                response['msg'] = "验证码错误"
                return JsonResponse(response)
        else:
            # print(email_form)
            return JsonResponse({'status': 110, 'msg': email_form.errors.\
                                 as_text().split("*")[-1]})
    else:
        return HttpResponse("只能post。。。")

# 验证验证码


def judge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        get_captcha = CaptchaStore.objects.filter(
            hashkey=captchaHashkey).first()
        if get_captcha and get_captcha.response == captchaStr.lower():
            # 图形验证码15分钟有效，get_captcha.expiration是过期时间
            if (get_captcha.expiration - timezone.now()).seconds >= 0:
                CaptchaStore.objects.filter(hashkey=captchaHashkey).delete()
                return True
    CaptchaStore.objects.filter(hashkey=captchaHashkey).delete()
    return False


# 【管理员】给用户增加1次修改姓名的机会
# http://127.0.0.1:8000/userprofile/modify_realname?id=1
def modify_realname_n(request):
    if request.user.is_staff and request.method == 'GET':
        user = UserProfile.objects.get(id=request.GET["id"])
        user.left_realname_n += 1
        logger.info(f'{request.user.id} add left_realname_n for {request.GET["id"]} ({user.left_realname_n})')
        return HttpResponse(f"为用户\"{user.realname}\"（id: {user.id}）增加一次修改姓名的次数成功！")
    else:
        return HttpResponse("别瞎玩")


# 【站长】给用户增加x、y、z次（对应）修改姓名、头像和签名的机会
# http://127.0.0.1:8000/userprofile/modify?id=1&x=0&y=1&z=200
def modify_n(request):
    if request.user.is_superuser and request.method == 'GET':
        user = UserProfile.objects.get(id=request.GET["id"])
        user.left_realname_n += request.GET["x"]
        user.left_avatar_n += request.GET["y"]
        user.left_signature_n += request.GET["z"]
        logger.info(f'{request.user.id}(superuser) modify_n for {request.GET["id"]} ({user.left_realname_n}, {user.left_avatar_n}, {user.left_signature_n})')
        return HttpResponse(f"为用户\"{user.realname}\"（id: {user.id}）增加修改姓名、头像、签名的次数成功！目前剩余（{user.left_realname_n}, {user.left_avatar_n}, {user.left_signature_n}）")
    else:
        return HttpResponse("别瞎玩")


scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(DjangoJobStore(), "default")

def delete_overdue_emailverifyrecord(name):
    # 定时清除过期邮箱验证码（1小时过期）
    start = timezone.now() - timezone.timedelta(seconds=3600)
    EmailVerifyRecord.objects.filter(send_time__lt=start).delete()

def delete_overdue_captcha(name):
    # 定时清除过期图形验证码（15分钟过期）
    # start = timezone.now() - timezone.timedelta(seconds=900)
    CaptchaStore.objects.filter(expiration__lt=timezone.now()).delete()
            

# scheduler.add_job(job1, "interval", seconds=10, args=['22'], id="job2", replace_existing=True)
scheduler.add_job(delete_overdue_emailverifyrecord, 'cron', hour='5', minute='10',
                   second = '02', args=['666'], id='delete_overdue_emailverifyrecord', replace_existing=True)
scheduler.add_job(delete_overdue_captcha, 'cron', hour='5', minute='34', second = '07', 
                  args=['666'], id='delete_overdue_captcha', replace_existing=True)
# 监控任务
register_events(scheduler)
# 调度器开始运行
try:
    scheduler.start()
except:
    print("定时任务启动失败！")

