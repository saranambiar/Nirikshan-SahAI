from django.apps import AppConfig


class InspectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inspector'


class ProfileOfUserConfig(AppConfig):
    name = 'profile_of_user'
