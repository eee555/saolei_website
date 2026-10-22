from ninja import Schema
from ninja.orm import create_schema

from .models import UserProfile


USER_INFO_FIELDS = [
    'id', 'username',
    'signature', 'country',
    'is_banned', 'is_staff',
    'last_change_avatar', 'last_change_signature',
    'left_avatar_n', 'left_signature_n',
]
PUBLIC_NAME_FIELDS = [('realname', str, ...), ('firstname', str, ...), ('lastname', str, ...)]


class RawUserNames(Schema):
    @staticmethod
    def resolve_realname(user):
        return user._realname

    @staticmethod
    def resolve_firstname(user):
        return user._firstname

    @staticmethod
    def resolve_lastname(user):
        return user._lastname


UserInfoOut = create_schema(
    UserProfile, name='UserInfoOut', fields=USER_INFO_FIELDS, custom_fields=PUBLIC_NAME_FIELDS,
)
SelfUserInfoOut = create_schema(
    UserProfile, name='SelfUserInfoOut', fields=[*USER_INFO_FIELDS, 'can_hide_realname', 'hide_realname'],
    custom_fields=PUBLIC_NAME_FIELDS, base_class=RawUserNames,
)
