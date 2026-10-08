from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def verified_user_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_verified:
            messages.warning(request, "Necesitas verificar tu cuenta")
            return redirect('accounts:profile')
        return view_func(request, *args, **kwargs)
    return wrapped