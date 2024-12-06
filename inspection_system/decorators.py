from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def college_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'college_id' not in request.session:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('college_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view