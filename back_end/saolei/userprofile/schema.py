from ninja.orm import create_schema

from .models import UserProfile


UserInfoOut = create_schema(
    UserProfile,
    fields=[
        'id', 'username',
        'firstname', 'lastname', 'realname',
        'signature', 'country',
        'is_banned', 'is_staff',
        'last_change_avatar', 'last_change_signature',
        'left_avatar_n', 'left_signature_n',
    ],
)
