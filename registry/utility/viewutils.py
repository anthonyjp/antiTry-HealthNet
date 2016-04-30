from functools import wraps

from django.shortcuts import get_object_or_404
from django.http import QueryDict, HttpResponseNotAllowed
from django.utils.decorators import available_attrs
from registry.models import User


def require_http_methods_not_none(request_method_list, *required):
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if request.method in request_method_list and len([x for x in required if x not in kwargs]) > 0:
                return HttpResponseNotAllowed(request_method_list)
            return func(request, *args, **kwargs)

        return inner

    return decorator


def ajax_success(**kwargs):
    kwargs.update({'success': True})
    return kwargs


def ajax_failure(**kwargs):
    kwargs.update({'success': False})
    return kwargs


def get_user_or_404(uuid):
    return User.objects.get_subclass(pk=get_object_or_404(User, pk=uuid).pk)


def is_safe_request(method):
    while hasattr(method, 'method'):
        method = method.method
    return method in ('GET', 'HEAD')


def read_request_body_to_post(request):
    request.POST = QueryDict(request.body)


def read_request_body_to(request, method='POST'):
    setattr(request, method, QueryDict(request.body))
