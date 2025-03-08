from django.http import JsonResponse

class ExceptionToResponse(Exception):
    def __init__(self, obj: str, category: str):
        self.obj = obj
        self.category = category

    def response(self):
        return JsonResponse({'type': 'error', 'object': self.obj, 'category': self.category})