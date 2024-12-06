from django.shortcuts import render, redirect
from django.contrib import messages
import pymongo
from inspection_system.settings import db
from mongoengine import DoesNotExist
from django.contrib.auth.decorators import login_required
from .models import certificate
from .forms import CertificateUploadForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password
from inspection_system.decorators import college_login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import College  # Import the College model

def signup_view(request):
    if request.method == 'POST':
        # Retrieve form data from POST request
        college_name = request.POST.get('college_name')
        college_id = request.POST.get('college_id')
        pin_id = request.POST.get('pin_id')
        email = request.POST.get('email')
        state = request.POST.get('state')
        city = request.POST.get('city')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the college ID already exists
        if College.objects(college_id=college_id).first():
            messages.error(request, 'College already exists. Please try logging in.')
            return redirect('signup')

        # Password match check
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        # Check if email already exists in the database
        if College.objects(email=email).first():
            messages.error(request, 'Email already exists. Please use another email.')
            return redirect('signup')

        # Create a new College document
        try:
            college = College(
                college_name=college_name,
                college_id=college_id,
                pin_id=pin_id,
                email=email,
                state=state,
                city=city,
                password=password,
                approved="Pending"
            )
            college.save()  # Save to the database
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('signup')

        # Success message and redirect to login or another page
        messages.success(request, 'Sign-up successful. You can now log in.')
        return redirect('college_login')

    # If request is not POST, render the signup page
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        college_name = request.POST.get('college_name')
        college_id = request.POST.get('college_code')
        password = request.POST.get('password')

        try:
            # Authenticate the user
            college = College.objects.get(college_name=college_name, college_id=college_id, password=password)

            # Check the approval status
            if college.approved == 'Pending':
                messages.error(request, 'Your college approval is still pending. Contact AICTE for further info.')
                return redirect('college_login')
            elif college.approved == 'Rejected':
                messages.error(request, 'Your college has been rejected. Contact AICTE for further info.')
                return redirect('college_login')
            elif college.approved == 'Approved':
                # Save session data
                request.session['college_name'] = college.college_name
                return redirect('index')  # Redirect to dashboard or index page

        except DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('college_login')

    return render(request, 'college_login.html')



# upload certificates
def upload_certificate(request):
    # Fixed certificate name (example: you can customize it further)
    fixed_certificate_name = "Certificate of Advocate"  # Adjust this based on the certificate type
    college_name = request.session.get('college_name')
    if request.method == 'POST':
        form = CertificateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Capture the file and certificate details
            file = form.cleaned_data['file']
            
            # Create the certificate entry with college metadata and fixed name
            cert = certificate(
                name=fixed_certificate_name,  # Fixed certificate name
                file=file,
                college_name=college_name  # Store the college name or other metadata
            )
            cert.save()

            messages.success(request, 'Certificate uploaded successfully!')
            return redirect('index')  # Redirect to the index page after upload
        else:
            messages.error(request, 'There was an error with the form.')
    else:
        form = CertificateUploadForm()

    return render(request, 'upload_certificate.html', {'form': form})
