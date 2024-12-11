from django.shortcuts import render, redirect
from django.contrib import messages
from mongoengine import DoesNotExist
from django.contrib.auth.decorators import login_required
from core.models import Certificate
from django.views.decorators.http import require_http_methods
from .models import Post, Reply,Inspector
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')

        try:
            # Authenticate the user
            user = Inspector.objects.get(user_id=user_id, password=password)
            # Save session data
            request.session['user_id'] = str(user.user_id)
            return redirect('view_reports')  # Redirect to dashboard
        except DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('inspector_login')

    return render(request, 'inspector/inspector_login.html')

def inspector_logout(request):
    request.session.flush()
    return render(request, 'options.html')



def view_reports(request):
    return render(request, 'inspector/view_reports.html')

# @login_required
# def discussion_forum(request):
#     posts = Post.objects.all().order_by('-timestamp')
#     context = {
#         'posts': posts,
#         'user': request.user,
#     }
#     return render(request, 'inspector/discussion_forum.html', context)

# @login_required
# def view_discussion(request, post_id):
#     post = Post.objects.get(id=post_id)
#     replies = Reply.objects.filter(post=post).order_by('timestamp')
#     context = {
#         'post': post,
#         'replies': replies,
#         'user': request.user,
#     }
#     return render(request, 'inspector/discussion.html', context)

# @login_required
# def create_post(request):
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         if content.strip():  # Check if content is not just whitespace
#             Post.objects.create(
#                 user1=request.user,
#                 post_content=content,
#                 # Remove timestamp=timezone.now() as it's handled by auto_now_add
#             )
#             messages.success(request, 'Post created successfully!')
#         else:
#             messages.error(request, 'Post content cannot be empty!')
#     return redirect('discussion_forum')

# @login_required
# def create_reply(request, post_id):
#     try:
#         post = Post.objects.get(id=post_id)
#         if request.method == 'POST':
#             content = request.POST.get('content')
#             if content.strip():
#                 Reply.objects.create(
#                     user=request.user,
#                     post=post,
#                     reply_content=content,
#                     # Remove timestamp=timezone.now()
#                 )
#                 messages.success(request, 'Reply added successfully!')
#             else:
#                 messages.error(request, 'Reply content cannot be empty!')
#     except Post.DoesNotExist:
#         messages.error(request, 'Post not found!')
#     return redirect('view_discussion', post_id=post_id)


from django.shortcuts import render, redirect
from django.contrib import messages
import pymongo
from inspection_system.settings import db
from institute.models import certificate
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse


from django.shortcuts import get_object_or_404


def view_certificates(request):
    """
    View function for inspectors to view certificates uploaded by institutes
    """

    try:
        # Using MongoEngine to query certificates
        uploaded_certificates = certificate.objects.all()

        # Prepare certificate details
        certificate_details = []
        for cert in uploaded_certificates:
            certificate_details.append({
                'name': cert.name,
                'college_name': cert.college_name,
                'id': str(cert.id)
            })

        return render(request, 'inspector/view_certificates.html',{'certificates': certificate_details})

    except Exception as e:
        # Log the error and show a user-friendly message
        print(f"Error retrieving certificates: {str(e)}")
        messages.error(request, "An error occurred while retrieving certificates")
        return render(request, 'inspector/view_certificates.html')
from django.http import FileResponse, Http404

def download_uploaded_certificate(request, certificate_id):
    """
    Download function for specific uploaded certificate.
    """
    try:
        # Find the specific certificate by ID
        cert = certificate.objects.get(id=certificate_id)

        # Ensure the file field exists and is accessible
        if not cert.file:
            raise ValueError("No file associated with this certificate.")

        # Create a response with the file
        response = FileResponse(cert.file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{cert.name}.pdf"'
        return response

    except certificate.DoesNotExist:
        messages.error(request, "Certificate not found.")
        return redirect('view_certificates')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('view_certificates')
    except Exception as e:
        print(f"Error downloading certificate: {str(e)}")
        messages.error(request, "An error occurred while downloading the certificate.")
        return redirect('view_certificates')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback
def submit_feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        college_name = request.POST.get('college_name')  # Ensure this is passed in the form
        inspector_name = request.session.get('inspector_name')  # Get inspector name from session

        if not inspector_name or not college_name:
            messages.error(request, "Inspector or College information is missing!")
            return redirect('feedback_page')  # Ensure this matches the URL name

        if not feedback_text.strip():
            messages.error(request, "Feedback text cannot be empty!")
            return redirect('feedback_page')

        # Save feedback
        feedback_entry = Feedback(
            inspector_name=inspector_name,
            college_name=college_name,
            feedback_text=feedback_text
        )
        feedback_entry.save()

        messages.success(request, "Feedback submitted successfully!")
        return redirect('feedback_page')  # Ensure this matches the URL name

    return render(request, 'inspector/feedback.html')  # Render the feedback form for GET requests

def feedback_page_view(request):
    return render(request, 'inspector/feedback.html')  # Adjust the template path as needed
