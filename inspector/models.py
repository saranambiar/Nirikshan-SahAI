# models.py
from django.db import models
from django.contrib.auth.models import User
from mongoengine import Document,StringField,ListField
from mongoengine import Document, StringField, EmailField, FileField
from django import forms
from mongoengine import  ReferenceField, DateTimeField
from django.utils.timezone import now

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
    college = StringField(required=False)

    meta = {
        'collection': 'inspector'  # Maps to the "inspector" collection in MongoDB
    }


from datetime import datetime

from mongoengine import Document, StringField, DateTimeField

class Feedback(Document):
    inspector_name = StringField(required=True)
    college_name = StringField(required=True)
    feedback_text = StringField(required=True, max_length=2000)  # Adjust max_length as needed
    created_at = DateTimeField(default=datetime.utcnow)
    def __str__(self):
        return f"Feedback from {self.inspector_name} for {self.college_name}"
