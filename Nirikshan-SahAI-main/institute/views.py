from django.shortcuts import render, redirect
from django.contrib import messages
import pymongo
from inspection_system.settings import db
from mongoengine import DoesNotExist
from django.contrib.auth.decorators import login_required
from core.models import Certificate
from django.views.decorators.http import require_http_methods

from django.contrib.auth.hashers import check_password

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
                request.session['college_id'] = str(college.id)
                return redirect('index')  # Redirect to dashboard or index page

        except DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('college_login')

    return render(request, 'college_login.html')



# upload certificates

@login_required
@require_http_methods(["GET", "POST"])
def upload_certificates(request):
    if request.method == "POST":
        institute = request.user.institute  # Assuming user is linked to institute
        
        certificate_types = [
            'anti_ragging_cert', 'ic_cert', 'ic_report', 'scst_cert',
            'iic_cert', 'abc_cert', 'digital_trans_cert'
        ]
        
        for cert_type in certificate_types:
            if cert_type in request.FILES:
                file = request.FILES[cert_type]
                cert_type_key = cert_type.replace('_cert', '')
                
                # Check if certificate already exists
                existing_cert = Certificate.objects.filter(
                    institute=institute,
                    cert_type=cert_type_key
                ).first()
                
                if existing_cert:
                    existing_cert.file = file
                    existing_cert.status = 'pending'
                    existing_cert.save()
                else:
                    Certificate.objects.create(
                        institute=institute,
                        cert_type=cert_type_key,
                        file=file
                    )
        
        messages.success(request, 'Certificates uploaded successfully')
        return redirect('institute_dashboard')
        
    return render(request, 'institute/upload_certificate.html')
