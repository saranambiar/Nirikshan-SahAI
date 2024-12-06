
from django.db import models
from django.contrib.auth.models import User

class Certificate(models.Model):
    name = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=255)
    file_url = models.URLField()
    upload_date = models.DateTimeField(auto_now_add=True)

