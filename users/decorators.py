from functools import wraps
from django.http import HttpResponseForbidden

def analyst_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Vous devez être connecté")
        # autorise L1, L2 ou superuser (admin)
        if request.user.role not in ['L1', 'L2'] and not request.user.is_superuser:
            return HttpResponseForbidden("Accès réservé aux analystes")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
