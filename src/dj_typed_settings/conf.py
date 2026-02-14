from typing import TYPE_CHECKING, Any

from django.conf import settings as django_settings

from dj_typed_settings.schema import SettingsSchema

if TYPE_CHECKING:

    class Settings(SettingsSchema):
        def __getattr__(self, name: str) -> Any: ...

    settings: Settings
else:

    class Settings:
        def __getattr__(self, name: str) -> Any:
            return getattr(django_settings, name)

    settings = Settings()
