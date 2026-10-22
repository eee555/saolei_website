from django.db import transaction

from msuser.models import UserMS
from userprofile.models import UserProfile
from userprofile.utils import validate_name


@transaction.atomic
def register_users(users: list[dict]):
    for user in users:
        validate_name(user['realname'])
    return [UserProfile.objects.create_user(userms=UserMS.objects.create(), **user) for user in users]
