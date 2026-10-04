from django.utils import timezone
from ninja import Schema


class ParticipantOutBase(Schema):
    @staticmethod
    def resolve_user_id(obj) -> int:
        return obj.user_id or 0

    @staticmethod
    def resolve_token(obj) -> str:
        return obj.token if obj.start_time <= timezone.now() else ''
