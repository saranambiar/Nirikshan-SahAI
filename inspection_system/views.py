from django.shortcuts import render

def index(request):
    college_name = request.GET.get('college_name', 'Guest')  # Fallback to 'Guest' if not provided
    return render(request, 'index.html', {'college_name': college_name})

def upload_certificate(request):
    college_name = request.GET.get('college_name', 'Guest')
    return render(request, 'index.html', {'college_name': college_name})