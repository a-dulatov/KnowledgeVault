from django.shortcuts import render

def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view that provides more user-friendly error message
    """
    context = {
        'title': 'CSRF Verification Failed',
        'reason': reason
    }
    return render(request, 'csrf_error.html', context)