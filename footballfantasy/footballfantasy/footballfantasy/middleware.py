from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings

EXEMPT_URLS = []
if hasattr (settings, 'LOGIN_EXEMPT_URLS'):
    for _url in settings.LOGIN_EXEMPT_URLS:
        if "reset_password" in _url:
            EXEMPT_URLS.append(reverse(_url, kwargs={'uidb64': '0', 'token':'0'}).strip('/'))
        else:
            EXEMPT_URLS.append(reverse(_url).strip('/'))

class UrlsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.strip('/')
        
        if "reset_password" in path:
            url_is_exempt = True 
        else:
            url_is_exempt = any((_url == path) for _url in EXEMPT_URLS)
        user_is_auth = request.user.is_authenticated
       
        if not user_is_auth and not url_is_exempt:
            return redirect('accounts:login')
        return None