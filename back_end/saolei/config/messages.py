from .global_settings import MaxSizes


class GeneralErrors:
    def stringsize(number, hilo, item=""):
        f'{item}不能{"超过" if hilo else "少于"}{number}个字符！'

    def empty(item=""):
        f'{item}不能为空！'


class FormErrors:
    email = {
        'max_length': GeneralErrors.stringsize(MaxSizes.EMAIL, True),
        'required': GeneralErrors.empty("邮箱"),
        'invalid': '邮箱格式错误！',
    }
    password = {
        'max_length': GeneralErrors.stringsize(MaxSizes.PASSWORD, True),
        'min_length': GeneralErrors.stringsize(MaxSizes.PASSWORD, False),
    }
    username = {
        'max_length': GeneralErrors.stringsize(MaxSizes.USERNAME, True),
        'required': GeneralErrors.empty("用户名"),
        'invalid': "非法用户名！",
    }
