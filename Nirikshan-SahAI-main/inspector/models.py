# models.py
from django.db import models
from django.contrib.auth.models import User
from mongoengine import Document,StringField

class Post(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE)
    post_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    reply_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = 'Replies'

class Inspector(Document):
    user_id = StringField(required=True, unique=True)
    password = StringField(required=True)

    meta = {
        'collection': 'inspector'  # Maps to the "inspector" collection in MongoDB
    }