from .models import AccountSaolei, AccountMinesweeperGames, AccountWorldOfMinesweeper
from datetime import datetime

def update_saolei_account(id):
    account = AccountSaolei.objects.filter(id=id).first()
    if not account:
        account = AccountSaolei.objects.create(id=id)
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()
    return account

def update_msgames_account(id):
    account = AccountMinesweeperGames.objects.filter(id=id).first()
    if not account:
        account = AccountMinesweeperGames.objects.create(id=id)
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()
    return account

def update_wom_account(id):
    account = AccountWorldOfMinesweeper.objects.filter(id=id).first()
    if not account:
        account = AccountWorldOfMinesweeper.objects.create(id=id)
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()
    return account