from django.shortcuts import redirect
from django.contrib import messages


def staff_required(view_func=None, *, login_url='/login/'):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.is_staff:
                if request.user.is_authenticated:
                    messages.error(request, 'Sin permisos de supervisor.')
                return redirect(login_url)
            return view(request, *args, **kwargs)
        return wrapper
    if view_func:
        return decorator(view_func)
    return decorator
