from django.db import models
from mongoengine import Document, StringField

class AICTEUser(Document):
    aicte_user = StringField(required=True, unique=True, max_length=100)  # Reflects 'aicte-user'
    password = StringField(required=True, max_length=255)  # Password remains unchanged

    meta = {
        'collection': 'admin',  # MongoDB collection name
    }
