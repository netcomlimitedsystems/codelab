from django.conf import settings

def installed_apps(request):
    return {
        'installed_apps': [app.split('.')[-1] for app in settings.INSTALLED_APPS]
    }