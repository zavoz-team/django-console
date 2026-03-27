from django.contrib import admin

from repository.django.models import AuditEntryRecord, UserRecord

admin.site.register(UserRecord)
admin.site.register(AuditEntryRecord)
