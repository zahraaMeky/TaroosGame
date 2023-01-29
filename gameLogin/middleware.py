from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from .models import extend_user
import time
from django.core.cache import cache
from importlib import import_module

class SessionIdleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if 'last_request' in request.session:
                elapsed = time.time() - request.session['last_request']
                if elapsed > settings.AUTO_LOGOUT_DELAY:
                    current_user = request.user.id
                    retrieve_obj_id = extend_user.objects.filter(id=current_user)
                    retrieve_obj_id.update(user_id=current_user,is_login=0, IP='')
                    del request.session['last_request'] 
                    auth.logout(request)
                    # flushing the complete session is an option as well!
                    # request.session.flush()  
            request.session['last_request'] = time.time()
        else:
            if 'last_request' in request.session:
                del request.session['last_request']

        response = self.get_response(request)

        return response

