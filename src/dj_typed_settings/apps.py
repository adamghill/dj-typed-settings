from django.apps import AppConfig
from django.core.checks import Tags, register

from dj_typed_settings.validator import validate_settings_check


class DjangoSettingsCheckConfig(AppConfig):
    name = "dj_typed_settings"
    verbose_name = "Django Settings Check"

    def ready(self):
        register(Tags.security)(validate_settings_check)
