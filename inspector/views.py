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
            request.session['inspector_id'] = str(user.id)
            return redirect('view_reports')  # Redirect to dashboard
        except DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('inspector_login')

    return render(request, 'inspector/inspector_login.html')

@login_required
def view_certificates(request):
    certificates = Certificate.objects.all().order_by('-upload_date')
    
    # Filter by institute if specified
    institute_id = request.GET.get('institute')
    if institute_id:
        certificates = certificates.filter(institute_id=institute_id)
    
    # Filter by certificate type
    cert_type = request.GET.get('type')
    if cert_type:
        certificates = certificates.filter(cert_type=cert_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        certificates = certificates.filter(status=status)
    
    context = {
        'certificates': certificates,
        'certificate_types': dict(Certificate.CERTIFICATE_TYPES),
        'statuses': dict(Certificate.STATUS_CHOICES),
    }
    return render(request, 'inspector/view_certificates.html', context)

@login_required
def certificate_detail(request, certificate_id):
    certificate = Certificate.objects.get(id=certificate_id)
    if request.method == "POST":
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        certificate.status = status
        certificate.remarks = remarks
        certificate.save()
        
        messages.success(request, 'Certificate status updated successfully')
        return redirect('view_certificates')
    
    return render(request, 'inspector/certificate_detail.html', {
        'certificate': certificate
    })





def view_reports(request):
    return render(request, 'inspector/view_reports.html')

@login_required
def discussion_forum(request):
    posts = Post.objects.all().order_by('-timestamp')
    context = {
        'posts': posts,
        'user': request.user,
    }
    return render(request, 'inspector/discussion_forum.html', context)

@login_required
def view_discussion(request, post_id):
    post = Post.objects.get(id=post_id)
    replies = Reply.objects.filter(post=post).order_by('timestamp')
    context = {
        'post': post,
        'replies': replies,
        'user': request.user,
    }
    return render(request, 'inspector/discussion.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():  # Check if content is not just whitespace
            Post.objects.create(
                user1=request.user,
                post_content=content,
                # Remove timestamp=timezone.now() as it's handled by auto_now_add
            )
            messages.success(request, 'Post created successfully!')
        else:
            messages.error(request, 'Post content cannot be empty!')
    return redirect('discussion_forum')

@login_required
def create_reply(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.method == 'POST':
            content = request.POST.get('content')
            if content.strip():
                Reply.objects.create(
                    user=request.user,
                    post=post,
                    reply_content=content,
                    # Remove timestamp=timezone.now()
                )
                messages.success(request, 'Reply added successfully!')
            else:
                messages.error(request, 'Reply content cannot be empty!')
    except Post.DoesNotExist:
        messages.error(request, 'Post not found!')
    return redirect('view_discussion', post_id=post_id)