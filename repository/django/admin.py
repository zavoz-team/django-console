from django.contrib import admin

from repository.django.models import AuditEntryRecord


@admin.register(AuditEntryRecord)
class AuditEntryRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'actor_email',
        'action',
        'target_type',
        'target_id',
        'status',
        'created_at',
    )
    search_fields = (
        'actor_email',
        'action',
        'target_type',
        'target_id',
        'trace_id',
    )
    list_filter = (
        'status',
        'target_type',
        'action',
        'created_at',
    )
    readonly_fields = (
        'id',
        'actor_email',
        'action',
        'target_type',
        'target_id',
        'status',
        'payload_json',
        'trace_id',
        'created_at',
    )

