from django.apps import AppConfig

class GameloginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gameLogin'
    # This function is the only new thing in this file
    # it just imports the signal file when the app is ready

 