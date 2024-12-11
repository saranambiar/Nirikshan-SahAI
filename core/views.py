# core/views.py
from django.shortcuts import render, redirect
from .models import Certificate
from django.contrib import messages
from inspector.models import Feedback

from inspector.models import Feedback

#common
def homepage(request):
    return render(request, 'homepage.html')

def options(request):
    return render(request, 'options.html')



#aicte
def aicte_login(request):
    return render(request, 'aicte/aicte_login.html')

def aictemain(request):
    aicte = request.GET.get('aicte', 'Guest')
    return render(request, 'aicte/aictemain.html',{'aicte': aicte})

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


def annexure(request):
    return render(request,'institute/annexure.html')

def upload_image(request):
    return render(request,'institute/upload_image.html')

def upload_excel(request):
    return render(request,'institute/upload_excel.html')

def classroom_upload(request):
    return render(request,'institute/classroom_upload.html')

def canteen_upload(request):
    return render(request,'institute/canteen_upload.html')

def report3(request):
    return render(request,'institute/report3.html')








#inspector

def view_reports(request):
    user_id = request.GET.get('user_id', 'Guest')
    return render(request, 'inspector/view_reports.html',{'user_id': user_id})


def discussion_forum(request):
    return render(request, 'inspector/discussion_forum.html')

def view_feedback(request):
    college_name = request.session.get('college_name')  # Get college name from session
    if not college_name:
        messages.error(request, "College information is missing!")
        return redirect('college_login')  # Redirect to a default page if college name is not found

    # Retrieve feedback entries for the specific college
    feedback_entry = Feedback.objects.all()
    
    for feedback in feedback_entry:
            print(f"Inspector Name: {feedback.inspector_name}, College Name: {feedback.college_name}, Feedback: {feedback.feedback_text}")

    context = {
        'feedback_entry': feedback_entry,
        'college_name': college_name  # Pass college name to the template
    }
    return render(request, 'feedback_view.html', context)  # Updated template name

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



def report3(request):
    # Fetch all feedback entries or filter as needed
    feedback_entries = Feedback.objects.all()

    # Pass data to the template
    context = {'feedback_entries': feedback_entries}
    return render(request, 'institute/report3.html', context)
