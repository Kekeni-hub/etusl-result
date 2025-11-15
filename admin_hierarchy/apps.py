from django.apps import AppConfig


class AdminHierarchyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_hierarchy'

    def ready(self):
        """Import signals when app is ready"""
        import admin_hierarchy.signals  # noqa
