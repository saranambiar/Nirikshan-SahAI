# core/views.py
from django.shortcuts import render, redirect
from .models import Certificate


#common
def homepage(request):
    return render(request, 'homepage.html')

def options(request):
    return render(request, 'options.html')



#aicte
def aicte_login(request):
    return render(request, 'aicte/aicte_login.html')

def aictemain(request):
    return render(request, 'aicte/aictemain.html')

def aicte_institutes(request):
    return render(request, 'aicte/aicte_institutes.html')


def aicte_inspector(request):
    return render(request, 'aicte/aicte_inspector.html')


def aicte_annexure(request):
    return render(request, 'aicte/aicte_annexure.html')



#college

def college_login(request):
    return render(request, 'institute/college_login.html')


def index(request):
    return render(request, 'institute/index.html')

def signup(request):
    return render(request, 'institute/signup.html')

def upload_certificate(request):
    return render(request,'institute/upload_certificate.html')











#inspector

def view_reports(request):
    return render(request, 'inspector/view_reports.html')


def discussion_forum(request):
    return render(request, 'inspector/discussion_forum.html')


def inspector_login(request):
    return render(request, 'inspector/inspector_login.html')

def view_image(request):
    return render(request, 'inspector/view_image.html')

def annexure(request):
    return render(request,'inspector/annexure.html')

def report2(request):
    return render(request,'inspector/report2.html')


def feedback(request):
    return render(request,'inspector/feedback.html')


def pattern_pred(request):
    return render(request,'inspector/pattern_pred.html')


def view_certificates(request):
    certificates = Certificate.objects.all()
    return render(request, 'inspector/view_certificates.html', {'certificates': certificates})


def view_classroom(request):
    return render(request,'inspector/view_classroom.html')


def view_lab(request):
    return render(request,'inspector/view_lab.html')


def view_washroom(request):
    return render(request,'inspector/view_washroom.html')


def view_parking(request):
    return render(request,'inspector/view_parking.html')


def view_pwd(request):
    return render(request,'inspector/view_pwd.html')


def view_canteen(request):
    return render(request,'inspector/view_canteen.html')


