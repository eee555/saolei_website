from ninja import Schema


class ParticipantUserIdOutBase(Schema):
    @staticmethod
    def resolve_user_id(obj) -> int:
        return obj.user_id or 0
