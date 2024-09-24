from .models import AccountSaolei, AccountMinesweeperGames, AccountWorldOfMinesweeper, Platform
from datetime import datetime
from userprofile.models import UserProfile

def update_account(platform: Platform, id, user: UserProfile | None):
    if platform == Platform.SAOLEI:
        update_saolei_account(id, user)
    elif platform == Platform.MSGAMES:
        update_msgames_account(id, user)
    elif platform == Platform.WOM:
        update_wom_account(id, user)
    else:
        ValueError()

def delete_account(user: UserProfile, platform: Platform):
    if platform == Platform.SAOLEI:
        user.account_saolei.delete()
    elif platform == Platform.MSGAMES:
        user.account_msgames.delete()
    elif platform == Platform.WOM:
        user.account_wom.delete()
    else:
        ValueError()

def update_saolei_account(id, user: UserProfile | None):
    account = AccountSaolei.objects.filter(id=id).first()
    if not account:
        account = AccountSaolei.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()

def update_msgames_account(id, user: UserProfile | None):
    account = AccountMinesweeperGames.objects.filter(id=id).first()
    if not account:
        account = AccountMinesweeperGames.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()

def update_wom_account(id, user: UserProfile | None):
    print(user)
    account = AccountWorldOfMinesweeper.objects.filter(id=id).first()
    if not account:
        account = AccountWorldOfMinesweeper.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()