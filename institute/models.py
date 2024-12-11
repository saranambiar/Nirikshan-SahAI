from django.db import models
from mongoengine import Document, StringField, EmailField, FileField
from django import forms
from django.utils.timezone import now

class College(Document):
    college_name = StringField(required=True)
    college_id = StringField(required=True, unique=True)
    pin_id = StringField(required=True)
    email = EmailField(required=True, unique=True)
    state = StringField(required=True)
    city = StringField(required=True)
    password = StringField(required=True)
    approved = StringField()

    meta = {
        'collection': 'college'  # Maps to the "college" collection in MongoDB
    }

class CollegeForm(forms.Form):
    college_name = forms.CharField(max_length=100, required=True, label="College Name")
    college_id = forms.CharField(max_length=100, required=True, label="College ID")
    pin_id = forms.CharField(max_length=10, required=True, label="PIN ID")
    email = forms.EmailField(required=True, label="Email")
    state = forms.CharField(max_length=100, required=True, label="State")
    city = forms.CharField(max_length=100, required=True, label="City")
    approved = forms.ChoiceField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], required=True, label="Approval Status")

class certificate(Document):
    name = StringField(required=True) 
    file = FileField(required=True)
    college_name = StringField(required=True)
    field_name = StringField(required=True) 

    meta = {
        'collection': 'certificate_unverified'
    }
    
    def url(self):
        # Ensure the URL is returned from the correct file field
        return self.file.url if self.file else None

class mandatory_dis(Document):
    name = StringField(required=True) 
    file = FileField(required=True)
    college_name = StringField(required=True)

    meta = {
        'collection': 'mandatory_disclosure'
    }


from datetime import datetime

from mongoengine import Document, StringField, DateTimeField

