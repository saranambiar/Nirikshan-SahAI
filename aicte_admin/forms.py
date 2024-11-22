from django import forms
from inspector.models import Inspector

class InspectorForm(forms.Form):
    user_id = forms.CharField(max_length=255, required=True, label="User ID")
    password = forms.CharField(widget=forms.PasswordInput, max_length=255, required=True, label="Password")