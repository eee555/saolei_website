import logging
logger = logging.getLogger('userprofile')
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from .forms import UserLoginForm, UserRegisterForm, UserRetrieveForm, EmailForm
from captcha.models import CaptchaStore
import json
import os
from .models import EmailVerifyRecord,UserProfile
from utils import send_email
from django.contrib.auth import get_user_model
from msuser.models import UserMS
from django_ratelimit.decorators import ratelimit
from django.views.decorators.http import require_GET, require_POST
from .decorators import staff_required
from django.utils import timezone
from django.conf import settings
from config.flags import EMAIL_SKIP

# Create your views here.


@ratelimit(key='ip', rate='60/h')
@require_POST
# 用账号、密码登录
# 此处要分成两个，密码容易碰撞，hash难碰撞
def user_login(request):
    user_login_form = UserLoginForm(data=request.POST)
    if not user_login_form.is_valid():
        return JsonResponse({'status': 106, 'msg': "表单错误！"})
    data = user_login_form.cleaned_data

    capt = data["captcha"]   # 用户提交的验证码
    key = data["hashkey"]    # 验证码hash
    username = data["username"]
    response = {'status': 100, 'msg': None}
    if not judge_captcha(capt, key):
        logger.info(f'用户 {username} 验证码错误')
        return JsonResponse({'status': 104, 'msg': "验证码错误！"})
    # 检验账号、密码是否正确匹配数据库中的某个用户
    # 如果均匹配则返回这个 user 对象
    user = authenticate(
        username=username, password=data['password'])
    if not user:
        logger.info(f'用户 {username} 账密错误')
        return JsonResponse({'status': 105, 'msg': "账号或密码输入有误。请重新输入~"})
    # 将用户数据保存在 session 中，即实现了登录动作
    login(request, user)
    response['msg'] = {
        "id": user.id, "username": user.username, 
        "realname": user.realname, "is_banned": user.is_banned, "is_staff": user.is_staff}
    if 'user_id' in data and data['user_id'] != str(user.id):
        # 检测到小号
        logger.warning(f'{data["user_id"][:50]} is diffrent from {str(user.id)}.')
    return JsonResponse(response)
        

@require_GET
# 用cookie登录
def user_login_auto(request):
    if request.user.is_authenticated:
        return JsonResponse({'id': request.user.id, 'username': request.user.username, 'realname': request.user.realname, 'is_banned': request.user.is_banned, 'is_staff': request.user.is_staff})
    return HttpResponse()

def user_logout(request):
    logout(request)
    return JsonResponse({'status': 100, 'msg': None})


# 用户找回密码
@ratelimit(key='ip', rate='60/h')
@require_POST
def user_retrieve(request):
    user_retrieve_form = UserRetrieveForm(data=request.POST)
    if not user_retrieve_form.is_valid():
        return JsonResponse({'status': 101, 'msg': user_retrieve_form.errors.\
                            as_text().split("*")[-1]})
    emailHashkey = request.POST.get("email_key", None)
    email_captcha = request.POST.get("email_captcha", None)
    get_email_captcha = EmailVerifyRecord.objects.filter(
        hashkey=emailHashkey).first()
    if get_email_captcha and email_captcha and get_email_captcha.code == email_captcha and\
        get_email_captcha.email == request.POST.get("email", None):
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
            logger.info(f'用户 {user.username}#{user.id} 邮箱找回密码')
            EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
            return JsonResponse({'status': 100, 'msg': user.realname})
        else:
            # 顺手把过期的验证码删了
            EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
            return JsonResponse({'status': 150, 'msg': "邮箱验证码已过期！" })
    else:
        return JsonResponse({'status': 102, 'msg': "邮箱验证码不正确！"})


