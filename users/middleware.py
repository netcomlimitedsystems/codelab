# users/middleware.py
from django.utils import translation
from django.conf import settings

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and has a language preference
        if request.user.is_authenticated:
            try:
                user_language = request.user.profile.language
                if user_language in [lang[0] for lang in settings.LANGUAGES]:
                    translation.activate(user_language)
                    request.LANGUAGE_CODE = user_language
            except:
                # Use default language if any error occurs
                pass
        
        response = self.get_response(request)
        return response