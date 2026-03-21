from django.http import JsonResponse


class ExceptionToResponse(Exception):
    """
    一个自定义异常类，用于将异常信息转换为JSON响应格式。

    核心功能：
    - 存储异常相关的对象和类别信息
    - 提供将异常信息转换为JSON响应的方法

    代码示例：
    try:
        # 一些可能抛出异常的代码
        raise ExceptionToResponse("user", "validation")
    except ExceptionToResponse as e:
        return e.response()

    构造函数参数：
    :param obj: str - 与异常相关的对象名称
    :param category: str - 异常的类别或类型

    使用限制：
    - 该类主要用于Web应用中处理需要返回JSON格式错误信息的场景
    - response()方法返回的JsonResponse需要Django框架支持
    """
    def __init__(self, obj: str, category: str):
        self.obj = obj
        self.category = category

    def response(self):
        return JsonResponse({'type': 'error', 'object': self.obj, 'category': self.category})
