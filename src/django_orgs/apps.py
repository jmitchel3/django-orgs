from django.apps import AppConfig


class DjangoOrgsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_orgs"
    verbose_name = "Django Organizations"

    def ready(self):
        try:
            import django_orgs.signals  # noqa
        except ImportError:
            pass
