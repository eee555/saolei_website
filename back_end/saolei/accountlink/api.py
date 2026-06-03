from typing import List

from ninja import Router
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from userprofile.decorators import staff_required
from .models import AccountLinkQueue

router = Router()


AccountLinkOut = create_schema(
    AccountLinkQueue,
    fields=[
        'id', 'platform',
        'identifier', 'userprofile',
        'verified',
    ],
)


@router.get('/admin/queue', response=List[AccountLinkOut])
@decorate_view(staff_required)
def get_account_link_queue(request):
    return AccountLinkQueue.objects.all()
