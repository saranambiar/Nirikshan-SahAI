from django.shortcuts import render, redirect
from django.contrib import messages
import pymongo
from django.http import JsonResponse
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
from django.shortcuts import render
from inspector.models import Feedback
import requests
import cloudinary.uploader

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

        fastapi_url = "http://localhost:8000/process-mandatory-disclosure/"

        # Get the uploaded file
        file = request.FILES['mandatory_doc']  # Assuming the input name is 'mandatory_doc'
        intake = request.POST.get("college_intake")

        # Create and save the mandatory document entry
        try:
            mandatory_document_entry = mandatory_dis(  # Assuming you are using the same model
                name="Mandatory Disclosure",  # You can customize this name as needed
                file=file,
                college_name=college_name,  # Add metadata like the college name
                college_intake=intake
            )
            mandatory_document_entry.save()  # Save to the database
            messages.success(request, 'Mandatory document uploaded successfully!')

            data = {    
                "college_name": college_name,
                "intake":intake
            }

            # Send the data to FastAPI
            response = requests.post(fastapi_url, json=data)

            # Handle FastAPI's response
            if response.status_code == 200:
                messages.success(request, "Mandatory disclosure processed successfully.")
            else:
                messages.error(request, f"FastAPI returned an error: {response.status_code}, details: {response.json()}")

            return redirect('index')  # Redirect to the index or another page after successful upload
        except Exception as e:
            messages.error(request, f"Error uploading document: {str(e)}")
            return redirect('upload_excel')

    return render(request, 'upload_excel.html')


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


def view_feedback(request):
    college_name = request.session.get('college_name')  # Get college name from session
    if not college_name:
        messages.error(request, "College information is missing!")
        return redirect('college_login')  # Redirect to a default page if college name is not found

    # Retrieve feedback entries for the specific college
    feedback_entry = Feedback.objects.all()

    context = {
        'feedback_entry': feedback_entry,
        'college_name': college_name  # Pass college name to the template
    }
    return render(request, 'inspector/feedback_view.html', context)  # Updated template name

from django.shortcuts import redirect
from django.http import FileResponse, Http404
from django.contrib import messages
from inspector.models import Feedback

def download_manual_report(request, feedback_id):
    """
    Download the manual report uploaded by the inspector.
    """
    try:
        # Fetch the feedback document by ID
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        messages.error(request, "Feedback entry not found.")
        return redirect('report3')  # Redirect to the appropriate page if feedback does not exist

    # Check if the manual report exists
    if not feedback.manual_report:
        messages.error(request, "No manual report associated with this feedback.")
        return redirect('report3')  # Redirect to the appropriate page if no manual report

    try:
        # Serve the manual report as a file response
        response = FileResponse(feedback.manual_report, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{feedback.college_name}_report.pdf"'
        return response
    except Exception as e:
        print(f"Error downloading report: {e}")
        messages.error(request, "An error occurred while downloading the report.")
        return redirect('report3')




#clodinary

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine import DoesNotExist
import cloudinary
from .models import Images, College

@csrf_exempt
def u_i(request):
    if request.method == 'POST':
        print("Request received")  # Debugging: Confirm request received

        uploaded_files = request.FILES.getlist('image')  # Get all uploaded files
        route = request.POST.get('route')  # Get the route sent from the frontend
        college_id = request.POST.get('college_id')  # Get the college ID from the POST data
        branch = request.POST.get('branch')  # Get the branch from the POST data
        itbk = request.POST.get('itbk')  # Get the intake of branch from the POST data
        nod = request.POST.get('nod')  # Get the number of divisions from the POST data
        nob = request.POST.get('nob')  # Get the number of batches from the POST data

        print(f"Route: {route}")  # Log route
        print(f"College ID: {college_id}")  # Debugging: Log college_id

        if not uploaded_files or not route or not college_id:
            print("Missing required parameters")
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        try:
            # Query the database for the College record
            try:
                college = College.objects.get(college_id=college_id)
            except DoesNotExist:
                print("College not found")
                return JsonResponse({'error': 'College not found'}, status=404)

            # Map full routes to the correct database fields
            route_to_field_map = {
                '/classroom_upload/': 'classroom',
                '/lab_upload/': 'lab',
                '/canteen_upload/': 'canteen',
                '/pwd_upload/': 'pwd',
                '/parking_upload/': 'parking',
                '/washroom_upload/': 'washroom',
            }

            target_field = route_to_field_map.get(route)
            if not target_field:
                print("Invalid route")
                return JsonResponse({'error': 'Invalid route or upload type'}, status=400)

            # Check if the images document for the college already exists
            images_entry = Images.objects(college=college.college_name).first()
            if not images_entry:
                # If it doesn't exist, create a new one
                images_entry = Images(college=college.college_name)

            # Create a unique key for the upload data
            upload_key = f"{branch}{itbk}{nod}_{nob}"

            # Initialize the upload data if it doesn't exist
            if not hasattr(images_entry, target_field):
                setattr(images_entry, target_field, [])

            # Find the existing upload data object or create a new one
            existing_upload_data = next((item for item in getattr(images_entry, target_field) if item['branch'] == branch and item['itbk'] == itbk and item['nod'] == nod and item['nob'] == nob), None)

            if existing_upload_data is None:
                # Create a new upload data object if it doesn't exist
                existing_upload_data = {
                    'branch': branch,
                    'itbk': itbk,
                    'nod': nod,
                    'nob': nob,
                    'url': []  # Initialize the URL list
                }
                getattr(images_entry, target_field).append(existing_upload_data)

            # Process each uploaded file
            for uploaded_file in uploaded_files:
                # Upload file to Cloudinary
                upload_result = cloudinary.uploader.upload(uploaded_file)
                file_url = upload_result.get('url')
                print(f"Uploaded file URL: {file_url} (Length: {len(file_url)})")  # Debugging: Check URL length

                # Append the uploaded file URL to the existing upload data's url list
                existing_upload_data['url'].append(file_url)

            # Save the images entry to the database
            images_entry.save()
            print("Images entry saved successfully.")

            return JsonResponse({'message': 'Files uploaded successfully', 'uploaded_data': existing_upload_data}, status=200)

        except Exception as e:
            print(f"Error during file upload: {e}")
            return JsonResponse({'error': 'An error occurred during file upload'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)