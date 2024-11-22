from django.db import models
from mongoengine import Document, StringField, EmailField
from django import forms
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
