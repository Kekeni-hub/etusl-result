from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout


def require_profile(profile_attr, login_url='home'):
    """Decorator that requires a logged-in user to have a given profile attribute.

    - If not authenticated: redirects to `login_url` with a warning.
    - If authenticated but missing the profile attribute: logs out the user,
      shows a warning and redirects to `home`.

    Usage: @require_profile('lecturer_profile', login_url='lecturer_login')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'You must be logged in to access that page.')
                return redirect(login_url)

            if not hasattr(request.user, profile_attr):
                # Clear session to avoid role confusion and warn the user
                try:
                    logout(request)
                except Exception:
                    pass
                messages.warning(request, 'You do not have permission to view that page.')
                return redirect('home')

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
