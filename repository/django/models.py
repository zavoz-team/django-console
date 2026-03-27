from django.db import models


class UserRecord(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    email = models.CharField(max_length=254, db_index=True)
    name = models.CharField(max_length=255)


class AuditEntryRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    actor_email = models.CharField(max_length=254, db_index=True)
    action = models.CharField(max_length=255, db_index=True)
    target_type = models.CharField(max_length=255, db_index=True)
    target_id = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=64, db_index=True)
    payload_json = models.JSONField()
    trace_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
