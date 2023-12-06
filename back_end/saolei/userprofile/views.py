import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from .forms import UserLoginForm, UserRegisterForm, UserRegisterCaptchaForm, UserRetrieveForm
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
import json
from django.views.generic import View
# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .models import EmailVerifyRecord,UserProfile
from django.core.mail import send_mail
from utils import send_register_email
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import get_user_model
from msuser.models import UserMS

User = get_user_model()


# Create your views here.


def user_login(request):
    if request.method == 'POST':
        # print(request.session.get("login"))
        # print(request.session.keys())
        # print(request.session.session_key)
        # print(request.session.get("_auth_user_id"))
        # print(request.session.get("_auth_user_backend"))
        # print(request.session.get("_auth_user_hash"))
        # print(request.user)

        # 用cookie登录
        response = {'status': 100, 'msg': None}
        if request.user.is_authenticated:
            # login(request, request.user)
            response['msg'] = response['msg'] = {"id": request.user.id, "name": request.user.username, "is_banned": request.user.is_banned}
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
            # .cleaned_data 清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(
                username=data['username'], password=data['password'])
            # print(data)
            # print(user)
            if user:
                # 将用户数据保存在 session 中，即实现了登录动作
                login(request, user)
                # response = http.JsonResponse({"code":0,"errmsg":"注册成功"})
                # response.set_cookie("username",user.username,max_age=3600*24*14)
                response['msg'] = {"id": user.id, "name": user.username, "is_banned": user.is_banned}
                if 'user_id' in data and data['user_id'] != str(user.id):
                    # 检测到小号
                    logger.info(f'{data["user_id"][:50]} is diffrent from {str(user.id)}.')
                return JsonResponse(response)
            else:
                response['status'] = 105
                response['msg'] = "账号或密码输入有误。请重新输入~"
                return JsonResponse(response)
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
def user_retrieve(request):
    if request.method == 'POST':
        user_retrieve_form = UserRetrieveForm(data=request.POST)
        if user_retrieve_form.is_valid():
            emailHashkey = request.POST.get("usertoken", None)
            email_captcha = request.POST.get("email_captcha", None)
            get_email_captcha = EmailVerifyRecord.objects.filter(
                hashkey=emailHashkey).first()
            if get_email_captcha and email_captcha and get_email_captcha.code == email_captcha:
                user = UserProfile.objects.filter(email=user_retrieve_form.cleaned_data['email'])
                if not user:
                    return JsonResponse({'status': 109, 'msg': "该邮箱尚未注册，请先注册！"})
                # 设置密码(哈希)
                user.set_password(
                    user_retrieve_form.cleaned_data['password'])
                user.save()
                # 保存好数据后立即登录
                login(request, user)
                return JsonResponse({'status': 100, 'msg': None})
            else:
                return JsonResponse({'status': 102, 'msg': "邮箱验证码不正确！"})
        else:
            return JsonResponse({'status': 101, 'msg': user_retrieve_form.errors.\
                                 as_text().split("*")[-1]})
    else:
        return HttpResponse("别瞎玩")

# @method_decorator(ensure_csrf_cookie)
def user_register(request):
    # print(request.POST)
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        # print(request.POST)
        # print(user_register_form.cleaned_data.get('username'))
        if user_register_form.is_valid():
            emailHashkey = request.POST.get("usertoken", None)
            email_captcha = request.POST.get("email_captcha", None)
            get_email_captcha = EmailVerifyRecord.objects.filter(
                hashkey=emailHashkey).first()
            if get_email_captcha and email_captcha and get_email_captcha.code == email_captcha:
                new_user = user_register_form.save(commit=False)
                # print(new_user)
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
                # request.session['login'] = '1'
                # # print(request.session)
                # Jresponse = JsonResponse(response)
                # Jresponse.set_cookie('login','1', max_age=30*24*3600)
                # # print(Jresponse.cookies)
                return JsonResponse({'status': 100, 'msg': None})
                # return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                return JsonResponse({'status': 102, 'msg': "邮箱验证码不正确！"})
        else:
            # print(user_register_form.cleaned_data)
            # print(user_register_form.errors.as_json())
            
            return JsonResponse({'status': 101, 'msg': user_register_form.errors.\
                                 as_text().split("*")[-1]})
    else:
        return HttpResponse("别瞎玩")

# 站长任命解除管理员
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

# 管理员封禁用户
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
def captcha(request):
    hashkey = CaptchaStore.generate_key()  # 验证码答案
    print(f"?captcha-image={hashkey}")
    # image_url = captcha_image_url(hashkey)  # 验证码地址
    # http://127.0.0.1:8000/userprofile/captcha/image/846d863374767ce04f8949882b05b3b21c697765
    captcha = {'hashkey': hashkey}
    return captcha

# 刷新验证码
def refresh_captcha(request):
    return HttpResponse(json.dumps(captcha(request)), content_type='application/json')

# 验证验证码，若通过，发送email
def get_email_captcha(request):
    if request.method == 'POST':
        capt = request.POST.get("captcha", None)  # 用户提交的验证码
        key = request.POST.get("hashkey", None)  # 验证码hash
        response = {'status': 100, 'msg': None, "hashkey": None}
        if judge_captcha(capt, key):
            hashkey = send_register_email(request.POST.get("email", None))
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
        return HttpResponse("只能post。。。")

# 验证验证码


def judge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        get_captcha = CaptchaStore.objects.filter(
            hashkey=captchaHashkey).first()
        if get_captcha and get_captcha.response == captchaStr.lower():
            return True
    return False


# class IndexView(View):
#     def get(self, request):
#         hashkey = CaptchaStore.generate_key()  # 验证码答案
#         image_url = captcha_image_url(hashkey)  # 验证码地址
#         print(hashkey,image_url)
#         captcha = {'hashkey': hashkey, 'image_url': image_url}
#         return render(request, "login.html", locals())

#     def post(self, request):
#         capt = request.POST.get("captcha", None)  # 用户提交的验证码
#         key = request.POST.get("hashkey", None)  # 验证码答案
#         if jarge_captcha(capt, key):
#             return HttpResponse("验证码正确")
#         else:
#             return HttpResponse("验证码错误")
