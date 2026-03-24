from django.db import models


class UserRecord(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    email = models.CharField(max_length=254, db_index=True)
    name = models.CharField(max_length=255)
