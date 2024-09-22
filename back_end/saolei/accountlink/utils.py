from .models import AccountSaolei

def update_saolei_account(id):
    account = AccountSaolei.objects.filter(id=id).first()
    if not account:
        account = AccountSaolei.objects.create(id=id)
    # 给account的各attribute赋值
    account.save()