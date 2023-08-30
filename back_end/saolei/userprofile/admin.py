from django.contrib import admin

from .models import EmailVerifyRecord

@admin.register(EmailVerifyRecord)
class EamilVerifyRecordAdmin(admin.ModelAdmin):
    '''Admin View for EamilVerifyRecord'''

    list_display = ('code',)