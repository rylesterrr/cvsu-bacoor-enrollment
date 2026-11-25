from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow only authenticated users whose role is in ``roles``."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.role in roles:
                return view(request, *args, **kwargs)
            raise PermissionDenied

        return wrapped

    return decorator


def admin_required(view):
    """Allow administrators and superusers."""

    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if request.user.is_administrator:
            return view(request, *args, **kwargs)
        raise PermissionDenied

    return wrapped


student_required = role_required("STUDENT")
