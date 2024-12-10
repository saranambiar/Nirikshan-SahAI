from django.shortcuts import render, redirect
from django.contrib import messages
import pymongo
from inspection_system.settings import db
from mongoengine import DoesNotExist
from django.contrib.auth.decorators import login_required
from .models import certificate,mandatory_dis
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
    print("E")
    if request.method == 'POST':
        print("POST request received")
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

def upload_mandatory_dis(request):
    if request.method == 'POST':
        print("POST received for mandatory document upload")  # Debugging statement

        # Check if a file is included in the request
        if 'mandatory_doc' not in request.FILES:
            print("HELLO")
            messages.error(request, "No mandatory document uploaded!")
            return redirect('upload_excel')

        college_name = request.session.get('college_name')  # Fetch college name from session

        # Get the uploaded file
        file = request.FILES['mandatory_doc']  # Assuming the input name is 'mandatory_doc'

        # Create and save the mandatory document entry
        try:
            mandatory_document_entry = mandatory_dis(  # Assuming you are using the same model
                name="Mandatory Disclosure",  # You can customize this name as needed
                file=file,
                college_name=college_name  # Add metadata like the college name
            )
            mandatory_document_entry.save()  # Save to the database
            messages.success(request, 'Mandatory document uploaded successfully!')
        except Exception as e:
            messages.error(request, f"Error uploading document: {str(e)}")
            return redirect('upload_excel')

        return redirect('index')  # Redirect to the index or another page after successful upload

    return render(request, 'upload_excel.html')  # Render the upload page if not a POST request


# upload certificates
def upload_certificate(request):
    if request.method == 'POST':
        print("POST received")  # Debugging statement

        # Check if a file is included in the request
        if 'advocate_cert' not in request.FILES:
            print("JKEWNFUwie")
            messages.error(request, "No file uploaded!")
            return redirect('upload_certificate')

        college_name = request.session.get('college_name')  # Fetch college name from session

        names = {
            'anti_ragging_cert': "Anti-Ragging Committee Certificate",
            'internal_committee_cert': "Internal Committee Certificate",
            'annual_ic_report': "Annual Internal Committee Report",
            'scst_committee_cert': "SC/ST Committee Certificate",
            'iic_cert': "Institution’s Innovation Council (IIC) Certificate",
            'abc_cert': "Academic Bank of Credit (ABC) Compliance",
            'digital_transactions_cert': "Digital Transactions Certificate",
            'mental_health_cert': "Mental Health Counselling Center Certificate",
            'internal_assessment_cert': "Internal Assessment and Laboratory Work Compliance Certificate",
            'fire_safety_cert': "Fire and Life Safety Certificate",
            'occupancy_cert': "Approved Plan and Occupancy Certificate",
            'financial_statement_cert': "Audited Financial Statement",
            'advocate_cert': "Certificate of Advocate",
            'architect_cert': "Certificate of Architect Registered with Council of Architecture",
            'bank_manager_cert': "Certificate of the Bank Manager",
            'incorporation_cert': "Certificate of Incorporation",
            'building_cert': "Occupancy/Completion/Building License Certificate",
            'minority_status_cert': "Certificate Regarding Minority Status",
            'architect_details_cert': "Certificate by an Architect",
            'structural_stability_cert': "Structural Stability Certificate",
            'institute_undertaking': "Undertaking by the Institute"
        }


        uploaded_certificates = []


        for field, cert_name in names.items():
            if field in request.FILES:  # Check if the file input exists in the uploaded files
                file = request.FILES[field]  # Get the uploaded file
                uploaded_certificates.append({
                    'certificate_name': cert_name,
                    'file': file
                })
            else:
                # Log or handle missing files if required
                print(f"{cert_name} is missing.")

        # Create and save the certificate
        for cert in uploaded_certificates:
            # Save to the database or perform other processing
            certificate_entry = certificate(
                name=cert['certificate_name'],
                file=cert['file'],
                college_name=request.session.get('college_name')  # Add metadata like the college name
            )
            certificate_entry.save()

        messages.success(request, 'Certificate uploaded successfully!')
        return redirect('index')

    return redirect('upload_certificate')

def college_logout(request):
    request.session.flush()
    return render(request, 'options.html')
