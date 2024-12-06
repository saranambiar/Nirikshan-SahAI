from django import forms

class CertificateUploadForm(forms.Form):
    file = forms.FileField(label="Upload Certificate")