# 用户注册
# @method_decorator(ensure_csrf_cookie)
@ratelimit(key='ip', rate='6/h')
@require_POST
def user_register(request):
    user_register_form = UserRegisterForm(data=request.POST)
    if user_register_form.is_valid():
        emailHashkey = request.POST.get("email_key", None)
        email_captcha = request.POST.get("email_captcha", None)
        get_email_captcha = EmailVerifyRecord.objects.filter(hashkey=emailHashkey).first()
        if EMAIL_SKIP or (get_email_captcha and email_captcha and get_email_captcha.code == email_captcha and\
            get_email_captcha.email == request.POST.get("email", None)):
            if EMAIL_SKIP or (timezone.now() - get_email_captcha.send_time).seconds <= 3600:
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
                logger.info(f'用户 {new_user.username}#{new_user.id} 注册')
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
        if "email" not in user_register_form.cleaned_data or "username" not in user_register_form.cleaned_data:
            # 可能发生前端验证正确，而后端验证不正确（后端更严格），此时clean会直接删除email字段
            # 重复的邮箱、用户名也会被删掉
            errors_dict = json.loads(user_register_form.errors.as_json())
            errors = list(errors_dict.values())[0]
            return JsonResponse({'status': 105, 'msg': errors[0]["message"]})
        else:
            return JsonResponse({'status': 101, 'msg': user_register_form.errors.\
                                as_text().split("*")[-1]})


# 【站长】任命解除管理员
# http://127.0.0.1:8000/userprofile/set_staff/?id=1&is_staff=True
@require_GET
def set_staff(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    user = UserProfile.objects.get(id=request.GET["id"])
    user.is_staff = request.GET["is_staff"]
    logger.info(f'{request.user.id} set_staff {request.GET["id"]} {request.GET["is_staff"]}')
    if request.GET["is_staff"] == "True":
        user.is_staff = True
        user.save()
        logger.info(f'用户 {user.username}#{user.id} 成为管理员')
        return HttpResponse(f"设置\"{user.realname}\"为管理员成功！")
    elif request.GET["is_staff"] == "False":
        user.is_staff = False
        user.save()
        logger.info(f'用户 {user.username}#{user.id} 卸任管理员')
        return HttpResponse(f"解除\"{user.realname}\"的管理员权限！")
    else:
        return HttpResponse("失败！is_staff需要为\"True\"或\"False\"（首字母大写）")

# 【管理员】删除用户的个人信息，从服务器磁盘上完全删除，但不影响是否封禁
# 站长可以删除管理员信息（如果站长也是管理员）。
# http://127.0.0.1:8000/userprofile/del_user_info/?id=1
@require_GET
@staff_required
def del_user_info(request):
    user = UserProfile.objects.get(id=request.GET["id"])
    if user.is_staff and not request.user.is_superuser:
        return HttpResponse("没有删除管理员信息的权限！")
    logger.info(f'管理员 {request.user.username}#{request.user.id} 删除用户 {user.username}#{user.id}')
    user.realname = ""
    user.signature = ""
    if user.avatar:
        if os.path.isfile(user.avatar.path):
            os.remove(user.avatar.path)
    user.avatar = None

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
@require_POST
def get_email_captcha(request):
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
        return JsonResponse({'status': 110, 'msg': email_form.errors.\
                            as_text().split("*")[-1]})

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

# 管理员使用的操作接口，调用方式见前端的StaffView.vue
get_userProfile_fields = ["id", "userms__identifiers", "userms__video_num_limit", "username", "first_name", "last_name", "email", "realname", "signature", "country", "left_realname_n", "left_avatar_n", "left_signature_n", "is_banned"] # 可获取的域列表
@require_GET
@staff_required
def get_userProfile(request):
    userlist = UserProfile.objects.filter(id=request.GET["id"]).values(*get_userProfile_fields)
    if not userlist:
        return HttpResponseNotFound()
    return JsonResponse(userlist[0])

# 管理员使用的操作接口，调用方式见前端的StaffView.vue
set_userProfile_fields = ["userms__identifiers", "userms__video_num_limit", "username", "first_name", "last_name", "email", "realname", "signature", "country", "left_realname_n", "left_avatar_n", "left_signature_n", "is_banned"] # 可修改的域列表
@require_POST
@staff_required
def set_userProfile(request):
    userid = request.POST.get("id")
    user = UserProfile.objects.get(id=userid)
    if user.is_staff and user != request.user:
        return HttpResponseForbidden() # 不能修改除自己以外管理员的信息
    field = request.POST.get("field")
    if field not in set_userProfile_fields:
        return HttpResponseForbidden() # 只能修改特定的域
    if field == "is_banned" and user.is_superuser:
        return HttpResponseForbidden() # 站长不可被封禁
    value = request.POST.get("value")
    logger.warning(f'管理员 {request.user.username}#{request.user.id} 修改用户 {user.username}#{user.id} 域 {field} 从 {getattr(user, field)} 到 {value}')
    setattr(user, field, value)
    user.save()
    return HttpResponse()