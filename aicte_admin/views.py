from django.shortcuts import render, redirect, get_object_or_404
from .models import AICTEUser
from django.contrib import messages
from mongoengine import DoesNotExist  
from inspector.models import Inspector
from inspection_system.settings import db
from .forms import InspectorForm
from django.http import Http404,JsonResponse
from institute.models import College,CollegeForm
from bson import ObjectId

# collection=db['admin']
def login_view(request):
    if request.method == 'POST':
        # Get username and password from the form
        username = request.POST.get('aicte-user')  
        password = request.POST.get('login-pass')  

        try:
            # Authenticate the user by fetching from the AICTEUser model
            user = AICTEUser.objects.get(aicte_user=username, password=password)
            
            # If the user is found, login is successful
            messages.success(request, 'Login successful!')
            return redirect('aictemain') 

        except DoesNotExist:
            # Authentication failed, show an error message
            messages.error(request, 'Invalid credentials, please try again.')

        return redirect('aicte_login')

    return render(request, 'aicte_login.html')
# List all inspectors
def inspector_list(request):
    inspectors = Inspector.objects.all()  
    return render(request, 'aicte/aicte_inspector.html', {'inspectors': inspectors})

# Create a new inspector
def inspector_create(request):
    if request.method == 'POST':
        form = InspectorForm(request.POST)
        if form.is_valid():
            # Manually save the data to MongoDB
            inspector = Inspector(
                user_id=form.cleaned_data['user_id'],
                password=form.cleaned_data['password']
            )
            inspector.save()
            return redirect('inspector_list')
    else:
        form = InspectorForm()

    return render(request, 'aicte/aicte_inspector.html', {'form': form})

# View inspector details
def inspector_detail(request, pk):
    try:
        inspector = Inspector.objects.get(id=pk)
        # Return JSON response for AJAX requests
        return JsonResponse({
            'user_id': inspector.user_id,
            'password': inspector.password,
        })
    except Inspector.DoesNotExist:
        return JsonResponse({'error': 'Inspector not found'}, status=404)

# Update an inspector
def inspector_update(request, pk):
    try:
        inspector = Inspector.objects.get(id=pk)
    except Inspector.DoesNotExist:
        raise Http404("Inspector does not exist")

    if request.method == 'POST':
        # Update inspector details
        inspector.user_id = request.POST.get('user_id')
        inspector.password = request.POST.get('password')
        inspector.save()
        return redirect('inspector_list')  

    return render(request, 'aicte/aicte_inspector.html', {'inspector': inspector})


# Delete an inspector
def inspector_delete(request, pk):
    try:
        inspector = Inspector.objects.get(id=pk)
    except Inspector.DoesNotExist:
        raise Http404("Inspector does not exist")

    inspector.delete()
    return redirect('inspector_list')


def institute_list(request):
    institutes = College.objects.all()
    return render(request, 'aicte/aicte_institutes.html', {'institutes': institutes})

def institute_detail(request, pk):
    try:
        institute = College.objects.get(id=ObjectId(pk))  # Fetch using ObjectId
    except College.DoesNotExist:
        raise Http404("Institute does not exist")
    return render(request, 'aicte/aicte_institutes.html', {'institute': institute})

def institute_update(request, pk):
    try:
        # Fetch the college (institute) instance by primary key
        institute = College.objects.get(id=ObjectId(pk))
    except College.DoesNotExist:
        raise Http404("Institute does not exist")

    if request.method == 'POST':
        # Update college information with the POST data
        institute.college_name = request.POST.get('college_name')
        institute.college_code = request.POST.get('college_code')
        institute.email = request.POST.get('email')
        institute.pin_id = request.POST.get('pin_id')
        institute.state = request.POST.get('state')
        institute.city = request.POST.get('city')
        institute.approved = request.POST.get('approved')
        institute.save()

        return redirect('institute_list')  # Redirect after successful update

    return render(request, 'aicte/aicte_institutes.html', {'institute': institute})